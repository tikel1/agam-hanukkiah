"""The futuristic layer of beat 6: Claude as a character, a hologram table, glowing construction lines, data rain.

Claude is drawn as a small friendly block creature in Claude's coral, built from flat-shaded 3D boxes like the rest
of the film (body, two arm nubs, four short legs, two tall eyes). It can wave, point and wink.
Glow is the one soft effect of the film, and only here: it says "inside the computer".
"""

from __future__ import annotations

import math

from geom import Camera, box
from style import DOTS, F, INK, PAPER, mix

CLAUDE = "#D97757"          # Claude's coral
CLAUDE_DARK = "#B95F42"
EYE = "#1F1E1D"
HOLO = "#8FD3E8"            # hologram cyan, a lighter light_blue
GLOW_DEFS = ('<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
             '<feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/>'
             '<feMergeNode in="SourceGraphic"/></feMerge></filter>')


def claude(cx: float, base_y: float, size: float = 1.0, pose: str = "wave", yaw: float = -24) -> str:
    """The character standing with its feet at (cx, base_y). pose: wave | point | wink | stand."""
    cam = Camera(yaw=yaw, pitch=12, zoom=size, target=(0, 0, 0), cx=cx, cy=base_y)
    parts = []
    for lx in (-46, -18, 18, 46):                                    # legs, back pair first
        parts.append(box(cam, lx - 7, lx + 7, 0, 26, -16, -2, CLAUDE_DARK))
    for lx in (-46, -18, 18, 46):
        parts.append(box(cam, lx - 7, lx + 7, 0, 26, 2, 16, CLAUDE_DARK))
    parts.append(box(cam, -66, 66, 26, 106, -30, 30, CLAUDE))        # body
    parts.append(box(cam, -86, -66, 50, 72, -12, 12, CLAUDE))        # left arm nub
    if pose == "wave":
        parts.append(box(cam, 66, 84, 70, 128, -10, 10, CLAUDE))     # right arm up
    elif pose == "point":
        parts.append(box(cam, 66, 112, 62, 80, -10, 10, CLAUDE))     # right arm out
    else:
        parts.append(box(cam, 66, 86, 50, 72, -12, 12, CLAUDE))
    left_eye = box(cam, -34, -22, 58, 86, 30, 32, EYE)
    right_eye = (box(cam, 20, 36, 66, 72, 30, 32, EYE) if pose == "wink" else box(cam, 22, 34, 58, 86, 30, 32, EYE))
    parts += [left_eye, right_eye]
    shadow = cam.project(0, 0, 0)
    return (f'<ellipse cx="{shadow[0]:.1f}" cy="{shadow[1] + 4:.1f}" rx="{90 * size:.1f}" ry="{16 * size:.1f}" '
            f'fill="{INK}" opacity="0.35"/>' + "".join(parts))


def hand_point(cx: float, base_y: float, size: float = 1.0, pose: str = "wave", yaw: float = -24):
    """Screen point of the raised / pointing hand, for the beam."""
    cam = Camera(yaw=yaw, pitch=12, zoom=size, target=(0, 0, 0), cx=cx, cy=base_y)
    return cam.project(75, 128, 0)[:2] if pose == "wave" else cam.project(112, 71, 0)[:2]


def holo_floor(cam: Camera, radius: float = 700, step: float = 70) -> str:
    """A hologram table: a dotted grid on the floor plane, fading out towards its rim."""
    out = []
    n = int(radius // step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, z = i * step, j * step
            d = math.hypot(x, z) / radius
            if d > 1:
                continue
            px, py, _ = cam.project(x, 0, z)
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.6 + 1.6 * (1 - d):.1f}" fill="{HOLO}" '
                       f'opacity="{0.15 + 0.55 * (1 - d):.2f}"/>')
    for r in (radius * 0.55, radius * 0.85):
        pts = [cam.project(r * math.sin(a), 0, r * math.cos(a))[:2] for a in (k * 2 * math.pi / 96 for k in range(97))]
        out.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
                   f'" fill="none" stroke="{HOLO}" stroke-width="2.5" opacity="0.5"/>')
    return "".join(out)


