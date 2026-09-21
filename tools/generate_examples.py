"""Build six self-contained example delivery directories from the templates."""

from __future__ import annotations

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
TEMPLATE_NAMES = (
    "convergence",
    "prediction",
    "sensitivity",
    "pareto",
    "spatial",
    "composite",
)
DELIVERY_FILES = ("plot.py", "config.py", "data_manifest.json", "README.md")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _project_version() -> str:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["version"])


def _template_config(template_name: str) -> dict[str, object]:
    module = import_module(f"templates.{template_name}.config")
    return dict(module.CONFIG)


def _run_copied_script(script_path: Path, destination: Path) -> None:
    command = [sys.executable, str(script_path), "--output-dir", str(destination)]
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
    config: dict[str, object],
    source: Path,
) -> None:
    artifacts = sorted(
        path.name
        for path in destination.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".svg", ".pdf"}
    )
    manifest = {
        "package_version": _project_version(),
        "template": destination.name,
        "data_file": source.relative_to(PROJECT_ROOT).as_posix(),
        "data_sha256": _sha256(source),
        "config_summary": json.loads(json.dumps(config, default=str)),
        "artifacts": artifacts,
        "source_status": "generated from the copied template source and config",
    }
    (destination / "generation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(output_root: str | Path | None = None) -> list[Path]:
    """Copy, execute, and provenance-stamp all six practice templates."""

    root = Path(output_root) if output_root else PROJECT_ROOT / "examples" / "outputs"
    root.mkdir(parents=True, exist_ok=True)
    destinations: list[Path] = []
    for template_name in TEMPLATE_NAMES:
        template_dir = PROJECT_ROOT / "templates" / template_name
        config = _template_config(template_name)
        destination = root / str(config["figure_id"])
        destination.mkdir(parents=True, exist_ok=True)
        for filename in DELIVERY_FILES:
            shutil.copy2(template_dir / filename, destination / filename)
        source = PROJECT_ROOT / str(config["data_file"])
        _run_copied_script(destination / "plot.py", destination)
        _write_generation_manifest(destination, config, source)
        destinations.append(destination)
    return destinations


if __name__ == "__main__":
    for output in main():
        print(output)
