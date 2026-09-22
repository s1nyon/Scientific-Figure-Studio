"""Round 04 Design A: one-panel, directly labelled objective trajectories."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import CONFIG
from matplotlib.ticker import MultipleLocator

from figure_studio.analysis import running_best
from figure_studio.annotations import add_panel_label, label_line_end
from figure_studio.export import export_figure
from figure_studio.manifest import (
    build_data_provenance,
    load_manifest,
)
from figure_studio.nature_adapter import require_nature_context
from figure_studio.palettes import get_palette
from figure_studio.style import figure_style

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SKILL_ROOT = Path(r"C:\Users\Administrator\.codex\skills\nature-figure")


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the raw exercise table without changing observations."""

    frame = pd.read_csv(path)
    required = {"algorithm", "iteration", "objective"}
    if not required.issubset(frame.columns):
        missing = sorted(required.difference(frame.columns))
        raise ValueError(f"missing required columns: {missing}")
    if frame.empty or frame[list(required)].isna().any().any():
        raise ValueError("the required data columns must be non-empty and non-missing")
    if not np.isfinite(frame["objective"].to_numpy(dtype=float)).all():
        raise ValueError("objective must contain only finite values")
    if not np.isfinite(frame["iteration"].to_numpy(dtype=float)).all():
        raise ValueError("iteration must contain only finite values")
    if not np.equal(frame["iteration"], frame["iteration"].astype(int)).all():
        raise ValueError("iteration must contain integer-valued indices")
    if frame.duplicated(["algorithm", "iteration"]).any():
        raise ValueError("duplicate algorithm/iteration pairs are not allowed")
    frame = frame.sort_values(["algorithm", "iteration"], kind="stable").reset_index(drop=True)
    expected = set(CONFIG["algorithm_order"])
    observed = set(frame["algorithm"])
    if observed != expected:
        raise ValueError(f"algorithms differ from the design contract: {observed}")
    return frame


