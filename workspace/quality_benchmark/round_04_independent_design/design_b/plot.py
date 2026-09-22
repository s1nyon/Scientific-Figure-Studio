"""Round 04 Design B: trajectory evidence paired with endpoint arithmetic."""

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
from figure_studio.manifest import build_data_provenance, load_manifest
from figure_studio.nature_adapter import require_nature_context
from figure_studio.palettes import get_palette
from figure_studio.style import figure_style

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SKILL_ROOT = Path(r"C:\Users\Administrator\.codex\skills\nature-figure")


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the raw exercise table without changing observations."""

    frame = pd.read_csv(path)
    required = {"algorithm", "iteration", "objective"}
    if not required.issubset(frame.columns):
        raise ValueError(f"missing required columns: {sorted(required.difference(frame.columns))}")
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
    observed = set(frame["algorithm"])
    expected = set(CONFIG["algorithm_order"])
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


def style_axis(ax, palette) -> None:
    """Apply a small shared axis treatment to both evidence panels."""

    ax.tick_params(which="major", length=3.0, width=0.7, pad=3)
    ax.spines["left"].set_linewidth(CONFIG["axes_line_width"])
    ax.spines["bottom"].set_linewidth(CONFIG["axes_line_width"])
    ax.spines["left"].set_color(palette.ink)
    ax.spines["bottom"].set_color(palette.ink)


def draw_trajectory(ax, grouped: dict[str, pd.DataFrame], palette) -> None:
    """Draw the left-hand current-objective path panel."""

    for algorithm in CONFIG["algorithm_order"]:
        subset = grouped[algorithm]
        color = CONFIG["algorithm_colors"][algorithm]
        marker = CONFIG["algorithm_markers"][algorithm]
        ax.plot(
            subset["iteration"], subset["objective"],
            color=color, linewidth=CONFIG["line_width"], marker=marker,
            markersize=CONFIG["marker_size"], markerfacecolor=palette.background,
            markeredgewidth=1.0, markeredgecolor=color, zorder=3,
        )
        final = subset.iloc[-1]
        label_line_end(
            ax, float(final["iteration"]), float(final["objective"]),
            f"{algorithm}  {final['objective']:.2f}",
            color=color, fontsize=CONFIG["base_font_size"], fontweight="bold",
            clip_on=False, ha="left", xytext=(7, 0),
        )

    proposed = grouped["Proposed"]
    mismatch = proposed.loc[proposed["objective"] != proposed["historical_best"]]
    if not mismatch.empty:
        row = mismatch.iloc[0]
        ax.plot(
            row["iteration"], row["historical_best"], marker="o",
            markersize=CONFIG["marker_size"] + 0.6, markerfacecolor=palette.background,
            markeredgecolor=palette.muted, markeredgewidth=1.0, linestyle="none", zorder=4,
        )
        ax.vlines(
            row["iteration"], row["historical_best"], row["objective"],
            color=palette.muted, linewidth=0.8, linestyle=(0, (2, 2)), zorder=2,
        )
        ax.annotate(
            "temporary increase  +0.02", xy=(row["iteration"], row["objective"]),
            xytext=(7, 11), textcoords="offset points", color=palette.muted,
            fontsize=CONFIG["footnote_size"],
            arrowprops={"arrowstyle": "-", "color": palette.muted, "lw": 0.7},
        )

    ax.set_xlim(*CONFIG["main_x_lim"])
    ax.set_ylim(*CONFIG["objective_ylim"])
    ax.set_xlabel("Iteration", labelpad=7)
    ax.set_ylabel("Objective value  (lower is better)", labelpad=7)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.72)
    style_axis(ax, palette)


def draw_endpoint_summary(ax, grouped: dict[str, pd.DataFrame], palette) -> None:
    """Draw start-to-end values without implying speed or uncertainty."""

    rows = {algorithm: len(CONFIG["algorithm_order"]) - 1 - index
            for index, algorithm in enumerate(CONFIG["algorithm_order"])}
    for algorithm in CONFIG["algorithm_order"]:
        subset = grouped[algorithm]
        start = float(subset.iloc[0]["objective"])
        end = float(subset.iloc[-1]["objective"])
        net = end - start
        y = rows[algorithm]
        color = CONFIG["algorithm_colors"][algorithm]
        marker = CONFIG["algorithm_markers"][algorithm]
        ax.plot([start, end], [y, y], color=color, linewidth=CONFIG["endpoint_line_width"],
                solid_capstyle="round", zorder=2)
        ax.scatter([start], [y], s=CONFIG["endpoint_marker_size"] ** 2, marker="o",
                   facecolor=palette.background, edgecolor=color, linewidth=1.0, zorder=4)
        ax.scatter([end], [y], s=CONFIG["endpoint_marker_size"] ** 2, marker=marker,
                   facecolor=color, edgecolor=palette.background, linewidth=0.7, zorder=4)
        ax.text(start - 0.035, y + 0.18, f"{start:.2f}", ha="right", va="bottom",
                color=palette.muted, fontsize=CONFIG["footnote_size"])
        ax.text(end + 0.035, y + 0.18, f"{end:.2f}", ha="left", va="bottom",
                color=color, fontsize=CONFIG["footnote_size"], fontweight="bold")
        ax.text(2.84, y - 0.19, f"Δ {net:+.2f}", ha="right", va="top",
                color=color, fontsize=CONFIG["footnote_size"], fontweight="bold")

    ax.set_xlim(*CONFIG["summary_x_lim"])
    ax.set_ylim(-0.65, 2.65)
    ax.set_yticks([rows[algorithm] for algorithm in CONFIG["algorithm_order"]])
    ax.set_yticklabels(CONFIG["algorithm_order"])
    for label, algorithm in zip(ax.get_yticklabels(), CONFIG["algorithm_order"]):
        label.set_color(CONFIG["algorithm_colors"][algorithm])
        label.set_fontweight("bold")
    ax.set_xlabel("Objective value\n(lower is better)", labelpad=7)
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.grid(axis="x", color=palette.grid, linewidth=0.55, alpha=0.72)
    style_axis(ax, palette)


def build_figure(frame: pd.DataFrame):
    """Build the independent Design B figure."""

    palette = get_palette(CONFIG["palette_name"])
    grouped = series_by_algorithm(frame)
    with figure_style(CONFIG["style_name"], canvas="wide"):
        fig = plt.figure(figsize=(CONFIG["figure_width"], CONFIG["figure_height"]))
        fig.patch.set_facecolor(palette.background)
        main_ax = fig.add_axes(CONFIG["main_rect"])
        summary_ax = fig.add_axes(CONFIG["summary_rect"])

        add_panel_label(main_ax, "a", color=palette.ink, fontsize=CONFIG["base_font_size"])
        main_ax.set_title(CONFIG["title_main"], loc="left", pad=14,
                          fontsize=CONFIG["title_size"], fontweight="bold")
        draw_trajectory(main_ax, grouped, palette)

        add_panel_label(summary_ax, "b", color=palette.ink, fontsize=CONFIG["base_font_size"])
        summary_ax.set_title(CONFIG["title_summary"], loc="left", pad=14,
                             fontsize=CONFIG["title_size"], fontweight="bold")
        draw_endpoint_summary(summary_ax, grouped, palette)

        fig.text(
            CONFIG["main_rect"][0], 0.078, "illustrative practice data",
            ha="left", va="bottom", color=palette.muted,
            fontsize=CONFIG["footnote_size"],
        )
        fig.text(
            CONFIG["summary_rect"][0] + CONFIG["summary_rect"][2], 0.078,
            "open = first  ·  filled = last  ·  Δ = last − first",
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
    """Render Design B through the project runner."""

    output = Path(output_dir or Path(__file__).parent).resolve()
    data = Path(data_path or PROJECT_ROOT / "examples/data/convergence_practice.csv").resolve()
    manifest_file = Path(manifest_path or Path(__file__).with_name("data_manifest.json")).resolve()
    manifest = load_manifest(manifest_file).with_data_path(data, PROJECT_ROOT)
    nature_context = require_nature_context(skill_root or DEFAULT_SKILL_ROOT)
    frame = load_data(data)
    figure = build_figure(frame)
    grouped = series_by_algorithm(frame)
    provenance = build_data_provenance(
        manifest,
        {
            "figure_design": {
                "round": 4,
                "option": "B",
                "hero_panel": "a",
                "support_panels": ["b"],
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
                for algorithm, values in grouped.items()
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
