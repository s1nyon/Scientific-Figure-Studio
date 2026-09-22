from pathlib import Path

import pytest


def test_pinned_nature_tree_contract_declares_complete_fixed_tree():
    from tools.nature_figure_lock import EXPECTED_FILES, PINNED_COMMIT

    assert PINNED_COMMIT == "1930963cbc004da9ac8e3af7944d4f0a3488d3e1"
    assert len(EXPECTED_FILES) == 30
    assert "SKILL.md" in EXPECTED_FILES
    assert "references/figure-contract.md" in EXPECTED_FILES
    assert "assets/chart-atlas/atlas-10-network-matrix.png" in EXPECTED_FILES


def test_incomplete_nature_tree_is_rejected(tmp_path: Path):
    from tools.verify_nature_figure import verify_nature_tree

    (tmp_path / "nature-figure").mkdir()
    with pytest.raises(ValueError, match="missing"):
        verify_nature_tree(tmp_path / "nature-figure")


def test_nature_context_requires_verified_references(tmp_path: Path):
    from figure_studio.nature_adapter import build_nature_context

    (tmp_path / "SKILL.md").write_text("---\nname: nature-figure\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        build_nature_context(tmp_path, ("references/figure-contract.md",))
