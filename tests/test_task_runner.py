import json
import subprocess
import sys
from pathlib import Path

import pytest

from templates.illustration.flowchart.plot import main as render_flowchart
from tools.run_figure_task import run_figure_task

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_ROOT = Path.home() / ".codex" / "skills" / "nature-figure"


def _write_renderer(folder: Path) -> Path:
    renderer = folder / "plot.py"
    renderer.write_text(
        """
from pathlib import Path

import matplotlib.pyplot as plt

from figure_studio.export import export_figure


def main(output_dir=None, data_path=None, manifest_path=None, skill_root=None, overwrite=False):
    destination = Path(output_dir)
    figure, axis = plt.subplots(figsize=(3.2, 2.2))
    axis.plot([0, 1, 2], [2.0, 1.0, 0.8], color="#166A8F")
    axis.set_xlabel("iteration")
    axis.set_ylabel("practice objective")
    try:
        return export_figure(
            figure,
            destination / "figure",
            formats=("png", "svg", "pdf"),
            dpi=120,
            overwrite=overwrite,
            provenance={"renderer_test": True, "data_path_provided": data_path is not None},
        )
    finally:
        plt.close(figure)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (folder / "config.py").write_text("FIGURE_WIDTH = 3.2\n", encoding="utf-8")
    return renderer


def _write_brief(path: Path, nature_references: list[str] | None = None) -> None:
    payload = {
        "task": "Render a small practice evidence chart.",
        "data_sources": ["practice.csv"],
        "fields": {"x": "iteration", "y": "practice objective"},
        "units": {"x": "count", "y": "practice unit"},
        "claim": "The practice objective decreases over the supplied iterations.",
        "evidence_panels": [{"id": "a", "role": "hero evidence", "source": "practice.csv"}],
        "archetype": "quantitative grid",
        "backend": "Python",
        "task_mode": "ordinary",
        "nature_references": nature_references or [],
        "renderer": "plot.py",
        "review_risks": ["This is practice data."],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_manifest(folder: Path, data_path: Path) -> Path:
    manifest = folder / "data_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "figure_id": "test_task",
                "data_status": "illustrative practice data",
                "data_file": data_path.name,
                "fields": {"x": "iteration", "y": "practice objective"},
                "units": {"x": "count", "y": "practice unit"},
                "unsupported_claims": ["formal result"],
            }
        ),
        encoding="utf-8",
    )
    return manifest


def test_run_figure_task_writes_outputs_receipts_and_source_hashes(tmp_path):
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    renderer = _write_renderer(source_folder)
    data_path = source_folder / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source_folder, data_path)
    brief = source_folder / "figure_brief.json"
    _write_brief(brief)
    output_dir = tmp_path / "output"

    result = run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
    )

    assert {path.suffix for path in result["outputs"].values()} == {".png", ".svg", ".pdf"}
    assert (output_dir / "task_manifest.json").exists()
    assert (output_dir / "design_receipt.json").exists()
    assert (output_dir / "plot.py").exists()
    assert (output_dir / "config.py").exists()
    assert (output_dir / "data_manifest.json").exists()
    task_manifest = json.loads((output_dir / "task_manifest.json").read_text(encoding="utf-8"))
    assert task_manifest["backend"] == "Python"
    assert not Path(task_manifest["renderer"]).is_absolute()
    assert task_manifest["source_files"]["plot.py"]["sha256"]
    assert task_manifest["inputs"]["data"]["sha256"]
    assert task_manifest["outputs"]["png"] == "figure.png"


def test_run_figure_task_records_verified_nature_context(tmp_path):
    if not DEFAULT_SKILL_ROOT.is_dir():
        pytest.skip("fixed Nature Skill has not been installed in this environment")
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    renderer = _write_renderer(source_folder)
    data_path = source_folder / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source_folder, data_path)
    brief = source_folder / "figure_brief.json"
    _write_brief(brief, ["SKILL.md", "references/figure-contract.md"])
    output_dir = tmp_path / "output"

    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
        nature_skill_root=DEFAULT_SKILL_ROOT,
    )

    receipt = json.loads((output_dir / "design_receipt.json").read_text(encoding="utf-8"))
    assert receipt["nature"]["commit"] == "1930963cbc004da9ac8e3af7944d4f0a3488d3e1"
    assert receipt["nature"]["references_loaded"] == [
        "SKILL.md",
        "references/figure-contract.md",
    ]
    assert receipt["nature"]["host_skill_invocation_required"] is True


def test_run_figure_task_requires_explicit_overwrite_for_existing_outputs(tmp_path):
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    renderer = _write_renderer(source_folder)
    data_path = source_folder / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source_folder, data_path)
    brief = source_folder / "figure_brief.json"
    _write_brief(brief)
    output_dir = tmp_path / "output"

    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
    )
    with pytest.raises(FileExistsError):
        run_figure_task(
            renderer=renderer,
            brief_path=brief,
            output_dir=output_dir,
            data_path=data_path,
            manifest_path=manifest,
        )
    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
        overwrite=True,
    )


def test_run_figure_task_explicit_overwrite_updates_delivery_source(tmp_path):
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    renderer = _write_renderer(source_folder)
    data_path = source_folder / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source_folder, data_path)
    brief = source_folder / "figure_brief.json"
    _write_brief(brief)
    output_dir = tmp_path / "output"

    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
    )
    renderer.write_text(
        renderer.read_text(encoding="utf-8") + "\n# revised source\n",
        encoding="utf-8",
    )
    with pytest.raises(FileExistsError):
        run_figure_task(
            renderer=renderer,
            brief_path=brief,
            output_dir=output_dir,
            data_path=data_path,
            manifest_path=manifest,
        )

    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
        overwrite=True,
    )
    assert "# revised source" in (output_dir / "plot.py").read_text(encoding="utf-8")


def test_run_figure_task_protects_outputs_from_renderer_ignoring_overwrite(tmp_path):
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    renderer = _write_renderer(source_folder)
    renderer.write_text(
        renderer.read_text(encoding="utf-8").replace(
            "overwrite=overwrite,", "overwrite=True,"
        ),
        encoding="utf-8",
    )
    data_path = source_folder / "practice.csv"
    data_path.write_text("x,y\n0,2\n1,1\n2,0.8\n", encoding="utf-8")
    manifest = _write_manifest(source_folder, data_path)
    brief = source_folder / "figure_brief.json"
    _write_brief(brief)
    output_dir = tmp_path / "output"

    run_figure_task(
        renderer=renderer,
        brief_path=brief,
        output_dir=output_dir,
        data_path=data_path,
        manifest_path=manifest,
    )
    with pytest.raises(FileExistsError):
        run_figure_task(
            renderer=renderer,
            brief_path=brief,
            output_dir=output_dir,
            data_path=data_path,
            manifest_path=manifest,
        )


def test_run_figure_task_cli_is_runnable_from_project_root():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "run_figure_task.py"), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--renderer" in result.stdout


def test_run_figure_task_supports_existing_flowchart_renderer(tmp_path):
    output_dir = tmp_path / "flowchart"
    result = run_figure_task(
        renderer="templates.illustration.flowchart.plot",
        brief_path=ROOT / "examples" / "data" / "phase3_flowchart_brief.json",
        output_dir=output_dir,
        data_path=ROOT / "examples" / "data" / "illustration_flowchart.json",
        manifest_path=ROOT
        / "templates"
        / "illustration"
        / "flowchart"
        / "data_manifest.json",
    )

    assert {path.suffix for path in result["outputs"].values()} == {".png", ".svg", ".pdf"}
    assert (output_dir / "illustration_flowchart.json").exists()
    assert (output_dir / "data_manifest.json").exists()
    packaged_manifest = json.loads(
        (output_dir / "data_manifest.json").read_text(encoding="utf-8")
    )
    assert packaged_manifest["data_file"] == "illustration_flowchart.json"


def test_flowchart_renderer_accepts_external_data_path_directly(tmp_path):
    output_dir = tmp_path / "direct-flowchart"
    outputs = render_flowchart(
        output_dir=output_dir,
        data_path=ROOT / "examples" / "data" / "illustration_flowchart.json",
        manifest_path=ROOT
        / "templates"
        / "illustration"
        / "flowchart"
        / "data_manifest.json",
    )

    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}


def test_flowchart_renderer_requires_explicit_overwrite(tmp_path):
    output_dir = tmp_path / "protected-flowchart"
    render_flowchart(
        output_dir=output_dir,
        data_path=ROOT / "examples" / "data" / "illustration_flowchart.json",
        manifest_path=ROOT
        / "templates"
        / "illustration"
        / "flowchart"
        / "data_manifest.json",
    )

    with pytest.raises(FileExistsError):
        render_flowchart(
            output_dir=output_dir,
            data_path=ROOT / "examples" / "data" / "illustration_flowchart.json",
            manifest_path=ROOT
            / "templates"
            / "illustration"
            / "flowchart"
            / "data_manifest.json",
        )
