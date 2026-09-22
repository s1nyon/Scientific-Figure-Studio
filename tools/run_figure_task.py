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
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.artifacts import (  # noqa: E402
    REPRODUCTION_MANIFEST,
    commit_staged_directory,
    directory_status,
    write_run_manifest,
)
from figure_studio.figure_brief import FigureBrief, load_figure_brief  # noqa: E402
from figure_studio.gallery import GalleryIndex  # noqa: E402
from figure_studio.nature_adapter import build_nature_context  # noqa: E402
from figure_studio.validation import validate_artifact  # noqa: E402

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


def _ensure_destination_ready(output_dir: Path, *, overwrite: bool) -> None:
    """Preflight the final target before staging or copying any delivery files."""

    status = directory_status(output_dir)
    if status in {"accepted", "candidate"}:
        raise PermissionError(f"refusing to modify immutable {status} version: {output_dir}")
    if output_dir.exists() and not output_dir.is_dir():
        raise FileExistsError(f"output target is not a directory: {output_dir}")
    if not output_dir.is_dir() or overwrite:
        return
    existing = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if existing:
        raise FileExistsError(f"refusing to replace existing delivery files: {existing}")


def _gallery_reference_records(
    gallery_root: Path | None,
    references: tuple[str, ...],
) -> list[dict[str, Any]]:
    if not references:
        return []
    if gallery_root is None:
        raise ValueError("gallery_root is required when gallery_references are requested")
    gallery = GalleryIndex(gallery_root)
    indexed = {record.relative_path: record for record in gallery.scan()}
    records: list[dict[str, Any]] = []
    for relative in references:
        record = indexed.get(relative)
        if record is None or record.availability != "present":
            raise FileNotFoundError(f"gallery reference is not indexed: {relative}")
        records.append(
            {
                "relative_path": record.relative_path,
                "sha256": record.sha256,
                "favorite": record.favorite,
                "chart_type": record.chart_type,
                "application": record.application,
                "visual_analysis_status": record.visual_analysis_status,
            }
        )
    return records


