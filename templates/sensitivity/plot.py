"""Generate a parameter-response curve and a signed sensitivity heatmap."""

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

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
    """Read curve and heatmap rows while validating each row type separately."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    if set(frame["record_type"].dropna()) != {"curve", "heatmap"}:
        raise ValueError("record_type must contain curve and heatmap rows")
    curve = frame[frame["record_type"] == "curve"]
    heatmap = frame[frame["record_type"] == "heatmap"]
    validate_numeric_frame(curve, ["parameter_value", "response"])
    validate_numeric_frame(heatmap, ["alpha", "beta", "response"])
    return frame


def build_figure(frame: pd.DataFrame, config: dict[str, object]) -> plt.Figure:
    """Build a one-parameter response curve and observed two-parameter map."""

    palette = get_palette(str(config["palette_name"]))
    curve = frame[frame["record_type"] == "curve"].sort_values("parameter_value")
    heatmap = frame[frame["record_type"] == "heatmap"]
    pivot = heatmap.pivot(index="alpha", columns="beta", values="response").sort_index()
    values = pivot.to_numpy(dtype=float)
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    center = float(config["color_center"])
    if not vmin < center < vmax:
        raise ValueError("color_center must lie strictly inside the heatmap value range")
    norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)

    with figure_style(str(config["style_name"]), canvas="wide"):
        with plt.rc_context(
            {
                "font.size": float(config["font_size"]),
                "axes.labelsize": float(config["font_size"]),
                "xtick.labelsize": float(config["font_size"]) - 1.0,
                "ytick.labelsize": float(config["font_size"]) - 1.0,
            }
        ):
            fig, (curve_ax, heat_ax) = plt.subplots(
                1,
                2,
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                width_ratios=(1.0, 1.08),
                layout="constrained",
            )
            curve_ax.plot(
                curve["parameter_value"],
                curve["response"],
                color=palette.primary,
                linewidth=float(config["line_width"]),
                marker="o",
                markersize=float(config["marker_size"]),
                label="Observed response",
            )
            curve_ax.set_xlabel("Regularization parameter λ (a.u.)")
            curve_ax.set_ylabel("Response change (a.u.)")
            curve_ax.set_title("One-parameter effect", loc="left", pad=10)
            curve_ax.legend(loc=str(config["legend_location"]))
            curve_ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.8)

            image = heat_ax.imshow(
                values,
                cmap=str(config["heatmap_cmap"]),
                norm=norm,
                origin="lower",
                aspect="auto",
                extent=(
                    float(pivot.columns.min()),
                    float(pivot.columns.max()),
                    float(pivot.index.min()),
                    float(pivot.index.max()),
                ),
                interpolation="nearest",
            )
            heat_ax.set_xlabel("Parameter β (a.u.)")
            heat_ax.set_ylabel("Parameter α (a.u.)")
            heat_ax.set_title("Joint parameter effect", loc="left", pad=10)
            colorbar = fig.colorbar(image, ax=heat_ax, pad=0.02, fraction=0.05)
            colorbar.set_label("Response change (a.u.)")
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
    """Generate sensitivity artifacts and return their paths."""

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
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    figure = build_figure(load_data(source), runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="wide"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=True,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "color_center": float(CONFIG["color_center"]),
                        "plot_transformations": [
                            "Pivoted observed alpha-beta-response rows"
                        ],
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
