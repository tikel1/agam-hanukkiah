"""2D/3D building blocks shared by every part: pleated outlines, keyed D shapes, sockets."""

from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Part, Polygon, Pos, Rot, extrude

import config as cfg

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def tooth_count(tip_diameter: float, pitch: float = cfg.TOOTH_PITCH) -> int:
    """Teeth round a ring. The candle ring's count is rounded to a multiple of CANDLE_COUNT, so
    every cup can sit over a tooth tip (CANDLE_ON_TOOTH_TIP)."""
    count = max(6, round(math.pi * tip_diameter / pitch))
    candle_ring = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].diameter_ratio * cfg.MAIN_DIAMETER
    if cfg.CANDLE_ON_TOOTH_TIP and abs(tip_diameter - candle_ring) < 1e-6:
        count = cfg.CANDLE_COUNT * max(1, round(count / cfg.CANDLE_COUNT))
    return count


def sawtooth_points(
    tip_radius: float,
    teeth: int,
    depth: float,
    lean: float = cfg.TOOTH_LEAN,
    tip_flat: float = cfg.TOOTH_TIP_FLAT,
) -> list[tuple[float, float]]:
    """Plan outline of a pleated drum: `teeth` V teeth around a circle, tips slightly blunted."""
    root_radius = tip_radius - depth
    pitch = 2 * math.pi / teeth
    half_flat = (tip_flat / tip_radius) / 2
    points = []
    for index in range(teeth):
        start = index * pitch
        tip = start + lean * pitch
        for radius, angle in ((root_radius, start), (tip_radius, tip - half_flat), (tip_radius, tip + half_flat)):
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _toward(a: tuple[float, float], b: tuple[float, float], distance: float) -> tuple[float, float]:
    length = math.dist(a, b)
    return (a[0] + (b[0] - a[0]) * distance / length, a[1] + (b[1] - a[1]) * distance / length)


def _outward(point: tuple[float, float], angle: float, amount: float) -> tuple[float, float]:
    return (point[0] + amount * math.cos(angle), point[1] + amount * math.sin(angle))


def _corner_ridge(prev_pt, corner, next_pt, angle: float, width: float, height: float) -> list[tuple[float, float]]:
    """Replace a V corner by a ridge `width` wide standing `height` proud of both faces."""
    v1 = (prev_pt[0] - corner[0], prev_pt[1] - corner[1])
    v2 = (next_pt[0] - corner[0], next_pt[1] - corner[1])
    cos_apex = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
    half_apex = math.acos(max(-1.0, min(1.0, cos_apex))) / 2
    along = (width / 2) / math.sin(half_apex)
    lift = height / math.sin(half_apex)
    a = _toward(corner, prev_pt, along)
    b = _toward(corner, next_pt, along)
    return [a, _outward(a, angle, lift), _outward(b, angle, lift), b]


def ridged_sawtooth_points(
    tip_radius: float,
    teeth: int,
    depth: float,
    lean: float = cfg.TOOTH_LEAN,
    ridge_width: float = cfg.RIDGE_WIDTH,
    ridge_height: float = cfg.RIDGE_HEIGHT,
    rotation: float = 0.0,
    crest: bool = True,
    root: bool = True,
) -> list[tuple[float, float]]:
    """Pleated outline with a paint-dam ridge along every crest and every valley, so each
    face is its own colouring zone (concept: ridges ~0.8 wide, ~0.6 high)."""
    root_radius = tip_radius - depth
    pitch = 2 * math.pi / teeth
    roots = [(root_radius * math.cos(rotation + i * pitch), root_radius * math.sin(rotation + i * pitch)) for i in range(teeth)]
    tip_angles = [rotation + (i + lean) * pitch for i in range(teeth)]
    tips = [(tip_radius * math.cos(a), tip_radius * math.sin(a)) for a in tip_angles]
    points = []
    for i in range(teeth):
        prev_tip = tips[i - 1]
        if root:
            points += _corner_ridge(prev_tip, roots[i], tips[i], rotation + i * pitch, ridge_width, ridge_height)
        else:
            points.append(roots[i])
        next_root = roots[(i + 1) % teeth]
        if crest:
            points += _corner_ridge(roots[i], tips[i], next_root, tip_angles[i], ridge_width, ridge_height)
        else:
            points.append(tips[i])
    return points


