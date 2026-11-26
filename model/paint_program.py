"""The colour program (config RING_PAINT and friends) turned into paint names.

One source for every consumer:
* `face_table()` gives the ground paint of every pleat face, and `motif_shapes()` /
  `face_regions()` the motifs as exact vector shapes (no pixels): each face carries one tooth's
  slice of its picture, clipped along the true outline (used by the maps and the guide),
* `cell_paints()` gives the paint of every triangle of an assembled mesh (used by the renders
  and the GLB export).

Pleat faces are numbered per ring from the front (concept angle 0) going counter-clockwise
seen from above, which is left to right for someone facing the ring. Tooth k has a `left`
face (turned to your left) and then a `right` face.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

import config as cfg
import fountain

SIDES = ("left", "right")
PAINT_BY_NAME = {paint.name: paint for paint in cfg.PAINTS}


def paint(name: str) -> cfg.Paint:
    if name not in PAINT_BY_NAME:
        raise KeyError(f"Unknown paint {name!r} in the colour program; known: {sorted(PAINT_BY_NAME)}")
    return PAINT_BY_NAME[name]


def drum_by_name(ring_name: str) -> cfg.Drum:
    return next(drum for drum in cfg.DRUMS if drum.name == ring_name)


# --- Ring geometry, as the pleats are built in profiles.py --------------------------------


def teeth_of(ring_name: str) -> int:
    import profiles

    return profiles.tooth_count(fountain.drum_diameter(drum_by_name(ring_name)))


def front_tooth(teeth: int) -> int:
    """Index of the tooth (as built, tooth 0 starts at world +X) that holds concept angle 0."""
    pitch = 2 * math.pi / teeth
    return int(math.floor((math.radians(-90) % (2 * math.pi)) / pitch))


def concept_angle(world_radians: np.ndarray | float) -> np.ndarray | float:
    """World angle (from +X, CCW) to concept degrees (0 = front, CCW seen from above)."""
    return (np.degrees(world_radians) + 90.0) % 360.0


def face_span(ring_name: str, side: str, k: int) -> tuple[float, float]:
    """Concept-angle span (degrees, start < end, may exceed 360) of face k on one side."""
    teeth = teeth_of(ring_name)
    pitch = 360.0 / teeth
    tooth = (k + front_tooth(teeth)) % teeth
    start_world = tooth * pitch
    split = start_world + cfg.TOOTH_LEAN * pitch
    lo, hi = (start_world, split) if side == "left" else (split, start_world + pitch)
    start = (lo + 90.0) % 360.0
    return start, start + (hi - lo)


# --- Programs ---------------------------------------------------------------------------


def stripe_colour(stripes: cfg.Stripes, k: int) -> str:
    colour = stripes.colours[((k + stripes.offset) // stripes.run) % len(stripes.colours)]
    return cfg.COMPLEMENT[colour] if stripes.complement else colour


def tooth_start(ring_name: str, k: int) -> float:
    """Concept angle where tooth k (counted from the front) begins."""
    return face_span(ring_name, "left", k)[0]


def ground_colour(ground: cfg.Stripes | cfg.Sectors, ring_name: str, k: int) -> str:
    if isinstance(ground, cfg.Stripes):
        return stripe_colour(ground, k)
    pitch = 360.0 / teeth_of(ring_name)
    offset = (tooth_start(ring_name, k) + pitch / 2 - ground.start_deg) % 360.0
    begin = 0.0
    for number, sector in enumerate(ground.sectors):
        last = number == len(ground.sectors) - 1
        if offset < begin + sector.span_deg or last:
            return stripe_colour(sector.stripes, int((offset - begin) // pitch))
        begin += sector.span_deg
    raise ValueError(f"{ring_name}: empty Sectors")


def has_motifs(ring_name: str) -> bool:
    ring = cfg.RING_PAINT[ring_name]
    return bool(ring.left.motifs or ring.right.motifs)


def arc_of(ring_name: str, concept_deg: float) -> float:
    """Arc length (mm, at the tooth tips) from the front, in -L/2 .. L/2."""
    tip = fountain.drum_diameter(drum_by_name(ring_name)) / 2
    return ((concept_deg + 180.0) % 360.0 - 180.0) * math.pi / 180.0 * tip


def sketch_to_shapely(sketch, transform):
    """A build123d sketch as a shapely (Multi)Polygon, each point mapped by transform(x, y)."""
    from shapely.geometry import Polygon as ShapelyPolygon
    from shapely.ops import unary_union

    steps = [i / cfg.MOTIF_CURVE_POINTS for i in range(cfg.MOTIF_CURVE_POINTS + 1)]

    def ring(wire):
        return [transform(p.X, p.Y) for p in wire.positions(steps)]

    return unary_union([ShapelyPolygon(ring(face.outer_wire()), [ring(hole) for hole in face.inner_wires()]).buffer(0) for face in sketch.faces()])


COLUMN_OVERLAP = 0.02  # mm: a column's edges sit just past its tooth's edges, never on them (GEOS overlay
# fails on exactly coincident edges); far too small to see on the ring or the maps


def column_layout(ring_name: str, motif) -> tuple[float, tuple]:
    """(concept angle where the first column's tooth starts, the columns) of a "columns" motif:
    centred on the motif's angle and snapped to tooth edges."""
    import column_letters

    columns = column_letters.word_columns(motif.text)
    pitch = 360.0 / teeth_of(ring_name)
    phase = tooth_start(ring_name, 0) % pitch
    return round((motif.centre_deg - len(columns) * pitch / 2 - phase) / pitch) * pitch + phase, columns


def column_word(ring_name: str, motif, height: float):
    """A "columns" motif as one shapely geometry, unrolled: each column exactly one tooth of the picture,
    centred on the motif's angle and snapped to tooth edges."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    start, columns = column_layout(ring_name, motif)
    pitch = 360.0 / teeth_of(ring_name)
    tip = fountain.drum_diameter(drum_by_name(ring_name)) / 2
    arc = lambda degrees: math.radians(degrees) * tip  # noqa: E731  (unrolled x, not wrapped)
    cap = height * motif.height_fraction
    foot = (height - cap) / 2
    pieces = []
    for k, column in enumerate(columns):
        left, right = arc(start + k * pitch) - COLUMN_OVERLAP, arc(start + (k + 1) * pitch) + COLUMN_OVERLAP
        for bottom_left, top_left, bottom_right, top_right in column:
            z = lambda fraction: foot + fraction * cap  # noqa: E731
            pieces.append(Polygon([(left, z(bottom_left)), (right, z(bottom_right)), (right, z(top_right)), (left, z(top_left))]))
    return unary_union(pieces)


def face_pitch(ring_name: str) -> float:
    """One tooth face in the unrolled picture, mm at the tooth tip."""
    return 2 * math.pi * (fountain.drum_diameter(drum_by_name(ring_name)) / 2) / teeth_of(ring_name)


def grid_stretch(ring_name: str, motif, motif_height: float) -> float:
    """The motif's horizontal stretch, snapped so its corners fall on ridges (user: shapes cross whole
    faces). A Magen David's corners sit at 0, 1, 2 and 3 steps of R/(2*sqrt 3) from its centre, so one
    step becomes one face and the true star needs no faceting. A disc spans DISC_HALF_FACES faces each
    side, so its sides close to a point on a ridge. Other motifs keep their configured stretch."""
    radius = motif_height / 2
    if motif.shape == "star":
        return face_pitch(ring_name) * 2 * math.sqrt(3) / radius
    if motif.shape in ("disc", "sufganiyah"):
        return face_pitch(ring_name) * cfg.DISC_HALF_FACES / radius
    return motif.stretch


def faceted(ring_name: str, geometry, motif_height: float):
    """A motif zone rebuilt on this ring's tooth grid: each piece spans its whole face (facets.py)."""
    import facets

    tip = fountain.drum_diameter(drum_by_name(ring_name)) / 2
    return facets.facet(geometry, math.radians(tooth_start(ring_name, 0)) * tip, face_pitch(ring_name), motif_height)


