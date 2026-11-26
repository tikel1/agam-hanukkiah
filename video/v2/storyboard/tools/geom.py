"""Orthographic 3D drawn flat: the storyboard's stand-in for the engine.

Real geometry (pleats, toothed rings, cylinders) is projected by an orthographic camera and written as flat SVG
polygons, so the key frames show what the engine will show: true 3D, no lighting gradients, palette colours.
Shading has exactly two values: a face turned away from the key light gets a 14% navy step (engine need N2).
Pictures ride on pleat faces three ways: a flat colour, colour runs sampled from a small picture (the hidden
Hanukkah pictures, one column per tooth), or a real photo strip mapped by an affine transform (photo pleats).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import Image

from style import INK, mix

DEG = math.pi / 180
LIGHT = (-0.55, 0.45, 0.70)
_l = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _l for c in LIGHT)
SHADE_STEP = 0.14


@dataclass
class Camera:
    yaw: float = 0.0          # degrees, + = camera moves to the right of the subject
    pitch: float = 0.0        # degrees, + = camera above, looking down
    zoom: float = 1.0
    target: tuple = (0.0, 0.0, 0.0)
    cx: float = 540.0
    cy: float = 1000.0

    def rotate(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        cy_, sy_ = math.cos(self.yaw * DEG), math.sin(self.yaw * DEG)
        cp, sp = math.cos(self.pitch * DEG), math.sin(self.pitch * DEG)
        x1 = x * cy_ - z * sy_
        z1 = x * sy_ + z * cy_
        up = y * cp - z1 * sp
        depth = z1 * cp + y * sp
        return x1, up, depth

    def project(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        tx, ty, tz = self.target
        x1, up, depth = self.rotate(x - tx, y - ty, z - tz)
        return self.cx + x1 * self.zoom, self.cy - up * self.zoom, depth

    def facing(self, n: tuple) -> float:
        """> 0 when a face with world normal n looks towards the camera."""
        return self.rotate(*n)[2]


def shade(colour: str, normal: tuple) -> str:
    lit = sum(a * b for a, b in zip(normal, LIGHT))
    return colour if lit > 0.12 else mix(colour, INK, SHADE_STEP)


def poly(points, fill: str, extra: str = "") -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}"{extra}/>'


# ---- pictures on faces ---------------------------------------------------------------------------------
class Picture:
    """A small picture read one column per pleat (or per tooth): runs of equal colour from top to bottom."""

    def __init__(self, image: Image.Image):
        self.image = image.convert("RGB")
        self.cols, self.rows = self.image.size
        self._cache: dict[int, list] = {}

    def runs(self, col: int) -> list[tuple[float, float, str]]:
        col %= self.cols
        if col not in self._cache:
            px = self.image.load()
            out, start, prev = [], 0, px[col, 0]
            for r in range(1, self.rows + 1):
                cur = px[col, r] if r < self.rows else None
                if cur != prev:
                    out.append((start / self.rows, r / self.rows, "#%02X%02X%02X" % prev))
                    start, prev = r, cur
            self._cache[col] = out
        return self._cache[col]


@dataclass
class PhotoSkin:
    href: str
    width: int
    height: int


_clip_counter = [0]


def photo_face(defs: list, skin: PhotoSkin, u0: float, u1: float, p_tl, p_tr, p_bl, opacity: float = 1.0) -> str:
    """Maps image columns u0..u1 (pixels) onto the screen parallelogram p_tl, p_tr, p_bl."""
    du = max(u1 - u0, 1e-6)
    a, b = (p_tr[0] - p_tl[0]) / du, (p_tr[1] - p_tl[1]) / du
    c, d = (p_bl[0] - p_tl[0]) / skin.height, (p_bl[1] - p_tl[1]) / skin.height
    e, f = p_tl[0] - a * u0, p_tl[1] - b * u0
    _clip_counter[0] += 1
    cid = f"pc{_clip_counter[0]}"
    defs.append(f'<clipPath id="{cid}"><rect x="{u0 - 0.4:.2f}" y="0" width="{du + 0.8:.2f}" '
                f'height="{skin.height}"/></clipPath>')
    op = f' opacity="{opacity}"' if opacity < 1 else ""
    return (f'<g transform="matrix({a:.5f},{b:.5f},{c:.5f},{d:.5f},{e:.2f},{f:.2f})"{op}>'
            f'<image href="{skin.href}" x="0" y="0" width="{skin.width}" height="{skin.height}" '
            f'preserveAspectRatio="none" clip-path="url(#{cid})"/></g>')


# ---- pleated sheet / toothed ring ------------------------------------------------------------------------
@dataclass
class Pleats:
    """A pleated band: `pleats` V folds over `length` units, `height` tall, standing on y = base.
    bend 0 = flat sheet in the x/y plane facing +z; bend 1 = closed into a toothed ring around the y axis.
    Skins per face set (A = faces seen from the left, B = from the right): a hex colour, a function of the pleat
    index returning a colour, a Picture, or a PhotoSkin."""
    pleats: int
    length: float
    height: float
    base: float = 0.0
    depth_ratio: float = 0.65
    bend: float = 0.0
    spin: float = 0.0                      # degrees, turns a ring about its axis
    centre: tuple = (0.0, 0.0, 0.0)
    skin_a: object = "#F2C94C"
    skin_b: object = "#F4F1E4"
    cap: str | None = None                 # top cap colour for rings
    cap_inner: float = 0.0                 # radius of a hole in the cap (0 = solid)
    back: str = "#E7E3D6"                  # colour of a face seen from behind (open sheets)
    shaded: bool = True
    photo_opacity: float = 1.0
    ridge_out: bool = True
    reveal: object = None                  # callable(i) -> 0..1, A faces drawn from the top down

    def _frame(self, u: float):
        """Base point and outward normal of the band at arc position u (0..length)."""
        cx, cy, cz = self.centre
        if self.bend < 1e-4:
            return (cx + u - self.length / 2, cz), (0.0, 1.0)
        total = 2 * math.pi * self.bend
        radius = self.length / total
        phi = (u / self.length - 0.5) * total + self.spin * DEG
        if self.bend >= 0.999:
            return (cx + radius * math.sin(phi), cz + radius * math.cos(phi)), (math.sin(phi), math.cos(phi))
        # partly bent: the middle of the sheet stays put, the ends curl back
        return ((cx + radius * math.sin(phi), cz + radius * math.cos(phi) - radius),
                (math.sin(phi), math.cos(phi)))

    def points(self):
        p = self.length / self.pleats
        dep = p * self.depth_ratio * (1 if self.ridge_out else -1)
        for i in range(self.pleats):
            u0, um, u1 = i * p, (i + 0.5) * p, (i + 1) * p
            (b0, n0), (bm, nm), (b1, n1) = self._frame(u0), self._frame(um), self._frame(u1)
            ridge = (bm[0] + nm[0] * dep, bm[1] + nm[1] * dep)
            yield i, b0, ridge, b1

    @property
    def radius(self) -> float:
        return self.length / (2 * math.pi * max(self.bend, 1e-4))

    def faces(self):
        """(index, side, left xz, right xz, normal) for every face, normals pointing out of the pleat."""
        for i, b0, r, b1 in self.points():
            for side, pa, pb in (("A", b0, r), ("B", r, b1)):
                tx, tz = pb[0] - pa[0], pb[1] - pa[1]
                ln = math.hypot(tx, tz) or 1.0
                normal = (-tz / ln, 0.0, tx / ln)
                yield i, side, pa, pb, normal

    def draw(self, cam: Camera, defs: list) -> list[tuple[float, str]]:
        items = []
        y0, y1 = self.base + self.centre[1], self.base + self.centre[1] + self.height
        for i, side, pa, pb, normal in self.faces():
            facing = cam.facing(normal)
            tl = cam.project(pa[0], y1, pa[1]); tr = cam.project(pb[0], y1, pb[1])
            bl = cam.project(pa[0], y0, pa[1]); br = cam.project(pb[0], y0, pb[1])
            depth = (tl[2] + tr[2] + bl[2] + br[2]) / 4
            if facing <= 1e-4:
                if self.bend >= 0.999:
                    continue
                items.append((depth, poly([tl[:2], tr[:2], br[:2], bl[:2]], self.back)))
                continue
            skin = self.skin_a if side == "A" else self.skin_b
            if self.reveal is not None and side == "A":
                frac = max(0.0, min(1.0, self.reveal(i)))
                if frac <= 0:
                    continue
                yb = y1 - self.height * frac
                bl = cam.project(pa[0], yb, pa[1]); br = cam.project(pb[0], yb, pb[1])
            items.append((depth, self._skin_face(skin, i, side, normal, tl, tr, bl, br, defs)))
        return items

    def _skin_face(self, skin, i, side, normal, tl, tr, bl, br, defs) -> str:
        quad = [tl[:2], tr[:2], br[:2], bl[:2]]
        if isinstance(skin, PhotoSkin):
            u0 = i / self.pleats * skin.width
            u1 = (i + 1) / self.pleats * skin.width
            if side == "B":
                u0, u1 = u0, u1
            base = poly(quad, "#F4F1E4")
            return base + photo_face(defs, skin, u0, u1, tl[:2], tr[:2], bl[:2], self.photo_opacity)
        if isinstance(skin, Picture):
            out = []
            for v0, v1, colour in skin.runs(i):
                lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
                a, b = lerp(tl, bl, v0), lerp(tr, br, v0)
                c, d = lerp(tr, br, v1), lerp(tl, bl, v1)
                fill = shade(colour, normal) if self.shaded else colour
                out.append(poly([a, b, c, d], fill, ' stroke="%s" stroke-width="0.6"' % fill))
            return "".join(out)
        colour = skin(i) if callable(skin) else skin
        fill = shade(colour, normal) if self.shaded else colour
        return poly(quad, fill, ' stroke="%s" stroke-width="0.6"' % fill)

    def draw_cap(self, cam: Camera) -> str:
        if self.cap is None or self.bend < 0.999:
            return ""
        y = self.base + self.centre[1] + self.height
        outline = []
        for _, b0, r, _b1 in self.points():
            outline += [cam.project(b0[0], y, b0[1])[:2], cam.project(r[0], y, r[1])[:2]]
        out = poly(outline, self.cap)
        if self.cap_inner > 0:
            out += ellipse_xz(cam, self.centre[0], y, self.centre[2], self.cap_inner, mix(self.cap, INK, 0.1))
        return out


def ellipse_xz(cam: Camera, x: float, y: float, z: float, r: float, fill: str, extra: str = "") -> str:
    """A horizontal circle seen by the camera (an ellipse in an orthographic view)."""
    pts = [cam.project(x + r * math.cos(a), y, z + r * math.sin(a))[:2]
           for a in (k * 2 * math.pi / 72 for k in range(72))]
    return poly(pts, fill, extra)


def cylinder(cam: Camera, x: float, y0: float, y1: float, z: float, r: float, side: str, top: str,
             stripes: list[str] | None = None) -> str:
    """Vertical cylinder: front half of the side wall (optionally striped) and the top disc."""
    out = []
    n = 36 if not stripes else len(stripes) * 2
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        normal = (math.sin((a0 + a1) / 2), 0.0, math.cos((a0 + a1) / 2))
        if cam.facing(normal) <= 0:
            continue
        p = [cam.project(x + r * math.sin(a), yy, z + r * math.cos(a))[:2]
             for a, yy in ((a0, y1), (a1, y1), (a1, y0), (a0, y0))]
        colour = stripes[k // 2 % len(stripes)] if stripes and k % 2 == 0 else side
        fill = shade(colour, normal)
        out.append(poly(p, fill, f' stroke="{fill}" stroke-width="0.6"'))
    out.append(ellipse_xz(cam, x, y1, z, r, top))
    return "".join(out)


def flame(cx: float, base: float, h: float, w: float, lean: float = 0.0, glow: bool = False) -> str:
    """Flat three-layer flame, Agam colours, base at (cx, base) on screen."""
    def tear(hh, ww, dy=0.0):
        tip = (cx + lean * hh, base - hh)
        return (f"M{cx:.1f},{base - dy:.1f} C{cx - ww:.1f},{base - dy:.1f} {cx - ww * 0.9:.1f},{base - hh * 0.45:.1f} "
                f"{tip[0]:.1f},{tip[1]:.1f} C{cx + ww * 0.9:.1f},{base - hh * 0.45:.1f} {cx + ww:.1f},{base - dy:.1f} "
                f"{cx:.1f},{base - dy:.1f}Z")
    halo = (f'<circle cx="{cx:.1f}" cy="{base - h * 0.35:.1f}" r="{h * 0.75:.1f}" fill="#F6D21C" opacity="0.16"/>'
            if glow else "")
    return (halo + f'<path d="{tear(h, w / 2)}" fill="#F39A1E"/>'
            f'<path d="{tear(h * 0.66, w * 0.33, h * 0.04)}" fill="#F6D21C"/>'
            f'<path d="{tear(h * 0.3, w * 0.16, h * 0.08)}" fill="#FFF6C8"/>')


def jet(x0: float, y0: float, x1: float, y1: float, colour: str, width: float = 5, dot: float = 9,
        dot_colour: str | None = None, bow: float = 0.0) -> str:
    """A water jet drawn like a letter stroke of the titles: a straight line ending in a dot."""
    mx, my = (x0 + x1) / 2 + bow, (y0 + y1) / 2
    return (f'<path d="M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{y1:.1f}" stroke="{colour}" '
            f'stroke-width="{width}" fill="none" stroke-linecap="butt"/>'
            f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{dot}" fill="{dot_colour or colour}"/>')


def draw_groups(cam: Camera, groups: list, defs: list) -> str:
    """groups: list of objects (Pleats, or str already drawn, or callables(cam, defs) -> str), drawn in order.
    Within a Pleats object faces are depth-sorted back to front; its cap is drawn first."""
    out = []
    for g in groups:
        if isinstance(g, Pleats):
            out.append(g.draw_cap(cam))
            out += [svg for _, svg in sorted(g.draw(cam, defs), key=lambda t: t[0])]
        elif callable(g):
            out.append(g(cam, defs))
        else:
            out.append(g)
    return "".join(out)


def box(cam: Camera, x0, x1, y0, y1, z0, z1, colour: str, top: str | None = None, front: str | None = None) -> str:
    """A flat-shaded box: only faces turned to the camera, back to front, two-value shading."""
    faces = [
        ((0, 1, 0), [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top or mix(colour, "#FFFFFF", 0.18)),
        ((0, -1, 0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], colour),
        ((0, 0, 1), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], front or colour),
        ((0, 0, -1), [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], colour),
        ((1, 0, 0), [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], colour),
        ((-1, 0, 0), [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], colour),
    ]
    out = []
    for normal, pts, fill in faces:
        if cam.facing(normal) <= 1e-6:
            continue
        proj = [cam.project(*p) for p in pts]
        depth = sum(p[2] for p in proj) / 4
        tone = fill if normal[1] == 1 else shade(fill, normal)
        out.append((depth, poly([p[:2] for p in proj], tone, f' stroke="{tone}" stroke-width="0.6"')))
    return "".join(svg for _, svg in sorted(out))


def disc_x(cam: Camera, x: float, y: float, z: float, r: float, fill: str, extra: str = "") -> str:
    """A circle standing in the y/z plane (axis along x): a spool flange seen from the side."""
    pts = [cam.project(x, y + r * math.cos(a), z + r * math.sin(a))[:2]
           for a in (k * 2 * math.pi / 64 for k in range(64))]
    return poly(pts, fill, extra)


def spool_3d(cam: Camera, x: float, y: float, z: float, r: float, width: float) -> str:
    """Spool of white filament on a horizontal axle (along x): back flange, wound filament, front flange."""
    near = 1 if cam.rotate(1, 0, 0)[2] > 0 else -1
    far_x, near_x = x - near * width / 2, x + near * width / 2
    out = [disc_x(cam, far_x, y, z, r, "#9EA4A9")]
    steps = 8
    for k in range(steps + 1):
        xx = far_x + (near_x - far_x) * k / steps
        out.append(disc_x(cam, xx, y, z, r * 0.86, mix("#FBFAF6", INK, 0.06 if k % 2 else 0.0)))
    out.append(disc_x(cam, near_x, y, z, r, "#C9CED0"))
    out.append(disc_x(cam, near_x, y, z, r * 0.86, "none", ' stroke="#B9BEC2" stroke-width="3"'))
    out.append(disc_x(cam, near_x, y, z, r * 0.38, "#9EA4A9"))
    out.append(disc_x(cam, near_x, y, z, r * 0.16, "#2A2D33"))
    return "".join(out)
