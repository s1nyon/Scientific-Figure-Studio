"""Render an illustrative quantitative chart plus explicit mechanism schematic."""

import argparse
import hashlib
import json
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

from figure_studio.annotations import add_reference_line  # noqa: E402
from figure_studio.export import export_figure  # noqa: E402
from figure_studio.illustrations import (  # noqa: E402
    add_panel_label,
    draw_architecture,
)
from figure_studio.manifest import (  # noqa: E402
    build_data_provenance,
    load_manifest,
    provenance_data_label,
    resolve_data_path,
)
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402
from figure_studio.validation import validate_numeric_frame  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_data(path: str | Path, structure_path: str | Path | None = None) -> dict[str, object]:
    """Read quantitative panels and a separate explicit schematic JSON."""

    data_path = Path(path)
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = {"panel", "x", "y", "series"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"composite illustration data missing columns: {sorted(missing)}")
    validate_numeric_frame(frame, ["x", "y"])
    frame = frame.copy()
    frame["panel"] = frame["panel"].astype(str)
    frame["series"] = frame["series"].astype(str)
    if set(frame["panel"]) != {"hero", "evidence"}:
        raise ValueError("composite illustration data must contain hero and evidence panels")

    structure_file = Path(structure_path) if structure_path else data_path.with_suffix(".json")
    if not structure_file.is_file():
        raise FileNotFoundError(structure_file)
    structure = json.loads(structure_file.read_text(encoding="utf-8"))
    if not isinstance(structure, dict):
        raise ValueError("composite structure JSON must contain an object")
    if not isinstance(structure.get("nodes"), dict) or not isinstance(
        structure.get("edges"), list
    ):
        raise ValueError("composite structure JSON requires nodes and edges")
    return {"chart": frame, "structure": structure, "structure_path": structure_file}


def build_figure(data: dict[str, object], config: dict[str, object]) -> plt.Figure:
    """Build an asymmetric hero/evidence/schematic layout from supplied inputs."""

    frame = data["chart"]
    structure = data["structure"]
    palette = get_palette(str(config["palette_name"]))
    colors = dict(config["hero_colors"])
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
                3,
                2,
                width_ratios=(1.70, 1.0),
                height_ratios=(0.12, 1.0, 1.0),
                wspace=0.28,
                hspace=0.34,
            )
            note_ax = figure.add_subplot(grid[0, :])
            hero_ax = figure.add_subplot(grid[1:, 0])
            schematic_ax = figure.add_subplot(grid[1, 1])
            evidence_ax = figure.add_subplot(grid[2, 1])
            note_ax.axis("off")

            hero = frame[frame["panel"] == "hero"]
            for index, (series, group) in enumerate(hero.groupby("series", sort=False)):
                color = colors.get(
                    series,
                    palette.category_cycle[index % len(palette.category_cycle)],
                )
                group = group.sort_values("x")
                hero_ax.plot(
                    group["x"],
                    group["y"],
                    color=color,
                    linewidth=float(config["line_width"]),
                    marker="o",
                    markersize=float(config["marker_size"]),
                    label=series,
                )
            hero_ax.set_xlabel("Evaluation checkpoint (a.u.)")
            hero_ax.set_ylabel("Illustrative response (a.u.)")
            hero_ax.set_title("Quantitative evidence", loc="center", pad=10)
            hero_ax.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.8)
            hero_ax.legend(loc=str(config["legend_location"]))

            schematic_config = {
                **config,
                "x_limits": config["schematic_x_limits"],
                "y_limits": config["schematic_y_limits"],
            }
            draw_architecture(
                schematic_ax,
                structure["nodes"],
                structure["edges"],
                schematic_config,
            )
            schematic_ax.set_title("Mechanism schematic", loc="center", pad=10)

            evidence = frame[frame["panel"] == "evidence"].sort_values("x")
            evidence_ax.plot(
                evidence["x"],
                evidence["y"],
                color=palette.accent,
                linewidth=float(config["line_width"]) - 0.25,
                marker="o",
                markersize=max(2.8, float(config["marker_size"]) - 0.8),
            )
            add_reference_line(evidence_ax, 0.0, axis="y", color=palette.muted)
            evidence_ax.set_xlabel("Checkpoint (a.u.)")
            evidence_ax.set_ylabel("Residual (a.u.)")
            evidence_ax.set_title("Evidence check", loc="center", pad=10)
            evidence_ax.grid(axis="y", color=palette.grid, linewidth=0.5, alpha=0.75)

            panel_config = {"panel_label_size": float(config["font_size"]) + 0.5}
            add_panel_label(hero_ax, "(a)", panel_config)
            add_panel_label(schematic_ax, "(b)", panel_config)
            add_panel_label(evidence_ax, "(c)", panel_config)
            evidence_note = "Illustrative practice inputs; not experimental evidence."
            data_label = provenance_data_label(str(config.get("data_status", "")))
            note_ax.text(
                0.0,
                0.45,
                " · ".join(item for item in (evidence_note, data_label) if item),
                ha="left",
                va="center",
                color=palette.muted,
                fontsize=max(6.2, float(config["font_size"]) - 1.8),
            )
            return figure


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
):
    """Generate composite illustration artifacts and return their paths."""

    manifest_file = Path(manifest_path) if manifest_path else Path(__file__).with_name(
        "data_manifest.json"
    )
    manifest_base = manifest_file.parent if manifest_path else PROJECT_ROOT
    manifest = load_manifest(manifest_file, base_dir=manifest_base)
    if data_path is not None:
        manifest = manifest.with_data_path(data_path, PROJECT_ROOT)
    structure_file = resolve_data_path(
        str(manifest.raw.get("structure_file", Path(manifest.data_file).with_suffix(".json"))),
        manifest_base,
    )
    source = manifest.data_path
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    data = load_data(source, structure_file)
    figure = build_figure(data, runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="composite"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=True,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "structure_file": str(structure_file),
                        "structure_sha256": _sha256(structure_file),
                        "structure_status": manifest.raw.get(
                            "structure_status", "unknown"
                        ),
                        "panels": [
                            "Quantitative practice chart",
                            "Explicit mechanism schematic",
                            "Residual evidence check",
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
