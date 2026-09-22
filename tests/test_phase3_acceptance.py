import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATURE_OUTPUT = ROOT / "examples" / "outputs" / "fig_11_nature_first"
FLOW_OUTPUT = ROOT / "examples" / "outputs" / "fig_12_unified_flowchart"


def _assert_delivery_bundle(folder: Path) -> None:
    for name in (
        "plot.py",
        "config.py",
        "figure_brief.json",
        "data_manifest.json",
        "README.md",
        "figure.png",
        "figure.svg",
        "figure.pdf",
        "figure.manifest.json",
        "task_manifest.json",
        "design_receipt.json",
    ):
        assert (folder / name).is_file(), name


def test_phase3_nature_first_delivery_contains_verified_design_and_outputs():
    _assert_delivery_bundle(NATURE_OUTPUT)
    brief = json.loads((NATURE_OUTPUT / "figure_brief.json").read_text(encoding="utf-8"))
    receipt = json.loads((NATURE_OUTPUT / "design_receipt.json").read_text(encoding="utf-8"))
    assert brief["backend"] == "Python"
    assert brief["archetype"] == "quantitative grid"
    assert receipt["nature"]["commit"] == "1930963cbc004da9ac8e3af7944d4f0a3488d3e1"
    assert receipt["nature"]["host_skill_invocation_status"] == (
        "explicitly_loaded_in_codex_session"
    )
    assert receipt["review"]["status"] == "passed"
    assert "<text" in (NATURE_OUTPUT / "figure.svg").read_text(encoding="utf-8")


def test_phase3_unified_entry_delivers_explicit_flowchart_structure():
    _assert_delivery_bundle(FLOW_OUTPUT)
    brief = json.loads((FLOW_OUTPUT / "figure_brief.json").read_text(encoding="utf-8"))
    structure = json.loads(
        (FLOW_OUTPUT / "illustration_flowchart.json").read_text(encoding="utf-8")
    )
    assert brief["archetype"] == "schematic-led composite"
    assert brief["nature_references"] == []
    assert set(structure["nodes"]) == {
        "input",
        "prepare",
        "check",
        "fit",
        "revise",
        "report",
    }


def test_phase3_flowchart_delivery_runs_from_its_own_directory(tmp_path):
    destination = tmp_path / "standalone-flowchart"
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            str(FLOW_OUTPUT / "plot.py"),
            "--output-dir",
            str(destination),
            "--manifest-path",
            str(FLOW_OUTPUT / "data_manifest.json"),
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert all((destination / f"figure.{suffix}").is_file() for suffix in ("png", "svg", "pdf"))


def test_phase3_revision_preserves_before_snapshot_and_comparison():
    snapshot = NATURE_OUTPUT / "snapshots" / "before_revision"
    for name in ("plot.py", "config.py", "figure.png", "figure.svg", "figure.pdf"):
        assert (snapshot / name).is_file(), name
    comparison = NATURE_OUTPUT / "figure_before_after.png"
    comparison_manifest = NATURE_OUTPUT / "figure_before_after.manifest.json"
    assert comparison.is_file()
    assert comparison_manifest.is_file()
    manifest = json.loads(comparison_manifest.read_text(encoding="utf-8"))
    assert manifest["preserves_native_aspect"] is True
    before_config = (snapshot / "config.py").read_text(encoding="utf-8")
    after_config = (NATURE_OUTPUT / "config.py").read_text(encoding="utf-8")
    assert before_config != after_config
