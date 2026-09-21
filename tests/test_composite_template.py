from pathlib import Path

from templates.composite.config import CONFIG
from templates.composite.plot import build_figure, load_data

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_composite_has_one_hero_axis_and_two_evidence_axes():
    data = load_data(DATA / "composite_practice.csv")
    figure = build_figure(data, CONFIG)
    assert len(figure.axes) == 3
    assert figure.axes[0].get_position().width > figure.axes[1].get_position().width
    figure.clf()

