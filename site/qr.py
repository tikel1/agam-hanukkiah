"""QR code for the site, in the logo's colours (navy dots, coloured corner eyes, the fountain's stripes).

Usage: python site/qr.py   (writes site/qr.svg and site/qr.png)
"""

from __future__ import annotations

from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
URL = "https://tikel1.github.io/agam-hanukkiah/"
NAVY = "#232c5e"
PAPER = "#ffffff"
EYES = ("#e4432f", "#1fa3a8", "#6a5ea8")  # top left, top right, bottom left
STRIPES = ("#e4432f", "#f6d21c", "#1fa3a8", "#6a5ea8", "#6bb7e6", "#1b7f3e", "#f39a1e", "#4f63b0", "#cfa3d1", "#a81f2a")
CAPTION = "סרקו לצפייה בסרטון"
FONT = HERE.parent / "model" / "fonts" / "SecularOne-Regular.ttf"

MODULE = 40  # px per module in the PNG
QUIET = 4  # modules of white around the code
DOT = 0.42  # dot radius in modules
STRIPE_ROWS = 1.2  # height of the stripe band in modules
CAPTION_ROWS = 3.2  # room under the code for the caption


def matrix() -> list[list[bool]]:
    code = segno.make(URL, error="h", boost_error=False)
    return [[bool(cell) for cell in row] for row in code.matrix]


def in_eye(x: int, y: int, size: int) -> int | None:
    """Index of the 7x7 finder pattern holding (x, y), or None."""
    for index, (ex, ey) in enumerate(((0, 0), (size - 7, 0), (0, size - 7))):
        if ex <= x < ex + 7 and ey <= y < ey + 7:
            return index
    return None


def eye_shapes(size: int) -> list[tuple[str, float, float, float, float]]:
    """(kind, x, y, w, colour index) rings and centres of the three eyes, in modules."""
    shapes = []
    for index, (ex, ey) in enumerate(((0, 0), (size - 7, 0), (0, size - 7))):
        shapes.append(("ring", ex + 0.5, ey + 0.5, 6.0, index))
        shapes.append(("core", ex + 2.0, ey + 2.0, 3.0, index))
    return shapes


def to_svg(cells: list[list[bool]]) -> str:
    size = len(cells)
    width = size + 2 * QUIET
    height = width + STRIPE_ROWS + CAPTION_ROWS
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height:.2f}" width="{width * 20}" height="{height * 20:.0f}">',
             f'<rect width="{width}" height="{height:.2f}" fill="{PAPER}"/>']
    dots = [f'<circle cx="{x + QUIET + 0.5}" cy="{y + QUIET + 0.5}" r="{DOT}"/>'
            for y, row in enumerate(cells) for x, on in enumerate(row) if on and in_eye(x, y, size) is None]
    parts.append(f'<g fill="{NAVY}">{"".join(dots)}</g>')
    for kind, x, y, w, index in eye_shapes(size):
        colour = EYES[int(index)]
        if kind == "ring":
            parts.append(f'<rect x="{x + QUIET}" y="{y + QUIET}" width="{w}" height="{w}" rx="1.4" fill="none" stroke="{colour}" stroke-width="1"/>')
        else:
            parts.append(f'<rect x="{x + QUIET}" y="{y + QUIET}" width="{w}" height="{w}" rx="0.8" fill="{colour}"/>')
    stripe_w = width / len(STRIPES)
    top = width - 1.0
    parts += [f'<rect x="{i * stripe_w:.3f}" y="{top}" width="{stripe_w - 0.15:.3f}" height="{STRIPE_ROWS}" fill="{c}"/>'
              for i, c in enumerate(STRIPES)]
    parts.append(f'<text x="{width / 2}" y="{top + STRIPE_ROWS + 2.2:.2f}" font-family="Secular One, Assistant, Arial, sans-serif" '
                 f'font-size="1.9" fill="{NAVY}" text-anchor="middle" direction="rtl">{CAPTION}</text>')
    parts.append("</svg>")
    return "".join(parts)


def to_png(cells: list[list[bool]]) -> Image.Image:
    size = len(cells)
    width = (size + 2 * QUIET) * MODULE
    top = width - MODULE
    height = int(top + (STRIPE_ROWS + CAPTION_ROWS) * MODULE)
    image = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(image)
    radius = DOT * MODULE
    for y, row in enumerate(cells):
        for x, on in enumerate(row):
            if on and in_eye(x, y, size) is None:
                cx, cy = (x + QUIET + 0.5) * MODULE, (y + QUIET + 0.5) * MODULE
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=NAVY)
    for kind, x, y, w, index in eye_shapes(size):
        box = ((x + QUIET) * MODULE, (y + QUIET) * MODULE, (x + QUIET + w) * MODULE, (y + QUIET + w) * MODULE)
        if kind == "ring":
            half = MODULE / 2
            box = (box[0] - half, box[1] - half, box[2] + half, box[3] + half)
            draw.rounded_rectangle(box, radius=1.9 * MODULE, outline=EYES[index], width=MODULE)
        else:
            draw.rounded_rectangle(box, radius=0.8 * MODULE, fill=EYES[index])
    stripe_w = width / len(STRIPES)
    for i, colour in enumerate(STRIPES):
        draw.rectangle((i * stripe_w, top, (i + 1) * stripe_w - 0.15 * MODULE, top + STRIPE_ROWS * MODULE), fill=colour)
    font = ImageFont.truetype(str(FONT), int(1.9 * MODULE))
    caption = CAPTION[::-1]  # Pillow without libraqm lays text out left to right
    draw.text((width / 2, top + (STRIPE_ROWS + 1.6) * MODULE), caption, font=font, fill=NAVY, anchor="mm")
    return image


def main() -> None:
    cells = matrix()
    (HERE / "qr.svg").write_text(to_svg(cells), encoding="utf-8")
    to_png(cells).save(HERE / "qr.png", optimize=True)
    print(f"{len(cells)}x{len(cells)} modules -> {HERE / 'qr.svg'}, {HERE / 'qr.png'}")


if __name__ == "__main__":
    main()