@lru_cache(maxsize=None)
def motif_shapes(ring_name: str, side: str) -> tuple:
    """((shapely geometry in unrolled (x mm from the front, z mm from the bottom of the ring),
    ink), ...) for one face set, later entries painting over earlier ones. Exact vector outlines."""
    from shapely import affinity

    import emblems

    height = fountain.drum_height(drum_by_name(ring_name))
    circumference = math.pi * fountain.drum_diameter(drum_by_name(ring_name))
    shapes = []
    for motif in getattr(cfg.RING_PAINT[ring_name], side).motifs:
        centre = arc_of(ring_name, motif.centre_deg)
        if motif.shape == "band":
            from shapely.geometry import box

            half = math.radians(motif.width_deg) / 2 * circumference / (2 * math.pi)
            shapes.append((box(centre - half, -1.0, centre + half, height + 1.0), motif.inks[0]))
            continue
        if motif.shape == "columns":
            shapes.append((column_word(ring_name, motif, height), motif.inks[0]))
            continue
        for zone, ink in emblems.motif_zones(motif, height * motif.height_fraction):
            stretch = grid_stretch(ring_name, motif, height * motif.height_fraction)
            geometry = sketch_to_shapely(zone, lambda x, y, c=centre, s=stretch: (c + x * s, height / 2 + y))
            geometry = faceted(ring_name, geometry, height * motif.height_fraction)
            for shift in (-circumference, 0.0, circumference):  # a motif may cross the back seam
                moved = affinity.translate(geometry, xoff=shift)
                if abs(moved.centroid.x) < circumference:
                    shapes.append((moved, ink))
    return tuple(shapes)


