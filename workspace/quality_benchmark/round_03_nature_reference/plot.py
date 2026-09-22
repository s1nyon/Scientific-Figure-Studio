"""Render the round-03 reference-guided convergence figure.

The supplied journal figure is used only for visual design methods. This
renderer keeps the practice data unchanged, uses no external data, and keeps
the main claim limited to the displayed trajectories.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
from figure_studio.annotations import add_panel_label, label_line_end  # noqa: E402
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
    """Read the raw convergence table and validate its structural assumptions."""

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
    frame: pd.DataFrame, algorithms: list[str], objective_direction: str
) -> dict[str, dict[str, np.ndarray]]:
    series: dict[str, dict[str, np.ndarray]] = {}
    for algorithm in algorithms:
        group = frame.loc[frame["algorithm"] == algorithm].sort_values("iteration")
        iterations = group["iteration"].to_numpy(dtype=float)
        current = group["objective"].to_numpy(dtype=float)
        if len(iterations) < 2:
            raise ValueError(f"algorithm {algorithm!r} needs at least two iterations")
        if not np.all(np.diff(iterations) > 0):
            raise ValueError(f"iterations for {algorithm!r} must be strictly increasing")
        series[algorithm] = {
            "iteration": iterations,
            "current": current,
            "best": running_best(current, goal=objective_direction),
            "delta": np.diff(current),
        }
    return series


def _style_axis(axis: plt.Axes, palette) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(palette.ink)
    axis.spines["bottom"].set_color(palette.ink)
    axis.spines["left"].set_linewidth(float(CONFIG["axes_line_width"]))
    axis.spines["bottom"].set_linewidth(float(CONFIG["axes_line_width"]))
    axis.tick_params(axis="both", which="major", length=3, width=0.6, pad=2)
    axis.grid(False)


def _add_endpoint_labels(
    axis: plt.Axes,
    series: dict[str, dict[str, np.ndarray]],
    algorithms: list[str],
    colors: dict[str, str],
) -> None:
    """Place direct method labels at the terminal points."""

    offsets = {"Proposed": 0.0, "Adaptive": 0.015, "Baseline": -0.015}
    for algorithm in algorithms:
        values = series[algorithm]
        label_line_end(
            axis,
            float(values["iteration"][-1]),
            float(values["current"][-1] + offsets.get(algorithm, 0.0)),
            algorithm,
            color=colors[algorithm],
            fontsize=float(CONFIG["base_font_size"]),
            fontweight="semibold",
            clip_on=False,
        )


def build_figure(
    frame: pd.DataFrame,
    config: dict[str, object],
    objective_direction: str = "minimize",
    data_status: str = "illustrative practice data",
) -> plt.Figure:
    """Build a concise hero trajectory and subordinate update panel."""

    validate_numeric_frame(frame, ["iteration", "objective"])
    if objective_direction not in {"minimize", "maximize"}:
        raise ValueError("objective_direction must be 'minimize' or 'maximize'")
    algorithms = _ordered_algorithms(frame)
    if not algorithms:
        raise ValueError("no algorithms are available for plotting")
    series = _series_by_algorithm(frame, algorithms, objective_direction)
    palette = get_palette(str(config["palette_name"]))
    colors = {str(k): str(v) for k, v in dict(config["algorithm_colors"]).items()}
    markers = {str(k): str(v) for k, v in dict(config["algorithm_markers"]).items()}

    with figure_style(str(config["style_name"]), canvas="composite"):
        with plt.rc_context(
            {
                "font.size": float(config["base_font_size"]),
                "axes.labelsize": float(config["base_font_size"]),
                "xtick.labelsize": float(config["base_font_size"]) - 1.0,
                "ytick.labelsize": float(config["base_font_size"]) - 1.0,
                "legend.fontsize": float(config["legend_font_size"]),
            }
        ):
            figure = plt.figure(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                facecolor=palette.background,
            )
            grid = figure.add_gridspec(
                nrows=2,
                ncols=1,
                height_ratios=(
                    float(config["hero_height_ratio"]),
                    float(config["delta_height_ratio"]),
                ),
                left=float(config["grid_left"]),
                right=float(config["grid_right"]),
                top=float(config["grid_top"]),
                bottom=float(config["grid_bottom"]),
                hspace=float(config["grid_hspace"]),
            )
            hero = figure.add_subplot(grid[0])
            # Keep identical x limits for alignment, but do not share tick
            # locators: panel a starts at iteration 1, whereas panel b starts
            # at destination iteration 2.
            delta_axis = figure.add_subplot(grid[1])
            _style_axis(hero, palette)
            _style_axis(delta_axis, palette)

            add_panel_label(
                hero,
                "a",
                xy=(-0.06, 1.04),
                fontsize=float(config["panel_label_size"]),
                color=palette.ink,
            )
            add_panel_label(
                delta_axis,
                "b",
                xy=(-0.06, 1.12),
                fontsize=float(config["panel_label_size"]),
                color=palette.ink,
            )
            hero.set_title(
                str(config["panel_a_title"]),
                loc="left",
                pad=6,
                fontsize=float(config["panel_title_size"]),
                fontweight="semibold",
            )
            delta_axis.set_title(
                str(config["panel_b_title"]),
                loc="left",
                pad=6,
                fontsize=float(config["panel_title_size"]),
                fontweight="semibold",
            )

            # Hero: raw current objective is the primary evidence.
            for algorithm in algorithms:
                values = series[algorithm]
                hero.plot(
                    values["iteration"],
                    values["current"],
                    color=colors[algorithm],
                    marker=markers[algorithm],
                    markersize=float(config["marker_size"]),
                    linewidth=float(config["line_width"]),
                    markeredgewidth=0.55,
                    markeredgecolor=palette.background,
                    label=algorithm,
                    zorder=3,
                )

            hero.set_xlim(0.72, 11.05)
            hero.set_ylim(*tuple(float(v) for v in config["objective_ylim"]))
            hero.set_ylabel("Objective value\n(lower is better)", labelpad=6)
            hero.set_xlabel("Iteration", labelpad=3)
            hero.set_xticks(np.arange(1, 11, dtype=float))
            hero.set_yticks([1.0, 1.5, 2.0, 2.5])
            hero.axhline(1.0, color=palette.grid, linewidth=0.55, zorder=0)
            hero.axhline(1.5, color=palette.grid, linewidth=0.55, zorder=0)
            hero.axhline(2.0, color=palette.grid, linewidth=0.55, zorder=0)
            _add_endpoint_labels(hero, series, algorithms, colors)

            # The reference figure uses local callouts sparingly. Here a quiet
            # open marker preserves the one current-versus-incumbent distinction
            # without promoting it to the main claim.
            proposed = series.get("Proposed")
            if proposed is not None:
                mismatch = np.flatnonzero(
                    ~np.isclose(proposed["current"], proposed["best"], rtol=0.0, atol=1e-12)
                )
                if len(mismatch) == 1:
                    index = int(mismatch[0])
                    x_value = float(proposed["iteration"][index])
                    best_value = float(proposed["best"][index])
                    hero.plot(
                        [x_value, x_value],
                        [best_value, float(proposed["current"][index])],
                        color=palette.muted,
                        linewidth=0.85,
                        zorder=4,
                    )
                    hero.scatter(
                        [x_value],
                        [best_value],
                        s=24,
                        facecolors=palette.background,
                        edgecolors=palette.muted,
                        linewidths=0.9,
                        zorder=5,
                    )
                    hero.text(
                        x_value + 0.15,
                        best_value - 0.065,
                        "running best",
                        fontsize=float(config["footnote_font_size"]),
                        color=palette.muted,
                        ha="left",
                        va="top",
                    )

            # Support: signed adjacent-step changes on the same horizontal scale.
            delta_handles: list[mlines.Line2D] = []
            for algorithm in algorithms:
                values = series[algorithm]
                handle, = delta_axis.plot(
                    values["iteration"][1:],
                    values["delta"],
                    color=colors[algorithm],
                    marker=markers[algorithm],
                    markersize=float(config["delta_marker_size"]),
                    linewidth=float(config["delta_line_width"]),
                    markeredgewidth=0.45,
                    markeredgecolor=palette.background,
                    zorder=3,
                )
                delta_handles.append(handle)

            delta_axis.axhline(0.0, color=palette.ink, linewidth=0.75, zorder=1)
            delta_axis.set_xlim(0.72, 11.05)
            delta_axis.set_ylim(*tuple(float(v) for v in config["delta_ylim"]))
            delta_axis.set_yticks([-0.4, -0.2, 0.0])
            delta_axis.set_ylabel("Δ objective", labelpad=6)
            delta_axis.set_xlabel(
                "Destination iteration  ·  " + str(config["delta_note"]),
                labelpad=5,
            )
            delta_axis.set_xticks(np.arange(2, 11, dtype=float))
            delta_axis.set_xticklabels([str(int(value)) for value in np.arange(2, 11)])
            delta_axis.grid(axis="y", color=palette.grid, linewidth=0.5)
            delta_axis.legend(
                handles=delta_handles,
                labels=algorithms,
                loc="upper right",
                bbox_to_anchor=(1.0, 1.30),
                ncol=len(algorithms),
                frameon=False,
                handlelength=1.7,
                columnspacing=1.2,
                borderaxespad=0.0,
            )

            if proposed is not None:
                positive = np.flatnonzero(proposed["delta"] > 0)
                for index in positive:
                    x_value = float(proposed["iteration"][index + 1])
                    delta_value = float(proposed["delta"][index])
                    delta_axis.annotate(
                        f"+{delta_value:.2f}",
                        xy=(x_value, delta_value),
                        xytext=(x_value + 0.25, delta_value + 0.012),
                        fontsize=float(config["footnote_font_size"]),
                        color=palette.accent,
                        ha="left",
                        va="bottom",
                        arrowprops={
                            "arrowstyle": "-",
                            "color": palette.accent,
                            "linewidth": 0.7,
                        },
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
    """Write a portable Nature context record without a machine-specific path."""

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
    """Load the fixed Nature context, render, and export all requested artifacts."""

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
                            "support_panels": ["b"],
                            "current_vs_historical_best": "quiet local divergence marker only",
                            "long_figure_level_title": False,
                            "delta_heatmap": False,
                            "uncertainty_band": False,
                            "external_reference_data_reused": False,
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
