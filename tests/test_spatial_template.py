from pathlib import Path

from templates.spatial.config import CONFIG
from templates.spatial.plot import build_figure, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_spatial_data_has_start_end_nodes_and_two_routes():
    data = load_data(DATA / "spatial_practice.csv")
    assert set(data["nodes"]["role"]) >= {"start", "end"}
    assert set(data["paths"]["path_id"]) == {"route-1", "route-2"}


def test_spatial_figure_uses_equal_axis_scaling():
    data = load_data(DATA / "spatial_practice.csv")
    figure = build_figure(data, CONFIG)
    assert figure.axes[0].get_aspect() in (1.0, "equal")
    figure.clf()


def test_spatial_main_returns_three_formats(tmp_path):
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
