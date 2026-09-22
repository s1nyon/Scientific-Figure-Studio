"""Small runtime copied into the independent reproduction package."""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class Manifest:
    data_status: str
    data_file: str
    data_path: Path
    objective_direction: str | None
    raw: dict[str, Any]

    def with_data_path(self, data_path: str | Path) -> Manifest:
        path = Path(data_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return Manifest(
            self.data_status,
            str(data_path),
            path,
            self.objective_direction,
            self.raw,
        )


@dataclass(frozen=True)
class Palette:
    background: str = "#FFFFFF"
    ink: str = "#1F2D35"
    muted: str = "#66757E"
    grid: str = "#D9E1E5"
    category_cycle: tuple[str, ...] = ("#166A8F", "#2A9D8F", "#7A8793", "#D9822B")


def load_manifest(path: str | Path) -> Manifest:
    manifest_path = Path(path).expanduser().resolve()
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("manifest must contain an object")
    data_file = str(raw.get("data_file", ""))
    data_path = (manifest_path.parent / data_file).resolve()
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    status = str(raw.get("data_status", ""))
    if status not in {"formal input data", "illustrative practice data", "unknown source data"}:
        raise ValueError("unsupported data_status")
    direction = raw.get("objective_direction")
    return Manifest(status, data_file, data_path, str(direction) if direction else None, raw)


def validate_numeric_frame(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    if frame.empty:
        raise ValueError("data frame is empty")
    for column in columns:
        if column not in frame:
            raise ValueError(f"missing column: {column}")
        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"column is not finite: {column}")


def running_best(values: np.ndarray, direction: str) -> np.ndarray:
    if direction == "minimize":
        return np.minimum.accumulate(values)
    if direction == "maximize":
        return np.maximum.accumulate(values)
    raise ValueError("direction must be minimize or maximize")


def build_data_provenance(manifest: Manifest) -> dict[str, object]:
    digest = hashlib.sha256(manifest.data_path.read_bytes()).hexdigest()
    return {
        "data_status": manifest.data_status,
        "data_file": manifest.data_file,
        "data_sha256": digest,
        "transformations": list(manifest.raw.get("transformations", [])),
    }


@contextmanager
def figure_style(_name: str):
    with plt.rc_context({"font.family": "DejaVu Sans", "axes.spines.top": False}):
        yield


def get_palette(_name: str) -> Palette:
    return Palette()


def export_figure(
    figure: plt.Figure,
    output_stem: str | Path,
    *,
    formats: tuple[str, ...],
    dpi: int,
    overwrite: bool,
    provenance: dict[str, object],
) -> dict[str, Path]:
    stem = Path(output_stem).expanduser().resolve()
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = {format_name: stem.with_suffix(f".{format_name}") for format_name in formats}
    manifest_path = stem.with_suffix(".manifest.json")
    if not overwrite:
        conflicts = [path for path in (*outputs.values(), manifest_path) if path.exists()]
        if conflicts:
            raise FileExistsError(conflicts)
    for format_name, path in outputs.items():
        figure.savefig(path, format=format_name, dpi=dpi, facecolor="white")
    manifest_path.write_text(
        json.dumps({"formats": list(formats), "dpi": dpi, "provenance": provenance}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return outputs
