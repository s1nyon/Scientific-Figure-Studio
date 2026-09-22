from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "scientific-illustration" / "SKILL.md"
REFERENCE = (
    ROOT
    / ".agents"
    / "skills"
    / "scientific-illustration"
    / "references"
    / "illustration-contract.md"
)


def test_scientific_illustration_skill_has_required_scope_and_contract():
    text = SKILL.read_text(encoding="utf-8")
    assert "AGENTS.md" in text
    assert "figure_studio.illustrations" in text
    assert "draw_flowchart" in text
    assert "draw_architecture" in text
    assert "draw_geometry" in text
    assert "draw_surface" in text
    assert "draw_network" in text
    assert "not" in text and "ordinary line chart" in text
    assert "set_aspect(\"equal\")" in text
    assert "source" in text and "target" in text
    assert "finite" in text
    assert "actual" in text and "PNG" in text
    assert REFERENCE.exists()


def test_scientific_illustration_reference_forbids_invented_structure():
    text = REFERENCE.read_text(encoding="utf-8")
    assert "not invented" in text
    assert "equal x/y scale" in text
    assert "shape-matched arrays" in text
