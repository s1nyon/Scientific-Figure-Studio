import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAMES = ("convergence", "prediction", "sensitivity", "pareto", "spatial", "composite")


@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_template_contract_has_source_config_manifest_and_readme(name):
    folder = PROJECT_ROOT / "templates" / name
    assert (folder / "plot.py").exists()
    assert (folder / "config.py").exists()
    assert (folder / "data_manifest.json").exists()
    assert (folder / "README.md").exists()


@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_practice_manifest_declares_nonproduction_data(name):
    manifest = json.loads(
        (PROJECT_ROOT / "templates" / name / "data_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["data_status"] == "illustrative practice data"
