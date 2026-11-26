"""Hanukkiah logo in the line-and-dot style of the Agam Museum wordmark.

Hebrew letters are drawn as thin navy strokes with coloured dots on their top ends, and dots
separate the words, as in the museum's logo. Writes logo.svg (and returns the SVG text).

Usage: python logo.py
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
NAVY = "#232c5e"
# The museum logo's dot colours, in an order that never repeats a neighbour.
DOT_COLOURS = ("#e4432f", "#f6d21c", "#1fa3a8", "#6a5ea8", "#6bb7e6", "#1b7f3e",
               "#a81f2a", "#4f63b0", "#cfa3d1", "#f39a1e")
CAP = 100.0  # letter height
STROKE = 7.5
DOT_R = 10.5
LETTER_GAP = 26.0
WORD_GAP = 62.0  # holds a separator dot

# Each glyph: width, stroke paths (SVG path data in a 0..width x 0..CAP box), dot points.
GLYPHS: dict[str, tuple[float, list[str], list[tuple[float, float]]]] = {
    "ח": (58, ["M0,100 L12,0 H58 V100"], [(58, 0)]),  # left leg leans, like the מ's strokes
    "נ": (44, ["M8,0 H44 V93 L0,100"], [(8, 0)]),  # base slopes down to the left, like the מ's
    "ו": (0, ["M0,0 V100"], [(0, 0)]),
    "כ": (56, ["M0,0 H38 L56,50 L38,95 L0,100"], [(0, 0)]),  # diagonals like the museum ז, base sloped like the מ
    "י": (0, ["M0,0 V40"], [(0, 0)]),
    "ת": (64, ["M0,0 H64 V100", "M14,0 V100 H0"], [(0, 0)]),
    "א": (70, ["M0,0 L70,100", "M64,0 L44,62", "M28,40 L4,100"], [(0, 0), (64, 0)]),
    "ש": (70, ["M0,0 L12,100 H70 V0", "M36,0 L40,100"], [(0, 0), (36, 0), (70, 0)]),
    "מ": (90, ["M0,0 L32,48", "M14,82 L56,0 L90,94 L40,99"], [(0, 0), (56, 0)]),
    "ם": (60, ["M0,0 H60 V100 H0 Z"], [(0, 0), (60, 0)]),
}


def layout(words: list[str]) -> tuple[list[tuple[str, float]], list[float], float]:
    """Places letters right to left. Returns (letter, left x) pairs, separator x's and total width."""
    placed, separators, x = [], [], 0.0
    for index, word in enumerate(words):
        if index:
            separators.append(x + WORD_GAP / 2)
            x += WORD_GAP
        for position, letter in enumerate(word):
            if position:
                x += LETTER_GAP
            width = GLYPHS[letter][0]
            placed.append((letter, x, width))
            x += width
    total = x
    mirrored = [(letter, total - left - width) for letter, left, width in placed]
    return mirrored, [total - s for s in separators], total


def wordmark(words: list[str], origin_x: float, origin_y: float) -> tuple[list[str], float]:
    placed, separators, total = layout(words)
    strokes, dots, colour = [], [], iter(DOT_COLOURS * 10)
    for letter, left in placed:
        _, paths, points = GLYPHS[letter]
        tx = origin_x + left
        strokes += [f'<path d="{d}" transform="translate({tx:.1f},{origin_y:.1f})"/>' for d in paths]
        dots += [f'<circle cx="{tx + px:.1f}" cy="{origin_y + py:.1f}" r="{DOT_R}" fill="{next(colour)}"/>'
                 for px, py in points]
    for sx in separators:
        dots.append(f'<circle cx="{origin_x + sx:.1f}" cy="{origin_y + CAP / 2:.1f}" r="{DOT_R}" fill="{next(colour)}"/>')
    for end_x in (origin_x - WORD_GAP / 2, origin_x + total + WORD_GAP / 2):
        dots.append(f'<circle cx="{end_x:.1f}" cy="{origin_y + CAP / 2:.1f}" r="{DOT_R}" fill="{next(colour)}"/>')
    group = (f'<g fill="none" stroke="{NAVY}" stroke-width="{STROKE}" stroke-linejoin="miter" '
             f'stroke-linecap="butt">{"".join(strokes)}</g>{"".join(dots)}')
    return [group], total


def build_svg() -> str:
    pad, top = 50.0, 30.0
    parts, total = wordmark(["חנוכיית", "אש", "ומים"], pad + WORD_GAP / 2, top)
    width = total + 2 * pad + WORD_GAP
    subtitle_y = top + CAP + 78
    subtitle = (f'<text x="{width / 2:.1f}" y="{subtitle_y:.1f}" text-anchor="middle" direction="rtl" '
                f'font-family="Assistant, \'Segoe UI\', Arial, sans-serif" font-size="46" font-weight="600" '
                f'letter-spacing="2" fill="{NAVY}">מחווה לאמן יעקב אגם</text>')
    rule_y = top + CAP + 30
    rule = "".join(
        f'<circle cx="{pad + i * (width - 2 * pad) / 24:.1f}" cy="{rule_y:.1f}" r="4" fill="{DOT_COLOURS[i % len(DOT_COLOURS)]}"/>'
        for i in range(25))
    height = subtitle_y + 30
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
            f'width="{width:.0f}" height="{height:.0f}">{"".join(parts)}{rule}{subtitle}</svg>')


def main() -> None:
    out = HERE / "logo.svg"
    out.write_text(build_svg(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
