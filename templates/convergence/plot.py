"""Generate a direction-aware algorithm convergence figure."""

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

from figure_studio.analysis import running_best  # noqa: E402
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
    """Read and validate the convergence table without changing the source file."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    validate_numeric_frame(frame, ["iteration", "objective"])
    if frame["algorithm"].isna().any():
        raise ValueError("algorithm must not contain missing values")
    return frame.sort_values(["algorithm", "iteration"]).reset_index(drop=True)


def build_running_best(values, objective_direction: str = "minimize"):
    """Return the cumulative objective best for the requested direction."""

    return running_best(values, goal=objective_direction)


def build_figure(frame: pd.DataFrame, config: dict[str, object]) -> plt.Figure:
    """Build current-objective and historical-best curves."""

    validate_numeric_frame(frame, ["iteration", "objective"])
    palette = get_palette(str(config["palette_name"]))
    objective_direction = str(config.get("objective_direction", "minimize"))
    with figure_style(str(config["style_name"]), canvas="standard"):
        with plt.rc_context(
            {
                "font.size": float(config["font_size"]),
                "axes.labelsize": float(config["font_size"]),
                "xtick.labelsize": float(config["font_size"]) - 1.0,
                "ytick.labelsize": float(config["font_size"]) - 1.0,
                "legend.fontsize": float(config["font_size"]) - 1.0,
            }
        ):
            fig, ax = plt.subplots(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                layout="constrained",
            )
            colors = dict(config["algorithm_colors"])
            for index, (algorithm, group) in enumerate(frame.groupby("algorithm", sort=False)):
                group = group.sort_values("iteration")
                color = colors.get(
                    algorithm, palette.category_cycle[index % len(palette.category_cycle)]
                )
                best = build_running_best(
                    group["objective"].to_numpy(), objective_direction
                )
                if bool(config["show_current_objective"]):
                    ax.plot(
                        group["iteration"],
                        group["objective"],
                        color=color,
                        linewidth=float(config["auxiliary_line_width"]),
                        alpha=0.36,
                        linestyle=":",
                        marker="o",
                        markersize=float(config["marker_size"]) - 1.0,
                        label="_nolegend_",
                    )
                ax.plot(
                    group["iteration"],
                    best,
                    color=color,
                    linewidth=float(config["line_width"]),
                    marker="o",
                    markersize=float(config["marker_size"]),
                    label=algorithm,
                )

            ax.set_xlabel("Iteration")
            ax.set_ylabel("Objective value (a.u.)")
            ax.set_title("Objective convergence", loc="left", pad=10)
            ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.8)
            if config["x_limits"] is not None:
                ax.set_xlim(config["x_limits"])
            if config["y_limits"] is not None:
                ax.set_ylim(config["y_limits"])
            ax.legend(loc=str(config["legend_location"]), ncols=1)
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
):
    """Generate the convergence delivery and return exported artifact paths."""

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
    runtime_config = {
        **CONFIG,
        "data_status": manifest.data_status,
        "objective_direction": manifest.objective_direction or "minimize",
    }
    figure = build_figure(load_data(source), runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="standard"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=True,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "objective_direction": manifest.objective_direction or "minimize",
                        "historical_best": True,
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
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
    )
