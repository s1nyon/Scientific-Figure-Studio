import csv
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = ROOT / "figure_gallery" / "05_my_work" / "round_04_design_a_accepted"


def test_accepted_design_a_defaults_to_its_bundled_input():
    script = "\n".join(
        [
            "import sys",
            "from pathlib import Path",
            f"accepted = Path(r'{ACCEPTED}')",
            f"root = Path(r'{ROOT}')",
            "sys.path.insert(0, str(accepted))",
            "import plot",
            "assert plot.PROJECT_ROOT == root",
            "assert (accepted / plot.CONFIG['data_file']).is_file()",
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_gallery_provenance_and_brief_keep_local_source_boundaries():
    brief = json.loads((ACCEPTED / "figure_brief.json").read_text(encoding="utf-8"))
    assert brief["data_sources"] == ["convergence_practice.csv"]

    preferences = json.loads(
        (ROOT / "figure_gallery" / "_generated" / "gallery_preferences.json")
        .read_text(encoding="utf-8")
    )
    reference_path = "02_algorithm/nature_optimization_fig3.png"
    assert "unknown" in preferences[reference_path]["source"].lower()

    note = (
        ROOT / "figure_gallery" / "_generated" / "gallery_notes" / "nature_optimization_fig3.md"
    ).read_text(encoding="utf-8")
    assert "source/license status is unknown" in note

    with (ROOT / "figure_gallery" / "gallery_index.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        row = next(
            item for item in csv.DictReader(handle) if item["relative_path"] == reference_path
        )
    assert "unknown" in row["source"].lower()