def holo_ring(cam: Camera, radius: float, y0: float, y1: float, colour: str = HOLO, uprights: int = 16) -> str:
    """Glowing construction ring: top and bottom circles, uprights, a logo dot on every top joint."""
    out = []
    for y in (y0, y1):
        pts = [cam.project(radius * math.sin(a), y, radius * math.cos(a))[:2]
               for a in (k * 2 * math.pi / 72 for k in range(73))]
        out.append('<polyline points="' + " ".join(f"{x:.1f},{yy:.1f}" for x, yy in pts) +
                   f'" fill="none" stroke="{colour}" stroke-width="3"/>')
    for k in range(uprights):
        a = k * 2 * math.pi / uprights
        p0 = cam.project(radius * math.sin(a), y0, radius * math.cos(a))
        p1 = cam.project(radius * math.sin(a), y1, radius * math.cos(a))
        if p1[2] < -radius * 0.2:
            continue
        out.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{colour}" '
                   f'stroke-width="2" opacity="0.8"/>')
        out.append(f'<circle cx="{p1[0]:.1f}" cy="{p1[1]:.1f}" r="7" fill="{DOTS[k % 10]}"/>')
    return f'<g filter="url(#glow)">{"".join(out)}</g>'


def beam(x0: float, y0: float, x1: float, y1: float, spread: float = 120) -> str:
    """Light from Claude's hand to the model: a soft wedge and a dotted core."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln * spread, dx / ln * spread
    wedge = (f'<polygon points="{x0:.1f},{y0:.1f} {x1 + nx:.1f},{y1 + ny:.1f} {x1 - nx:.1f},{y1 - ny:.1f}" '
             f'fill="{HOLO}" opacity="0.16"/>')
    dots = "".join(f'<circle cx="{x0 + dx * t:.1f}" cy="{y0 + dy * t:.1f}" r="{3 + 4 * t:.1f}" fill="{DOTS[k % 10]}"/>'
                   for k, t in enumerate(i / 14 for i in range(1, 15)))
    return f'<g filter="url(#glow)">{wedge}</g>{dots}'


def data_rain(seed: int = 3, columns: int = 14, top: float = 220, bottom: float = 1460) -> str:
    """Falling columns of logo dots, brighter at the head: the data stream behind the hologram."""
    out, x = [], seed
    for c in range(columns):
        x = (x * 1103515245 + 12345) % 2 ** 31
        cx = 60 + c * (960 / (columns - 1))
        head = top + x % int(bottom - top)
        for k in range(10):
            y = head - k * 34
            if y < top:
                break
            out.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="{5 - k * 0.35:.1f}" fill="{DOTS[(c + k) % 10]}" '
                       f'opacity="{0.55 * (1 - k / 10):.2f}"/>')
    return "".join(out)


def scan_ring(cam: Camera, radius: float, y: float) -> str:
    """The colour wave's front as a glowing horizontal ring of light."""
    pts = [cam.project(radius * math.sin(a), y, radius * math.cos(a))[:2] for a in (k * 2 * math.pi / 96 for k in range(97))]
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return (f'<g filter="url(#glow)"><polyline points="{line}" fill="none" stroke="{F["mint"]}" stroke-width="6"/></g>'
            f'<polyline points="{line}" fill="none" stroke="#FFFFFF" stroke-width="2"/>')


def holo_panel(x: float, y: float, w: float, h: float, inner: str) -> str:
    """A floating hologram screen: glowing cyan edge, corner ticks, the content inside."""
    ticks = "".join(f'<path d="M{px},{py + sy * 30} V{py} H{px + sx * 30}" stroke="{HOLO}" stroke-width="5" fill="none"/>'
                    for px, py, sx, sy in ((x - 12, y - 12, 1, 1), (x + w + 12, y - 12, -1, 1),
                                           (x - 12, y + h + 12, 1, -1), (x + w + 12, y + h + 12, -1, -1)))
    return (f'<g filter="url(#glow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{HOLO}" '
            f'stroke-width="3"/></g>{inner}{ticks}')
