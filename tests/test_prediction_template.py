from pathlib import Path

from templates.prediction.config import CONFIG
from templates.prediction.plot import build_figure, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_prediction_keeps_train_validation_test_splits_visible():
    frame = load_data(DATA / "prediction_practice.csv")
    assert set(frame["split"]) == {"train", "validation", "test"}


def test_prediction_figure_has_prediction_and_residual_axes():
    frame = load_data(DATA / "prediction_practice.csv")
    figure = build_figure(frame, CONFIG)
    assert len(figure.axes) == 2
    assert figure.axes[1].get_ylabel() == "Residual (unit)"
    figure.clf()


def test_prediction_main_returns_three_formats(tmp_path):
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
