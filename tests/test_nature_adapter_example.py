from pathlib import Path

import pytest

from templates.nature_adapter.plot import main

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_ROOT = Path.home() / ".codex" / "skills" / "nature-figure"


def test_nature_adapter_refuses_unverified_or_missing_skill(tmp_path):
    with pytest.raises(ValueError, match="nature-figure"):
        main(output_dir=tmp_path / "missing", skill_root=tmp_path / "not-installed")


def test_nature_adapter_records_context_and_exports_when_fixed_skill_is_installed(tmp_path):
    if not DEFAULT_SKILL_ROOT.is_dir():
        pytest.skip("fixed Nature Skill has not been installed in this environment")
    outputs = main(output_dir=tmp_path, skill_root=DEFAULT_SKILL_ROOT)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
    context = (tmp_path / "nature_context.json").read_text(encoding="utf-8")
    assert "1930963cbc004da9ac8e3af7944d4f0a3488d3e1" in context
    assert "references/figure-contract.md" in context
    assert (tmp_path / "figure.manifest.json").exists()
