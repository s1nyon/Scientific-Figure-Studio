"""Generate a planar network and candidate path comparison figure."""

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

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


def load_data(path: str | Path) -> dict[str, pd.DataFrame]:
    """Split one spatial practice table into nodes, edges, obstacles, and paths."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = {"record_type", "x", "y"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"spatial data missing columns: {sorted(missing)}")
    nodes = frame[frame["record_type"] == "node"].copy()
    edges = frame[frame["record_type"] == "edge"].copy()
    obstacles = frame[frame["record_type"] == "obstacle"].copy()
    paths = frame[frame["record_type"] == "path"].copy()
    if nodes.empty or paths.empty:
        raise ValueError("spatial data must contain node and path records")
    for subset_name, subset, columns in (
        ("nodes", nodes, ["x", "y"]),
        ("edges", edges, ["x", "y", "x2", "y2"]),
        ("obstacles", obstacles, ["x", "y", "x2", "y2"]),
        ("paths", paths, ["x", "y", "order"]),
    ):
        for column in columns:
            if subset[column].isna().any():
                raise ValueError(f"{subset_name}.{column} contains missing coordinates")
    return {"nodes": nodes, "edges": edges, "obstacles": obstacles, "paths": paths}


def build_figure(data: dict[str, pd.DataFrame], config: dict[str, object]) -> plt.Figure:
    """Draw a spatial network with obstacles and direction-aware path arrows."""

    palette = get_palette(str(config["palette_name"]))
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
            fig, ax = plt.subplots(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                layout="constrained",
            )
            for _, row in data["edges"].iterrows():
                ax.plot(
                    [row["x"], row["x2"]],
                    [row["y"], row["y2"]],
                    color=palette.grid,
                    linewidth=1.0,
                    zorder=1,
                )
            for _, row in data["obstacles"].iterrows():
                ax.add_patch(
                    Rectangle(
                        (row["x"], row["y"]),
                        row["x2"] - row["x"],
                        row["y2"] - row["y"],
                        facecolor=palette.negative,
                        edgecolor=palette.negative,
                        alpha=0.14,
                        linewidth=0.9,
                        label=(
                            "Obstacle"
                            if row.name == data["obstacles"].index[0]
                            else "_nolegend_"
                        ),
                        zorder=0,
                    )
                )
            path_colors = [palette.primary, palette.accent]
            for index, (path_id, route) in enumerate(data["paths"].groupby("path_id", sort=False)):
                route = route.sort_values("order")
                color = path_colors[index % len(path_colors)]
                ax.plot(
                    route["x"],
                    route["y"],
                    color=color,
                    linewidth=float(config["path_line_width"]),
                    marker="o",
                    markersize=4.0,
                    label=f"{path_id}",
                    zorder=3,
                )
                if len(route) > 1:
                    start = route.iloc[0]
                    end = route.iloc[1]
                    ax.annotate(
                        "",
                        xy=(end["x"], end["y"]),
                        xytext=(start["x"], start["y"]),
                        arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.0},
                        zorder=4,
                    )
            nodes = data["nodes"]
            start = nodes[nodes["role"] == "start"]
            end = nodes[nodes["role"] == "end"]
            middle = nodes[~nodes["role"].isin(["start", "end"])]
            ax.scatter(
                middle["x"],
                middle["y"],
                s=float(config["node_size"]),
                color=palette.muted,
                label="Intermediate node",
                zorder=5,
            )
            ax.scatter(
                start["x"],
                start["y"],
                s=float(config["node_size"]) * 1.5,
                color=palette.positive,
                marker="o",
                label="Start",
                zorder=6,
            )
            ax.scatter(
                end["x"],
                end["y"],
                s=float(config["node_size"]) * 1.5,
                color=palette.accent,
                marker="s",
                label="End",
                zorder=6,
            )
            for _, row in nodes.iterrows():
                ax.annotate(
                    row["id"],
                    (row["x"], row["y"]),
                    xytext=(5, 4),
                    textcoords="offset points",
                    fontsize=max(6.5, float(config["font_size"]) - 1.0),
                    color=palette.ink,
                )
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("x coordinate (simulated unit)")
            ax.set_ylabel("y coordinate (simulated unit)")
            ax.set_title("Spatial path alternatives", loc="left", pad=10)
            ax.legend(loc=str(config["legend_location"]), ncols=2)
            data_label = provenance_data_label(str(config.get("data_status", "")))
            if data_label:
                fig.text(
                    0.01,
                    0.005,
                    f"二维模拟平面 · {data_label}",
                    color=palette.muted,
                    fontsize=max(6.5, float(config["font_size"]) - 1.5),
                )
            return fig


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
):
    """Generate spatial artifacts and return their paths."""

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
                        "coordinate_system": manifest.raw.get(
                            "coordinate_system", "unknown"
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
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
    )
