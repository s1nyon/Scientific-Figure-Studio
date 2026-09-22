"""Build the checked-in simple and complex independent reproduction packages."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.artifacts import certify_reproduction, package_reproduction  # noqa: E402

PACKAGES = (
    ("p1_simple", "simple_convergence", ["matplotlib>=3.8", "pandas>=2.1", "numpy>=1.26"]),
    ("p1_complex", "complex_nature_first", ["matplotlib>=3.8", "pandas>=2.1", "numpy>=1.26"]),
)


def _build_one(source_dir: Path, destination: Path, dependencies: list[str]) -> Path:
    if destination.exists():
        raise FileExistsError(f"reproduction destination already exists: {destination}")
    with tempfile.TemporaryDirectory(prefix="p1-reproduction-render-") as temporary:
        render_dir = Path(temporary)
        subprocess.run(
            [sys.executable, str(source_dir / "plot.py"), "--output-dir", str(render_dir)],
            cwd=source_dir,
            check=True,
        )
        names = (
            "plot.py",
            "config.py",
            "data_manifest.json",
            "figure_brief.json",
            "README.md",
            "convergence_practice.csv",
        )
        source_files = {name: source_dir / name for name in names}
        for name in ("figure.png", "figure.svg", "figure.pdf", "figure.manifest.json"):
            source_files[name] = render_dir / name
        if (source_dir / "standalone_runtime.py").is_file():
            source_files["standalone_runtime.py"] = source_dir / "standalone_runtime.py"
        package = package_reproduction(
            source_files,
            destination,
            entrypoint="plot.py",
            dependencies=dependencies,
            metadata={
                "figure_type": (
                    "simple data chart"
                    if "simple" in destination.name
                    else "complex multi-panel Figure"
                ),
                "data_status": "illustrative practice data",
                "nature_skill_runtime_dependency": False,
            },
        )
        return certify_reproduction(
            package,
            expected_outputs=("figure.png", "figure.svg", "figure.pdf"),
        )


def main(output_root: str | Path | None = None) -> list[Path]:
    root = (
        Path(output_root).expanduser().resolve()
        if output_root
        else PROJECT_ROOT / "examples" / "outputs" / "p1_independent_reproduction"
    )
    root.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    for source_name, output_name, dependencies in PACKAGES:
        source_dir = PROJECT_ROOT / "examples" / "reproduction_sources" / source_name
        built.append(_build_one(source_dir, root / output_name, dependencies))
    return built


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    for output in main(arguments.output_root):
        print(output)
