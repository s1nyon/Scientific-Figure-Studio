"""Create fixed-width paper-placement previews from the rendered PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def make_preview(source: Path, destination: Path, width_mm: float, dpi: int) -> None:
    """Downsample without changing the source aspect ratio or data."""

    with Image.open(source) as image:
        width_px = round(width_mm / 25.4 * dpi)
        height_px = round(image.height * width_px / image.width)
        preview = image.resize((width_px, height_px), Image.Resampling.LANCZOS)
        preview.save(destination, format="PNG", dpi=(dpi, dpi))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    make_preview(
        args.source,
        args.output_dir / "qa_preview_single_column_89mm.png",
        89.0,
        args.dpi,
    )
    make_preview(
        args.source,
        args.output_dir / "qa_preview_double_column_180mm.png",
        180.0,
        args.dpi,
    )


if __name__ == "__main__":
    main()
