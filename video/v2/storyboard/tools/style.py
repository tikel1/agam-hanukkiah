"""Style bible as code: palette, frame size, safe areas, line-and-dot titles, subtitles.

Glyphs are read from the engine (v2/engine/src/components/glyphs.js) so a title drawn here is the title the
engine will draw. Two new glyphs ('?' and '!') are added here and listed as an engine need.
"""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent                      # v2/storyboard
ENGINE = BOARD.parent / "engine"
W, H = 1080, 1920

# ---- palette -------------------------------------------------------------------------------------------
PAPER = "#F7F5EE"
WHITE = "#FFFFFF"
INK = "#232C5E"          # logo navy: titles, subtitles, darkest tone (there is no black)
NAVY = "#2B2F6B"         # fountain navy: dark shapes
NIGHT = "#1E2452"        # night sky, a step under INK
F = {
    "white": "#F4F1E4", "yellow": "#F2C94C", "orange": "#E8893F", "coral": "#E8655C", "brick": "#A8322A",
    "rose": "#DC8A86", "lilac": "#9A8CC0", "periwinkle": "#7484C4", "light_blue": "#A3C1E0", "blue": "#3E5FB0",
    "navy": "#2B2F6B", "mint": "#A8DDB5", "teal": "#3E8F7C", "green": "#4E9E5E", "grey": "#A9B3B6",
}
SPECTRUM = [F[k] for k in ("yellow", "orange", "coral", "brick", "rose", "lilac", "periwinkle", "blue",
                           "light_blue", "mint", "teal", "green")]
DOTS = ["#e4432f", "#f6d21c", "#1fa3a8", "#6a5ea8", "#6bb7e6", "#1b7f3e", "#a81f2a", "#4f63b0", "#cfa3d1", "#f39a1e"]
FLAME = {"outer": "#F39A1E", "inner": "#F6D21C", "core": "#FFF6C8"}
GOLD = "#E9B949"

# Grounds of the colour script (background per act)
GROUND = {
    "paper": PAPER, "sky": "#DCE7F2", "memory": "#F4E7D0", "amber": "#F6B54A", "ember": "#E8893F",
    "notebook": "#FBFAF5", "screen": INK, "studio": "#EEF0F0", "dusk": "#3A3F78", "night": NIGHT,
}

# ---- frame layout (1080 x 1920) ------------------------------------------------------------------------
SIDE = 72                 # side margin for titles and subtitles
TOP_RESERVED = 200        # status bar / player chrome: nothing important above this
TITLE_TOP = 250           # title block lives in y 250..640
TITLE_BOTTOM = 640
SUBJECT = (560, 1470)     # hero subject zone
SUB_BAND = (1490, 1700)   # subtitle band (two lines)
BOTTOM_RESERVED = 1720    # player controls: nothing important below this

TITLE_CAP = 150           # cap height of a big line-and-dot title
SUB_SIZE = 60             # subtitle font size, Secular One
SUB_LEADING = 92
SUB_MAX_W = 820          # widest subtitle line; wider lines shrink to SUB_MIN_SIZE, then must be re-broken
SUB_MIN_SIZE = 52
FONT_URL = "../../engine/assets/fonts/SecularOne-Regular.ttf"   # relative to storyboard/frames/

# ---- line-and-dot glyphs -------------------------------------------------------------------------------
LOGO = {"CAP": 100.0, "STROKE": 7.5, "DOT_R": 10.5, "LETTER_GAP": 26.0, "WORD_GAP": 62.0}


def _load_glyphs() -> tuple[dict, dict]:
    text = (ENGINE / "src" / "components" / "glyphs.js").read_text(encoding="utf-8")
    entry = re.compile(r"'(.)':\s*\[(-?\d+),\s*\[(.*?)\],\s*\[(.*?)\]\]")

    def table(block: str) -> dict:
        out = {}
        for ch, width, paths, dots in entry.findall(block):
            out[ch] = (float(width), re.findall(r"'([^']*)'", paths),
                       [(float(a), float(b)) for a, b in re.findall(r"\[(-?[\d.]+),\s*(-?[\d.]+)\]", dots)])
        return out

    glyph_block = text.split("export const GLYPHS")[1].split("export const DIGITS")[0]
    digit_block = text.split("export const DIGITS")[1].split("export function")[0]
    return table(glyph_block), table(digit_block)


