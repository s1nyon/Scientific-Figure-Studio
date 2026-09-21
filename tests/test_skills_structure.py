import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "modern-scientific-figure",
    "algorithm-visualization",
    "figure-design-review",
    "figure-reference-manager",
)


def _frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields = dict(
        line.split(":", 1)
        for line in match.group(1).splitlines()
        if ":" in line
    )
    return fields.get("name", "").strip(), fields.get("description", "").strip()


def test_project_skills_have_discoverable_metadata_and_references():
    for skill_name in SKILL_NAMES:
        skill_dir = ROOT / ".agents" / "skills" / skill_name
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.exists()
        name, description = _frontmatter(skill_file.read_text(encoding="utf-8"))
        assert name == skill_name
        assert description.startswith("Use when")
        assert "AGENTS.md" in skill_file.read_text(encoding="utf-8")
        references = skill_dir / "references"
        assert references.is_dir()
        assert any(references.iterdir())
