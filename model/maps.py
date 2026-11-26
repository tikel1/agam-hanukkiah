"""Flat painting maps: every ring unrolled, plus a plan of the top steps, dome and stem.

Each map is one A4 page at 1:1 (mm), written as SVG and PNG to out/maps/. Every pleat face,
pixel cell, top band and emblem zone shows its paint number; a degree scale, tooth numbers
and a FRONT marker run along each strip. Long rings are split into strips that overlap by
MAP_OVERLAP mm, with matching letter marks at the joins.

Usage:  .venv/Scripts/python maps.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle, Wedge  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

import config as cfg  # noqa: E402
import fountain  # noqa: E402
import hanukkiah  # noqa: E402
import paint_program as program  # noqa: E402
import profiles  # noqa: E402

MAP_DIR = cfg.MODEL_DIR / "out" / "maps"
A4 = (210.0, 297.0)
MARGIN = 10.0
MAP_OVERLAP = 10.0
STRIP_GAP = 24.0  # room for the scales between strips
LEGEND_ROOM = 22.0  # mm kept for the colour legend at the foot of a page
SEAM_DEG = cfg.SEAM_DEG  # where each unrolled ring is cut (config; the engraved start arrows sit here)
LABEL_FROM_TOP = 2.6  # mm: stripe numbers sit near the top edge, clear of the emblems
MM_PER_POINT = 25.4 / 72
PNG_DPI = 200
LINE = 0.25 / MM_PER_POINT  # 0.25 mm hairline, in points


def text_size(mm: float) -> float:
    return mm / MM_PER_POINT


def ink_for(paint_name: str) -> str:
    """Black or white label text, whichever reads on the paint."""
    hex_value = program.paint(paint_name).hex.lstrip("#")
    r, g, b = (int(hex_value[i : i + 2], 16) for i in (0, 2, 4))
    return "#111111" if 0.299 * r + 0.587 * g + 0.114 * b > 140 else "#ffffff"


def new_page() -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, A4[0])
    ax.set_ylim(A4[1], 0)  # y grows downward, like the page
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save_page(fig: plt.Figure, stem: str) -> list[Path]:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    paths = [MAP_DIR / f"{stem}.svg", MAP_DIR / f"{stem}.png"]
    fig.savefig(paths[0])
    fig.savefig(paths[1], dpi=PNG_DPI)
    plt.close(fig)
    return paths


def legend(ax: plt.Axes, names: set[str], y: float) -> None:
    used = sorted((program.paint(n) for n in names), key=lambda p: p.number)
    x = MARGIN
    for paint in used:
        ax.add_patch(Rectangle((x, y), 6, 6, facecolor=paint.hex, edgecolor="#333", lw=LINE))
        ax.text(x + 3, y + 3, str(paint.number), ha="center", va="center", fontsize=text_size(2.6), color=ink_for(paint.name))
        ax.text(x + 7.5, y + 3, paint.name, va="center", fontsize=text_size(2.6))
        x += 7.5 + 2.0 * len(paint.name) + 4
        if x > A4[0] - 30:
            x, y = MARGIN, y + 8


def header(ax: plt.Axes, title: str, lines: list[str]) -> float:
    ax.text(MARGIN, MARGIN + 4, title, fontsize=text_size(5.5), weight="bold")
    y = MARGIN + 10
    for line in lines:
        ax.text(MARGIN, y, line, fontsize=text_size(2.7))
        y += 4.2
    return y + 2


# --- Unrolled rings -----------------------------------------------------------------------


class Strip:
    """Maps concept degrees and ring height to page mm for one strip of an unrolled ring."""

    def __init__(self, circumference: float, start: float, width: float, top: float, height: float):
        self.circumference, self.start, self.width, self.top, self.height = circumference, start, width, top, height

    def s(self, degrees: float) -> float:
        """Arc mm from the seam (SEAM_DEG), going counter-clockwise seen from above."""
        return ((degrees - SEAM_DEG) % 360.0) / 360.0 * self.circumference

    def x(self, s: float) -> float:
        return MARGIN + s - self.start

    def y(self, z: float) -> float:
        return self.top + self.height - z

    def spans(self, deg_start: float, deg_end: float) -> list[tuple[float, float]]:
        """Page x ranges of a degree span, split at the seam and clipped to the strip."""
        s0 = self.s(deg_start)
        length = (deg_end - deg_start) / 360.0 * self.circumference
        pieces = [(s0, s0 + length)] if s0 + length <= self.circumference else [(s0, self.circumference), (0.0, s0 + length - self.circumference)]
        out = []
        for a, b in pieces:
            a, b = max(a, self.start), min(b, self.start + self.width)
            if b > a:
                out.append((self.x(a), self.x(b)))
        return out


def strip_starts(circumference: float) -> list[float]:
    usable = A4[0] - 2 * MARGIN
    starts, start = [], 0.0
    while True:
        starts.append(start)
        if start + usable >= circumference:
            return starts
        start += usable - MAP_OVERLAP


SIDE_LABEL = {"left": "A: LEFT faces", "right": "B: RIGHT faces"}


def runs(values: tuple) -> list[tuple[int, int, object]]:
    """(first, last + 1, value) for each run of equal values."""
    out, first = [], 0
    for index in range(1, len(values) + 1):
        if index == len(values) or values[index] != values[first]:
            out.append((first, index, values[first]))
            first = index
    return out


def shapely_patches(geometry, to_page) -> list:
    """Matplotlib patches (holes kept) for a shapely (multi)polygon, mapped by to_page(x, z)."""
    polygons = [geometry] if geometry.geom_type == "Polygon" else list(getattr(geometry, "geoms", []))
    patches = []
    for polygon in polygons:
        if polygon.geom_type != "Polygon" or polygon.is_empty:
            continue
        vertices, codes = [], []
        for number, ring in enumerate([polygon.exterior] + list(polygon.interiors)):
            points = [to_page(x, z) for x, z in ring.coords]
            area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
            if (area > 0) == (number == 0):
                points = points[::-1]
            vertices += points
            codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(points) - 2) + [MplPath.CLOSEPOLY]
        patches.append(MplPath(vertices, codes))
    return patches


def draw_face_set(ax: plt.Axes, strip: Strip, ring_name: str, side: str) -> set[str]:
    """One face set as its own picture: each face drawn the full tooth wide (the ground), then the
    motifs as exact vector shapes, so the map shows the picture as it is seen from that side."""
    used = set()
    table = program.face_table(ring_name)[side]
    teeth = program.teeth_of(ring_name)
    pitch = 360.0 / teeth
    shapes = program.motif_shapes(ring_name, side)
    for k in range(teeth):
        start = program.tooth_start(ring_name, k)
        name = table[k]
        if strip.spans(start, start + pitch):
            used.add(name)
        x_span = program.tooth_arc_span(ring_name, k)
        covered = sum(geometry.intersection(box_strip(x_span, strip.height)).area for geometry, _ in shapes)
        for x0, x1 in strip.spans(start, start + pitch):
            ax.add_patch(Rectangle((x0, strip.top), x1 - x0, strip.height, facecolor=program.paint(name).hex, edgecolor="none"))
            if covered < 0.3 * (x_span[1] - x_span[0]) * strip.height:
                ax.text((x0 + x1) / 2, strip.y(strip.height - LABEL_FROM_TOP), str(program.paint(name).number), ha="center", va="center", fontsize=text_size(2.0), color=ink_for(name))
    tip = strip.circumference / (2 * math.pi)
    for geometry, ink in shapes:
        if geometry.bounds[2] > -1e9:
            used.add(ink)

        def to_page(x: float, z: float) -> tuple[float, float]:  # unrolled x is arc mm from the front
            return strip.x(strip.s(math.degrees(x / tip))), strip.y(z)

        for path in shapely_patches(geometry, to_page):
            patch = ax.add_patch(PathPatch(path, facecolor=program.paint(ink).hex, edgecolor="none"))
            patch.set_clip_path(Rectangle((MARGIN, strip.top), strip.width, strip.height, transform=ax.transData))
    for k in range(teeth):
        start = program.tooth_start(ring_name, k)
        for x0, _ in strip.spans(start, start + pitch):
            ax.plot([x0, x0], [strip.top, strip.top + strip.height], color="#666", lw=LINE)
    return used


def box_strip(x_span: tuple[float, float], height: float):
    from shapely.geometry import box

    return box(x_span[0], 0.0, x_span[1], height)


def draw_motif_labels(ax: plt.Axes, strip: Strip, ring_name: str, side: str) -> None:
    """A bold number on each motif, so the picture's shapes read on the map."""
    for motif in getattr(cfg.RING_PAINT[ring_name], side).motifs:
        if motif.shape == "band":  # the ground under a motif: its colour shows in the map, no label
            continue
        s = strip.s(motif.centre_deg)
        if strip.start + 4 < s < strip.start + strip.width - 4:
            name = motif.inks[0]
            ax.text(strip.x(s), strip.top - 11.5, f"{motif.shape.replace('_', ' ')}: {program.paint(name).number} {name}", ha="center", fontsize=text_size(2.4), weight="bold")


