"""Explicit, provenance-aware figure export."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SUPPORTED_FORMATS = ("png", "svg", "pdf")


def _normalise_stem(output_stem: str | Path) -> Path:
    path = Path(output_stem)
    if path.suffix.lower().lstrip(".") in SUPPORTED_FORMATS:
        path = path.with_suffix("")
    return path


def export_figure(
    fig: Any,
    output_stem: str | Path,
    formats: tuple[str, ...] = SUPPORTED_FORMATS,
    dpi: int = 300,
    overwrite: bool = False,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Export a Matplotlib figure and a JSON manifest without implicit overwrite."""

    requested_formats = tuple(format_name.lower().lstrip(".") for format_name in formats)
    unknown = sorted(set(requested_formats).difference(SUPPORTED_FORMATS))
    if unknown:
        raise ValueError(f"Unsupported formats {unknown}; choose from {SUPPORTED_FORMATS}")
    if not requested_formats:
        raise ValueError("formats must contain at least one output format")
    if dpi <= 0:
        raise ValueError("dpi must be positive")

    stem = _normalise_stem(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    output_paths = {
        format_name: stem.with_suffix(f".{format_name}") for format_name in requested_formats
    }
    manifest_path = stem.with_suffix(".manifest.json")
    all_paths = [*output_paths.values(), manifest_path]
    if not overwrite:
        existing = [path for path in all_paths if path.exists()]
        if existing:
            raise FileExistsError(f"Refusing to overwrite existing files: {existing}")

    for format_name, path in output_paths.items():
        fig.savefig(
            path,
            format=format_name,
            dpi=dpi,
            bbox_inches=None,
            facecolor=fig.get_facecolor(),
        )

    manifest = {
        "created_utc": datetime.now(UTC).isoformat(),
        "formats": list(requested_formats),
        "dpi": dpi,
        "figure_size_inches": [float(fig.get_figwidth()), float(fig.get_figheight())],
        "provenance": provenance or {},
        "outputs": {key: str(value.name) for key, value in output_paths.items()},
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_paths
