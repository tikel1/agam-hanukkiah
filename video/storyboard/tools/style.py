"""Shared style constants and line-and-dot lettering for the storyboard frames.

Reuses the glyphs and colours of submission/logo.py and adds the letters and digits the
video titles need, drawn with the same rules: straight lines only, slight slants, a
coloured dot on the top end of some strokes.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # agam-hanukkiah/
sys.path.insert(0, str(ROOT / "submission"))
import logo  # noqa: E402  (the project's logo module, imported read-only)

W, H = 1920, 1080
FPS = 30

# Palette (fountain palette first, then the logo dot colours)
PAPER = "#F7F5EE"      # background white (warm)
WHITE = "#FFFFFF"
NAVY = logo.NAVY       # "#232c5e", lettering and darkest tone; there is no black
NAVY_D = "#2B2F6B"     # fountain navy, dark shapes
FOUNTAIN = {
    "white": "#F4F1E4", "yellow": "#F2C94C", "orange": "#E8893F", "coral": "#E8655C",
    "brick": "#A8322A", "rose": "#DC8A86", "lilac": "#9A8CC0", "periwinkle": "#7484C4",
    "light_blue": "#A3C1E0", "blue": "#3E5FB0", "navy": "#2B2F6B", "mint": "#A8DDB5",
    "teal": "#3E8F7C", "green": "#4E9E5E", "grey": "#A9B3B6",
}
SPECTRUM = [FOUNTAIN[k] for k in ("yellow", "orange", "coral", "brick", "rose", "lilac",
                                  "periwinkle", "blue", "light_blue", "mint", "teal", "green")]
DOTS = logo.DOT_COLOURS
FLAME_OUT, FLAME_IN = "#F39A1E", "#F6D21C"

# Sizes (px at 1920x1080)
TITLE_CAP = 150        # cap height of a line-and-dot title (stroke ~ 11, dot r ~ 15.8)
SUB_FONT_SIZE = 54     # subtitle font size (Secular One)
SUB_BASELINE_Y = 985   # subtitle baseline; band y 900..1040
SAFE = 96              # action-safe margin on every side
FONT_FILE = "../../../model/fonts/SecularOne-Regular.ttf"  # relative to storyboard/frames/
ASSET = "../../research"  # relative to storyboard/frames/

# New glyphs, same rules as logo.GLYPHS: (width, [stroke paths], [dot points]) in a 0..100 box.
EXTRA = {
    "ע": (62, ["M0,0 L26,70 L62,100", "M62,0 L40,56"], [(0, 0), (62, 0)]),
    "ק": (54, ["M0,0 H54 L50,50 H6", "M28,50 L24,116"], [(0, 0)]),
    "ב": (52, ["M0,0 H52 V94 L-4,100"], [(0, 0)]),
    "ג": (40, ["M0,0 H40 L32,60 L0,100"], [(0, 0)]),
    "פ": (50, ["M0,0 H50 V94 L2,100", "M0,0 L6,40 H28"], [(0, 0)]),
    "ף": (50, ["M0,0 H50 V118", "M0,0 L6,40 H30"], [(0, 0)]),
    "ל": (46, ["M8,-34 V30 L46,40 V100 H0"], [(8, -34)]),
    "ר": (46, ["M0,0 H46 L50,100"], [(0, 0)]),
    "ד": (54, ["M0,0 H54 V100"], [(0, 0), (54, 0)]),
    "ה": (56, ["M0,0 H56 V100", "M4,32 L0,100"], [(0, 0)]),
    "ס": (58, ["M14,0 H52 L58,60 L44,100 H6 L0,40 Z"], [(14, 0)]),
}
logo.GLYPHS.update(EXTRA)

# Digits (left to right): (width, strokes, dots)
DIGITS = {
    "1": (26, ["M0,22 L26,0 V100"], [(26, 0)]),
    "9": (44, ["M0,0 H44 V100 M0,0 V52 H44"], [(0, 0)]),
    "8": (44, ["M0,0 H44 V100 H0 Z M0,50 H44"], [(0, 0)]),
    "6": (44, ["M44,0 H0 V100 H44 V52 H0"], [(44, 0)]),
    "4": (48, ["M0,0 V56 H48", "M34,0 V100"], [(0, 0), (34, 0)]),
    "0": (44, ["M6,0 H44 L38,100 H0 Z"], [(6, 0)]),
}


def _wordmark_svg(words: list[str], scale: float, x: float, y: float) -> tuple[str, float]:
    parts, total = logo.wordmark(words, 0.0, 0.0)
    body = (f'<g transform="translate({x:.1f},{y:.1f}) scale({scale:.4f})">{"".join(parts)}</g>')
    return body, total


def title(words: list[str], cx: float, top: float, cap: float = TITLE_CAP) -> str:
    """Hebrew title in line-and-dot letters, centred on cx, letter tops at y=top."""
    scale = cap / logo.CAP
    _, total = _wordmark_svg(words, scale, 0, 0)
    body, total = _wordmark_svg(words, scale, cx - total * scale / 2, top)
    return body


def title_width(words: list[str], cap: float = TITLE_CAP) -> float:
    _, total = logo.wordmark(words, 0.0, 0.0)
    return total * cap / logo.CAP


def digits(text: str, cx: float, top: float, cap: float = TITLE_CAP) -> str:
    """Line-and-dot digits, left to right, centred on cx."""
    scale = cap / logo.CAP
    gap, total = logo.LETTER_GAP, 0.0
    for i, ch in enumerate(text):
        total += DIGITS[ch][0] + (gap if i else 0)
    x, out, colours = cx - total * scale / 2, [], iter(DOTS * 4)
    for i, ch in enumerate(text):
        wch, paths, pts = DIGITS[ch]
        if i:
            x += gap * scale
        strokes = "".join(f'<path d="{d}" transform="translate({x:.1f},{top:.1f}) scale({scale:.4f})"/>' for d in paths)
        out.append(f'<g fill="none" stroke="{NAVY}" stroke-width="{logo.STROKE * scale:.2f}" '
                   f'stroke-linejoin="miter" stroke-linecap="butt" vector-effect="none">{strokes}</g>')
        out += [f'<circle cx="{x + px * scale:.1f}" cy="{top + py * scale:.1f}" r="{logo.DOT_R * scale:.1f}" fill="{next(colours)}"/>'
                for px, py in pts]
        x += wch * scale
    return "".join(out)


def subtitle(text: str, cx: float = W / 2) -> str:
    """Sample subtitle in the safe band (stage 5 will do the real ones)."""
    return (f'<text x="{cx}" y="{SUB_BASELINE_Y}" text-anchor="middle" direction="rtl" font-family="SO" '
            f'font-size="{SUB_FONT_SIZE}" fill="{NAVY}" paint-order="stroke" stroke="{PAPER}" '
            f'stroke-width="14" stroke-linejoin="round">{text}</text>')


def label(text: str, x: float, y: float, size: int = 44, anchor: str = "middle", fill: str = NAVY) -> str:
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" direction="rtl" font-family="SO" '
            f'font-size="{size}" fill="{fill}">{text}</text>')


def svg_doc(body: str, bg: str = PAPER) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"><style>@font-face{{font-family:SO;'
            f'src:url("{FONT_FILE}")}}</style><rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')