@lru_cache(maxsize=None)
def motif_outlines(ring_name: str, side: str) -> tuple:
    """((shapely line geometry: the outline of each motif zone, unrolled), motif) for the guide
    relief. Ground bands are not motifs and get no outline."""
    from shapely.geometry import box

    height = fountain.drum_height(drum_by_name(ring_name))
    motifs = [m for m in getattr(cfg.RING_PAINT[ring_name], side).motifs if m.shape != "band"]
    out = []
    for geometry, ink in motif_shapes(ring_name, side):
        if geometry.geom_type == "Polygon" and geometry.equals(box(*geometry.bounds)) and geometry.bounds[1] < 0:
            continue  # a full-height band
        out.append((geometry.boundary, ink))
    del motifs, height
    return tuple(out)


def tooth_arc_span(ring_name: str, k: int) -> tuple[float, float]:
    """Unrolled x span (mm) of tooth k: each face of a set carries this slice of its picture."""
    tip = fountain.drum_diameter(drum_by_name(ring_name)) / 2
    start = arc_of(ring_name, tooth_start(ring_name, k))
    return start, start + 2 * math.pi * tip / teeth_of(ring_name)


@lru_cache(maxsize=None)
def face_regions(ring_name: str, side: str, k: int) -> tuple:
    """((shapely polygon in face coordinates (u 0..1 across the face, z mm), ink), ...) for the
    motif pieces on face k of a set, clipped exactly to the face. The ground fills the rest."""
    from shapely import affinity
    from shapely.geometry import box

    x0, x1 = tooth_arc_span(ring_name, k)
    strip = box(x0, -1.0, x1, fountain.drum_height(drum_by_name(ring_name)) + 1.0)
    regions = []
    for geometry, ink in motif_shapes(ring_name, side):
        piece = geometry.intersection(strip)
        if not piece.is_empty and piece.area > 1e-4:
            regions.append((affinity.affine_transform(piece, [1.0 / (x1 - x0), 0, 0, 1, -x0 / (x1 - x0), 0]), ink))
    return tuple(regions)


@lru_cache(maxsize=None)
def face_table(ring_name: str) -> dict[str, tuple[str, ...]]:
    """side -> face k (from the front) -> ground paint (motifs: face_regions / motif_shapes)."""
    teeth = teeth_of(ring_name)
    return {
        side: tuple(ground_colour(getattr(cfg.RING_PAINT[ring_name], side).ground, ring_name, k) for k in range(teeth))
        for side in SIDES
    }


def column_problems() -> list[str]:
    """Face-column words: bands inside the cap, and the config span (WORD_SPAN_DEG) equal to the real one."""
    import column_letters

    problems = column_letters.check_bands()
    for ring_name in cfg.RING_PAINT:
        for side in SIDES:
            for motif in getattr(cfg.RING_PAINT[ring_name], side).motifs:
                if motif.shape != "columns":
                    continue
                span = len(column_letters.word_columns(motif.text)) * 360.0 / teeth_of(ring_name)
                if abs(span - cfg.WORD_SPAN_DEG) > 1e-6:
                    problems.append(f"{ring_name} {side}: {motif.text} spans {span:g} deg, WORD_SPAN_DEG says {cfg.WORD_SPAN_DEG:g}")
    return problems


def validate() -> list[str]:
    """Problems in the colour program (unknown paints). Empty list = fine."""
    problems = []
    for ring_name in cfg.RING_PAINT:
        for side in SIDES:
            names = set(face_table(ring_name)[side]) | {ink for _, ink in motif_shapes(ring_name, side)}
            problems += [f"{ring_name} {side}: unknown paint {name!r}" for name in names if name not in PAINT_BY_NAME]
    problems += column_problems()
    for name in (cfg.PLINTH_PAINT, cfg.STEM_PAINT):
        if name not in PAINT_BY_NAME:
            problems.append(f"unknown paint {name!r}")
    return problems
