from pathlib import Path

from templates.prediction.config import CONFIG
from templates.prediction.plot import build_figure, load_data, main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"


def test_prediction_keeps_train_validation_test_splits_visible():
    frame = load_data(DATA / "prediction_practice.csv")
    assert set(frame["split"]) == {"train", "validation", "test"}


def test_prediction_accepts_only_test_split_and_computes_metrics_there(tmp_path):
    path = tmp_path / "test_only.csv"
    path.write_text(
        "sample,split,x,y_true,y_pred\n1,test,0.0,1.0,0.8\n2,test,1.0,1.5,1.7\n",
        encoding="utf-8",
    )

    frame = load_data(path)
    figure = build_figure(frame, CONFIG)

    assert set(frame["split"]) == {"test"}
    assert any("Test RMSE" in text.get_text() for text in figure.axes[0].texts)
    figure.clf()


def test_prediction_without_split_column_uses_all_label_and_no_test_metric(tmp_path):
    path = tmp_path / "all_rows.csv"
    path.write_text(
        "sample,x,y_true,y_pred\n1,0.0,1.0,0.8\n2,1.0,1.5,1.7\n",
        encoding="utf-8",
    )

    frame = load_data(path)
    figure = build_figure(frame, CONFIG)

    assert set(frame["split"]) == {"all"}
    assert not any("Test RMSE" in text.get_text() for text in figure.axes[0].texts)
    figure.clf()


def test_prediction_figure_has_prediction_and_residual_axes():
    frame = load_data(DATA / "prediction_practice.csv")
    figure = build_figure(frame, CONFIG)
    assert len(figure.axes) == 2
    assert figure.axes[1].get_ylabel() == "Residual (unit)"
    figure.clf()


def test_prediction_main_returns_three_formats(tmp_path):
    outputs = main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
