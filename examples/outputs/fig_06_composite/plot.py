"""Generate a linked three-panel practice figure with one hero panel."""

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
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

from figure_studio.annotations import add_panel_label, add_reference_line  # noqa: E402
from figure_studio.export import export_figure  # noqa: E402
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402
from figure_studio.validation import validate_numeric_frame  # noqa: E402


def load_data(path: str | Path) -> dict[str, pd.DataFrame]:
    """Read the linked hero, residual, and sensitivity records."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = {"record_type", "x", "y"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"composite data missing columns: {sorted(missing)}")
    data = {
        "hero": frame[frame["record_type"] == "hero"].copy(),
        "residual": frame[frame["record_type"] == "residual"].copy(),
        "sensitivity": frame[frame["record_type"] == "sensitivity"].copy(),
    }
    if any(part.empty for part in data.values()):
        raise ValueError("composite data must contain hero, residual, and sensitivity rows")
    validate_numeric_frame(data["hero"], ["x", "y"])
    validate_numeric_frame(data["residual"], ["x", "y"])
    validate_numeric_frame(data["sensitivity"], ["parameter", "response"])
    return data


def build_figure(data: dict[str, pd.DataFrame], config: dict[str, object]) -> plt.Figure:
    """Build an asymmetric hero-plus-evidence layout from one study table."""

    palette = get_palette(str(config["palette_name"]))
    colors = dict(config["algorithm_colors"])
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
            figure = plt.figure(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                layout="constrained",
            )
            grid = figure.add_gridspec(
                2,
                2,
                width_ratios=(1.72, 1.0),
                height_ratios=(1.0, 1.0),
                wspace=0.28,
                hspace=0.34,
            )
            hero_ax = figure.add_subplot(grid[:, 0])
            residual_ax = figure.add_subplot(grid[0, 1])
            sensitivity_ax = figure.add_subplot(grid[1, 1])

            for index, (algorithm, group) in enumerate(
                data["hero"].groupby("algorithm", sort=False)
            ):
                color = colors.get(
                    algorithm, palette.category_cycle[index % len(palette.category_cycle)]
                )
                group = group.sort_values("x")
                hero_ax.plot(
                    group["x"],
                    group["y"],
                    color=color,
                    linewidth=float(config["line_width"]),
                    marker="o",
                    markersize=float(config["marker_size"]),
                    label=algorithm,
                )
            hero_ax.set_xlabel("Evaluation checkpoint")
            hero_ax.set_ylabel("Normalized performance")
            hero_ax.set_title("Primary result", loc="left", pad=10)
            hero_ax.legend(loc=str(config["legend_location"]))
            hero_ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.8)

            for index, (algorithm, group) in enumerate(
                data["residual"].groupby("algorithm", sort=False)
            ):
                color = colors.get(
                    algorithm, palette.category_cycle[index % len(palette.category_cycle)]
                )
                group = group.sort_values("x")
                residual_ax.plot(
                    group["x"],
                    group["y"],
                    color=color,
                    linewidth=float(config["line_width"]) - 0.35,
                    marker="o",
                    markersize=max(2.5, float(config["marker_size"]) - 1.0),
                    label=algorithm,
                )
            add_reference_line(residual_ax, 0.0, axis="y", color=palette.muted)
            residual_ax.set_xlabel("Checkpoint")
            residual_ax.set_ylabel("Residual")
            residual_ax.set_title("Test residuals", loc="left", pad=8)
            residual_ax.grid(axis="y", color=palette.grid, linewidth=0.5, alpha=0.75)

            sensitivity = data["sensitivity"].sort_values("parameter")
            sensitivity_ax.plot(
                sensitivity["parameter"],
                sensitivity["response"],
                color=palette.accent,
                linewidth=float(config["line_width"]) - 0.2,
                marker="o",
                markersize=max(2.5, float(config["marker_size"]) - 0.8),
            )
            sensitivity_ax.set_xlabel("Parameter α (a.u.)")
            sensitivity_ax.set_ylabel("Response")
            sensitivity_ax.set_title("Parameter evidence", loc="left", pad=8)
            sensitivity_ax.grid(axis="y", color=palette.grid, linewidth=0.5, alpha=0.75)

            add_panel_label(hero_ax, "(a)", color=palette.ink)
            add_panel_label(residual_ax, "(b)", color=palette.ink)
            add_panel_label(sensitivity_ax, "(c)", color=palette.ink)
            figure.text(
                0.01,
                0.005,
                "同一模拟研究场景 · linked illustrative practice data",
                color=palette.muted,
                fontsize=max(6.5, float(config["font_size"]) - 1.5),
            )
            return figure


def main(output_dir: str | Path | None = None, data_path: str | Path | None = None):
    """Generate composite artifacts and return their paths."""

    source = PROJECT_ROOT / str(data_path or CONFIG["data_file"])
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    figure = build_figure(load_data(source), CONFIG)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="composite"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=True,
                provenance={
                    "data_status": "illustrative practice data",
                    "data_file": str(source.relative_to(PROJECT_ROOT)),
                    "panels": [
                        "Primary result by algorithm",
                        "Residual evidence",
                        "One-parameter sensitivity evidence",
                    ],
                },
            )
    finally:
        plt.close(figure)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--data-path", type=Path, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(output_dir=arguments.output_dir, data_path=arguments.data_path)
