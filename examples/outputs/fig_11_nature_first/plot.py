"""Render the Nature-first practice Figure after its Figure Contract is complete."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_configured_root = os.environ.get("SCIENTIFIC_FIGURE_STUDIO_ROOT")
PROJECT_ROOT = (
    Path(_configured_root).expanduser().resolve()
    if _configured_root
    else next(
        parent
        for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]
        if (parent / "figure_studio").is_dir()
    )
)
sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.analysis import running_best  # noqa: E402
from figure_studio.export import export_figure  # noqa: E402
from figure_studio.manifest import (  # noqa: E402
    build_data_provenance,
    load_manifest,
)
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402
from figure_studio.validation import validate_numeric_frame  # noqa: E402

from config import CONFIG  # noqa: E402


def load_data(path: str | Path) -> pd.DataFrame:
    """Load the supplied practice table without changing its observations."""

    data_path = Path(path).expanduser()
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = {"algorithm", "iteration", "objective"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"practice data missing columns: {sorted(missing)}")
    validate_numeric_frame(frame, ["iteration", "objective"])
    if frame["algorithm"].isna().any():
        raise ValueError("algorithm must not contain missing values")
    return frame.sort_values(["algorithm", "iteration"]).reset_index(drop=True)


def _summary(frame: pd.DataFrame, objective_direction: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for algorithm, group in frame.groupby("algorithm", sort=False):
        ordered = group.sort_values("iteration")
        values = ordered["objective"].to_numpy(dtype=float)
        best = running_best(values, goal=objective_direction)
        initial = float(values[0])
        final_best = float(best[-1])
        rows.append(
            {
                "algorithm": algorithm,
                "initial": initial,
                "final_best": final_best,
                "relative_decrease": 100.0 * (initial - final_best) / initial,
            }
        )
    return pd.DataFrame(rows)


def build_figure(
    frame: pd.DataFrame,
    config: dict[str, object],
    objective_direction: str = "minimize",
) -> plt.Figure:
    """Build the two-panel Figure Contract: hero trajectories plus derived evidence."""

    validate_numeric_frame(frame, ["iteration", "objective"])
    palette = get_palette(str(config["palette_name"]))
    method_colors = dict(config["algorithm_colors"])
    summary = _summary(frame, objective_direction)
    with figure_style(str(config["style_name"]), canvas="wide"):
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
                facecolor=palette.background,
            )
            grid = figure.add_gridspec(
                1,
                2,
                width_ratios=(1.65, 1.0),
                left=0.09,
                right=0.98,
                bottom=0.20,
                top=0.77,
                wspace=0.34,
            )
            axis_a = figure.add_subplot(grid[0, 0])
            axis_b = figure.add_subplot(grid[0, 1])

            for index, (algorithm, group) in enumerate(frame.groupby("algorithm", sort=False)):
                ordered = group.sort_values("iteration")
                color = method_colors.get(
                    str(algorithm),
                    palette.category_cycle[index % len(palette.category_cycle)],
                )
                observed = ordered["objective"].to_numpy(dtype=float)
                best = running_best(observed, goal=objective_direction)
                axis_a.plot(
                    ordered["iteration"],
                    observed,
                    color=color,
                    linewidth=float(config["raw_line_width"]),
                    linestyle=(0, (1.2, 2.2)),
                    alpha=0.52,
                    marker="o",
                    markersize=max(2.2, float(config["marker_size"]) - 1.0),
                    label="_nolegend_",
                )
                axis_a.plot(
                    ordered["iteration"],
                    best,
                    color=color,
                    linewidth=float(config["hero_line_width"]),
                    marker="o",
                    markersize=float(config["marker_size"]),
                    label=str(algorithm),
                )

            axis_a.set_title("Observed and historical-best trajectories", loc="left", pad=8)
            axis_a.set_xlabel("Iteration")
            axis_a.set_ylabel("Objective value (practice unit)")
            axis_a.grid(
                axis="y",
                color=palette.grid,
                linewidth=0.55,
                alpha=float(config["grid_alpha"]),
            )
            axis_a.legend(
                loc=str(config["legend_location"]),
                handlelength=2.4,
                borderaxespad=0.2,
            )
            y_values = frame["objective"].to_numpy(dtype=float)
            y_margin = max(0.05, (y_values.max() - y_values.min()) * 0.10)
            axis_a.set_xlim(
                float(frame["iteration"].min()) - 0.25,
                float(frame["iteration"].max()) + 0.25,
            )
            axis_a.set_ylim(y_values.min() - y_margin, y_values.max() + y_margin)
            axis_a.text(
                0.02,
                0.03,
                "solid: historical best   dotted: observed",
                transform=axis_a.transAxes,
                color=palette.muted,
                fontsize=max(6.5, float(config["font_size"]) - 1.5),
            )

            y_positions = np.arange(len(summary))
            bar_colors = [
                method_colors.get(
                    str(algorithm),
                    palette.category_cycle[index % len(palette.category_cycle)],
                )
                for index, algorithm in enumerate(summary["algorithm"])
            ]
            axis_b.barh(
                y_positions,
                summary["relative_decrease"],
                color=bar_colors,
                alpha=float(config["summary_bar_alpha"]),
                height=0.54,
            )
            axis_b.set_yticks(y_positions, labels=summary["algorithm"])
            axis_b.invert_yaxis()
            axis_b.set_xlabel("Decrease from first observation (%)")
            axis_b.set_title("Derived endpoint evidence", loc="left", pad=8)
            axis_b.grid(
                axis="x",
                color=palette.grid,
                linewidth=0.55,
                alpha=float(config["grid_alpha"]),
            )
            max_decrease = float(summary["relative_decrease"].max())
            axis_b.set_xlim(0, max(1.0, max_decrease * 1.28))
            for position, value in zip(y_positions, summary["relative_decrease"]):
                axis_b.text(
                    float(value) + max(0.4, max_decrease * 0.025),
                    position,
                    f"{value:.1f}%",
                    va="center",
                    color=palette.ink,
                )

            figure.text(
                0.09,
                0.92,
                "Convergence evidence across illustrative trajectories",
                fontsize=float(config["font_size"]) + 2.0,
                fontweight="bold",
                color=palette.ink,
            )
            figure.text(
                0.09,
                0.86,
                "A compact evidence hierarchy: trajectories first, derived endpoint change second",
                fontsize=float(config["font_size"]) - 0.2,
                color=palette.muted,
            )
            for axis, label in ((axis_a, "a"), (axis_b, "b")):
                axis.text(
                    -0.10,
                    1.08,
                    label,
                    transform=axis.transAxes,
                    fontsize=float(config["font_size"]) + 1.0,
                    fontweight="bold",
                    color=palette.ink,
                )
            if str(config.get("data_status", "")) == "illustrative practice data":
                figure.text(
                    0.09,
                    0.06,
                    "illustrative practice data · no replicate runs or uncertainty estimates",
                    color=palette.muted,
                    fontsize=max(6.5, float(config["font_size"]) - 1.5),
                )
            return figure


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    skill_root: str | Path | None = None,
    overwrite: bool = False,
):
    """Render the independently designed Figure and return its export paths."""

    del skill_root
    manifest_file = Path(manifest_path) if manifest_path else Path(__file__).with_name(
        "data_manifest.json"
    )
    manifest = load_manifest(manifest_file, base_dir=manifest_file.parent)
    if data_path is not None:
        manifest = manifest.with_data_path(data_path, PROJECT_ROOT)
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    figure = build_figure(
        load_data(manifest.data_path),
        runtime_config,
        objective_direction=manifest.objective_direction or "minimize",
    )
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="wide"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=overwrite,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "figure_archetype": "quantitative grid",
                        "panel_map": {
                            "a": "hero observed and historical-best trajectories",
                            "b": "derived endpoint decrease",
                        },
                        "design_method": "Nature Figure Contract completed before renderer selection",
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