GLYPHS, DIGITS = _load_glyphs()
# New for v2 (engine need N1): punctuation in the same spirit, a stroke with a dot instead of a curve.
# N1b: a clearer qof (user note 26.11): top bar into a slightly slanted right side, a separate left leg below the line.
GLYPHS["ק"] = (56.0, ["M0,0 H56 L60,100", "M8,36 L4,128"], [(0.0, 0.0)])
# tet, for "אמנות קינטית": the open box of the tet, its right arm turning in and down (straight lines only)
GLYPHS["ט"] = (62.0, ["M0,0 V100 H62 V0 H34 L28,40"], [(0.0, 0.0)])
GLYPHS["?"] = (40.0, ["M0,14 L14,0 H40 V44 L20,56 V74"], [(20.0, 100.0)])
GLYPHS["!"] = (0.0, ["M0,0 V72"], [(0.0, 100.0)])
GLYPHS["–"] = (40.0, ["M0,50 H40"], [])
# Latin letters for the "AI" title (left to right table, with the digits), museum-logo style
DIGITS["A"] = (70.0, ["M0,100 L35,0 L70,100", "M15,60 H55"], [(35.0, 0.0)])
DIGITS["I"] = (0.0, ["M0,0 V100"], [(0.0, 0.0)])


def _layout(words: list[str], rtl: bool) -> tuple[list, list, float]:
    table = GLYPHS if rtl else DIGITS
    items, seps, x = [], [], 0.0
    for wi, word in enumerate(words):
        if wi:
            seps.append(x + LOGO["WORD_GAP"] / 2)
            x += LOGO["WORD_GAP"]
        for ci, ch in enumerate(word):
            if ci:
                x += LOGO["LETTER_GAP"]
            if ch not in table:
                raise KeyError(f"no line-and-dot glyph for {ch!r}")
            width, paths, dots = table[ch]
            items.append((ch, x, width, paths, dots))
            x += width
    total = x
    if rtl:
        items = [(ch, total - x0 - w, w, p, d) for ch, x0, w, p, d in items]
        seps = [total - s for s in seps]
    return items, seps, total


def title_width(words: list[str], cap: float = TITLE_CAP, rtl: bool = True) -> float:
    _, _, total = _layout(words, rtl)
    return (total + LOGO["WORD_GAP"]) * cap / LOGO["CAP"]


def title(words: list[str], cx: float, top: float, cap: float = TITLE_CAP, ink: str = INK, rtl: bool = True,
          drawn: float = 1.0, end_dots: bool = True, dot_offset: int = 0) -> str:
    """Line-and-dot title centred on cx. drawn < 1 shows the write-on mid way (strokes right to left, dots last)."""
    items, seps, total = _layout(words, rtl)
    s = cap / LOGO["CAP"]
    x0 = cx - total * s / 2
    order = sorted(range(len(items)), key=lambda i: -items[i][1]) if rtl else list(range(len(items)))
    shown = int(round(drawn * len(items) + 0.0001))
    strokes, dots = [], []
    colours = iter((DOTS[dot_offset:] + DOTS[:dot_offset]) * 10)
    for rank, idx in enumerate(order):
        ch, lx, w, paths, pts = items[idx]
        if rank >= shown:
            continue
        tf = f'translate({x0 + lx * s:.1f},{top:.1f}) scale({s:.4f})'
        strokes.append(f'<g transform="{tf}">' + "".join(f'<path d="{d}"/>' for d in paths) + "</g>")
        if drawn >= 1.0 or rank < shown - 1:
            for px, py in pts:
                dots.append(f'<circle cx="{x0 + (lx + px) * s:.1f}" cy="{top + py * s:.1f}" '
                            f'r="{LOGO["DOT_R"] * s:.1f}" fill="{next(colours)}"/>')
    if drawn >= 1.0:
        for sx in seps:
            dots.append(f'<circle cx="{x0 + sx * s:.1f}" cy="{top + 50 * s:.1f}" r="{LOGO["DOT_R"] * s:.1f}" '
                        f'fill="{next(colours)}"/>')
        if end_dots:
            for ex in (x0 - LOGO["WORD_GAP"] / 2 * s, x0 + (total + LOGO["WORD_GAP"] / 2) * s):
                dots.append(f'<circle cx="{ex:.1f}" cy="{top + 50 * s:.1f}" r="{LOGO["DOT_R"] * s:.1f}" '
                            f'fill="{next(colours)}"/>')
    sw = LOGO["STROKE"]
    return (f'<g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="miter" stroke-linecap="butt">'
            + "".join(strokes) + "</g>" + "".join(dots))


def small_line(text: str, cx: float, y: float, size: int = 44, fill: str = INK, halo: str | None = None,
               rtl: bool = True) -> str:
    stroke = (f' stroke="{halo}" stroke-width="10" paint-order="stroke" stroke-linejoin="round"' if halo else "")
    return (f'<text x="{cx:.0f}" y="{y:.0f}" text-anchor="middle" direction="{'rtl' if rtl else 'ltr'}" font-family="Secular One" '
            f'font-size="{size}" letter-spacing="1.5" fill="{fill}"{stroke}>{text}</text>')


