import json

import pytest

from figure_studio.figure_brief import (
    FigureBrief,
    load_figure_brief,
    validate_figure_brief,
)


def valid_payload() -> dict[str, object]:
    return {
        "task": "Show the practice convergence evidence.",
        "data_sources": ["examples/data/convergence_practice.csv"],
        "fields": {
            "algorithm": "method label",
            "iteration": "iteration count",
            "objective": "objective value",
        },
        "units": {"iteration": "count", "objective": "practice unit"},
        "claim": "The practice trajectories approach lower objective values over iterations.",
        "evidence_panels": [
            {"id": "a", "role": "hero trajectory evidence", "source": "objective"},
            {"id": "b", "role": "derived endpoint evidence", "source": "objective"},
        ],
        "archetype": "quantitative grid",
        "backend": "Python",
        "task_mode": "ordinary",
        "nature_references": ["SKILL.md", "references/figure-contract.md"],
        "renderer": "examples/outputs/fig_11_nature_first/plot.py",
        "review_risks": ["practice data must not be presented as a competition result"],
        "design_requirements": ["hero panel dominates the evidence hierarchy"],
        "scientific_unknowns": ["No replicate runs are available."],
    }


def test_load_figure_brief_round_trips_scientific_fields(tmp_path):
    path = tmp_path / "figure_brief.json"
    path.write_text(json.dumps(valid_payload()), encoding="utf-8")

    brief = load_figure_brief(path)

    assert isinstance(brief, FigureBrief)
    assert brief.backend == "Python"
    assert brief.evidence_panels[0]["role"] == "hero trajectory evidence"
    assert brief.scientific_unknowns == ("No replicate runs are available.",)


@pytest.mark.parametrize("missing", ["claim", "evidence_panels", "archetype", "renderer"])
def test_validate_figure_brief_requires_core_design_fields(missing):
    payload = valid_payload()
    payload.pop(missing)

    with pytest.raises(ValueError, match=missing):
        validate_figure_brief(payload)


def test_validate_figure_brief_rejects_non_python_backend():
    payload = valid_payload()
    payload["backend"] = "R"

    with pytest.raises(ValueError, match="Python"):
        validate_figure_brief(payload)


def test_validate_figure_brief_rejects_unknown_task_mode():
    payload = valid_payload()
    payload["task_mode"] = "autonomous-platform"

    with pytest.raises(ValueError, match="task_mode"):
        validate_figure_brief(payload)


def test_validate_figure_brief_accepts_a_non_chart_with_empty_nature_references():
    payload = valid_payload()
    payload.update(
        {
            "task": "Draw the explicitly supplied algorithm structure.",
            "fields": {},
            "units": {},
            "archetype": "schematic-led composite",
            "nature_references": [],
            "renderer": "templates.illustration.flowchart.plot",
        }
    )

    brief = validate_figure_brief(payload)

    assert brief.nature_references == ()
    assert brief.archetype == "schematic-led composite"
