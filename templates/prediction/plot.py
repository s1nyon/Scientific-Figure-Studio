"""Generate an honest prediction and residual analysis figure."""

import argparse
import os
import sys
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_configured_root = os.environ.get("SCIENTIFIC_FIGURE_STUDIO_ROOT")
PROJECT_ROOT = (
    Path(_configured_root)
    if _configured_root
    else next(
        parent
        for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]
        if (parent / "figure_studio").is_dir()
    )
)
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .config import CONFIG
except ImportError:
    from config import CONFIG

from figure_studio.annotations import add_reference_line  # noqa: E402
from figure_studio.export import export_figure  # noqa: E402
from figure_studio.manifest import (  # noqa: E402
    build_data_provenance,
    load_manifest,
    provenance_data_label,
)
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402
from figure_studio.validation import validate_numeric_frame  # noqa: E402


def load_data(path: str | Path) -> pd.DataFrame:
    """Read prediction rows with optional, semantically explicit split labels."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    validate_numeric_frame(frame, ["sample", "x", "y_true", "y_pred"])
    frame = frame.copy()
    if "split" not in frame:
        frame["split"] = "all"
    else:
        frame["split"] = (
            frame["split"]
            .astype("string")
            .fillna("all")
            .str.strip()
            .replace("", "all")
        )
    frame["residual"] = frame["y_true"] - frame["y_pred"]
    return frame.sort_values("sample").reset_index(drop=True)


def build_figure(frame: pd.DataFrame, config: dict[str, object]) -> plt.Figure:
    """Build observed/predicted and residual panels from measured values."""

    validate_numeric_frame(frame, ["sample", "x", "y_true", "y_pred"])
    frame = frame.copy()
    if "split" not in frame:
        frame["split"] = "all"
    else:
        frame["split"] = (
            frame["split"]
            .astype("string")
            .fillna("all")
            .str.strip()
            .replace("", "all")
        )
    if "residual" not in frame:
        frame["residual"] = frame["y_true"] - frame["y_pred"]
    palette = get_palette(str(config["palette_name"]))
    with figure_style(str(config["style_name"]), canvas="composite"):
        with plt.rc_context(
            {
                "font.size": float(config["font_size"]),
                "axes.labelsize": float(config["font_size"]),
                "xtick.labelsize": float(config["font_size"]) - 1.0,
                "ytick.labelsize": float(config["font_size"]) - 1.0,
                "legend.fontsize": float(config["font_size"]) - 1.0,
            }
        ):
            fig, (main_ax, residual_ax) = plt.subplots(
                2,
                1,
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                sharex=True,
                height_ratios=(2.2, 1.0),
                layout="constrained",
            )
            ordered = frame.sort_values("x")
            main_ax.plot(
                ordered["x"],
                ordered["y_true"],
                color=palette.ink,
                linewidth=float(config["line_width"]),
                marker="o",
                markersize=float(config["marker_size"]),
                label="Observed",
            )
            split_colors = dict(config["split_colors"])
            split_markers = dict(config["split_markers"])
            split_names = list(dict.fromkeys(ordered["split"].tolist()))
            fallback_markers = tuple(palette.markers)
            for index, split in enumerate(split_names):
                subset = ordered[ordered["split"] == split]
                color = split_colors.get(
                    split, palette.category_cycle[index % len(palette.category_cycle)]
                )
                marker = split_markers.get(
                    split, fallback_markers[index % len(fallback_markers)]
                )
                main_ax.plot(
                    subset["x"],
                    subset["y_pred"],
                    color=color,
                    linewidth=float(config["line_width"]),
                    marker=marker,
                    markersize=float(config["marker_size"]),
                    label=f"Predicted · {split}",
                )
                residual_ax.scatter(
                    subset["x"],
                    subset["residual"],
                    color=color,
                    marker=marker,
                    s=(float(config["marker_size"]) * 2.5) ** 2,
                    label=split,
                    zorder=3,
                )

            test = ordered[ordered["split"] == "test"]
            if not test.empty:
                rmse = sqrt(float(np.mean(test["residual"] ** 2)))
                mae = float(np.mean(np.abs(test["residual"])))
                main_ax.text(
                    0.99,
                    0.04,
                    f"Test RMSE = {rmse:.3f}\nTest MAE = {mae:.3f}",
                    transform=main_ax.transAxes,
                    ha="right",
                    va="bottom",
                    color=palette.ink,
                    fontsize=max(6.5, float(config["font_size"]) - 1.0),
                )
            for split in split_names[1:]:
                first_x = float(ordered.loc[ordered["split"] == split, "x"].min())
                main_ax.axvline(first_x, color=palette.grid, linewidth=0.75, linestyle=":")
                residual_ax.axvline(first_x, color=palette.grid, linewidth=0.75, linestyle=":")
            add_reference_line(residual_ax, 0.0, axis="y", color=palette.muted, linewidth=0.8)
            main_ax.set_ylabel("Response (unit)")
            residual_ax.set_xlabel("Input (unit)")
            residual_ax.set_ylabel("Residual (unit)")
            main_ax.set_title("Prediction and residual analysis", loc="left", pad=10)
            main_ax.legend(loc=str(config["legend_location"]), ncols=2)
            residual_ax.legend(loc="upper right", ncols=3)
            if config["x_limits"] is not None:
                residual_ax.set_xlim(config["x_limits"])
            if config["y_limits"] is not None:
                main_ax.set_ylim(config["y_limits"])
            data_label = provenance_data_label(str(config.get("data_status", "")))
            if data_label:
                fig.text(
                    0.01,
                    0.005,
                    data_label,
                    color=palette.muted,
                    fontsize=max(6.5, float(config["font_size"]) - 1.5),
                )
            return fig


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    overwrite: bool = False,
):
    """Generate prediction artifacts and return their paths."""

    manifest_file = Path(manifest_path) if manifest_path else Path(__file__).with_name(
        "data_manifest.json"
    )
    manifest = load_manifest(
        manifest_file,
        base_dir=manifest_file.parent if manifest_path else PROJECT_ROOT,
    )
    if data_path is not None:
        manifest = manifest.with_data_path(data_path, PROJECT_ROOT)
    source = manifest.data_path
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    frame = load_data(source)
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    figure = build_figure(frame, runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="composite"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=overwrite,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "splits": sorted(frame["split"].astype(str).unique()),
                        "uncertainty_basis": (
                            "No prediction interval is shown; input data contain no interval basis."
                        ),
                    },
                ),
            )
    finally:
        plt.close(figure)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
        overwrite=arguments.overwrite,
    )
