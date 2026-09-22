import json
import subprocess
import sys
from pathlib import Path

from figure_studio.artifacts import build_source_hashes, promote_candidate, write_run_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_manage_figure_work_cli_lists_references_and_clones_accepted_work(tmp_path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "plot.py").write_text("print('candidate')\n", encoding="utf-8")
    (candidate / "figure.png").write_bytes(b"image")
    write_run_manifest(
        candidate,
        status="candidate",
        source_hashes=build_source_hashes({"plot.py": candidate / "plot.py"}),
        outputs={"png": candidate / "figure.png"},
    )
    accepted = tmp_path / "accepted"
    gallery = tmp_path / "gallery"
    promote_candidate(
        candidate,
        accepted,
        user_note="explicit CLI fixture acceptance",
        gallery_root=gallery,
    )

    works = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "manage_figure_work.py"),
            "works",
            "--gallery-root",
            str(gallery),
            "--query",
            "CLI fixture",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert works.returncode == 0, works.stderr
    assert json.loads(works.stdout)[0]["work_id"] == "candidate"
    assert json.loads(works.stdout)[0]["available"] is True

    clone = tmp_path / "clone"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "manage_figure_work.py"),
            "clone",
            "--accepted-dir",
            str(accepted),
            "--workspace-dir",
            str(clone),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads((clone / "version_manifest.json").read_text())["status"] == "workspace"
