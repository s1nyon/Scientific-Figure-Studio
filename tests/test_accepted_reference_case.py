import csv
import json
import os
import shutil
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
            "assert plot.DEFAULT_SKILL_ROOT == Path(r'C:\\tmp\\nature-skill')",
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["SFS_NATURE_SKILL_ROOT"] = r"C:\tmp\nature-skill"
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
    assert "user-supplied" in preferences[reference_path]["source"].lower()

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
    assert "user-supplied" in row["source"].lower()

def test_gallery_rescan_preserves_reference_provenance(tmp_path):
    source_image = ROOT / "figure_gallery" / "02_algorithm" / "nature_optimization_fig3.png"
    gallery_root = tmp_path / "gallery"
    image_path = gallery_root / "02_algorithm" / source_image.name
    image_path.parent.mkdir(parents=True)
    shutil.copy2(source_image, image_path)
    generated = gallery_root / "_generated"
    generated.mkdir()
    reference_path = "02_algorithm/nature_optimization_fig3.png"
    source = (
        "Unknown — user-supplied reference image; original publication and license "
        "source not provided."
    )
    (generated / "gallery_preferences.json").write_text(
        json.dumps({reference_path: {"source": source}}, ensure_ascii=False),
        encoding="utf-8",
    )

    from figure_studio.gallery import GalleryIndex

    index = GalleryIndex(gallery_root)
    first = index.scan()
    second = index.scan()
    assert first[0].source == source
    assert second[0].source == source
