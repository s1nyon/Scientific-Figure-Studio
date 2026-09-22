"""Create Python QA previews for final-size and before/after inspection."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "rendered_final_v2" / "figure.png"
STAGE1 = ROOT.parent / "stage_01_independent" / "rendered" / "figure.png"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\arial.ttf"):
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _resize_to_mm(image: Image.Image, width_mm: float, dpi: int = 300) -> Image.Image:
    width_px = round(width_mm / 25.4 * dpi)
    height_px = round(image.height * width_px / image.width)
    return image.resize((width_px, height_px), Image.Resampling.LANCZOS)


def _before_after(before: Image.Image, after: Image.Image) -> Image.Image:
    target_width = 1800
    before = before.resize(
        (target_width, round(before.height * target_width / before.width)),
        Image.Resampling.LANCZOS,
    )
    after = after.resize(
        (target_width, round(after.height * target_width / after.width)),
        Image.Resampling.LANCZOS,
    )
    label_height = 80
    canvas = Image.new(
        "RGB",
        (target_width * 2 + 30, max(before.height, after.height) + label_height),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    label_font = _font(34)
    draw.text((20, 18), "Stage 1 · independent text-only", fill="#23384A", font=label_font)
    draw.text(
        (target_width + 40, 18),
        "Stage 3 · source-compared final",
        fill="#23384A",
        font=label_font,
    )
    canvas.paste(before, (0, label_height))
    canvas.paste(after, (target_width + 30, label_height))
    return canvas


def main() -> dict[str, Path]:
    if not FINAL.is_file() or not STAGE1.is_file():
        raise FileNotFoundError("final and stage-1 PNGs are required before QA preview generation")
    with Image.open(FINAL) as final_image, Image.open(STAGE1) as stage1_image:
        final = final_image.convert("RGB")
        stage1 = stage1_image.convert("RGB")
        outputs = {
            "single_column_89mm": ROOT / "qa_single_column_89mm.png",
            "double_column_180mm": ROOT / "qa_double_column_180mm.png",
            "before_after": ROOT / "before_after.png",
        }
        _resize_to_mm(final, 89).save(outputs["single_column_89mm"], format="PNG")
        _resize_to_mm(final, 180).save(outputs["double_column_180mm"], format="PNG")
        _before_after(stage1, final).save(outputs["before_after"], format="PNG")
    return outputs


if __name__ == "__main__":
    for name, path in main().items():
        print(name, path)
