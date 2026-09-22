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


@pytest.mark.parametrize("name", ILLUSTRATION_NAMES)
def test_illustration_template_reads_explicit_example_and_exports_formats(name, tmp_path):
    module = importlib.import_module(f"templates.illustration.{name}.plot")
    data_path = ROOT / "examples" / "data" / {
        "flowchart": "illustration_flowchart.json",
        "architecture": "illustration_architecture.json",
        "composite": "illustration_composite.csv",
    }[name]
    data = module.load_data(data_path)
    if name == "flowchart":
        assert set(data["nodes"]) == {"input", "prepare", "check", "fit", "revise", "report"}
    elif name == "architecture":
        assert set(data["modules"]) == {"input", "encoder", "solver", "decoder", "output"}
    else:
        assert {"chart", "structure"}.issubset(data)
    outputs = module.main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
