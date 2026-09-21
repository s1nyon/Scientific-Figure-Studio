"""Input and exported-artifact validation helpers."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image, ImageStat
from pypdf import PdfReader


def validate_numeric_frame(
    frame: pd.DataFrame, required_columns: list[str] | tuple[str, ...]
) -> None:
    """Validate required numeric columns and finite values."""

    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"missing columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("data frame is empty")
    for column in required_columns:
        try:
            values = frame[column].to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"column {column!r} must be numeric") from exc
        if not np.isfinite(values).all():
            raise ValueError(f"column {column!r} must contain only finite values")


def _validate_png(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        image.load()
        stat = ImageStat.Stat(image.convert("L"))
        if image.width < 10 or image.height < 10:
            raise ValueError(f"PNG is too small: {path}")
        if stat.extrema[0][0] == stat.extrema[0][1]:
            raise ValueError(f"PNG appears blank: {path}")
        return {
            "width_px": image.width,
            "height_px": image.height,
            "mode": image.mode,
            "nonblank": True,
        }


def _validate_svg(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    has_svg_root = root.tag.rsplit("}", 1)[-1] == "svg"
    if not has_svg_root:
        raise ValueError(f"SVG root element is invalid: {path}")
    return {"has_svg_root": True, "text_nodes": len(root.findall(".//{*}text"))}


def _validate_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    if not reader.pages:
        raise ValueError(f"PDF contains no pages: {path}")
    return {"pages": len(reader.pages), "page_width": float(reader.pages[0].mediabox.width)}


def validate_artifact(path: str | Path, kind: str) -> dict[str, Any]:
    """Validate one exported artifact and return measured metadata."""

    artifact = Path(path)
    if not artifact.exists():
        raise FileNotFoundError(artifact)
    kind = kind.lower().lstrip(".")
    validators = {"png": _validate_png, "svg": _validate_svg, "pdf": _validate_pdf}
    if kind not in validators:
        raise ValueError("kind must be one of: png, svg, pdf")
    return validators[kind](artifact)