def top_lip(outline: Polygon, tip_radius: float, teeth: int, depth: float, height: float, z: float, width: float = cfg.RIDGE_WIDTH) -> Part:
    """Raised lip along the outer edge of a drum's top face (dam between side stripes and the top).
    The inner edge is the same saw-tooth moved inward so the lip is `width` wide on every face."""
    tangential = tip_radius * (2 * math.pi / teeth) * cfg.TOOTH_LEAN
    half_apex = math.atan2(tangential, depth)
    inner = Polygon(*sawtooth_points(tip_radius - width / math.sin(half_apex), teeth, depth, cfg.TOOTH_LEAN, 0.0), align=None)
    return Pos(0, 0, z) * extrude(outline - inner, amount=height)


def pleated_prism(
    tip_diameter: float,
    height: float,
    relief: bool = True,
    lip_height: float | None = None,
) -> Part:
    """Pleated ring. relief=True adds paint-dam ridges on every crest and valley; lip_height
    adds a lip along the top edge (only where the top face is exposed)."""
    teeth = tooth_count(tip_diameter)
    depth = cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    if not relief:
        outline = Polygon(*sawtooth_points(tip_diameter / 2, teeth, depth), align=None)
        return extrude(outline, amount=height)
    outline = Polygon(*ridged_sawtooth_points(tip_diameter / 2, teeth, depth), align=None)
    body = extrude(outline, amount=height)
    if lip_height:
        body = body + top_lip(outline, tip_diameter / 2, teeth, depth, lip_height, height)
    return body


def d_shape(diameter: float, height: float, flat_depth: float) -> Part:
    """Cylinder standing on z=0 with one flat side (at +Y), so mating parts only fit one way."""
    disc = Cylinder(diameter / 2, height, align=BOTTOM)
    cutter = Pos(0, diameter / 2 - flat_depth, -1) * Box(
        diameter * 2, diameter, height + 2, align=(Align.CENTER, Align.MIN, Align.MIN)
    )
    return disc - cutter


def spine_hole(depth: float, z_start: float = 0.0) -> Part:
    """D-shaped hole for the spine, `depth` long from z_start upward, with joint clearance."""
    return Pos(0, 0, z_start - 0.01) * d_shape(
        cfg.SPINE_DIAMETER + 2 * cfg.JOINT_CLEAR,
        depth + 0.02,
        cfg.SPINE_FLAT - cfg.JOINT_CLEAR,
    )


def stud_hole(top_z: float, depth: float = cfg.STUD_HOLE_DEPTH) -> Part:
    """Plain tap hole for a cup's threaded stud, opening at top_z (the stud self-taps)."""
    return Pos(0, 0, top_z - depth) * Cylinder(cfg.STUD_HOLE_D / 2, depth + 1, align=BOTTOM)


def seat_radius() -> float:
    """Radius of the flat, bare seat under each washer."""
    return cfg.WASHER_D / 2


def radial_ridges(count: int, radius: float, z: float, height: float, start_deg: float) -> Part:
    """`count` vertical paint-dam ridges on a cylinder of `radius` (standing RIDGE_HEIGHT proud,
    reaching 0.4 mm in so they bond), the first at world angle start_deg."""
    depth = cfg.RIDGE_HEIGHT + 0.4
    ridges = None
    if count <= 0:
        return None
    for index in range(count):
        ridge = Rot(0, 0, start_deg + 360 * index / count) * Pos(radius - 0.4 + depth / 2, 0, z) * Box(
            depth, cfg.RIDGE_WIDTH, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        ridges = ridge if ridges is None else ridges + ridge
    return ridges
