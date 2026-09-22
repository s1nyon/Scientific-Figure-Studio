import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATION_NAMES = ("flowchart", "architecture", "composite")


@pytest.mark.parametrize("name", ILLUSTRATION_NAMES)
def test_illustration_template_has_delivery_contract(name):
    folder = ROOT / "templates" / "illustration" / name
    assert (folder / "plot.py").exists()
    assert (folder / "config.py").exists()
    assert (folder / "data_manifest.json").exists()
    assert (folder / "README.md").exists()


@pytest.mark.parametrize("name", ILLUSTRATION_NAMES)
def test_illustration_template_exposes_load_build_and_main(name):
    module = importlib.import_module(f"templates.illustration.{name}.plot")
    assert callable(module.load_data)
    assert callable(module.build_figure)
    assert callable(module.main)
