"""Run a prepared Python renderer and package its reproducible delivery bundle."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import inspect
import json
import shutil
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.figure_brief import FigureBrief, load_figure_brief  # noqa: E402
from figure_studio.nature_adapter import build_nature_context  # noqa: E402

REQUIRED_FORMATS = ("png", "svg", "pdf")
REVIEW_STATUSES = {"not_reviewed", "needs_revision", "passed"}
INVOCATION_STATUSES = {
    "not_verified",
    "explicitly_loaded_in_codex_session",
    "not_required",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_for_delivery(source: Path, target: Path, *, overwrite: bool = False) -> Path:
    source = source.expanduser().resolve()
    target = target.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"delivery source does not exist: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.resolve() == source:
            return target
        if _sha256(source) == _sha256(target):
            return target
        if not overwrite:
            raise FileExistsError(f"refusing to replace delivery file: {target}")
    shutil.copy2(source, target)
    return target


def _prepare_manifest_for_delivery(
    source: Path,
    target: Path,
    data_path: Path | None,
    *,
    overwrite: bool = False,
) -> Path:
    """Copy a manifest without leaving a package-dependent source path."""

    if data_path is None:
        return _copy_for_delivery(source, target, overwrite=overwrite)

    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("manifest JSON must contain an object")
    raw["data_file"] = data_path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FileExistsError(f"refusing to replace delivery file: {target}") from exc
        if existing == raw:
            return target
        if not overwrite:
            raise FileExistsError(f"refusing to replace delivery file: {target}")
    _write_json(target, raw)
    return target


def _load_renderer(renderer: str | Path) -> tuple[ModuleType, Path, str]:
    renderer_path = Path(renderer).expanduser()
    if renderer_path.is_file():
        source = renderer_path.resolve()
        module_name = f"_figure_task_renderer_{hashlib.sha1(str(source).encode()).hexdigest()[:12]}"
        sys.path.insert(0, str(source.parent))
        try:
            spec = importlib.util.spec_from_file_location(module_name, source)
            if spec is None or spec.loader is None:
                raise ImportError(f"cannot load renderer file: {source}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        finally:
            if sys.path[0] == str(source.parent):
                sys.path.pop(0)
        return module, source, str(source)

    module = importlib.import_module(str(renderer))
    source_value = getattr(module, "__file__", None)
    if source_value is None:
        raise ValueError(f"renderer module has no source file: {renderer}")
    return module, Path(source_value).resolve(), str(renderer)


def _call_renderer(
    module: ModuleType,
    output_dir: Path,
    data_path: Path | None,
    manifest_path: Path | None,
    nature_skill_root: Path | None,
    overwrite: bool,
) -> object:
    renderer_main = getattr(module, "main", None)
    if not callable(renderer_main):
        raise AttributeError("renderer must expose a callable main()")
    candidate_kwargs: dict[str, object] = {
        "output_dir": output_dir,
        "data_path": data_path,
        "manifest_path": manifest_path,
        "skill_root": nature_skill_root,
        "overwrite": overwrite,
    }
    parameters = inspect.signature(renderer_main).parameters
    accepts_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    kwargs = (
        candidate_kwargs
        if accepts_kwargs
        else {key: value for key, value in candidate_kwargs.items() if key in parameters}
    )
    return renderer_main(**kwargs)


def _normalise_output_paths(result: object, output_dir: Path) -> dict[str, Path]:
    values: list[Path] = []
    if isinstance(result, Mapping):
        values = [Path(value) for value in result.values()]
    elif isinstance(result, (list, tuple, set)):
        values = [Path(value) for value in result]
    elif result is not None:
        raise TypeError("renderer main() must return a mapping, sequence, or None")

    if not values:
        values = [
            path
            for path in output_dir.iterdir()
            if path.is_file() and path.suffix.lower().lstrip(".") in REQUIRED_FORMATS
        ]
    output_root = output_dir.resolve()
    by_format: dict[str, Path] = {}
    for value in values:
        path = value.expanduser().resolve()
        try:
            path.relative_to(output_root)
        except ValueError as exc:
            raise ValueError(f"renderer output is outside output_dir: {path}") from exc
        if not path.is_file():
            raise FileNotFoundError(f"renderer did not create output: {path}")
        format_name = path.suffix.lower().lstrip(".")
        if format_name in REQUIRED_FORMATS:
            by_format[format_name] = path
    missing = sorted(set(REQUIRED_FORMATS).difference(by_format))
    if missing:
        raise ValueError(f"renderer must export PNG, SVG, and PDF; missing {missing}")
    return by_format


def _relative_label(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": _relative_label(path, root),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _prepare_delivery_sources(
    renderer_source: Path,
    brief_path: Path,
    manifest_path: Path | None,
    data_path: Path | None,
    output_dir: Path,
    *,
    overwrite: bool = False,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "plot.py": _copy_for_delivery(
            renderer_source, output_dir / "plot.py", overwrite=overwrite
        ),
        "figure_brief.json": _copy_for_delivery(
            brief_path, output_dir / "figure_brief.json", overwrite=overwrite
        ),
    }
    sibling_config = renderer_source.with_name("config.py")
    if sibling_config.is_file():
        files["config.py"] = _copy_for_delivery(
            sibling_config, output_dir / "config.py", overwrite=overwrite
        )
    if manifest_path is not None:
        files["data_manifest.json"] = _prepare_manifest_for_delivery(
            manifest_path,
            output_dir / "data_manifest.json",
            data_path,
            overwrite=overwrite,
        )
    if data_path is not None:
        files[data_path.name] = _copy_for_delivery(
            data_path, output_dir / data_path.name, overwrite=overwrite
        )
    return files


def _prepare_runtime_manifest(
    manifest_path: Path | None,
    data_path: Path | None,
    output_dir: Path,
) -> Path | None:
    """Create a temporary self-contained manifest for legacy renderer contracts."""

    if manifest_path is None or data_path is None:
        return manifest_path
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("manifest JSON must contain an object")
    raw["data_file"] = data_path.name
    runtime_path = output_dir / ".runtime_data_manifest.json"
    _write_json(runtime_path, raw)
    return runtime_path


def _ensure_output_space(output_dir: Path, *, overwrite: bool) -> None:
    """Protect existing rendered files even when a renderer ignores overwrite."""

    if overwrite or not output_dir.is_dir():
        return
    existing = sorted(
        path.name
        for path in output_dir.iterdir()
        if path.is_file() and path.suffix.lower().lstrip(".") in REQUIRED_FORMATS
    )
    if existing:
        raise FileExistsError(f"refusing to replace existing render outputs: {existing}")


def run_figure_task(
    *,
    renderer: str | Path,
    brief_path: str | Path,
    output_dir: str | Path,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    nature_skill_root: str | Path | None = None,
    review_status: str = "not_reviewed",
    review_notes: tuple[str, ...] = (),
    host_skill_invocation_status: str = "not_verified",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Execute one renderer and write an auditable delivery receipt."""

    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"review_status must be one of: {sorted(REVIEW_STATUSES)}")
    if host_skill_invocation_status not in INVOCATION_STATUSES:
        raise ValueError(
            "host_skill_invocation_status must be one of: "
            f"{sorted(INVOCATION_STATUSES)}"
        )

    brief_file = Path(brief_path).expanduser().resolve()
    destination = Path(output_dir).expanduser().resolve()
    data_file = Path(data_path).expanduser().resolve() if data_path else None
    manifest_file = Path(manifest_path).expanduser().resolve() if manifest_path else None
    skill_root = Path(nature_skill_root).expanduser().resolve() if nature_skill_root else None
    brief: FigureBrief = load_figure_brief(brief_file)
    if data_file is not None and not data_file.is_file():
        raise FileNotFoundError(f"data file does not exist: {data_file}")
    if manifest_file is not None and not manifest_file.is_file():
        raise FileNotFoundError(f"manifest file does not exist: {manifest_file}")
    if brief.nature_references and skill_root is None:
        raise ValueError("nature_skill_root is required when nature_references are requested")

    module, renderer_source, _renderer_label = _load_renderer(renderer)
    packaged_sources = _prepare_delivery_sources(
        renderer_source,
        brief_file,
        manifest_file,
        data_file,
        destination,
        overwrite=overwrite,
    )
    _ensure_output_space(destination, overwrite=overwrite)
    runtime_manifest = _prepare_runtime_manifest(manifest_file, data_file, destination)

    nature_context: dict[str, Any] | None = None
    if brief.nature_references:
        nature_context = build_nature_context(
            skill_root,
            references=tuple(brief.nature_references),
        )
        nature_context = {
            **nature_context,
            "skill_root": "<installed nature-figure skill>",
            "host_skill_invocation_required": True,
            "host_skill_invocation_status": host_skill_invocation_status,
            "host_skill_invocation_note": (
                "This field is a manual Codex-session attestation; Python file "
                "verification is not proof of host Skill execution."
            ),
        }
        _write_json(destination / "nature_context.json", nature_context)

    try:
        result = _call_renderer(
            module,
            destination,
            data_file,
            runtime_manifest,
            skill_root,
            overwrite,
        )
    finally:
        if runtime_manifest is not None and runtime_manifest.name == ".runtime_data_manifest.json":
            runtime_manifest.unlink(missing_ok=True)
    outputs = _normalise_output_paths(result, destination)
    source_files = {
        name: _file_record(path, destination)
        for name, path in packaged_sources.items()
        if path.is_file()
    }
    if (destination / "nature_context.json").is_file():
        source_files["nature_context.json"] = _file_record(
            destination / "nature_context.json", destination
        )

    input_records: dict[str, Any] = {
        "figure_brief": _file_record(destination / "figure_brief.json", destination),
    }
    if data_file is not None:
        input_records["data"] = _file_record(
            destination / data_file.name, destination
        )
    if manifest_file is not None:
        input_records["manifest"] = _file_record(
            destination / "data_manifest.json", destination
        )

    output_records = {
        format_name: path.name for format_name, path in sorted(outputs.items())
    }
    task_manifest = {
        "schema_version": "0.1",
        "created_utc": datetime.now(UTC).isoformat(),
        "backend": brief.backend,
        "renderer": _relative_label(renderer_source, PROJECT_ROOT),
        "renderer_source": "plot.py",
        "figure_brief": "figure_brief.json",
        "nature_context": "nature_context.json" if nature_context else None,
        "inputs": input_records,
        "source_files": source_files,
        "outputs": output_records,
    }
    _write_json(destination / "task_manifest.json", task_manifest)

    receipt = {
        "schema_version": "0.1",
        "created_utc": datetime.now(UTC).isoformat(),
        "backend": brief.backend,
        "design": {
            "claim": brief.claim,
            "archetype": brief.archetype,
            "evidence_panels": list(brief.evidence_panels),
            "design_requirements": list(brief.design_requirements),
            "renderer": "plot.py",
            "template_reuse": brief.renderer.startswith("templates."),
        },
        "figure_brief": brief.to_mapping(),
        "nature": (
            {
                "requested": True,
                "skill_name": nature_context["skill_name"],
                "commit": nature_context["commit"],
                "references_loaded": nature_context["references_loaded"],
                "reference_sha256": nature_context["reference_sha256"],
                "host_skill_invocation_required": True,
                "host_skill_invocation_status": host_skill_invocation_status,
                "adapter_read_is_not_host_invocation_proof": True,
            }
            if nature_context
            else {
                "requested": False,
                "host_skill_invocation_required": False,
                "host_skill_invocation_status": "not_required",
            }
        ),
        "review": {
            "status": review_status,
            "notes": list(review_notes),
            "visual_review_is_manual": True,
        },
        "task_manifest": "task_manifest.json",
    }
    _write_json(destination / "design_receipt.json", receipt)
    return {
        "outputs": outputs,
        "task_manifest": destination / "task_manifest.json",
        "design_receipt": destination / "design_receipt.json",
        "source_files": packaged_sources,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", required=True, help="Dotted module or renderer .py path")
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--data-path", type=Path)
    parser.add_argument("--manifest-path", type=Path)
    parser.add_argument("--nature-skill-root", type=Path)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Forward explicit overwrite permission to a renderer that supports it",
    )
    parser.add_argument(
        "--review-status",
        choices=sorted(REVIEW_STATUSES),
        default="not_reviewed",
    )
    parser.add_argument("--review-note", action="append", default=[])
    parser.add_argument(
        "--host-skill-invocation-status",
        choices=sorted(INVOCATION_STATUSES),
        default="not_verified",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    run_figure_task(
        renderer=arguments.renderer,
        brief_path=arguments.brief,
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
        nature_skill_root=arguments.nature_skill_root,
        review_status=arguments.review_status,
        review_notes=tuple(arguments.review_note),
        host_skill_invocation_status=arguments.host_skill_invocation_status,
        overwrite=arguments.overwrite,
    )
