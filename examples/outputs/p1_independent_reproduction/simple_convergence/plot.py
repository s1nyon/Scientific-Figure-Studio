"""Independent, editable convergence renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from config import (
    ALGORITHM_COLORS,
    DPI,
    FIGURE_HEIGHT,
    FIGURE_WIDTH,
    FONT_SIZE,
    LINE_WIDTH,
    OUTPUT_FORMATS,
)
from standalone_runtime import (
    build_data_provenance,
    export_figure,
    figure_style,
    get_palette,
    load_manifest,
    running_best,
    validate_numeric_frame,
)

ROOT = Path(__file__).resolve().parent


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    manifest_file = (
        Path(manifest_path).expanduser().resolve()
        if manifest_path
        else ROOT / "data_manifest.json"
    )
    manifest = load_manifest(manifest_file)
    if data_path is not None:
        manifest = manifest.with_data_path(data_path)
    frame = pd.read_csv(manifest.data_path)
    validate_numeric_frame(frame, ("iteration", "objective"))
    destination = Path(output_dir).expanduser().resolve() if output_dir else ROOT
    palette = get_palette("algorithm_research")
    with figure_style("algorithm_research"):
        with plt.rc_context({"font.size": FONT_SIZE}):
            figure, axis = plt.subplots(
                figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), layout="constrained"
            )
            for index, (algorithm, group) in enumerate(frame.groupby("algorithm", sort=False)):
                group = group.sort_values("iteration")
                color = ALGORITHM_COLORS.get(str(algorithm), palette.category_cycle[index])
                best = running_best(group["objective"].to_numpy(dtype=float), "minimize")
                axis.plot(
                    group["iteration"],
                    best,
                    color=color,
                    linewidth=LINE_WIDTH,
                    marker="o",
                    label=str(algorithm),
                )
            axis.set_xlabel("Iteration")
            axis.set_ylabel("Objective value (practice unit)")
            axis.set_title("Independent convergence reproduction", loc="left")
            axis.grid(axis="y", color=palette.grid, linewidth=0.6)
            axis.legend(frameon=False)
            figure.text(
                0.01,
                0.01,
                "illustrative practice data",
                color=palette.muted,
                fontsize=7.5,
            )
            try:
                return export_figure(
                    figure,
                    destination / "figure",
                    formats=OUTPUT_FORMATS,
                    dpi=DPI,
                    overwrite=overwrite,
                    provenance=build_data_provenance(manifest),
                )
            finally:
                plt.close(figure)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--data-path", type=Path)
    parser.add_argument("--manifest-path", type=Path)
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
