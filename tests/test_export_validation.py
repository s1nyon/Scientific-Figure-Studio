from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from figure_studio.export import export_figure
from figure_studio.validation import validate_artifact, validate_numeric_frame


def test_export_figure_writes_vector_and_raster_outputs(tmp_path):
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    ax.plot([0, 1], [0, 1])
    outputs = export_figure(fig, tmp_path / "figure", provenance={"practice": True})
    assert {path.suffix for path in outputs.values()} == {".png", ".svg", ".pdf"}
    assert all(path.stat().st_size > 0 for path in outputs.values())
    assert (tmp_path / "figure.manifest.json").exists()
    plt.close(fig)


def test_export_figure_refuses_implicit_overwrite(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    export_figure(fig, tmp_path / "figure")
    with pytest.raises(FileExistsError):
        export_figure(fig, tmp_path / "figure")
    plt.close(fig)


def test_export_figure_normalises_svg_line_end_whitespace(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    outputs = export_figure(fig, tmp_path / "figure", formats=("svg",))
    svg_lines = outputs["svg"].read_text(encoding="utf-8").splitlines()
    assert all(line == line.rstrip() for line in svg_lines)
    plt.close(fig)


def test_validate_artifacts_reports_real_metadata(tmp_path):
    fig, ax = plt.subplots(figsize=(3.0, 2.0))
    ax.plot([0, 1], [0, 1])
    export_figure(fig, tmp_path / "figure")
    png_report = validate_artifact(tmp_path / "figure.png", "png")
    svg_report = validate_artifact(tmp_path / "figure.svg", "svg")
    pdf_report = validate_artifact(tmp_path / "figure.pdf", "pdf")
    assert png_report["width_px"] > 100
    assert svg_report["has_svg_root"] is True
    assert pdf_report["pages"] == 1
    plt.close(fig)


def test_validate_numeric_frame_reports_missing_and_nonfinite_columns():
    frame = pd.DataFrame({"x": [1.0, float("nan")]})
    with pytest.raises(ValueError, match="missing columns"):
        validate_numeric_frame(frame, ["x", "y"])
    with pytest.raises(ValueError, match="finite"):
        validate_numeric_frame(frame, ["x"])


def test_validate_artifact_rejects_unknown_kind(tmp_path):
    path = Path(tmp_path) / "figure.unknown"
    path.write_text("data", encoding="utf-8")
    with pytest.raises(ValueError, match="png"):
        validate_artifact(path, "unknown")
