import json
from pathlib import Path

from figure_studio.artifacts import sha256
from figure_studio.validation import validate_artifact

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "examples" / "outputs" / "p1_gallery_acceptance"


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_nature_gallery_task_records_both_reference_channels():
    output = ACCEPTANCE / "nature_gallery_task"
    for suffix in ("png", "svg", "pdf"):
        validate_artifact(output / f"figure.{suffix}", suffix)
    receipt = _read_json(output / "design_receipt.json")
    assert receipt["nature"]["commit"] == "1930963cbc004da9ac8e3af7944d4f0a3488d3e1"
    assert receipt["references"]["gallery"][0]["relative_path"] == (
        "02_algorithm/nature_first_reference.png"
    )
    assert receipt["references"]["gallery"][0]["visual_analysis_status"] == (
        "agent_reviewed"
    )
    assert receipt["references"]["code"] == [
        "examples/outputs/p1_independent_reproduction/complex_nature_first/plot.py"
    ]
    assert receipt["references"]["code_records"][0]["sha256"]
    assert receipt["references"]["user_note"].startswith("Acceptance fixture")


def test_gallery_analysis_and_work_link_preserve_separate_ownership():
    gallery_root = ACCEPTANCE / "reference_gallery"
    rows = (gallery_root / "gallery_index.csv").read_text(encoding="utf-8")
    assert "agent_reviewed" in rows
    assert "visual_analysis_viewed" in rows
    visual_notes = list((gallery_root / "_generated" / "gallery_visual_analysis").glob("*.md"))
    assert len(visual_notes) == 1
    assert "composition" in visual_notes[0].read_text(encoding="utf-8")

    link = _read_json(
        gallery_root / "_generated" / "work_links" / "candidate_work.json"
    )
    assert link["status"] == "accepted"
    assert link["user_evaluation"].startswith("Explicit P1 acceptance")
    accepted = ACCEPTANCE / "accepted_work"
    code_reference = link["code_reference"]
    for relative in code_reference.values():
        if isinstance(relative, str) and relative in {
            "plot.py",
            "config.py",
            "version_manifest.json",
            "task_manifest.json",
            "reproduction_manifest.json",
        }:
            assert (accepted / relative).is_file()


def test_accepted_work_is_hash_linked_and_clone_is_editable():
    candidate = ACCEPTANCE / "candidate_work"
    accepted = ACCEPTANCE / "accepted_work"
    clone = ACCEPTANCE / "derived_workspace"
    accepted_manifest = _read_json(accepted / "version_manifest.json")
    assert accepted_manifest["status"] == "accepted"
    assert accepted_manifest["run_id"] == "accepted_work"
    assert accepted_manifest["user_note"].startswith("Explicit P1 acceptance")
    for relative in ("plot.py", "config.py", "convergence_practice.csv", "figure.png"):
        assert sha256(candidate / relative) == sha256(accepted / relative)
    clone_manifest = _read_json(clone / "version_manifest.json")
    assert clone_manifest["status"] == "workspace"
    assert clone_manifest["derived_from_accepted"] is True


def test_snapshot_manifest_covers_editable_bundle():
    snapshot = _read_json(ACCEPTANCE / "workspace_snapshot" / "snapshot_manifest.json")
    restored = ACCEPTANCE / "derived_workspace"
    for relative, record in snapshot["files"].items():
        assert sha256(restored / relative) == record["sha256"]
