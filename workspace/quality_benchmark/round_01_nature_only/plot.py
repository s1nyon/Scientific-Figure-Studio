"""Render the round-01 Nature-style convergence evidence figure."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator

_configured_root = os.environ.get("SCIENTIFIC_FIGURE_STUDIO_ROOT")
_root_candidates: list[Path] = []
if _configured_root:
    _root_candidates.append(Path(_configured_root))
_here = Path(__file__).resolve()
_root_candidates.extend([_here, *_here.parents, Path.cwd(), *Path.cwd().parents])
PROJECT_ROOT = next(
    (candidate for candidate in _root_candidates if (candidate / "figure_studio").is_dir()),
    Path.cwd(),
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .config import CONFIG
except ImportError:
    from config import CONFIG

from figure_studio.analysis import running_best  # noqa: E402
from figure_studio.annotations import add_panel_label  # noqa: E402
from figure_studio.export import export_figure  # noqa: E402
from figure_studio.manifest import (  # noqa: E402
    build_data_provenance,
    load_manifest,
    provenance_data_label,
)
from figure_studio.nature_adapter import require_nature_context  # noqa: E402
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402
from figure_studio.validation import validate_numeric_frame  # noqa: E402

DEFAULT_SKILL_ROOT = Path.home() / ".codex" / "skills" / "nature-figure"


def load_data(path: str | Path) -> pd.DataFrame:
    """Read and validate the supplied convergence table without changing it."""

    data_path = Path(path)
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = ["algorithm", "iteration", "objective"]
    missing = sorted(set(required).difference(frame.columns))
    if missing:
        raise ValueError(f"data is missing required columns: {missing}")
    validate_numeric_frame(frame, ["iteration", "objective"])
    if frame["algorithm"].isna().any():
        raise ValueError("algorithm must not contain missing values")
    if frame.duplicated(["algorithm", "iteration"]).any():
        raise ValueError("algorithm/iteration pairs must be unique")
    if not np.equal(frame["iteration"].to_numpy(dtype=float) % 1, 0).all():
        raise ValueError("iteration must contain integer-like counts")
    return frame.sort_values(["algorithm", "iteration"]).reset_index(drop=True)


def _ordered_algorithms(frame: pd.DataFrame) -> list[str]:
    configured = [str(item) for item in CONFIG["algorithm_order"]]
    present = [str(item) for item in frame["algorithm"].drop_duplicates()]
    return [name for name in configured if name in present] + [
        name for name in present if name not in configured
    ]


def _series_by_algorithm(
    frame: pd.DataFrame, algorithms: list[str]
) -> dict[str, dict[str, np.ndarray]]:
    series: dict[str, dict[str, np.ndarray]] = {}
    for algorithm in algorithms:
        group = frame.loc[frame["algorithm"] == algorithm].sort_values("iteration")
        current = group["objective"].to_numpy(dtype=float)
        iterations = group["iteration"].to_numpy(dtype=float)
        series[algorithm] = {
            "iteration": iterations,
            "current": current,
            "best": running_best(current, goal=str(CONFIG["objective_direction"])),
            "delta": np.diff(current),
        }
    return series


def _style_axis(axis: plt.Axes, palette) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(palette.ink)
    axis.spines["bottom"].set_color(palette.ink)
    axis.tick_params(axis="both", which="major", length=3, width=0.6, pad=2)
    axis.grid(False)


def _make_delta_cmap(palette):
    return mcolors.LinearSegmentedColormap.from_list(
        "objective_delta",
        ["#D7E5EB", palette.primary, "#FFFFFF", "#F7E8DA", palette.accent],
        N=256,
    )


def build_figure(
    frame: pd.DataFrame,
    config: dict[str, object],
    objective_direction: str = "minimize",
    data_status: str = "illustrative practice data",
) -> plt.Figure:
    """Build the three-panel evidence figure from the validated input frame."""

    validate_numeric_frame(frame, ["iteration", "objective"])
    if objective_direction not in {"minimize", "maximize"}:
        raise ValueError("objective_direction must be 'minimize' or 'maximize'")
    algorithms = _ordered_algorithms(frame)
    if not algorithms:
        raise ValueError("no algorithms are available for plotting")
    series = _series_by_algorithm(frame, algorithms)
    palette = get_palette(str(config["palette_name"]))
    colors = dict(config["algorithm_colors"])
    markers = dict(config["algorithm_markers"])

    with figure_style(str(config["style_name"]), canvas="composite"):
        with plt.rc_context(
            {
                "font.size": float(config["base_font_size"]),
                "axes.labelsize": float(config["base_font_size"]),
                "xtick.labelsize": float(config["base_font_size"]) - 1.0,
                "ytick.labelsize": float(config["base_font_size"]) - 1.0,
                "legend.fontsize": float(config["base_font_size"]) - 1.0,
                "axes.linewidth": float(config["axes_line_width"]),
            }
        ):
            figure = plt.figure(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                facecolor=palette.background,
            )
            gridspec = figure.add_gridspec(
                2,
                2,
                width_ratios=(
                    float(config["main_width_ratio"]),
                    float(config["support_width_ratio"]),
                ),
                left=float(config["grid_left"]),
                right=float(config["grid_right"]),
                top=float(config["grid_top"]),
                bottom=float(config["grid_bottom"]),
                wspace=float(config["grid_wspace"]),
                hspace=float(config["grid_hspace"]),
            )
            axis_a = figure.add_subplot(gridspec[:, 0])
            axis_b = figure.add_subplot(gridspec[0, 1])
            axis_c = figure.add_subplot(gridspec[1, 1])

            figure.text(
                float(config["grid_left"]),
                0.962,
                str(config["title"]),
                ha="left",
                va="top",
                fontsize=float(config["header_font_size"]),
                fontweight="bold",
                color=palette.ink,
            )
            figure.text(
                float(config["grid_left"]),
                0.925,
                str(config["subtitle"]),
                ha="left",
                va="top",
                fontsize=float(config["base_font_size"]) - 0.4,
                color=palette.muted,
            )

            for axis, label in ((axis_a, "a"), (axis_b, "b"), (axis_c, "c")):
                add_panel_label(
                    axis,
                    label,
                    xy=(
                        float(config["panel_label_x"]),
                        float(config["panel_label_y"]),
                    ),
                    fontsize=float(config["panel_label_size"]),
                    color=palette.ink,
                    ha="right",
                )
                _style_axis(axis, palette)

            # Panel a: raw values retain every observation; solid traces are the
            # direction-aware incumbent, so a temporary regression remains visible.
            for algorithm in algorithms:
                values = series[algorithm]
                color = colors.get(algorithm, palette.category_cycle[0])
                marker = markers.get(algorithm, "o")
                axis_a.plot(
                    values["iteration"],
                    values["current"],
                    color=color,
                    linewidth=float(config["current_line_width"]),
                    linestyle=":",
                    alpha=0.62,
                    marker=marker,
                    markersize=float(config["current_marker_size"]),
                    markerfacecolor=palette.background,
                    markeredgecolor=color,
                    markeredgewidth=0.75,
                    zorder=2,
                )
                axis_a.plot(
                    values["iteration"],
                    values["best"],
                    color=color,
                    linewidth=float(config["line_width"]),
                    linestyle="-",
                    marker=marker,
                    markersize=float(config["marker_size"]),
                    markerfacecolor=color,
                    markeredgecolor=palette.background,
                    markeredgewidth=0.6,
                    zorder=3,
                )
                axis_a.annotate(
                    algorithm,
                    xy=(values["iteration"][-1], values["best"][-1]),
                    xytext=(7, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=float(config["base_font_size"]) - 0.4,
                    fontweight="bold",
                    color=color,
                    bbox={
                        "boxstyle": "round,pad=0.12",
                        "facecolor": palette.background,
                        "edgecolor": "none",
                        "alpha": 0.9,
                    },
                )

            axis_a.set_title(
                "Objective trajectory",
                loc="left",
                pad=float(config["panel_title_pad"]),
                fontsize=float(config["title_font_size"]),
                fontweight="bold",
                color=palette.ink,
            )
            axis_a.set_xlabel("Iteration")
            axis_a.set_ylabel("Objective value (practice unit)\n(lower is better)")
            axis_a.set_xlim(0.7, 12.25)
            axis_a.set_xticks(np.arange(1, 11))
            axis_a.set_ylim(0.75, 2.55)
            axis_a.yaxis.set_major_locator(FixedLocator([0.8, 1.2, 1.6, 2.0, 2.4]))
            axis_a.grid(axis="y", color=palette.grid, linewidth=0.5, alpha=0.9)
            series_handles = [
                mlines.Line2D(
                    [],
                    [],
                    color=palette.ink,
                    linewidth=float(config["line_width"]),
                    marker="o",
                    markersize=4.0,
                    label="historical best",
                ),
                mlines.Line2D(
                    [],
                    [],
                    color=palette.muted,
                    linewidth=float(config["current_line_width"]),
                    linestyle=":",
                    marker="o",
                    markersize=3.2,
                    markerfacecolor=palette.background,
                    label="current objective",
                ),
            ]
            axis_a.legend(
                handles=series_handles,
                loc="upper right",
                bbox_to_anchor=(0.985, 0.995),
                frameon=False,
                handlelength=2.1,
                borderaxespad=0,
            )

            # Panel b: the local update view makes sign and non-monotonic steps
            # explicit without inventing a threshold or an uncertainty estimate.
            delta_matrix = np.vstack([series[algorithm]["delta"] for algorithm in algorithms])
            max_abs_delta = float(np.max(np.abs(delta_matrix)))
            delta_norm = mcolors.TwoSlopeNorm(
                vmin=-max_abs_delta,
                vcenter=0.0,
                vmax=max_abs_delta,
            )
            image = axis_b.imshow(
                delta_matrix,
                cmap=_make_delta_cmap(palette),
                norm=delta_norm,
                aspect="auto",
                interpolation="nearest",
            )
            axis_b.set_title(
                "Stepwise update Δobjective",
                loc="left",
                pad=float(config["panel_title_pad"]),
                fontsize=float(config["title_font_size"]),
                fontweight="bold",
                color=palette.ink,
            )
            axis_b.set_xticks(np.arange(delta_matrix.shape[1]))
            axis_b.set_xticklabels(
                [str(int(value)) for value in series[algorithms[0]]["iteration"][1:]]
            )
            axis_b.set_yticks(np.arange(len(algorithms)))
            axis_b.set_yticklabels(algorithms)
            axis_b.set_xlabel("Destination iteration\n- improvement · + regression", labelpad=4)
            axis_b.tick_params(axis="both", which="major", length=0, pad=3)
            axis_b.set_xticks(np.arange(-0.5, delta_matrix.shape[1], 1), minor=True)
            axis_b.set_yticks(np.arange(-0.5, len(algorithms), 1), minor=True)
            axis_b.grid(which="minor", color=palette.background, linewidth=0.9)
            axis_b.tick_params(which="minor", bottom=False, left=False)
            for row_index, algorithm in enumerate(algorithms):
                for column_index, value in enumerate(series[algorithm]["delta"]):
                    if value > 0:
                        axis_b.text(
                            column_index,
                            row_index,
                            f"{value:+.2f}",
                            ha="center",
                            va="center",
                            fontsize=float(config["base_font_size"]) - 0.8,
                            fontweight="bold",
                            color=palette.accent,
                        )
            colorbar = figure.colorbar(
                image,
                ax=axis_b,
                orientation="horizontal",
                fraction=0.08,
                pad=0.34,
                aspect=24,
            )
            colorbar.set_ticks([-max_abs_delta, 0.0, max_abs_delta])
            colorbar.set_ticklabels(
                [f"-{max_abs_delta:.2f}", "0", f"+{max_abs_delta:.2f}"]
            )
            colorbar.ax.tick_params(labelsize=5.8, length=2, pad=1)
            colorbar.set_label("Δ objective", fontsize=6.2, labelpad=1)
            colorbar.outline.set_linewidth(0.35)

            # Panel c: an endpoint dumbbell avoids a zero-baseline bar and keeps
            # the start/end values in the original objective scale.
            y_positions = np.arange(len(algorithms))[::-1]
            for y_position, algorithm in zip(y_positions, algorithms, strict=True):
                values = series[algorithm]
                color = colors.get(algorithm, palette.category_cycle[0])
                start = float(values["current"][0])
                end = float(values["current"][-1])
                delta = end - start
                axis_c.plot(
                    [end, start],
                    [y_position, y_position],
                    color=palette.grid,
                    linewidth=4.0,
                    solid_capstyle="round",
                    zorder=1,
                )
                axis_c.scatter(
                    [start],
                    [y_position],
                    s=34,
                    facecolors=palette.background,
                    edgecolors=color,
                    linewidths=1.15,
                    zorder=3,
                )
                axis_c.scatter(
                    [end],
                    [y_position],
                    s=39,
                    facecolors=color,
                    edgecolors=palette.background,
                    linewidths=0.65,
                    zorder=4,
                )
                axis_c.text(
                    start,
                    y_position + 0.19,
                    f"{start:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=float(config["base_font_size"]) - 0.5,
                    color=palette.muted,
                )
                axis_c.text(
                    end,
                    y_position - 0.19,
                    f"{end:.2f}",
                    ha="center",
                    va="top",
                    fontsize=float(config["base_font_size"]) - 0.5,
                    fontweight="bold",
                    color=color,
                )
                axis_c.text(
                    max(start, end) + 0.08,
                    y_position,
                    f"Δ {delta:+.2f}",
                    ha="left",
                    va="center",
                    fontsize=float(config["base_font_size"]) - 0.5,
                    color=color,
                )
            axis_c.set_title(
                "Net change over shown window",
                loc="left",
                pad=float(config["panel_title_pad"]),
                fontsize=float(config["title_font_size"]),
                fontweight="bold",
                color=palette.ink,
            )
            axis_c.set_xlabel("Objective value (practice unit)")
            axis_c.set_yticks(y_positions)
            axis_c.set_yticklabels(algorithms)
            axis_c.set_xlim(0.72, 2.92)
            axis_c.set_ylim(-0.55, float(len(algorithms) - 1) + 0.58)
            axis_c.set_xticks([0.8, 1.2, 1.6, 2.0, 2.4, 2.8])
            axis_c.grid(axis="x", color=palette.grid, linewidth=0.5, alpha=0.9)
            axis_c.text(
                0.0,
                1.02,
                "open = iteration 1  ·  filled = iteration 10",
                transform=axis_c.transAxes,
                ha="left",
                va="bottom",
                fontsize=float(config["base_font_size"]) - 1.4,
                color=palette.muted,
            )

            status_label = provenance_data_label(str(data_status)) or str(
                config["data_status_note"]
            )
            figure.text(
                float(config["grid_left"]),
                0.045,
                status_label,
                ha="left",
                va="bottom",
                fontsize=float(config["footnote_font_size"]),
                color=palette.muted,
            )
            figure.text(
                float(config["grid_right"]),
                0.045,
                "objective direction: minimize",
                ha="right",
                va="bottom",
                fontsize=float(config["footnote_font_size"]),
                color=palette.muted,
            )
            return figure


def _write_nature_context(path: Path, context: dict[str, object]) -> None:
    """Write a portable context record without exposing a machine-specific path."""

    if path.is_file():
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            record = {}
    else:
        record = {}
    if not isinstance(record, dict):
        record = {}
    record.update({key: value for key, value in context.items() if key != "skill_root"})
    record["skill_root"] = "<installed nature-figure skill>"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    skill_root: str | Path | None = None,
    overwrite: bool = False,
):
    """Load the fixed Nature context, render, and return exported artifact paths."""

    nature_context = require_nature_context(skill_root or DEFAULT_SKILL_ROOT)
    manifest_file = Path(manifest_path) if manifest_path else Path(__file__).with_name(
        "data_manifest.json"
    )
    manifest = load_manifest(
        manifest_file,
        base_dir=manifest_file.parent if manifest_path else PROJECT_ROOT,
    )
    if data_path is not None:
        manifest = manifest.with_data_path(data_path, PROJECT_ROOT)
    destination = Path(output_dir) if output_dir else Path(__file__).parent
    destination.mkdir(parents=True, exist_ok=True)
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    figure = build_figure(
        load_data(manifest.data_path),
        runtime_config,
        objective_direction=manifest.objective_direction
        or str(CONFIG["objective_direction"]),
        data_status=manifest.data_status,
    )
    context_path = destination / "nature_context.json"
    _write_nature_context(context_path, nature_context)
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
                        "nature_context_file": context_path.name,
                        "nature_commit": nature_context["commit"],
                        "nature_references_loaded": nature_context["references_loaded"],
                        "project_backend": nature_context["project_backend"],
                        "upstream_r_track_preserved": nature_context[
                            "upstream_r_track_preserved"
                        ],
                        "figure_design": {
                            "hero_panel": "a",
                            "support_panels": ["b", "c"],
                            "current_vs_historical_best": True,
                            "uncertainty_band": False,
                        },
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
    parser.add_argument("--skill-root", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
        skill_root=arguments.skill_root,
        overwrite=arguments.overwrite,
    )
