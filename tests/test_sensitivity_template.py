import json
from pathlib import Path

from templates.sensitivity.config import CONFIG
from templates.sensitivity.plot import build_figure, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_sensitivity_manifest_contains_units_and_center_value():
    manifest = json.loads(
        (ROOT / "templates/sensitivity/data_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["units"]["parameter"]
    assert manifest["color_center"] == 0


def test_sensitivity_figure_has_curve_and_heatmap_axes():
    frame = load_data(DATA / "sensitivity_practice.csv")
    figure = build_figure(frame, CONFIG)
    assert len(figure.axes) >= 2
    figure.clf()


def test_sensitivity_main_returns_three_formats(tmp_path):
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
