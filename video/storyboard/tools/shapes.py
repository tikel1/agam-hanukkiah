"""Flat Agam-style building blocks: stripes, toothed rings, flames, water, hands, menorah."""

from __future__ import annotations

from style import FLAME_IN, FLAME_OUT, FOUNTAIN as F, NAVY, NAVY_D, PAPER, SPECTRUM, WHITE

_clip_counter = [0]


def poly(points: list[tuple[float, float]], fill: str, extra: str = "") -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" {extra}/>'


def rect(x: float, y: float, w: float, h: float, fill: str, extra: str = "") -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" {extra}/>'


def circle(cx: float, cy: float, r: float, fill: str) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>'


def clip_group(shape_markup: str, content: str) -> str:
    """Content clipped to a shape (a polygon/rect/circle element string)."""
    _clip_counter[0] += 1
    cid = f"c{_clip_counter[0]}"
    return f'<clipPath id="{cid}">{shape_markup}</clipPath><g clip-path="url(#{cid})">{content}</g>'


def stripes(x: float, y: float, w: float, h: float, colours: list[str], sw: float,
            white: str = PAPER, phase: float = 0.0, skew: float = 0.0, white_ratio: float = 1.0) -> str:
    """Vertical stripes, colour then white, every colour followed by a white stripe."""
    out, cx, i = [], x - phase, 0
    while cx < x + w:
        is_colour = i % 2 == 0
        step = sw if is_colour else sw * white_ratio
        col = colours[(i // 2) % len(colours)] if is_colour else white
        if skew:
            out.append(poly([(cx, y), (cx + step, y), (cx + step + skew, y + h), (cx + skew, y + h)], col))
        else:
            out.append(rect(cx, y, step + 0.6, h, col))
        cx += step
        i += 1
    return "".join(out)


def toothed_outline(cx: float, top: float, w: float, h: float, teeth: int, amp: float = 12) -> list[tuple[float, float]]:
    x0, step = cx - w / 2, w / teeth
    upper = [(x0 + i * step, top + (amp if i % 2 else 0)) for i in range(teeth + 1)]
    lower = [(x0 + w - i * step, top + h - (amp if i % 2 else 0)) for i in range(teeth + 1)]
    return upper + lower


def ring(cx: float, top: float, w: float, h: float, colours: list[str], sw: float,
         phase: float = 0.0, teeth: int = 20, layers: float | None = None) -> str:
    """One toothed drum seen from the side: stripes clipped to a zigzag-edged band.

    layers=None draws painted stripes; layers=p (0..1) draws a 3D-print look: horizontal layers up to p.
    """
    outline = poly(toothed_outline(cx, top, w, h, teeth), WHITE)
    if layers is None:
        return clip_group(outline, stripes(cx - w / 2, top - 2, w, h + 4, colours, sw, phase=phase, white_ratio=0.3))
    rows, y, i = [], top + h + 2, 0
    while y > top + h * (1 - layers):
        rows.append(rect(cx - w / 2, y - 11, w, 11, colours[i % len(colours)]))
        y -= 11
        i += 1
    return clip_group(outline, "".join(rows))


RING_SPECS = [  # top to bottom: width, height, spectrum offset
    (230, 92, 0), (390, 112, 3), (760, 170, 6), (390, 112, 9), (230, 92, 1)]


def ring_stack(cx: float, top: float, phases: list[float] | None = None, scale: float = 1.0,
               visible: int = 5, offsets: list[float] | None = None, layers: float | None = None,
               mono: list[str] | None = None) -> str:
    out, y = [], top
    for i, (w, h, off) in enumerate(RING_SPECS):
        ph = phases[i] if phases else 0.0
        dx = offsets[i] if offsets else 0.0
        w, h = w * scale, h * scale
        if i < visible:
            cols = mono or [SPECTRUM[(off + k) % len(SPECTRUM)] for k in range(4)]
            out.append(ring(cx + dx, y, w, h, cols, max(8, w / 22), phase=ph, teeth=max(10, int(w / 38)), layers=layers))
        y += h - 14 * scale
    return "".join(out)


def stack_height(scale: float = 1.0) -> float:
    return sum(h for _, h, _ in RING_SPECS) * scale - 14 * scale * (len(RING_SPECS) - 1)


def flame(cx: float, base: float, h: float, w: float, lean: float = 0.0) -> str:
    outer = [(cx + lean, base - h), (cx + w * 0.5, base - h * 0.38), (cx + w * 0.34, base),
             (cx - w * 0.34, base), (cx - w * 0.5, base - h * 0.38)]
    inner = [(cx + lean * 0.7, base - h * 0.62), (cx + w * 0.26, base - h * 0.24), (cx + w * 0.18, base),
             (cx - w * 0.18, base), (cx - w * 0.26, base - h * 0.24)]
    return poly(outer, FLAME_OUT) + poly(inner, FLAME_IN)


def water_jets(cx: float, base: float, spread: float, height: float, n: int = 7) -> str:
    """Water as slanted blue columns rising either side of the rings, a dot at each tip."""
    cols = [F["blue"], F["light_blue"], F["teal"], F["periwinkle"]]
    out = []
    for i in range(n):
        for side in (-1, 1):
            x = cx + side * (spread * 0.55 + i * spread * 0.11)
            top_y = base - height * (1 - 0.13 * i)
            shift = side * 34
            out.append(poly([(x - 9, base), (x + 9, base), (x + 9 + shift, top_y), (x - 9 + shift, top_y)], cols[(i + (side > 0)) % 4]))
            out.append(circle(x + shift, top_y - 10, 13, cols[(i + 1) % 4]))
    return "".join(out)


def basin(cx: float, y: float, w: float) -> str:
    cols = [F["blue"], F["light_blue"], F["teal"]]
    return "".join(rect(cx - w / 2 + i * 26, y + (10 if i % 2 else 0), 16, 44 - (10 if i % 2 else 0), cols[i % 3])
                   for i in range(int(w / 26) + 1))


def person(x: float, base: float, h: float, colour: str) -> str:
    return (circle(x, base - h + h * 0.11, h * 0.11, colour) +
            poly([(x - h * 0.13, base - h * 0.74), (x + h * 0.13, base - h * 0.74), (x + h * 0.2, base),
                  (x - h * 0.2, base)], colour))


def hand(x: float, y: float, angle: float = -8, scale: float = 1.0, colour: str = NAVY_D, flip: bool = False) -> str:
    """Flat silhouette of a forearm with a pointing index finger (points left; flip points right)."""
    shapes = [poly([(300, 108), (640, 80), (640, 310), (300, 280)], colour),
              poly([(120, 112), (310, 96), (320, 282), (140, 262)], NAVY),
              poly([(-170, 128), (130, 120), (130, 170), (-170, 158)], colour),
              poly([(20, 178), (135, 172), (140, 214), (24, 212)], colour),
              poly([(34, 220), (140, 218), (142, 254), (40, 250)], colour),
              poly([(52, 260), (144, 258), (144, 290), (60, 284)], colour)]
    sx = -scale if flip else scale
    return f'<g transform="translate({x},{y}) rotate({angle}) scale({sx},{scale})">{"".join(shapes)}</g>'


def brush(x: float, y: float, angle: float = 35, colour: str = F["coral"]) -> str:
    return (f'<g transform="translate({x},{y}) rotate({angle})">{rect(0, -8, 260, 16, F["yellow"])}'
            f'{poly([(-46, -14), (0, -10), (0, 10), (-46, 14), (-70, 0)], colour)}</g>')


def ny_menorah(cx: float, base: float, h: float) -> str:
    """Large gold menorah with diagonal branches (redrawn, not a copy of any photo)."""
    gold, gold_d = F["yellow"], F["orange"]
    out = [poly([(cx - h * 0.22, base), (cx + h * 0.22, base), (cx + h * 0.12, base - h * 0.08),
                 (cx - h * 0.12, base - h * 0.08)], gold_d)]
    out.append(rect(cx - h * 0.025, base - h, h * 0.05, h * 0.93, gold))
    for side in (-1, 1):
        for k in range(4):
            top_x = cx + side * h * (0.12 + 0.11 * k)
            top_y = base - h * (0.62 + 0.09 * k)
            out.append(poly([(cx + side * h * 0.02, base - h * 0.2), (cx + side * h * 0.05, base - h * 0.2),
                             (top_x + side * h * 0.02, top_y), (top_x - side * h * 0.02, top_y)], gold if k % 2 else gold_d))
            out.append(rect(top_x - h * 0.03, top_y - h * 0.035, h * 0.06, h * 0.035, gold))
    return "".join(out)


def recycle(cx: float, cy: float, r: float, colours: list[str]) -> str:
    """Three chasing arrows, straight lines only."""
    pts = [(cx, cy - r), (cx + r * 0.87, cy + r * 0.5), (cx - r * 0.87, cy + r * 0.5)]
    out = []
    for i in range(3):
        a, b = pts[i], pts[(i + 1) % 3]
        mx, my = a[0] + (b[0] - a[0]) * 0.75, a[1] + (b[1] - a[1]) * 0.75
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{mx:.1f}" y2="{my:.1f}" '
                   f'stroke="{colours[i]}" stroke-width="{r * 0.16:.1f}"/>')
        nx, ny = (b[1] - a[1]) / 3.2, -(b[0] - a[0]) / 3.2
        tip = (a[0] + (b[0] - a[0]) * 0.97, a[1] + (b[1] - a[1]) * 0.97)
        out.append(poly([(mx + nx, my + ny), (mx - nx, my - ny), tip], colours[i]))
    return "".join(out)


def flat_hanukkiah(cx: float, top: float, scale: float = 1.0, lit: bool = False, mono: list[str] | None = None,
                   flick: float = 0.0, ink: str = F["blue"]) -> str:
    """The hanukkiah redrawn as a flat 2D illustration: 9 candles, 5 toothed rings, stem and foot."""
    cand, y3 = [], 230 + 78 + 98
    xs = [-330, -255, -180, -100, 100, 180, 255, 330]
    for i, x in enumerate(xs):
        h = 190 if i % 2 else 170
        cand.append(rect(x - 17, y3 + 8 - h, 34, h, ink))
        cand.append(rect(x - 26, y3 - 6, 52, 14, F["yellow"]))
        if lit:
            sign = 1 if i % 2 else -1
            cand.append(flame(x, y3 + 8 - h - 4, 74 * (1 + 0.15 * flick * sign), 36, lean=7 * flick * sign))
    cand.append(rect(-19, 0, 38, 252, ink))
    cand.append(rect(-28, 232, 56, 14, F["yellow"]))
    if lit:
        cand.append(flame(0, -4, 92 * (1 + 0.12 * flick), 44, lean=-6 * flick))
    foot = poly([(-30, 752), (30, 752), (40, 800), (-40, 800)], F["white"]) + poly(
        [(-230, 800), (230, 800), (250, 842), (-250, 842)], F["grey"])
    body = ring_stack(0, 230, mono=mono) + "".join(cand) + foot
    return f'<g transform="translate({cx},{top}) scale({scale})">{body}</g>'


def ring_close_up(cx: float, top: float, w: float, h: float, side: str) -> str:
    """One big flat ring, seen from the left (green Magen David on yellow) or right (HANUKKAH on white)."""
    from style import NAVY as INK  # noqa: F401  (kept for clarity of palette use)
    outline = poly(toothed_outline(cx, top, w, h, 28, 16), WHITE)
    if side == "back":
        art = (stripes(cx - w / 2, top, w, h, [F["rose"], F["lilac"], F["periwinkle"]], 46, white_ratio=0.3)
               + circle(cx, top + h / 2, 118, F["orange"]) + circle(cx, top + h / 2, 34, F["brick"]))
    elif side == "left":
        cols = [F["periwinkle"], F["yellow"], F["blue"], F["yellow"]]
        star = poly([(cx, top + h * 0.12), (cx + 90, top + h * 0.7), (cx - 90, top + h * 0.7)], F["green"]) +             poly([(cx, top + h * 0.88), (cx + 90, top + h * 0.3), (cx - 90, top + h * 0.3)], F["green"])
        art = stripes(cx - w / 2, top, w, h, cols, 46, white_ratio=0.3) + star
    else:  # right
        cols = [F["coral"], F["rose"], F["brick"], F["coral"]]
        art = (stripes(cx - w / 2, top, w, h, cols, 46, white_ratio=0.3) + rect(cx - 330, top + h * 0.25, 660, h * 0.5, WHITE)
               + f'<text x="{cx}" y="{top + h * 0.64}" text-anchor="middle" font-family="SO" font-size="{h * 0.36:.0f}" '
                 f'fill="{F["blue"]}" letter-spacing="6">HANUKKAH</text>')
    return clip_group(outline, art)