def draw_scales(ax: plt.Axes, strip: Strip, ring_name: str, index: int, count: int, has_start_arrow: bool = True) -> None:
    top, bottom = strip.top, strip.top + strip.height
    for degrees in range(0, 360, 15):
        s = strip.s(degrees)
        if strip.start <= s <= strip.start + strip.width:
            x = strip.x(s)
            ax.plot([x, x], [top - 2.5, top], color="#222", lw=LINE * 2)
            ax.text(x, top - 3.2, f"{degrees}°", ha="center", fontsize=text_size(2.2))
    front = strip.s(0.0)
    if strip.start <= front <= strip.start + strip.width:
        x = strip.x(front)
        ax.add_patch(Polygon([(x - 2.5, top - 9.5), (x + 2.5, top - 9.5), (x, top - 6.5)], color="#c2283f"))
        ax.text(x + 3.5, top - 8, "FRONT", fontsize=text_size(2.6), color="#c2283f", weight="bold", va="center")
    if index == 0 and has_start_arrow and cfg.START_ARROWS_ENABLED:  # the map starts at the engraved start arrow
        x = strip.x(strip.start)
        ax.add_patch(Polygon([(x, bottom + 7.5), (x + 6, bottom + 9.5), (x, bottom + 11.5)], color="#c2283f"))
        ax.text(x + 7.5, bottom + 9.5, "START: engraved arrow on the ring's top and bottom (tail here, points this way)",
                fontsize=text_size(2.2), color="#c2283f", weight="bold", va="center")
    teeth = program.teeth_of(ring_name)
    for k in range(0, teeth, 5):
        for x0, x1 in strip.spans(*program.face_span(ring_name, "left", k)):
            ax.text(x0, bottom + 3.0, f"t{k}", fontsize=text_size(1.9), color="#444")
    marks = "ABCDEFGH"
    if index > 0:
        ax.add_patch(Rectangle((MARGIN, top), MAP_OVERLAP, strip.height, facecolor="none", edgecolor="#000", lw=LINE * 3, ls="--"))
        ax.text(MARGIN + 1, bottom + 6.5, f"◀ overlap {marks[index - 1]}", fontsize=text_size(2.2))
    if index < count - 1:
        x = strip.x(strip.start + strip.width)
        ax.add_patch(Rectangle((x - MAP_OVERLAP, top), MAP_OVERLAP, strip.height, facecolor="none", edgecolor="#000", lw=LINE * 3, ls="--"))
        ax.text(x - MAP_OVERLAP, bottom + 6.5, f"overlap {marks[index]} ▶", fontsize=text_size(2.2))


