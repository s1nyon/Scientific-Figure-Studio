"""Create a non-scientific three-round visual comparison without distortion."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        import matplotlib.font_manager as font_manager

        return ImageFont.truetype(font_manager.findfont("DejaVu Sans"), size=size)
    except (ImportError, OSError):
        return ImageFont.load_default()


def _resize_to_height(image: Image.Image, height: int) -> Image.Image:
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round-01", type=Path, required=True)
    parser.add_argument("--round-02", type=Path, required=True)
    parser.add_argument("--round-03", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image-height", type=int, default=520)
    args = parser.parse_args()
    entries = [
        ("Round 01", args.round_01),
        ("Round 02", args.round_02),
        ("Round 03", args.round_03),
    ]
    cards: list[tuple[str, Image.Image, tuple[int, int]]] = []
    for label, path in entries:
        with Image.open(path) as image:
            cards.append(
                (
                    label,
                    _resize_to_height(image.convert("RGB"), args.image_height),
                    image.size,
                )
            )
    margin, header_height, gap = 36, 82, 24
    canvas_width = margin * 2 + sum(card[1].width for card in cards) + gap * (len(cards) - 1)
    canvas = Image.new("RGB", (canvas_width, header_height + args.image_height + margin), "white")
    draw = ImageDraw.Draw(canvas)
    title_font, label_font = _font(28), _font(22)
    x = margin
    for label, image, original_size in cards:
        draw.text((x, 12), label, fill="#1B2A3A", font=title_font)
        draw.text(
            (x, 45),
            f"{original_size[0]} × {original_size[1]} px",
            fill="#657482",
            font=label_font,
        )
        canvas.paste(image, (x, header_height))
        x += image.width + gap
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, format="PNG", dpi=(150, 150))


if __name__ == "__main__":
    main()
