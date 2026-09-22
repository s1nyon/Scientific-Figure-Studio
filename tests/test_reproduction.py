import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

from figure_studio.artifacts import package_reproduction

ROOT = Path(__file__).resolve().parents[1]


def _run_checked_in_package(package_name: str, tmp_path: Path) -> Path:
    source_package = ROOT / "examples" / "outputs" / "p1_independent_reproduction" / package_name
    package = tmp_path / "copied_package"
    shutil.copytree(source_package, package)
    output = tmp_path / package_name / "rerender"
    environment = os.environ.copy()
    environment.pop("SCIENTIFIC_FIGURE_STUDIO_ROOT", None)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(package / "plot.py"), "--output-dir", str(output)],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return output


def test_checked_in_simple_reproduction_runs_outside_repository(tmp_path):
    output = _run_checked_in_package("simple_convergence", tmp_path)
    with Image.open(output / "figure.png") as image:
        image.load()
        assert image.width > 10 and image.height > 10
    assert (output / "figure.svg").read_text(encoding="utf-8").startswith("<?xml")
    assert (output / "figure.pdf").stat().st_size > 1000


def test_checked_in_complex_reproduction_runs_outside_repository(tmp_path):
    output = _run_checked_in_package("complex_nature_first", tmp_path)
    with Image.open(output / "figure.png") as image:
        image.load()
        assert image.width > 10 and image.height > 10
    assert "Independent Nature-first" in (output / "figure.svg").read_text(encoding="utf-8")
    assert (output / "figure.pdf").stat().st_size > 1000


def test_reproduction_package_runs_outside_repository_without_project_paths(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    plot = source / "plot.py"
    plot.write_text(
        """
from pathlib import Path
import matplotlib.pyplot as plt

output = Path(__file__).with_name('outputs')
output.mkdir(exist_ok=True)
figure, axis = plt.subplots(figsize=(2.8, 2.0))
axis.plot([0, 1, 2], [2.0, 1.0, 0.5], color='#166A8F')
axis.set_xlabel('iteration')
axis.set_ylabel('practice value')
for suffix in ('png', 'svg', 'pdf'):
    figure.savefig(output / f'figure.{suffix}', dpi=120)
plt.close(figure)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    package = package_reproduction(
        {"plot.py": plot},
        tmp_path / "standalone-package",
        entrypoint="plot.py",
        dependencies=["matplotlib"],
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    environment = os.environ.copy()
    environment.pop("SCIENTIFIC_FIGURE_STUDIO_ROOT", None)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(package / "plot.py")],
        cwd=outside,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    output_dir = package / "outputs"
    assert all((output_dir / f"figure.{suffix}").is_file() for suffix in ("png", "svg", "pdf"))
    with Image.open(output_dir / "figure.png") as image:
        image.load()
        assert image.width > 10 and image.height > 10
    manifest = json.loads((package / "reproduction_manifest.json").read_text())
    assert manifest["project_independent"] is False
    assert manifest["independence_status"] == "not_verified"
