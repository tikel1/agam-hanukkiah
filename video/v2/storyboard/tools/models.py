"""The two heroes of the film as storyboard models: the 1986 fountain and our hanukkiah.

Proportions are ours (model/README.md for the hanukkiah, research §4 for the fountain), in world units where
1 unit = 1 px at zoom 1. y = 0 is the ground (the pool's water line or the table).
The R3 ring of the hanukkiah carries the two hidden pictures, one column per tooth, as painted from the
colouring maps (model/out/maps/map_R3_A_left / map_R3_B_right): from the left the Magen David and the dreidel
on yellow, from the right HANUKKAH and the sufganiyah on white.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from geom import Camera, Picture, Pleats, cylinder, ellipse_xz, flame, jet, poly
from style import F, INK, PAPER, SPECTRUM, mix

R3_TEETH = 80
R3_RADIUS = 360
R3_HEIGHT = 150
# 70 degree folds (model/README.md): each face 35 degrees off the radius -> depth / pitch = tan(55) / 2 = 0.71.
# Past 35 degrees the near teeth hide the other face set completely, so one picture reads alone.
R_DEPTH = 0.71


# ---- hidden pictures -----------------------------------------------------------------------------------
def _ring_canvas(teeth: int, radius: float, height: int, ground: str):
    width = round(2 * math.pi * radius)
    img = Image.new("RGB", (width, height), ground)
    return img, ImageDraw.Draw(img), width


def _col_x(col: float, width: int, teeth: int) -> float:
    return (col + 0.5) / teeth * width


def _to_columns(img: Image.Image, teeth: int) -> Picture:
    w, h = img.size
    cols = Image.new("RGB", (teeth, h))
    for i in range(teeth):
        cols.paste(img.crop((int(_col_x(i, w, teeth)), 0, int(_col_x(i, w, teeth)) + 1, h)), (i, 0))
    return Picture(cols)


def _star(draw, cx, cy, r, fill):
    for start in (90, 270):
        pts = [(cx + r * math.cos(math.radians(start + k * 120)), cy - r * math.sin(math.radians(start + k * 120)))
               for k in range(3)]
        draw.polygon(pts, fill=fill)


def picture_a() -> Picture:
    """Left faces: yellow ground, green Magen David at the front, orange dreidel just after it, warm bands behind."""
    img, d, w = _ring_canvas(R3_TEETH, R3_RADIUS, R3_HEIGHT, F["yellow"])
    col = lambda c: _col_x(c, w, R3_TEETH)
    d.rectangle((col(56), 0, col(61), R3_HEIGHT), fill=F["lilac"])  # bands behind the pictures
    d.rectangle((col(61), 0, col(80) + 40, R3_HEIGHT), fill=F["rose"])
    d.rectangle((0, 0, col(4), R3_HEIGHT), fill=F["rose"])
    d.rectangle((col(4), 0, col(10), R3_HEIGHT), fill=F["orange"])
    _star(d, col(39.5), 78, 70, F["green"])
    # dreidel: handle, body, point (straight lines only)
    cx = col(49.5)
    d.rectangle((cx - 14, 14, cx + 14, 40), fill=F["orange"])
    d.polygon([(cx - 66, 40), (cx + 66, 40), (cx + 66, 96), (cx, 140), (cx - 66, 96)], fill=F["orange"])
    return _to_columns(img, R3_TEETH)


BLOCK = {  # 3 x 5 block letters for HANUKKAH, one cell = one tooth wide
    "H": ["X.X", "X.X", "XXX", "X.X", "X.X"], "A": [".X.", "X.X", "XXX", "X.X", "X.X"],
    "N": ["X.X", "XXX", "XXX", "XXX", "X.X"], "U": ["X.X", "X.X", "X.X", "X.X", "XXX"],
    "K": ["X.X", "XX.", "X..", "XX.", "X.X"],
}


def picture_b() -> Picture:
    """Right faces: white ground, HANUKKAH in blue across the front, orange sufganiyah with brick jam behind."""
    img, d, w = _ring_canvas(R3_TEETH, R3_RADIUS, R3_HEIGHT, F["white"])
    col = lambda c: _col_x(c, w, R3_TEETH)
    d.rectangle((0, 0, col(8), R3_HEIGHT), fill=F["periwinkle"])
    d.rectangle((col(8), 0, col(12), R3_HEIGHT), fill=F["lilac"])
    word, start = "HANUKKAH", 40 - 16
    for k, ch in enumerate(word):
        for r, row in enumerate(BLOCK[ch]):
            for c, cell in enumerate(row):
                if cell == "X":
                    x0 = col(start + k * 4 + c) - w / R3_TEETH / 2
                    d.rectangle((x0, 22 + r * 21, x0 + w / R3_TEETH, 22 + (r + 1) * 21), fill=F["blue"])
    cx = col(66)
    d.ellipse((cx - 120, 38, cx + 120, 118), fill=F["orange"])
    d.rectangle((cx - 26, 62, cx + 26, 88), fill=F["brick"])
    return _to_columns(img, R3_TEETH)


PIC_A, PIC_B = picture_a(), picture_b()


def spectrum_from(offset: int, n: int):
    """One spectral turn around a ring, starting at offset: Agam's colour-wheel order."""
    return lambda i: SPECTRUM[(offset + i * len(SPECTRUM) // n) % len(SPECTRUM)]


# ---- hanukkiah ------------------------------------------------------------------------------------------
HANUKKIAH_RINGS = [  # name, teeth, radius, height, base, spectrum offset
    ("R1", 40, 150, 62, 95, 6), ("R2", 56, 225, 78, 157, 2), ("R3", R3_TEETH, R3_RADIUS, R3_HEIGHT, 235, 0),
    ("R4", 44, 185, 64, 385, 8), ("R5", 28, 105, 56, 449, 4),
]
CANDLE_RING = 296
CANDLE_COLOURS = [F["blue"]] * 8   # as in the model renders: blue candles in gold cups


def hanukkiah_rings(spin: float = 0.0, painted: float = 1.0, offset_y: dict | None = None, white: bool = False,
                    r3_pictures: bool = True) -> list[Pleats]:
    """painted: 0..1 colour wave rising from the bottom (1 = all painted). offset_y: exploded view per ring."""
    rings = []
    total = 449 + 56
    for name, teeth, radius, height, base, off in HANUKKIAH_RINGS:
        dy = (offset_y or {}).get(name, 0.0)
        is_painted = (not white) and (base + height / 2) / total <= painted + 1e-6
        if name == "R3" and r3_pictures and is_painted:
            a, b = PIC_A, PIC_B
        elif is_painted:
            a, b = spectrum_from(off, teeth), F["white"]
        else:
            a, b = "#FBFAF6", "#EDEBE4"
        rings.append(Pleats(pleats=teeth, length=2 * math.pi * radius, height=height, base=base + dy, bend=1.0,
                            spin=spin, skin_a=a, skin_b=b, cap="#F4F1E4" if not white else "#FBFAF6",
                            depth_ratio=R_DEPTH))
    return rings


def hanukkiah(cam: Camera, defs: list, spin: float = 0.0, painted: float = 1.0, lit: int = 0, night: bool = False,
              white: bool = False, offset_y: dict | None = None, candles: bool = True, glow: bool = False) -> str:
    """Draws foot, stem, the five rings and the candles. lit = number of flames (shamash first)."""
    out = [cylinder(cam, 0, 0, 34, 0, 230, "#E9E6DC", "#F4F1E4"), cylinder(cam, 0, 34, 95, 0, 58, "#E9E6DC", "#F4F1E4")]
    out.append(_plaque(cam))
    rings = hanukkiah_rings(spin, painted, offset_y, white)
    from geom import draw_groups
    behind, front = _candles(cam, lit, rings[2].base + R3_HEIGHT, night, glow) if candles else ("", "")
    out.append(draw_groups(cam, rings[:3], defs))
    out.append(behind)
    out.append(draw_groups(cam, rings[3:], defs))
    out.append(_shamash(cam, rings[4].base + 56, lit > 0, night, glow) if candles else "")
    out.append(front)
    return "".join(out)


def _plaque(cam: Camera) -> str:
    """The name plaque on the front of the foot, as printed: the logo in line-and-dot letters (blue on white)."""
    from style import title
    yaw = math.radians(cam.yaw)
    x, y, depth = cam.project(230 * math.sin(yaw), 17, 230 * math.cos(yaw))
    cap = 13 * cam.zoom
    if cap < 4:
        return ""
    return title(["חנוכיית", "אש", "ומים"], x, y - cap * 0.55, cap=cap, ink=F["blue"], end_dots=False)


def _candle(cam, x, y, z, colour, lit, night, h=150, glow=False):
    s = cylinder(cam, x, y, y + 24, z, 27, "#D9B24A", "#E9C766")
    s += cylinder(cam, x, y + 24, y + 24 + h, z, 15, colour, mix(colour, PAPER, 0.35))
    if lit:
        top = cam.project(x, y + 24 + h, z)
        s += flame(top[0], top[1] - 4 * cam.zoom, 62 * cam.zoom, 30 * cam.zoom, glow=glow or night)
    return s


def _candles(cam, lit, y, night, glow):
    behind, front = [], []
    order = list(range(8))
    for k in order:
        phi = math.radians(-157.5 + k * 45)
        x, z = CANDLE_RING * math.sin(phi), CANDLE_RING * math.cos(phi)
        depth = cam.rotate(x, y, z)[2]
        svg = _candle(cam, x, y, z, CANDLE_COLOURS[k], k < lit - 1, night, glow=glow)
        (front if depth > 0 else behind).append((depth, svg))
    return ("".join(s for _, s in sorted(behind)), "".join(s for _, s in sorted(front)))


def _shamash(cam, y, lit, night, glow):
    return _candle(cam, 0, y, 0, F["blue"], lit, night, h=170, glow=glow)


# ---- the fountain (1986) --------------------------------------------------------------------------------
FOUNTAIN_RINGS = [  # teeth, radius, height, base, spectrum offset, turns (the middle three turned)
    (40, 210, 92, 70, 9, False), (52, 290, 104, 196, 3, True), (72, 410, 138, 336, 0, True),
    (52, 310, 100, 510, 5, True), (36, 200, 86, 646, 7, False),
]


def fountain(cam: Camera, defs: list, spin: float = 0.0, rings: int = 5, water: float = 0.0, fire: float = 0.0,
             silhouette: str | None = None, pool: bool = True, drop: dict | None = None) -> str:
    """water / fire 0..1. silhouette = one flat colour for the whole fountain (the ghost in beat 7)."""
    out = []
    if pool:
        out.append(ellipse_xz(cam, 0, 0, 0, 640, mix(F["light_blue"], PAPER, 0.15) if not silhouette else "none"))
        if not silhouette:
            for r, c in ((560, "#F4F1E4"), (470, F["light_blue"]), (380, "#F4F1E4"), (300, F["light_blue"])):
                out.append(ellipse_xz(cam, 0, 0, 0, r, "none", f' stroke="{c}" stroke-width="{5 * cam.zoom:.1f}"'))
    from geom import draw_groups
    jets_behind, jets_front = _jets(cam, water) if water > 0 and not silhouette else ("", "")
    out.append(jets_behind)
    out.append(cylinder(cam, 0, 0, FOUNTAIN_RINGS[0][3], 0, 40, silhouette or "#C9CED0", silhouette or "#DADDDC"))
    for k, (teeth, radius, height, base, off, turns) in enumerate(FOUNTAIN_RINGS[:rings]):
        skin_b = F["white"] if k % 2 == 0 else spectrum_from(off + 6, teeth)
        ring = Pleats(pleats=teeth, length=2 * math.pi * radius, height=height, base=base + (drop or {}).get(k, 0.0), bend=1.0,
                      spin=spin * (1 if k % 2 else -1) if turns else 0.0, depth_ratio=0.6,
                      skin_a=silhouette or spectrum_from(off, teeth), skin_b=silhouette or skin_b,
                      cap=silhouette or "#F4F1E4", shaded=not silhouette)
        out.append(draw_groups(cam, [ring], defs))
        top = base + height
        nxt = FOUNTAIN_RINGS[k + 1][3] if k + 1 < len(FOUNTAIN_RINGS) else top + 12
        if (k + 1 < rings or k == len(FOUNTAIN_RINGS) - 1) and not (drop or {}).get(k + 1):
            out.append(cylinder(cam, 0, top, nxt, 0, 40 if k + 1 < len(FOUNTAIN_RINGS) else 30,
                                silhouette or "#C9CED0", silhouette or "#DADDDC"))
    out.append(jets_front)
    if fire > 0 and rings >= 5:
        top = cam.project(0, 732, 0)
        out.append(flame(top[0], top[1], 300 * fire * cam.zoom, 120 * cam.zoom, lean=0.04, glow=True))
    return "".join(out)


def _jets(cam: Camera, amount: float) -> tuple[str, str]:
    """Water as line-and-dot strokes: rising from the pool, arching in towards the stack, ending in a dot.
    Returns (behind, front) so the back jets pass behind the rings."""
    behind, front = [], []
    n = 22
    for k in range(n):
        phi = 2 * math.pi * (k + 0.5) / n
        x, z = 560 * math.sin(phi), 560 * math.cos(phi)
        depth = cam.rotate(x, 0, z)[2]
        h = (300 + 260 * ((k * 7) % 5) / 4) * amount
        p0 = cam.project(x, 0, z)
        p1 = cam.project(x * 0.70, h, z * 0.70)
        colour = "#FFFFFF" if k % 2 else F["light_blue"]
        svg = jet(p0[0], p0[1], p1[0], p1[1], colour, 5 * cam.zoom, 9 * cam.zoom,
                  dot_colour=[F["light_blue"], F["blue"], F["mint"], "#FFFFFF", F["teal"]][k % 5],
                  bow=-0.18 * (p1[0] - cam.cx))
        (front if depth > 0 else behind).append(svg)
    return "".join(behind), "".join(front)
