"""Reproducible snapshots and native-aspect before/after comparisons."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        return {
            "size_px": [width, height],
            "aspect_ratio": round(width / height, 8) if height else None,
            "mode": image.mode,
            "sha256": _sha256(path),
        }


def snapshot_artifacts(
    paths: list[str | Path] | tuple[str | Path, ...],
    snapshot_dir: str | Path,
) -> dict[str, Any]:
    """Copy a pre-edit source/output set into a recoverable snapshot directory."""

    destination = Path(snapshot_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        source = Path(raw_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"snapshot source does not exist: {source}")
        name = source.name
        target = destination / name
        if name in files and target.resolve() != source:
            raise ValueError(f"snapshot contains duplicate file name: {name}")
        if target.exists() and target.resolve() != source:
            raise FileExistsError(f"snapshot target already contains another file: {target}")
        if target.resolve() != source:
            shutil.copy2(source, target)
        files[name] = {
            "sha256": _sha256(source),
            "bytes": source.stat().st_size,
            "kind": source.suffix.lower().lstrip(".") or "file",
        }

    record = {
        "schema_version": "0.1",
        "created_utc": datetime.now(UTC).isoformat(),
        "files": files,
    }
    (destination / "snapshot_manifest.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return record


def restore_snapshot(snapshot_dir: str | Path, destination_dir: str | Path) -> dict[str, Path]:
    """Restore files from a snapshot without deleting unrelated destination files."""

    source_dir = Path(snapshot_dir).expanduser().resolve()
    manifest_path = source_dir / "snapshot_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"snapshot manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    destination = Path(destination_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    restored: dict[str, Path] = {}
    for name in manifest.get("files", {}):
        source = source_dir / name
        if not source.is_file():
            raise FileNotFoundError(f"snapshot file does not exist: {source}")
        target = destination / name
        shutil.copy2(source, target)
        restored[name] = target
    return restored


def build_before_after_comparison(
    before_path: str | Path,
    after_path: str | Path,
    output_path: str | Path,
    *,
    title: str = "Before / After",
    dpi: int = 200,
    overwrite: bool = False,
) -> Path:
    """Render two PNGs side by side while preserving each image's native aspect ratio."""

    before = Path(before_path).expanduser().resolve()
    after = Path(after_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    for path in (before, after):
        if not path.is_file():
            raise FileNotFoundError(f"comparison input does not exist: {path}")
    if output.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite comparison: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    before_info = _image_info(before)
    after_info = _image_info(after)
    with Image.open(before) as before_image, Image.open(after) as after_image:
        before_array = np.asarray(before_image.convert("RGBA"))
        after_array = np.asarray(after_image.convert("RGBA"))

    figure, axes = plt.subplots(1, 2, figsize=(10.0, 5.6), constrained_layout=True)
    for axis, array, label, info in (
        (axes[0], before_array, "Before", before_info),
        (axes[1], after_array, "After", after_info),
    ):
        axis.imshow(array, aspect="equal", interpolation="nearest")
        axis.set_title(f"{label}\n{info['size_px'][0]} × {info['size_px'][1]} px", pad=8)
        axis.set_axis_off()
    figure.suptitle(title, fontsize=12, fontweight="bold")
    try:
        figure.savefig(
            output,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
        )
    finally:
        plt.close(figure)

    manifest = {
        "schema_version": "0.1",
        "created_utc": datetime.now(UTC).isoformat(),
        "before": before_info,
        "after": after_info,
        "preserves_native_aspect": True,
        "output": output.name,
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output
