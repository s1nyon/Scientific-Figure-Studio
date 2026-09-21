from pathlib import Path

import pandas as pd

from templates.pareto.config import CONFIG
from templates.pareto.plot import build_figure, build_front, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_pareto_template_does_not_call_all_points_a_front():
    frame = pd.DataFrame(
        {"solution": ["a", "b", "c"], "cost": [1, 2, 3], "risk": [3, 2, 4]}
    )
    front = build_front(frame, ("minimize", "minimize"))
    assert set(front["solution"]) == {"a", "b"}


def test_pareto_figure_contains_feasible_and_front_layers():
    frame = load_data(DATA / "pareto_practice.csv")
    figure = build_figure(frame, CONFIG)
    assert len(figure.axes) == 1
    assert len(figure.axes[0].collections) >= 2
    figure.clf()


def test_pareto_main_returns_three_formats(tmp_path):
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
