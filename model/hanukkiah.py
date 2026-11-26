"""Hanukkiah features on the sculpture: R3 with 8 cup stud holes, washer seats and emblems;
the holder heights; and the safety/halacha checks of hanukkiah/concept.md §1/§3/§5."""

from __future__ import annotations

import math

from build123d import Cylinder, Part, Polygon, Pos

import config as cfg
import fountain
import profiles
import start_marks


def tip_alignment() -> float:
    """Degrees to turn the cups so cup 1 sits over the nearest R3 tooth tip (0 if disabled)."""
    if not cfg.CANDLE_ON_TOOTH_TIP:
        return 0.0
    teeth = profiles.tooth_count(fountain.drum_diameter(cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]))
    pitch = 360 / teeth
    first = -90 + cfg.CANDLE_ANGLE_OFFSET
    shift = (cfg.TOOTH_LEAN * pitch - first) % pitch
    return shift - pitch if shift > pitch / 2 else shift


def candle_angles() -> list[float]:
    """World angles in degrees (from +X, counter-clockwise); concept angle 0 = front (-Y)."""
    step = 360 / cfg.CANDLE_COUNT
    first = -90 + cfg.CANDLE_ANGLE_OFFSET + tip_alignment()
    return [first + step * index for index in range(cfg.CANDLE_COUNT)]


def hole_wall(x: float, y: float, outline: list[tuple[float, float]]) -> float:
    """Plastic between a stud hole at (x, y) and the nearest point of the pleated outline."""
    nearest = math.inf
    for (ax, ay), (bx, by) in zip(outline, outline[1:] + outline[:1]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        nearest = min(nearest, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return nearest - cfg.STUD_HOLE_D / 2


def candle_positions() -> list[tuple[float, float]]:
    r = cfg.CANDLE_RING_RADIUS
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in candle_angles()]


def r3_part(with_holes: bool = True) -> Part:
    """R3: pleats with paint ridges, a paint lip that stops short of each washer seat, the
    top-step circles, the embossed emblems and 8 stud holes (concept §2.2/§5)."""
    index = cfg.CANDLE_DRUM_INDEX
    drum = cfg.DRUMS[index]
    height = fountain.drum_height(drum)
    tip_radius = fountain.drum_diameter(drum) / 2
    depth = cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    teeth = profiles.tooth_count(2 * tip_radius)
    ring = profiles.pleated_prism(2 * tip_radius, height)
    keepout = profiles.seat_radius() + cfg.SEAT_CLEARANCE
    outline = Polygon(*profiles.ridged_sawtooth_points(tip_radius, teeth, depth), align=None)
    lip = profiles.top_lip(outline, tip_radius, teeth, depth, cfg.RIDGE_HEIGHT, height)
    for x, y in candle_positions():
        lip = lip - Pos(x, y, height - 1) * Cylinder(keepout, cfg.RIDGE_HEIGHT + 2, align=profiles.BOTTOM)
    ring = start_marks.engrave(ring + lip, tip_radius, height)
    if cfg.GUIDES_ENABLED:
        import guides

        for solid in guides.motif_guides(drum.name):
            ring = ring + solid
        for x, y in candle_positions():
            ring = ring + guides.seat_ring(x, y, height)
    if not with_holes:  # test rings: seat marks only, flat closed bottom
        return ring
    for x, y in candle_positions():
        ring = ring - Pos(x, y, 0) * profiles.stud_hole(height)
    return ring - profiles.spine_hole(height)


# --- Holder heights ------------------------------------------------------------------------


def ring_rim_z() -> float:
    return fountain.r3_top_z() + cfg.HOLDER_VISIBLE


def shamash_rim_z() -> float:
    return fountain.shamash_seat_z() + cfg.HOLDER_VISIBLE


def cup_spots() -> list[tuple[float, float, float, float]]:
    """(x, y, seat z, cup rim z) for the 8 ring cups, then the shamash (assembled)."""
    spots = [(x, y, fountain.r3_top_z(), ring_rim_z()) for x, y in candle_positions()]
    spots.append((0.0, 0.0, fountain.shamash_seat_z(), shamash_rim_z()))
    return spots


# --- Checks -------------------------------------------------------------------------------


def safety_report() -> list[tuple[str, bool, str]]:
    r3 = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    r5 = cfg.DRUMS[-1]
    r3_tip = fountain.drum_diameter(r3) / 2
    r3_root = r3_tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    r4_tip = fountain.drum_diameter(cfg.DRUMS[cfg.CANDLE_DRUM_INDEX + 1]) / 2
    higher = max(fountain.drum_diameter(r5) / 2, fountain.dome_radius() if cfg.DOME_ENABLED else 0.0)
    radius = cfg.CANDLE_RING_RADIUS
    spacing = 2 * radius * math.sin(math.pi / cfg.CANDLE_COUNT)
    outline = profiles.sawtooth_points(r3_tip, profiles.tooth_count(2 * r3_tip), cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH)
    wall = min(hole_wall(x, y, outline) for x, y in candle_positions())
    rim, shamash = ring_rim_z(), shamash_rim_z()
    r4_above = fountain.r4_top_z() - rim
    washer_out = radius + profiles.seat_radius()
    r5_height = fountain.drum_height(r5) + (fountain.dome_crown_height() if cfg.DOME_ENABLED else 0.0)
    floor = r5_height - cfg.SHAMASH_STUD_HOLE_DEPTH - cfg.SPINE_TOP_DEPTH
    return [
        ("8 cup rims at one height, 45 deg apart", True, f"Z {rim:.1f} mm on r {radius}"),
        ("holders visible <= 11 above R3", cfg.HOLDER_VISIBLE <= cfg.MAX_HOLDER_VISIBLE, f"{cfg.HOLDER_VISIBLE:.1f} mm (washer {cfg.WASHER_T} + cup {cfg.CUP_HEIGHT})"),
        ("R4 rises <= 7 above the rims", r4_above <= cfg.MAX_R4_RISE + 1e-6, f"{r4_above:.1f} mm"),
        ("axis to R4 tooth tips >= 25", radius - r4_tip >= cfg.MIN_AXIS_TO_R4_TIPS, f"{radius - r4_tip:.1f} mm (check in the test burn)"),
        ("axis to other plastic above the rims (R5) >= 40", radius - higher >= cfg.MIN_AXIS_TO_HIGHER_PLASTIC, f"{radius - higher:.1f} mm"),
        ("flame spacing >= 40", spacing >= cfg.MIN_FLAME_SPACING, f"{spacing:.1f} mm between neighbours"),
        ("shamash >= 20 above the ring", shamash - rim >= cfg.MIN_SHAMASH_ABOVE_RING, f"+{shamash - rim:.1f} mm (rim Z {shamash:.1f})"),
        ("stud hole wall to R3's pleated outline >= 3", wall >= cfg.HOLE_WALL_MIN, f"{wall:.2f} mm (cups over tooth tips, turned {tip_alignment():+.2f} deg)"),
        ("washers inside R3's tooth tips", washer_out <= r3_tip, f"washer edge r {washer_out:.1f} (tips r {r3_tip:.1f})"),
        ("shamash stud hole clear of the spine", floor >= cfg.MIN_FLOOR_ABOVE_SPINE, f"{floor:.1f} mm of PETG between them (hole {cfg.SHAMASH_STUD_HOLE_DEPTH}, spine {cfg.SPINE_TOP_DEPTH} into R5)"),
    ]