def series_by_algorithm(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return deterministic per-algorithm slices with direction-aware diagnostics."""

    series: dict[str, pd.DataFrame] = {}
    for algorithm in CONFIG["algorithm_order"]:
        subset = frame.loc[frame["algorithm"] == algorithm].copy()
        subset["historical_best"] = running_best(
            subset["objective"].to_numpy(), CONFIG["objective_direction"]
        )
        subset["delta_objective"] = subset["objective"].diff()
        series[algorithm] = subset
    return series


def build_figure(frame: pd.DataFrame):
    """Build the independent Design A figure."""

    palette = get_palette(CONFIG["palette_name"])
    grouped = series_by_algorithm(frame)
    with figure_style(CONFIG["style_name"], canvas="wide"):
        fig = plt.figure(figsize=(CONFIG["figure_width"], CONFIG["figure_height"]))
        fig.patch.set_facecolor(palette.background)
        ax = fig.add_axes(
            [CONFIG["grid_left"], CONFIG["grid_bottom"],
             CONFIG["grid_right"] - CONFIG["grid_left"],
             CONFIG["grid_top"] - CONFIG["grid_bottom"]]
        )
        add_panel_label(ax, "a", color=palette.ink, fontsize=CONFIG["base_font_size"])
        ax.set_title(CONFIG["title"], loc="left", pad=14, fontsize=CONFIG["title_size"],
                     fontweight="bold")

        for algorithm in CONFIG["algorithm_order"]:
            subset = grouped[algorithm]
            color = CONFIG["algorithm_colors"][algorithm]
            marker = CONFIG["algorithm_markers"][algorithm]
            ax.plot(
                subset["iteration"],
                subset["objective"],
                color=color,
                linewidth=CONFIG["line_width"],
                marker=marker,
                markersize=CONFIG["marker_size"],
                markerfacecolor=palette.background,
                markeredgewidth=1.0,
                markeredgecolor=color,
                label=algorithm,
                zorder=3,
            )
            final = subset.iloc[-1]
            label_line_end(
                ax,
                float(final["iteration"]),
                float(final["objective"]),
                f"{algorithm}  {final['objective']:.2f}",
                color=color,
                fontsize=CONFIG["base_font_size"],
                fontweight="bold",
                clip_on=False,
                ha="left",
                xytext=(7, 0),
            )

        proposed = grouped["Proposed"]
        mismatch = proposed.loc[proposed["objective"] != proposed["historical_best"]]
        if not mismatch.empty:
            row = mismatch.iloc[0]
            ax.plot(
                row["iteration"],
                row["historical_best"],
                marker="o",
                markersize=CONFIG["marker_size"] + 0.6,
                markerfacecolor=palette.background,
                markeredgecolor=palette.muted,
                markeredgewidth=1.0,
                linestyle="none",
                zorder=4,
            )
            ax.vlines(
                row["iteration"], row["historical_best"], row["objective"],
                color=palette.muted, linewidth=0.8, linestyle=(0, (2, 2)), zorder=2,
            )
            ax.annotate(
                "temporary increase  +0.02",
                xy=(row["iteration"], row["objective"]),
                xytext=(8, 12),
                textcoords="offset points",
                color=palette.muted,
                fontsize=CONFIG["footnote_size"],
                arrowprops={"arrowstyle": "-", "color": palette.muted, "lw": 0.7},
            )

        ax.set_xlim(*CONFIG["x_lim"])
        ax.set_ylim(*CONFIG["objective_ylim"])
        ax.set_xlabel("Iteration", labelpad=7)
        ax.set_ylabel("Objective value  (lower is better)", labelpad=8)
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.72)
        ax.tick_params(which="major", length=3.2, width=0.7, pad=3)
        ax.spines["left"].set_linewidth(CONFIG["axes_line_width"])
        ax.spines["bottom"].set_linewidth(CONFIG["axes_line_width"])
        ax.spines["left"].set_color(palette.ink)
        ax.spines["bottom"].set_color(palette.ink)

        fig.text(
            CONFIG["grid_left"], 0.065, CONFIG["data_status_note"],
            ha="left", va="bottom", color=palette.muted, fontsize=CONFIG["footnote_size"],
        )
        fig.text(
            CONFIG["grid_right"], 0.065,
            "current objective shown; historical best marked only at divergence",
            ha="right", va="bottom", color=palette.muted, fontsize=CONFIG["footnote_size"],
        )
        return fig


def main(
    output_dir: Path | str | None = None,
    data_path: Path | str | None = None,
    manifest_path: Path | str | None = None,
    skill_root: Path | str | None = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Render Design A through the project runner."""

    output = Path(output_dir or Path(__file__).parent).resolve()
    data = Path(
        data_path or Path(__file__).with_name(CONFIG["data_file"])
    ).resolve()
    manifest_file = Path(manifest_path or Path(__file__).with_name("data_manifest.json")).resolve()
    manifest = load_manifest(manifest_file).with_data_path(data, PROJECT_ROOT)
    nature_context = require_nature_context(skill_root or DEFAULT_SKILL_ROOT)
    frame = load_data(data)
    figure = build_figure(frame)
    provenance = build_data_provenance(
        manifest,
        {
            "figure_design": {
                "round": 4,
                "option": "A",
                "hero_panel": "a",
                "support_panels": [],
                "uncertainty_band": False,
                "historical_figure_inputs_used_before_draft": False,
            },
            "nature_context": nature_context,
            "objective_summary": {
                algorithm: {
                    "start": float(values.iloc[0]["objective"]),
                    "end": float(values.iloc[-1]["objective"]),
                    "net_change": float(values.iloc[-1]["objective"] - values.iloc[0]["objective"]),
                }
                for algorithm, values in series_by_algorithm(frame).items()
            },
        },
    )
    paths = export_figure(
        figure,
        output / CONFIG["figure_id"],
        formats=CONFIG["output_formats"],
        dpi=CONFIG["dpi"],
        overwrite=overwrite,
        provenance=provenance,
    )
    plt.close(figure)
    return paths


if __name__ == "__main__":
    main()
