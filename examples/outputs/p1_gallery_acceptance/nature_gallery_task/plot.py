"""Independent, editable two-panel evidence renderer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import (
    ALGORITHM_COLORS,
    DPI,
    FIGURE_HEIGHT,
    FIGURE_WIDTH,
    FONT_SIZE,
    HERO_LINE_WIDTH,
    MARKER_SIZE,
    OUTPUT_FORMATS,
    RAW_LINE_WIDTH,
    SUMMARY_BAR_ALPHA,
)

ROOT = Path(__file__).resolve().parent


def _load_manifest(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("data manifest must contain an object")
    return raw


def _running_best(values: np.ndarray) -> np.ndarray:
    return np.minimum.accumulate(values)


def _data_provenance(manifest: dict[str, object], data_path: Path) -> dict[str, object]:
    return {
        "data_status": manifest["data_status"],
        "data_file": str(manifest["data_file"]),
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "transformations": manifest.get("transformations", []),
    }


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
    manifest = _load_manifest(manifest_file)
    input_path = (
        Path(data_path).expanduser().resolve()
        if data_path
        else (manifest_file.parent / str(manifest["data_file"])).resolve()
    )
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    frame = pd.read_csv(input_path)
    required = {"algorithm", "iteration", "objective"}
    if not required.issubset(frame.columns):
        raise ValueError(f"missing columns: {sorted(required.difference(frame.columns))}")
    if not np.isfinite(frame[["iteration", "objective"]].to_numpy(dtype=float)).all():
        raise ValueError("numeric input must be finite")

    destination = Path(output_dir).expanduser().resolve() if output_dir else ROOT
    destination.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(FIGURE_WIDTH, FIGURE_HEIGHT),
        gridspec_kw={"width_ratios": (1.65, 1.0)},
        layout="constrained",
    )
    summary: list[tuple[str, float]] = []
    for index, (algorithm, group) in enumerate(frame.groupby("algorithm", sort=False)):
        ordered = group.sort_values("iteration")
        values = ordered["objective"].to_numpy(dtype=float)
        best = _running_best(values)
        initial = float(values[0])
        decrease = 100.0 * (initial - float(best[-1])) / initial
        summary.append((str(algorithm), decrease))
        color = ALGORITHM_COLORS.get(
            str(algorithm), ("#166A8F", "#2A9D8F", "#7A8793")[index]
        )
        axes[0].plot(
            ordered["iteration"],
            values,
            color=color,
            linewidth=RAW_LINE_WIDTH,
            linestyle=(0, (1.2, 2.2)),
            alpha=0.52,
            marker="o",
            markersize=max(2.2, MARKER_SIZE - 1.0),
        )
        axes[0].plot(
            ordered["iteration"],
            best,
            color=color,
            linewidth=HERO_LINE_WIDTH,
            marker="o",
            markersize=MARKER_SIZE,
            label=str(algorithm),
        )

    axes[0].set_title("Observed and historical-best trajectories", loc="left")
    axes[0].set_xlabel("Iteration")
    axes[0].set_ylabel("Objective value (practice unit)")
    axes[0].grid(axis="y", color="#D9E1E5", linewidth=0.55)
    axes[0].legend(frameon=False)
    axes[1].barh(
        np.arange(len(summary)),
        [value for _algorithm, value in summary],
        color=[
            ALGORITHM_COLORS.get(algorithm, "#166A8F")
            for algorithm, _value in summary
        ],
        alpha=SUMMARY_BAR_ALPHA,
        height=0.54,
    )
    axes[1].set_yticks(
        np.arange(len(summary)),
        labels=[algorithm for algorithm, _value in summary],
    )
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Decrease from first observation (%)")
    axes[1].set_title("Derived endpoint evidence", loc="left")
    axes[1].grid(axis="x", color="#D9E1E5", linewidth=0.55)
    for position, (_algorithm, value) in enumerate(summary):
        axes[1].text(
            value + 0.3,
            position,
            f"{value:.1f}%",
            va="center",
            fontsize=FONT_SIZE - 1,
        )
    figure.suptitle(
        "Independent Nature-first practice Figure",
        x=0.05,
        ha="left",
        fontsize=FONT_SIZE + 2,
        fontweight="bold",
    )
    figure.text(
        0.05,
        0.01,
        "illustrative practice data · no replicate runs or uncertainty estimates",
        color="#66757E",
        fontsize=7.5,
    )
    for axis, label in zip(axes, ("a", "b"), strict=True):
        axis.text(
            -0.10,
            1.04,
            label,
            transform=axis.transAxes,
            fontsize=FONT_SIZE + 1,
            fontweight="bold",
        )

    outputs = {format_name: destination / f"figure.{format_name}" for format_name in OUTPUT_FORMATS}
    manifest_output = destination / "figure.manifest.json"
    if not overwrite:
        conflicts = [path for path in (*outputs.values(), manifest_output) if path.exists()]
        if conflicts:
            raise FileExistsError(conflicts)
    try:
        for format_name, path in outputs.items():
            figure.savefig(path, format=format_name, dpi=DPI, facecolor="white")
    finally:
        plt.close(figure)
    manifest_output.write_text(
        json.dumps(
            {
                "provenance": _data_provenance(manifest, input_path),
                "formats": list(OUTPUT_FORMATS),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return outputs


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
