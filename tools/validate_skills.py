"""Validate project Skill metadata and local references without claiming host discovery."""

from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, text[end + len("\n---\n") :]


def _validate_skill(skill_dir: Path, project_root: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]
    try:
        fields, body = _frontmatter(skill_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{skill_dir.name}: {exc}"]
    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name must be {skill_dir.name!r}")
    if not NAME_PATTERN.fullmatch(name):
        errors.append(f"{skill_dir.name}: name contains unsupported characters")
    if not description.startswith("Use when"):
        errors.append(f"{skill_dir.name}: description must start with 'Use when'")
    if "AGENTS.md" not in body:
        errors.append(f"{skill_dir.name}: SKILL.md does not reference AGENTS.md")
    references = skill_dir / "references"
    if not references.is_dir() or not any(references.iterdir()):
        errors.append(f"{skill_dir.name}: references directory is missing or empty")
    for target in LINK_PATTERN.findall(body):
        if target.startswith(("http://", "https://", "#")):
            continue
        target_path = (skill_file.parent / target).resolve()
        if not target_path.exists():
            errors.append(f"{skill_dir.name}: missing linked path {target}")
    if not (project_root / "AGENTS.md").exists():
        errors.append("project root: missing AGENTS.md")
    return errors


def main(project_root: str | Path | None = None) -> int:
    """Return zero only when all project Skill files pass local validation."""

    root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
    skills_root = root / ".agents" / "skills"
    if not skills_root.is_dir():
        print(f"Skill root not found: {skills_root}", file=sys.stderr)
        return 1
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    errors: list[str] = []
    names: list[str] = []
    for skill_dir in skill_dirs:
        names.append(skill_dir.name)
        errors.extend(_validate_skill(skill_dir, root))
    if len(names) != len(set(names)):
        errors.append("skill directory names are not unique")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(skill_dirs)} project Skill(s) under {skills_root}")
    print("Host Codex runtime discovery was not tested by this local validator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
