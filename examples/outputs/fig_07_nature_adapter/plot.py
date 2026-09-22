"""Generate a Python chart after reading the fixed upstream Nature context."""

import argparse
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

from figure_studio.analysis import running_best  # noqa: E402
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
    """Read the practice convergence table without changing its values."""

    data_path = Path(path)
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    frame = pd.read_csv(data_path)
    required = ["algorithm", "iteration", "objective"]
    missing = set(required).difference(frame.columns)
    if missing:
        raise ValueError(f"Nature adapter data missing columns: {sorted(missing)}")
    validate_numeric_frame(frame, ["iteration", "objective"])
    if frame["algorithm"].isna().any():
        raise ValueError("algorithm must not contain missing values")
    return frame.sort_values(["algorithm", "iteration"]).reset_index(drop=True)


def build_figure(
    frame: pd.DataFrame,
    config: dict[str, object],
    objective_direction: str = "minimize",
) -> plt.Figure:
    """Build a compact chart using the project renderer after Nature context loading."""

    validate_numeric_frame(frame, ["iteration", "objective"])
    palette = get_palette(str(config["palette_name"]))
    colors = dict(config["algorithm_colors"])
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
            figure, axis = plt.subplots(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                layout="constrained",
            )
            for index, (algorithm, group) in enumerate(frame.groupby("algorithm", sort=False)):
                group = group.sort_values("iteration")
                color = colors.get(
                    algorithm,
                    palette.category_cycle[index % len(palette.category_cycle)],
                )
                current = group["objective"].to_numpy()
                best = running_best(current, goal=objective_direction)
                axis.plot(
                    group["iteration"],
                    current,
                    color=color,
                    linewidth=float(config["auxiliary_line_width"]),
                    linestyle=":",
                    alpha=0.40,
                    marker="o",
                    markersize=max(2.5, float(config["marker_size"]) - 1.0),
                    label="_nolegend_",
                )
                axis.plot(
                    group["iteration"],
                    best,
                    color=color,
                    linewidth=float(config["line_width"]),
                    marker="o",
                    markersize=float(config["marker_size"]),
                    label=algorithm,
                )
            axis.set_xlabel("Iteration")
            axis.set_ylabel("Objective value (practice unit)")
            axis.set_title("Nature-guided convergence evidence", loc="left", pad=10)
            axis.grid(axis="y", color=palette.grid, linewidth=0.55, alpha=0.8)
            axis.legend(loc=str(config["legend_location"]))
            data_label = provenance_data_label(str(config.get("data_status", "")))
            if data_label:
                figure.text(
                    0.01,
                    0.005,
                    data_label,
                    color=palette.muted,
                    fontsize=max(6.5, float(config["font_size"]) - 1.5),
                )
            return figure


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    skill_root: str | Path | None = None,
):
    """Load verified Nature references, render, and return artifact paths."""

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
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    source = manifest.data_path
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    figure = build_figure(
        load_data(source),
        runtime_config,
        objective_direction=manifest.objective_direction or "minimize",
    )
    context_path = destination / "nature_context.json"
    context_path.write_text(
        json.dumps(nature_context, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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
                        "nature_context_file": context_path.name,
                        "nature_commit": nature_context["commit"],
                        "nature_references_loaded": nature_context["references_loaded"],
                        "project_backend": nature_context["project_backend"],
                        "upstream_r_track_preserved": nature_context[
                            "upstream_r_track_preserved"
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
    parser.add_argument("--skill-root", type=Path, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
        skill_root=arguments.skill_root,
    )
