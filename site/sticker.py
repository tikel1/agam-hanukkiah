"""Black-and-white QR sticker for the Niimbot D101 (203 dpi thermal head, 25 mm wide roll).

Usage: python site/sticker.py   (writes site/sticker_25x30.png and site/sticker_25x40.png, 1-bit, 203 dpi)
Every QR module is a whole number of print dots, so the thermal head prints clean edges.
"""

from __future__ import annotations

from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
URL = "https://tikel1.github.io/agam-hanukkiah/"
FONT = HERE.parent / "model" / "fonts" / "SecularOne-Regular.ttf"
DPI = 203
DOTS_PER_MM = DPI / 25.4
WIDTH_MM = 25
DOT = 5  # print dots per QR module (0.63 mm)
QUIET = 2  # modules of white around the code (the label edge adds more)
LINES = ("סרקו לצפייה בסרטון", "חנוכיית אש ומים")
LABELS = {"sticker_25x30.png": (30, 1), "sticker_25x40.png": (40, 2)}  # file: (length mm, text lines)


def qr_image() -> Image.Image:
    code = segno.make(URL, error="m", boost_error=False)
    rows = [[bool(cell) for cell in row] for row in code.matrix]
    size = (len(rows) + 2 * QUIET) * DOT
    image = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(rows):
        for x, on in enumerate(row):
            if on:
                left, top = (x + QUIET) * DOT, (y + QUIET) * DOT
                draw.rectangle((left, top, left + DOT - 1, top + DOT - 1), fill=0)
    return image


def label(length_mm: int, line_count: int) -> Image.Image:
    width, height = round(WIDTH_MM * DOTS_PER_MM), round(length_mm * DOTS_PER_MM)
    image = Image.new("1", (width, height), 1)
    code = qr_image()
    text_height = 24 * line_count
    top = max(0, (height - code.height - text_height) // 2)
    image.paste(code, ((width - code.width) // 2, top))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(FONT), 18)
    for index, line in enumerate(LINES[:line_count]):
        # Pillow without libraqm lays text out left to right, so Hebrew goes in reversed
        draw.text((width / 2, top + code.height + 10 + index * 24), line[::-1], font=font, fill=0, anchor="mm")
    return image


def main() -> None:
    for name, (length_mm, line_count) in LABELS.items():
        image = label(length_mm, line_count)
        image.save(HERE / name, dpi=(DPI, DPI))
        print(f"{name}: {image.width}x{image.height} dots")


if __name__ == "__main__":
    main()
