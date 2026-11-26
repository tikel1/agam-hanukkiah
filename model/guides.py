"""Very subtle guide relief for taping and painting (user, viewer v4 feedback):

* a fine raised line (GUIDE_LINE_HEIGHT x GUIDE_LINE_WIDTH) along each motif's outline, only on
  the face set that carries the motif, so it cannot give the motif away from the other side;
* a thin locating ring round every cup seat (the washer drops inside it).

The lines follow the exact vector outlines from paint_program.motif_shapes, mapped onto each
pleat face (by angle, the same way the paint is mapped), and stop short of the crest and valley
ridges and of the ring's top and bottom edges.
"""

from __future__ import annotations

import math

from build123d import Cylinder, Face, Part, Plane, Pos, Wire, extrude

import config as cfg
import fountain
import paint_program as program
import profiles

EMBED = 0.2  # mm the guide solids reach into the face so the union bonds


def face_line(ring_name: str, side: str, k: int) -> tuple[tuple[float, float], tuple[float, float]]:
    """Plan points (start, end) of face k of a set, start at the face's u = 0 end."""
    teeth = program.teeth_of(ring_name)
    tip = fountain.drum_diameter(program.drum_by_name(ring_name)) / 2
    root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    pitch = 2 * math.pi / teeth
    tooth = (k + program.front_tooth(teeth)) % teeth
    start, split = tooth * pitch, tooth * pitch + cfg.TOOTH_LEAN * pitch
    if side == "left":
        return (root * math.cos(start), root * math.sin(start)), (tip * math.cos(split), tip * math.sin(split))
    end = start + pitch
    return (tip * math.cos(split), tip * math.sin(split)), (root * math.cos(end), root * math.sin(end))


def along_face(ring_name: str, side: str, k: int, u: float) -> float:
    """Distance (mm) along face k from its start to where the ray at face coordinate u meets it."""
    (ax, ay), (bx, by) = face_line(ring_name, side, k)
    lo, hi = program.face_span(ring_name, side, k)
    world = math.radians(lo + u * (hi - lo) - 90.0)
    dx, dy = bx - ax, by - ay
    ux, uy = math.cos(world), math.sin(world)
    denominator = dx * uy - dy * ux
    t = 0.0 if abs(denominator) < 1e-12 else (ax * uy - ay * ux) / -denominator
    return t * math.hypot(dx, dy)


def outline_bands(ring_name: str, side: str, k: int):
    """Shapely polygons (in face mm: along the face, up) of the guide lines on face k."""
    from shapely import affinity
    from shapely.geometry import LineString, MultiLineString, box
    from shapely.ops import transform, unary_union

    x0, x1 = program.tooth_arc_span(ring_name, k)
    height = fountain.drum_height(program.drum_by_name(ring_name))
    strip = box(x0, -1.0, x1, height + 1.0)
    (ax, ay), (bx, by) = face_line(ring_name, side, k)
    length = math.hypot(bx - ax, by - ay)
    margin = cfg.RIDGE_WIDTH / 2 / math.sin(math.radians(cfg.TOOTH_INCLUDED_ANGLE / 2)) + cfg.GUIDE_LINE_WIDTH
    keep = box(margin, cfg.GUIDE_LINE_WIDTH, length - margin, height - cfg.GUIDE_LINE_WIDTH)
    lines = []
    for geometry, motif in program.motif_outlines(ring_name, side):
        cut = geometry.intersection(strip)
        if cut.is_empty:
            continue
        local = affinity.affine_transform(cut, [1.0 / (x1 - x0), 0, 0, 1, -x0 / (x1 - x0), 0])
        mapped = transform(lambda u, z: (_vector_along(ring_name, side, k, u), z), local)
        lines.append(mapped)
    if not lines:
        return None
    bands = unary_union([line.buffer(cfg.GUIDE_LINE_WIDTH / 2, cap_style="flat") for line in lines]).intersection(keep)
    return None if bands.is_empty else bands


def _vector_along(ring_name: str, side: str, k: int, u):
    try:
        return [along_face(ring_name, side, k, value) for value in u]
    except TypeError:
        return along_face(ring_name, side, k, u)


def polygons_of(geometry) -> list:
    if geometry.geom_type == "Polygon":
        return [geometry]
    return [g for g in getattr(geometry, "geoms", []) if g.geom_type == "Polygon"]


def face_solids(ring_name: str, side: str, k: int) -> list[Part]:
    """The guide lines on one face as thin solids standing GUIDE_LINE_HEIGHT proud of the face."""
    bands = outline_bands(ring_name, side, k)
    if bands is None:
        return []
    (ax, ay), (bx, by) = face_line(ring_name, side, k)
    length = math.hypot(bx - ax, by - ay)
    direction = ((bx - ax) / length, (by - ay) / length, 0.0)
    outward = (direction[1], -direction[0], 0.0) if side == "left" else (direction[1], -direction[0], 0.0)
    z0 = fountain.stack_heights()[ring_name] * 0  # built in print orientation: the ring's bottom is z = 0
    plane = Plane(origin=(ax, ay, z0), x_dir=direction, z_dir=outward).offset(-EMBED)
    solids = []
    for polygon in polygons_of(bands):
        if polygon.area < 0.05:
            continue
        outer = Wire.make_polygon([(x, y, 0) for x, y in list(polygon.exterior.coords)[:-1]], close=True)
        holes = [Wire.make_polygon([(x, y, 0) for x, y in list(hole.coords)[:-1]], close=True) for hole in polygon.interiors]
        face = plane * Face(outer, holes)
        solids.append(extrude(face, amount=cfg.GUIDE_LINE_HEIGHT + EMBED, dir=outward))
    return solids


def motif_guides(ring_name: str) -> list[Part]:
    """Every guide-line solid on a ring (print orientation)."""
    solids = []
    for side in program.SIDES:
        if not getattr(cfg.RING_PAINT[ring_name], side).motifs:
            continue
        for k in range(program.teeth_of(ring_name)):
            solids += face_solids(ring_name, side, k)
    return solids


def seat_ring(x: float, y: float, z: float) -> Part:
    """Thin locating ring round a cup seat: the washer drops inside it."""
    inner = profiles.seat_radius() + cfg.GUIDE_SEAT_CLEARANCE
    ring = Cylinder(inner + cfg.GUIDE_LINE_WIDTH, cfg.GUIDE_LINE_HEIGHT, align=profiles.BOTTOM) - Cylinder(inner, cfg.GUIDE_LINE_HEIGHT, align=profiles.BOTTOM)
    return Pos(x, y, z) * ring
