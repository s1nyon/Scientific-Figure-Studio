"""Create exact-width paper previews from a rendered PNG for visual QA."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

MM_PER_INCH = 25.4
PREVIEW_DPI = 300


def make_preview(source: Path, destination: Path, width_mm: float) -> dict[str, object]:
    """Downsample a rendered figure to the requested paper width without cropping."""

    with Image.open(source) as image:
        width_px = round(width_mm / MM_PER_INCH * PREVIEW_DPI)
        height_px = round(image.height * width_px / image.width)
        preview = image.convert("RGB").resize((width_px, height_px), Image.Resampling.LANCZOS)
        preview.save(destination, dpi=(PREVIEW_DPI, PREVIEW_DPI))
    return {
        "source": source.name,
        "output": destination.name,
        "width_mm": width_mm,
        "dpi": PREVIEW_DPI,
        "width_px": width_px,
        "height_px": height_px,
        "cropped": False,
        "method": "Pillow LANCZOS downsample of the final rendered PNG",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()
    source = arguments.source.resolve()
    output_dir = arguments.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [
        make_preview(
            source,
            output_dir / f"{arguments.prefix}_single_column_89mm.png",
            89.0,
        ),
        make_preview(
            source,
            output_dir / f"{arguments.prefix}_double_column_180mm.png",
            180.0,
        ),
    ]
    manifest = {
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "previews": records,
        "input_preserved": True,
    }
    (output_dir / f"{arguments.prefix}_preview_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
