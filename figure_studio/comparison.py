"""Reproducible snapshots and native-aspect before/after comparisons."""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .artifacts import commit_staged_directory, directory_status, sha256


def _sha256(path: Path) -> str:
    return sha256(path)


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

    raw_destination = Path(snapshot_dir).expanduser()
    if raw_destination.is_symlink():
        raise ValueError(f"snapshot directory must not be a symlink: {raw_destination}")
    destination = raw_destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        raw_source = Path(raw_path).expanduser()
        if raw_source.is_symlink():
            raise FileNotFoundError(f"snapshot source does not exist: {raw_source}")
        source = raw_source.resolve()
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


def restore_snapshot(
    snapshot_dir: str | Path,
    destination_dir: str | Path | None = None,
    *,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Restore verified files into a new directory or an explicitly writable workspace."""

    raw_source_dir = Path(snapshot_dir).expanduser()
    if raw_source_dir.is_symlink():
        raise ValueError(f"snapshot directory must not be a symlink: {raw_source_dir}")
    source_dir = raw_source_dir.resolve()
    manifest_path = source_dir / "snapshot_manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise FileNotFoundError(f"snapshot manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), dict):
        raise ValueError("snapshot manifest requires a files object")

    verified: list[tuple[str, Path, dict[str, object]]] = []
    for raw_name, raw_record in manifest["files"].items():
        raw_path = Path(raw_name) if isinstance(raw_name, str) else Path(".")
        if (
            not isinstance(raw_name, str)
            or raw_path.is_absolute()
            or ".." in raw_path.parts
        ):
            raise ValueError(f"unsafe snapshot file name: {raw_name}")
        if not isinstance(raw_record, dict):
            raise ValueError(f"snapshot record must be an object: {raw_name}")
        raw_source = source_dir / raw_name
        if raw_source.is_symlink():
            raise ValueError(f"snapshot file is a symlink: {raw_name}")
        source = raw_source.resolve()
        if not source.is_relative_to(source_dir) or not source.is_file():
            raise ValueError(f"snapshot file escapes snapshot directory: {raw_name}")
        expected_hash = raw_record.get("sha256")
        if not isinstance(expected_hash, str) or _sha256(source) != expected_hash:
            raise ValueError(f"snapshot hash mismatch: {raw_name}")
        expected_bytes = raw_record.get("bytes")
        if expected_bytes is not None and source.stat().st_size != expected_bytes:
            raise ValueError(f"snapshot byte count mismatch: {raw_name}")
        verified.append((raw_name, source, raw_record))

    if destination_dir is None:
        destination = source_dir.parent / (
            f"{source_dir.name}_recovery_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        )
        suffix = 0
        while destination.exists():
            suffix += 1
            destination = source_dir.parent / (
                f"{source_dir.name}_recovery_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}_{suffix}"
            )
    else:
        raw_destination = Path(destination_dir).expanduser()
        if raw_destination.is_symlink():
            raise ValueError(f"restore destination must not be a symlink: {raw_destination}")
        destination = raw_destination.resolve()
    if directory_status(destination) in {"accepted", "candidate"}:
        raise PermissionError(f"refusing to restore into immutable version: {destination}")
    if destination.exists() and destination.is_symlink():
        raise ValueError(f"restore destination must not be a symlink: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    staging_parent = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.restore-", dir=destination.parent)
    )
    staging = staging_parent / "restored"
    try:
        staging.mkdir()
        for name, source, _record in verified:
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        commit_staged_directory(staging, destination, overwrite=overwrite)
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)
    return {name: destination / name for name, _source, _record in verified}


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
