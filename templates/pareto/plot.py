"""Generate a direction-aware feasible-set and Pareto-front figure."""

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

from figure_studio.analysis import pareto_mask  # noqa: E402
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
    """Read feasible solutions and convert the key flag to a boolean."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    validate_numeric_frame(frame, ["cost", "risk"])
    frame = frame.copy()
    frame["is_key_solution"] = frame["is_key_solution"].astype(str).str.lower().eq("true")
    return frame


def build_front(frame: pd.DataFrame, directions: tuple[str, str]) -> pd.DataFrame:
    """Return only non-dominated rows, ordered by the first objective."""

    mask = pareto_mask(frame[["cost", "risk"]].to_numpy(), directions)
    return frame.loc[mask].sort_values("cost").reset_index(drop=True)


def build_figure(frame: pd.DataFrame, config: dict[str, object]) -> plt.Figure:
    """Draw all feasible points and the calculated Pareto front separately."""

    palette = get_palette(str(config["palette_name"]))
    front = build_front(frame, tuple(config["objective_directions"]))
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
            ax.scatter(
                frame["cost"],
                frame["risk"],
                s=float(config["marker_size"]),
                color=palette.muted,
                alpha=0.52,
                label="Feasible solutions",
                zorder=2,
            )
            ax.plot(
                front["cost"],
                front["risk"],
                color=palette.primary,
                linewidth=float(config["front_line_width"]),
                marker="o",
                markersize=5.0,
                label="Computed Pareto front",
                zorder=4,
            )
            key = front[front["is_key_solution"]]
            ax.scatter(
                key["cost"],
                key["risk"],
                s=float(config["marker_size"]) * 1.8,
                facecolor=palette.background,
                edgecolor=palette.accent,
                linewidth=1.4,
                label="Key solutions",
                zorder=5,
            )
            for _, row in key.iterrows():
                ax.annotate(
                    row["solution"],
                    (row["cost"], row["risk"]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    color=palette.ink,
                    fontsize=max(6.5, float(config["font_size"]) - 1.0),
                )
            ax.set_xlabel("Cost (a.u.)")
            ax.set_ylabel("Risk (a.u.)")
            ax.set_title("Feasible set and Pareto front", loc="left", pad=10)
            ax.legend(loc=str(config["legend_location"]), ncols=1)
            ax.grid(color=palette.grid, linewidth=0.55, alpha=0.65)
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
    """Generate Pareto artifacts and return their paths."""

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
        "objective_directions": manifest.objective_directions or CONFIG["objective_directions"],
    }
    figure = build_figure(load_data(source), runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="standard"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=overwrite,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "objective_directions": list(
                            manifest.objective_directions or CONFIG["objective_directions"]
                        ),
                        "front_definition": (
                            "No other feasible point is no worse in every objective "
                            "and strictly better in one."
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