def dot_rule(cx: float, y: float, width: float, n: int = 13, r: float = 5.5, offset: int = 0) -> str:
    """The dotted rule of our logo, used under titles and as a divider."""
    step = width / (n - 1)
    return "".join(f'<circle cx="{cx - width / 2 + i * step:.1f}" cy="{y:.1f}" r="{r}" '
                   f'fill="{DOTS[(i + offset) % len(DOTS)]}"/>' for i in range(n))


_FONT_CACHE: dict = {}


def text_width(text: str, size: int = SUB_SIZE) -> float:
    from PIL import ImageFont
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(str(ENGINE / "assets" / "fonts" / "SecularOne-Regular.ttf"), size)
    return _FONT_CACHE[size].getlength(text)


SLANT = 0.07              # the slat ends lean like the museum letters' strokes


def subtitle(lines: list[str], dark: bool = False, word: float = 0.62, accent: int = 0) -> str:
    """Subtitles as a design element (user note 26.11): every line sits on its own paper slat with slanted ends,
    a small Agam stripe stamp marks where the line starts (right, as Hebrew reads), and a logo dot hops along
    under the word being spoken (word = 0..1 through the cue; the key frames freeze it there).
    Secular One 60, max two lines, centred in the band y 1490..1700."""
    fill, slat, edge = (PAPER, "#2E3570", "#3A427F") if dark else (INK, "#FFFFFF", "#E4E0D4")
    size = SUB_SIZE
    widest = max(text_width(line) for line in lines)
    if widest > SUB_MAX_W:
        size = max(SUB_MIN_SIZE, int(SUB_SIZE * SUB_MAX_W / widest))
        if text_width(max(lines, key=text_width), size) > SUB_MAX_W + 1:
            print("subtitle too long, re-break:", lines)
    n = len(lines)
    pad, slat_h = 34, 78
    base = SUB_BAND[0] + (SUB_BAND[1] - SUB_BAND[0]) / 2 - (n - 1) * SUB_LEADING / 2
    words_all = [w for line in lines for w in line.split()]
    current = min(int(word * len(words_all)), len(words_all) - 1)
    out, k = [], 0
    for i, line in enumerate(lines):
        cy = base + i * SUB_LEADING
        tw = text_width(line, size)
        x0, x1 = W / 2 - tw / 2 - pad, W / 2 + tw / 2 + pad + 30
        y0, y1 = cy - slat_h / 2, cy + slat_h / 2
        dx = slat_h * SLANT
        out.append(f'<polygon points="{x0 + dx + 6:.1f},{y0 + 6:.1f} {x1 + dx + 6:.1f},{y0 + 6:.1f} {x1 - dx + 6:.1f},'
                   f'{y1 + 6:.1f} {x0 - dx + 6:.1f},{y1 + 6:.1f}" fill="{edge}"/>')
        out.append(f'<polygon points="{x0 + dx:.1f},{y0:.1f} {x1 + dx:.1f},{y0:.1f} {x1 - dx:.1f},{y1:.1f} '
                   f'{x0 - dx:.1f},{y1:.1f}" fill="{slat}"/>')
        # stripe stamp at the start of the line (right end): colour, white, colour...
        for j in range(5):
            sx = x1 - 30 + j * 6 - dx * 0.2
            colour = SPECTRUM[(accent + i * 5 + j) % 12] if j % 2 == 0 else slat
            out.append(f'<polygon points="{sx + dx:.1f},{y0:.1f} {sx + 6 + dx:.1f},{y0:.1f} {sx + 6 - dx:.1f},{y1:.1f} '
                       f'{sx - dx:.1f},{y1:.1f}" fill="{colour}"/>')
        out.append(f'<text x="{W / 2 - 15:.0f}" y="{cy + SUB_SIZE * 0.36:.0f}" text-anchor="middle" direction="rtl" '
                   f'font-family="Secular One" font-size="{size}" fill="{fill}">{line}</text>')
        # the hopping dot under the current word (words laid right to left)
        right = W / 2 - 15 + tw / 2
        space = text_width(" ", size)
        for w in line.split():
            ww = text_width(w, size)
            if k == current:
                out.append(f'<circle cx="{right - ww / 2:.1f}" cy="{y1 + 2:.1f}" r="9" fill="{DOTS[(accent + k) % 10]}"/>')
            right -= ww + space
            k += 1
    return "".join(out)


def svg_doc(body: str, bg: str = PAPER, defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs><style>@font-face{{font-family:"Secular One";src:url("{FONT_URL}");}}</style>{defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')


def mix(a: str, b: str, t: float) -> str:
    """Linear mix of two hex colours (t=0 -> a)."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(pa, pb))
