"""Generate the Nature-adapted and three scientific-illustration deliveries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from importlib import import_module
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

DELIVERY_FILES = ("plot.py", "config.py", "data_manifest.json", "README.md")
PHASE2_TEMPLATES = (
    ("nature_adapter", "fig_07_nature_adapter", ("examples/data/convergence_practice.csv",)),
    (
        "illustration.flowchart",
        "fig_08_illustration_flowchart",
        ("examples/data/illustration_flowchart.json",),
    ),
    (
        "illustration.architecture",
        "fig_09_illustration_architecture",
        ("examples/data/illustration_architecture.json",),
    ),
    (
        "illustration.composite",
        "fig_10_illustration_composite",
        (
            "examples/data/illustration_composite.csv",
            "examples/data/illustration_composite.json",
        ),
    ),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _project_version() -> str:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["version"])


def _run_copied_script(script_path: Path, destination: Path, skill_root: Path | None) -> None:
    command = [
        sys.executable,
        str(script_path),
        "--output-dir",
        str(destination),
        "--overwrite",
    ]
    if skill_root is not None:
        command.extend(["--skill-root", str(skill_root)])
    environment = os.environ.copy()
    environment["SCIENTIFIC_FIGURE_STUDIO_ROOT"] = str(PROJECT_ROOT)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        details = "\n".join(part for part in (result.stdout, result.stderr) if part)
        raise RuntimeError(f"Failed to run {script_path}:\n{details}")


def _write_generation_manifest(
    destination: Path,
    template_name: str,
    config: dict[str, object],
    input_paths: list[Path],
) -> None:
    artifacts = sorted(
        path.name
        for path in destination.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".svg", ".pdf"}
    )
    manifest = {
        "package_version": _project_version(),
        "template": template_name,
        "input_files": [
            {"name": path.name, "sha256": _sha256(path)} for path in input_paths
        ],
        "config_summary": json.loads(json.dumps(config, default=str)),
        "artifacts": artifacts,
        "nature_context": (
            "nature_context.json"
            if (destination / "nature_context.json").exists()
            else None
        ),
        "source_status": (
            "generated from the copied template source, config, manifest, and input files"
        ),
    }
    (destination / "generation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(
    output_root: str | Path | None = None,
    skill_root: str | Path | None = None,
) -> list[Path]:
    """Copy, execute, and provenance-stamp all phase-two example templates."""

    root = Path(output_root) if output_root else PROJECT_ROOT / "examples" / "outputs"
    root.mkdir(parents=True, exist_ok=True)
    nature_skill = Path(skill_root).expanduser() if skill_root else None
    destinations: list[Path] = []
    for template_name, figure_id, relative_inputs in PHASE2_TEMPLATES:
        template_dir = PROJECT_ROOT / "templates" / Path(*template_name.split("."))
        module = import_module(f"templates.{template_name}.config")
        config = dict(module.CONFIG)
        destination = root / figure_id
        destination.mkdir(parents=True, exist_ok=True)
        for filename in DELIVERY_FILES:
            shutil.copy2(template_dir / filename, destination / filename)
        input_paths: list[Path] = []
        for relative_input in relative_inputs:
            source = PROJECT_ROOT / relative_input
            copied_input = destination / source.name
            shutil.copy2(source, copied_input)
            input_paths.append(copied_input)
        _run_copied_script(
            destination / "plot.py",
            destination,
            nature_skill if template_name == "nature_adapter" else None,
        )
        _write_generation_manifest(destination, template_name, config, input_paths)
        destinations.append(destination)
    return destinations


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--skill-root", type=Path, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    for output in main(output_root=arguments.output_root, skill_root=arguments.skill_root):
        print(output)