def _code_reference_records(
    brief_file: Path,
    references: tuple[str, ...],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for reference in references:
        candidates = (
            PROJECT_ROOT / reference,
            brief_file.parent / reference,
        )
        source = next(
            (
                candidate
                for candidate in candidates
                if candidate.is_file() and not candidate.is_symlink()
            ),
            None,
        )
        if source is None:
            raise FileNotFoundError(f"code reference does not exist: {reference}")
        records.append(
            {
                "reference": reference,
                "path": _relative_label(source, PROJECT_ROOT),
                "sha256": _sha256(source),
                "bytes": source.stat().st_size,
            }
        )
    return records


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
    version_status: str = "workspace",
    parent_run: str | None = None,
    gallery_root: str | Path | None = None,
    dependencies: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Execute one renderer and write an auditable delivery receipt."""

    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"review_status must be one of: {sorted(REVIEW_STATUSES)}")
    if host_skill_invocation_status not in INVOCATION_STATUSES:
        raise ValueError(
            "host_skill_invocation_status must be one of: "
            f"{sorted(INVOCATION_STATUSES)}"
        )
    if version_status not in {"workspace", "candidate"}:
        raise ValueError(
            "version_status must be 'workspace' or 'candidate'; "
            "accepted uses promote_candidate"
        )

    brief_file = Path(brief_path).expanduser().resolve()
    raw_destination = Path(output_dir).expanduser()
    if raw_destination.is_symlink():
        raise ValueError(f"output target must not be a symlink: {raw_destination}")
    destination = raw_destination.resolve()
    data_file = Path(data_path).expanduser().resolve() if data_path else None
    manifest_file = Path(manifest_path).expanduser().resolve() if manifest_path else None
    skill_root = Path(nature_skill_root).expanduser().resolve() if nature_skill_root else None
    gallery_directory = Path(gallery_root).expanduser().resolve() if gallery_root else None
    brief: FigureBrief = load_figure_brief(brief_file)
    if data_file is not None and not data_file.is_file():
        raise FileNotFoundError(f"data file does not exist: {data_file}")
    if manifest_file is not None and not manifest_file.is_file():
        raise FileNotFoundError(f"manifest file does not exist: {manifest_file}")
    if brief.nature_references and skill_root is None:
        raise ValueError("nature_skill_root is required when nature_references are requested")

    _ensure_destination_ready(destination, overwrite=overwrite)
    destination.parent.mkdir(parents=True, exist_ok=True)
    module, renderer_source, _renderer_label = _load_renderer(renderer)
    gallery_records = _gallery_reference_records(gallery_directory, brief.gallery_references)
    code_records = _code_reference_records(brief_file, brief.code_references)
    staging_parent = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.task-", dir=destination.parent)
    )
    staging = staging_parent / "delivery"
    staging.mkdir()
    staged_packaged_sources: dict[str, Path] = {}
    nature_context: dict[str, Any] | None = None
    try:
        staged_packaged_sources = _prepare_delivery_sources(
            renderer_source,
            brief_file,
            manifest_file,
            data_file,
            staging,
            overwrite=False,
        )
        runtime_manifest = _prepare_runtime_manifest(manifest_file, data_file, staging)
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
            _write_json(staging / "nature_context.json", nature_context)

        try:
            staged_data_file = staging / data_file.name if data_file is not None else None
            result = _call_renderer(
                module,
                staging,
                staged_data_file,
                runtime_manifest,
                skill_root,
                False,
            )
        finally:
            if (
                runtime_manifest is not None
                and runtime_manifest.name == ".runtime_data_manifest.json"
            ):
                runtime_manifest.unlink(missing_ok=True)
        staged_outputs = _normalise_output_paths(result, staging)
        for format_name, path in staged_outputs.items():
            validate_artifact(path, format_name)
        source_files = {
            name: _file_record(path, staging)
            for name, path in staged_packaged_sources.items()
            if path.is_file()
        }
        if (staging / "nature_context.json").is_file():
            source_files["nature_context.json"] = _file_record(
                staging / "nature_context.json", staging
            )

        input_records: dict[str, Any] = {
            "figure_brief": _file_record(staging / "figure_brief.json", staging),
        }
        if data_file is not None:
            input_records["data"] = _file_record(staging / data_file.name, staging)
        if manifest_file is not None:
            input_records["manifest"] = _file_record(staging / "data_manifest.json", staging)

        output_records = {
            format_name: path.name for format_name, path in sorted(staged_outputs.items())
        }
        _write_json(
            staging / REPRODUCTION_MANIFEST,
            {
                "schema_version": "0.1",
                "entrypoint": "plot.py",
                "dependencies": list(dependencies),
                "project_independent": False,
                "independence_status": "runner_delivery_not_certified_as_standalone",
                "nature_skill_runtime_dependency": False,
                "source_files": sorted(source_files),
                "output_files": sorted(output_records.values()),
                "reproduction_notes": (
                    "This is a runner delivery bundle. It preserves the exact source, "
                    "inputs, configuration, and outputs used for this run. Use the "
                    "explicit package_reproduction workflow for a separately certified "
                    "repository-independent package."
                ),
            },
        )
        source_files[REPRODUCTION_MANIFEST] = _file_record(
            staging / REPRODUCTION_MANIFEST, staging
        )
        task_manifest = {
            "schema_version": "0.2",
            "created_utc": datetime.now(UTC).isoformat(),
            "backend": brief.backend,
            "renderer": _relative_label(renderer_source, PROJECT_ROOT),
            "renderer_source": "plot.py",
            "figure_brief": "figure_brief.json",
            "nature_context": "nature_context.json" if nature_context else None,
            "reproduction_manifest": REPRODUCTION_MANIFEST,
            "inputs": input_records,
            "source_files": source_files,
            "outputs": output_records,
            "references": {
                "gallery": gallery_records,
                "code": list(brief.code_references),
                "code_records": code_records,
            },
            "version": {
                "status": version_status,
                "run_id": destination.name,
                "parent_run": parent_run,
            },
        }
        _write_json(staging / "task_manifest.json", task_manifest)

        receipt = {
            "schema_version": "0.2",
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
            "references": {
                "gallery": gallery_records,
                "code": list(brief.code_references),
                "code_records": code_records,
                "user_note": brief.user_reference_note,
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
        _write_json(staging / "design_receipt.json", receipt)
        source_hashes = {
            name: record["sha256"] for name, record in source_files.items()
        }
        version_source_files = dict(staged_packaged_sources)
        if (staging / "nature_context.json").is_file():
            version_source_files["nature_context.json"] = staging / "nature_context.json"
        version_source_files[REPRODUCTION_MANIFEST] = staging / REPRODUCTION_MANIFEST
        write_run_manifest(
            staging,
            status=version_status,
            source_hashes=source_hashes,
            source_files=version_source_files,
            outputs=staged_outputs,
            run_id=destination.name,
            parent_run=parent_run,
            metadata={
                "task_manifest": "task_manifest.json",
                "design_receipt": "design_receipt.json",
            },
        )
        commit_staged_directory(staging, destination, overwrite=overwrite)
        outputs = {
            format_name: destination / path.relative_to(staging)
            for format_name, path in staged_outputs.items()
        }
        packaged_sources = {
            name: destination / path.relative_to(staging)
            for name, path in staged_packaged_sources.items()
        }
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)
    return {
        "outputs": outputs,
        "task_manifest": destination / "task_manifest.json",
        "design_receipt": destination / "design_receipt.json",
        "source_files": packaged_sources,
        "version_manifest": destination / "version_manifest.json",
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
    parser.add_argument("--version-status", choices=("workspace", "candidate"), default="workspace")
    parser.add_argument("--parent-run")
    parser.add_argument("--gallery-root", type=Path)
    parser.add_argument(
        "--dependency",
        action="append",
        default=[],
        help="Record one runtime dependency in reproduction_manifest.json",
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
        version_status=arguments.version_status,
        parent_run=arguments.parent_run,
        gallery_root=arguments.gallery_root,
        dependencies=tuple(arguments.dependency),
    )