def ring_map(ring_name: str, side: str, stem: str | None = None, title_note: str = "") -> list[Path]:
    """One face set unrolled; strips continue on a second page when the ring is too tall."""
    drum = program.drum_by_name(ring_name)
    tip = fountain.drum_diameter(drum) / 2
    height = fountain.drum_height(drum)
    circumference = 2 * math.pi * tip
    starts = strip_starts(circumference)
    teeth = program.teeth_of(ring_name)
    label = ring_name.split("_")[1]
    other = "RIGHT" if side == "left" else "LEFT"
    usable = A4[0] - 2 * MARGIN
    pitch_y = height + STRIP_GAP + 4
    stem = stem or f"map_{label}_{'A_left' if side == 'left' else 'B_right'}"
    if title_note:
        label = f"{label} ({title_note})"
    written, index, page = [], 0, 1
    while index < len(starts):
        fig, ax = new_page()
        y = header(ax, f"{label}, picture {SIDE_LABEL[side]} (unrolled, 1:1 at the tooth tips)" + (f", page {page}" if page > 1 else ""), [
            f"Ø {2 * tip:.0f} mm, {height:.1f} mm tall, {teeth} teeth, cut open at {SEAM_DEG:g}°. Paint this picture on the {side.upper()} face of every tooth",
            f"(the face turned to your {side} as you face the ring). Each grey line is one tooth: its {side} face carries that slice.",
            f"Leave the {other} faces for the other map. Numbers = paint numbers. Strips overlap by {MAP_OVERLAP:.0f} mm (dashed boxes, same letter).",
        ])
        fits = max(1, int((A4[1] - MARGIN - LEGEND_ROOM - (y + 16)) // pitch_y))
        used, row = set(), 0
        for index in range(index, min(len(starts), index + fits)):
            top = y + 16 + row * pitch_y
            start = starts[index]
            strip = Strip(circumference, start, min(usable, circumference - start), top, height)
            used |= draw_face_set(ax, strip, ring_name, side)
            draw_scales(ax, strip, ring_name, index, len(starts))
            draw_motif_labels(ax, strip, ring_name, side)
            ax.add_patch(Rectangle((MARGIN, top), strip.width, height, facecolor="none", edgecolor="#000", lw=LINE * 2))
            row += 1
        index += 1
        legend(ax, used, y + 16 + row * pitch_y)
        written += save_page(fig, stem if page == 1 else f"{stem}_page{page}")
        page += 1
    return written


def coupon_map(spec=None) -> list[Path]:
    """Both pictures of a test coupon (an arc of R3), A above B, at 1:1."""
    import coupon

    spec = spec or coupon.MAIN
    ring_name = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name
    drum = program.drum_by_name(ring_name)
    tip, height = fountain.drum_diameter(drum) / 2, fountain.drum_height(drum)
    circumference = 2 * math.pi * tip
    lo, hi = coupon.coupon_range(spec)
    probe = Strip(circumference, 0.0, circumference, 0.0, height)
    start, width = probe.s(lo), (hi - lo) / 360.0 * circumference
    fig, ax = new_page()
    y = header(ax, f"{spec.name} (R3 arc): painting map, both pictures, 1:1", [
        f"The coupon is R3 from {lo:g}° to {hi:g}°. Paint picture A on the LEFT face of every tooth, then picture B on the RIGHT faces.",
        "The fine raised lines on the print follow the motif edges (tape along them). The small ring on top centres the washer.",
        spec.check,
    ])
    used = set()
    for row, side in enumerate(program.SIDES):
        top = y + 22 + row * (height + STRIP_GAP + 14)
        ax.text(MARGIN, top - 14, f"Picture {SIDE_LABEL[side]}", fontsize=text_size(3.2), weight="bold")
        strip = Strip(circumference, start, width, top, height)
        used |= draw_face_set(ax, strip, ring_name, side)
        draw_scales(ax, strip, ring_name, 0, 1, has_start_arrow=False)  # coupons are cut away from the seam
        ax.add_patch(Rectangle((MARGIN, top), width, height, facecolor="none", edgecolor="#000", lw=LINE * 2))
    legend(ax, used, y + 22 + 2 * (height + STRIP_GAP + 14))
    return save_page(fig, f"map_{spec.name}")


# --- Top steps, dome, stem -----------------------------------------------------------------


def annulus(ax: plt.Axes, center: tuple[float, float], r0: float, r1: float, name: str, label_deg: float) -> None:
    ax.add_patch(Wedge(center, r1, 0, 360, width=r1 - r0, facecolor=program.paint(name).hex, edgecolor="#333", lw=LINE))
    mid = (r0 + r1) / 2
    x = center[0] + mid * math.cos(math.radians(label_deg))
    y = center[1] + mid * math.sin(math.radians(label_deg))
    ax.text(x, y, str(program.paint(name).number), ha="center", va="center", fontsize=text_size(2.6), color=ink_for(name), weight="bold")


def plan_point(center: tuple[float, float], radius: float, concept_deg: float) -> tuple[float, float]:
    """Plan view seen from above with the front at the bottom of the page."""
    world = math.radians(-90 + concept_deg)
    return center[0] + radius * math.cos(world), center[1] - radius * math.sin(world)


def draw_plan(ax: plt.Axes, center: tuple[float, float]) -> set[str]:
    """Every top face stays white: show the steps, the washer seats and the stud holes only."""
    names = [d.name for d in cfg.DRUMS]
    for name in names[2:]:
        tip = fountain.drum_diameter(program.drum_by_name(name)) / 2
        ax.add_patch(Circle(center, tip, facecolor=program.paint("bare").hex, edgecolor="#333", lw=LINE * 2))
    spots = [(x, y) for x, y in hanukkiah.candle_positions()] + [(0.0, 0.0)]
    for x, y in spots:
        hole = (center[0] + x, center[1] - y)
        ax.add_patch(Circle(hole, profiles.seat_radius(), facecolor="none", edgecolor="#777", lw=LINE, ls="--"))
        ax.add_patch(Circle(hole, cfg.STUD_HOLE_D / 2, facecolor="#ffffff", edgecolor="#000", lw=LINE * 2))
    ax.text(center[0], center[1] + 40, "all top faces: leave WHITE (unpainted)", ha="center", fontsize=text_size(3.2), weight="bold")
    return {"bare"}


def draw_plan_scale(ax: plt.Axes, center: tuple[float, float], radius: float) -> None:
    for degrees in range(0, 360, 15):
        inner, outer = plan_point(center, radius + 1, degrees), plan_point(center, radius + 3.5, degrees)
        ax.plot([inner[0], outer[0]], [inner[1], outer[1]], color="#222", lw=LINE * 2)
        if degrees % 45 == 0:
            tx, ty = plan_point(center, radius + 7, degrees)
            ax.text(tx, ty, f"{degrees}°", ha="center", va="center", fontsize=text_size(2.4))
    fx, fy = plan_point(center, radius + 12, 0)
    ax.text(fx, fy, "▼ FRONT", ha="center", va="center", fontsize=text_size(3), color="#c2283f", weight="bold")


def draw_stem(ax: plt.Axes, top: float) -> set[str]:
    radius, height = fountain.stem_radius(), fountain.stem_height()
    ax.text(MARGIN, top, f"Foot stem (Ø {2 * radius:.0f}, {height:.1f} mm tall): {program.paint(cfg.STEM_PAINT).number} {cfg.STEM_PAINT}, like the fountain's steel stem.", fontsize=text_size(2.6))
    ax.text(MARGIN, top + 5, f"Foot rim: {program.paint(cfg.PLINTH_PAINT).number} {cfg.PLINTH_PAINT} (the fountain's blue pool); its top stays white.", fontsize=text_size(2.6))
    return {cfg.PLINTH_PAINT, cfg.STEM_PAINT}


def tops_map() -> list[Path]:
    fig, ax = new_page()
    y = header(ax, "Top view and stem: painting map (plan from above, 1:1)", [
        "Every top face (R3, R4, R5 steps and the plinth top) stays white, unpainted. Only the pleated sides get colour.",
        "Dashed circles: where each washer sits (8 on R3, the shamash on R5's centre). Dots = stud holes.",
    ])
    radius = fountain.drum_diameter(cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]) / 2
    center = (A4[0] / 2, y + radius + 10)
    used = draw_plan(ax, center)
    draw_plan_scale(ax, center, radius)
    stem_top = center[1] + radius + 26
    used |= draw_stem(ax, stem_top)
    legend(ax, used, stem_top + fountain.stem_height() + 8)
    return save_page(fig, "map_tops_stem")


# --- Checks and entry point ------------------------------------------------------------------


def narrow_zones() -> list[str]:
    """Pleat faces narrower than MIN_ZONE_WIDTH (motif edges are exact curves, painted by eye)."""
    problems = []
    depth = cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    for ring_name in cfg.RING_PAINT:
        tip = fountain.drum_diameter(program.drum_by_name(ring_name)) / 2
        face = math.hypot(tip * (2 * math.pi / program.teeth_of(ring_name)) * cfg.TOOTH_LEAN, depth) - cfg.RIDGE_WIDTH
        if face < cfg.MIN_ZONE_WIDTH:
            problems.append(f"{ring_name}: pleat face {face:.2f} mm")
    return problems


def write_all() -> list[Path]:
    import coupon

    problems = program.validate() + narrow_zones()
    for problem in problems:
        print(f"  colour program warning: {problem}")
    written = []
    for stale in list(MAP_DIR.glob("map_R[0-9].*")) + list(MAP_DIR.glob("map_R*_page*.*")):  # older layouts
        stale.unlink()
    for drum in cfg.DRUMS:
        for side in program.SIDES:
            written += ring_map(drum.name, side)
    written += tops_map()
    for spec in coupon.COUPONS:
        written += coupon_map(spec)
    return written


if __name__ == "__main__":
    for path in write_all():
        print(f"  map {path.relative_to(cfg.MODEL_DIR)}")
