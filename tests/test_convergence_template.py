from pathlib import Path

import pandas as pd

from figure_studio.analysis import running_best
from templates.convergence.config import CONFIG
from templates.convergence.plot import build_figure, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_convergence_uses_running_best_for_minimization():
    frame = pd.DataFrame({"iteration": [1, 2, 3], "objective": [3.0, 2.0, 2.5]})
    assert running_best(frame["objective"], goal="minimize").tolist() == [3.0, 2.0, 2.0]


def test_convergence_loads_practice_data_with_three_algorithms():
    frame = load_data(DATA / "convergence_practice.csv")
    assert set(frame["algorithm"]) == {"Proposed", "Adaptive", "Baseline"}
    assert frame["objective"].notna().all()


def test_convergence_builds_one_axes_and_main_returns_three_formats(tmp_path):
    frame = load_data(DATA / "convergence_practice.csv")
    figure = build_figure(frame, CONFIG)
    assert len(figure.axes) == 1
    figure.clf()
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
