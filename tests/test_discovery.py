from pathlib import Path

from tools.validate_skills import main as validate_skills


def test_project_skill_validator_accepts_current_tree():
    assert validate_skills(Path(__file__).resolve().parents[1]) == 0

