"""The sculpture: plinth disc + stem, pleated rings R1-R5, dome, spine (concept §2/§4).

Every part is built in print orientation (flat face on z = 0, no overhangs).
`stack_heights()` gives where each part sits in the assembled model.
"""

from __future__ import annotations

import math

from build123d import Axis, Cylinder, Ellipse, Part, Plane, Pos, Rectangle, Rot, fillet, revolve

import config as cfg
import profiles
import start_marks
from profiles import BOTTOM


def h_unit() -> float:
    """Sculpture height H in mm (concept: H = main diameter / 1.54)."""
    return cfg.MAIN_DIAMETER * cfg.H_PER_MAIN


def drum_diameter(drum: cfg.Drum) -> float:
    return drum.diameter_ratio * cfg.MAIN_DIAMETER


def drum_height(drum: cfg.Drum) -> float:
    return drum.height_ratio_h * h_unit()


def stem_radius() -> float:
    """Radius of the foot's stem where R1 sits."""
    return cfg.FOOT_STEM_TOP_DIAMETER / 2


def stem_height() -> float:
    return cfg.FOOT_STEM_HEIGHT


def dome_radius() -> float:
    return cfg.DOME_DIAMETER_RATIO * cfg.MAIN_DIAMETER / 2


def dome_height() -> float:
    return cfg.DOME_HEIGHT_RATIO_H * h_unit()


def top_is_exposed(index: int) -> bool:
    """A ring's top face shows (and gets a paint lip) when the ring above is narrower."""
    if index == len(cfg.DRUMS) - 1:
        return True
    return cfg.DRUMS[index + 1].diameter_ratio < cfg.DRUMS[index].diameter_ratio


def ring_lip(radius: float, z: float, height: float = cfg.RIDGE_HEIGHT) -> Part:
    """Raised ridge ring of RIDGE_WIDTH just inside `radius` at height z."""
    return Pos(0, 0, z) * (Cylinder(radius, height, align=BOTTOM) - Cylinder(radius - cfg.RIDGE_WIDTH, height, align=BOTTOM))


def plain_drum(index: int) -> Part:
    drum = cfg.DRUMS[index]
    height = drum_height(drum)
    lip = cfg.RIDGE_HEIGHT if top_is_exposed(index) else None
    ring = profiles.pleated_prism(drum_diameter(drum), height, lip_height=lip)
    ring = start_marks.engrave(ring, drum_diameter(drum) / 2, height)
    if index == cfg.CANDLE_DRUM_INDEX - 1 and cfg.R3_GAP_HUB[1] > 0:  # the hub under R3, on R2's top
        diameter, hub_height = cfg.R3_GAP_HUB
        ring = ring + Pos(0, 0, height) * Cylinder(diameter / 2, hub_height, align=BOTTOM)
        height += hub_height
    return ring - profiles.spine_hole(height)


def hub_height() -> float:
    return cfg.R3_GAP_HUB[1]


def foot_stem() -> Part:
    """Concave goblet stem: bottom flare, waist, top flare (revolved spline), on the base."""
    from build123d import BuildLine, BuildSketch, Line, Spline, make_face

    half = cfg.FOOT_STEM_HEIGHT
    rb, rw, rt = cfg.FOOT_STEM_BOTTOM_DIAMETER / 2, cfg.FOOT_STEM_WAIST_DIAMETER / 2, cfg.FOOT_STEM_TOP_DIAMETER / 2
    with BuildSketch(Plane.XZ) as profile:
        with BuildLine():
            Spline((rb, 0), (rw, half * 0.45), (rt, half), tangents=((-0.3, 1), (0.6, 1)))
            Line((rt, half), (0, half))
            Line((0, half), (0, 0))
            Line((0, 0), (rb, 0))
        make_face()
    return Pos(0, 0, cfg.PLINTH_HEIGHT) * revolve(profile.sketch, Axis.Z)


def plinth_stem_part() -> Part:
    """Goblet foot: round base (rounded top edge, ballast pockets underneath) and a concave stem."""
    disc = Cylinder(cfg.PLINTH_DIAMETER / 2, cfg.PLINTH_HEIGHT, align=BOTTOM)
    top_edges = disc.edges().filter_by(lambda e: e.center().Z > cfg.PLINTH_HEIGHT - 0.01)
    disc = fillet(top_edges, cfg.PLINTH_EDGE_ROUND)
    for k in range(cfg.BALLAST_POCKETS):
        angle = math.radians(45 + 360 * k / cfg.BALLAST_POCKETS)
        center = (cfg.BALLAST_POCKET_RADIUS * math.cos(angle), cfg.BALLAST_POCKET_RADIUS * math.sin(angle), -0.01)
        disc = disc - Pos(*center) * Cylinder(cfg.BALLAST_POCKET_DIAMETER / 2, cfg.BALLAST_POCKET_DEPTH, align=BOTTOM)
    top = cfg.PLINTH_HEIGHT + stem_height()
    part = disc + foot_stem()
    sector_dams = profiles.radial_ridges(cfg.STEM_SECTORS, stem_radius(), cfg.PLINTH_HEIGHT, stem_height(), -90.0)
    if sector_dams is not None:
        part = part + sector_dams
    return part - profiles.spine_hole(cfg.SPINE_BASE_DEPTH + 1, top - cfg.SPINE_BASE_DEPTH)


def dome_crown_height() -> float:
    """Height of the dome once its crown is cut flat to DOME_CROWN_FLAT_D (shamash washer seat)."""
    radius, height = dome_radius(), dome_height()
    flat = min(cfg.DOME_CROWN_FLAT_D / 2, radius * 0.95)
    return height * math.sqrt(1 - (flat / radius) ** 2)


def dome_solid(base_z: float) -> Part:
    """Half-ellipsoid dome standing on z = base_z, crown cut flat for the shamash washer."""
    radius, height, crown = dome_radius(), dome_height(), dome_crown_height()
    half = Plane.XZ * (Ellipse(radius, height) & Pos(radius / 2, crown / 2) * Rectangle(radius, crown))
    return Pos(0, 0, base_z) * revolve(half, Axis.Z)


def r5_dome_part() -> Part:
    """R5 with the shamash stud hole in its top centre (or in the dome's flat crown, if enabled)."""
    index = len(cfg.DRUMS) - 1
    drum = cfg.DRUMS[index]
    height = drum_height(drum)
    body = profiles.pleated_prism(drum_diameter(drum), height, lip_height=cfg.RIDGE_HEIGHT)
    body = start_marks.engrave(body, drum_diameter(drum) / 2, height)
    seat = height
    if cfg.DOME_ENABLED:
        body = body + dome_solid(height) + ring_lip(dome_radius() + cfg.RIDGE_WIDTH + 0.6, height)
        seat += dome_crown_height()
    if cfg.GUIDES_ENABLED:
        import guides

        body = body + guides.seat_ring(0.0, 0.0, seat)
    body = body - profiles.stud_hole(seat, cfg.SHAMASH_STUD_HOLE_DEPTH)
    return body - profiles.spine_hole(cfg.SPINE_TOP_DEPTH)


def spine_length() -> float:
    inner = sum(drum_height(d) for d in cfg.DRUMS[:-1]) + hub_height()
    return cfg.SPINE_BASE_DEPTH + inner + cfg.SPINE_TOP_DEPTH


def spine_part() -> Part:
    """D-shaft, printed lying on its flat (rotated so the flat faces down)."""
    length = spine_length()
    shaft = profiles.d_shape(cfg.SPINE_DIAMETER, length, cfg.SPINE_FLAT)
    lying = Rot(-90, 0, 0) * shaft  # axis along +Y, flat now faces -Z
    box = lying.bounding_box()
    return Pos(0, -length / 2, -box.min.Z) * lying


def pool_part() -> Part:
    """Optional decorative pool tray (POOL_ENABLED). Lies under everything, below every flame."""
    outer = cfg.POOL_DIAMETER / 2
    tray = Cylinder(outer, cfg.POOL_RIM_HEIGHT, align=BOTTOM)
    basin = Pos(0, 0, cfg.POOL_FLOOR) * Cylinder(outer - cfg.POOL_RIM_WIDTH, cfg.POOL_RIM_HEIGHT, align=BOTTOM)
    return tray - basin + ring_lip(outer - cfg.POOL_RIM_WIDTH, cfg.POOL_FLOOR)


def base_z() -> float:
    return cfg.POOL_FLOOR if cfg.POOL_ENABLED else 0.0


def stack_heights() -> dict[str, float]:
    """Z of the bottom of each stacked part in the assembled model."""
    z = base_z() + cfg.PLINTH_HEIGHT + stem_height()
    heights = {"pool": 0.0, "plinth_stem": base_z()}
    for drum in cfg.DRUMS:
        heights[drum.name] = z
        z += drum_height(drum) + (hub_height() if drum is cfg.DRUMS[cfg.CANDLE_DRUM_INDEX - 1] else 0.0)
    return heights


def spine_bottom_z() -> float:
    return base_z() + cfg.PLINTH_HEIGHT + stem_height() - cfg.SPINE_BASE_DEPTH


def r3_top_z() -> float:
    r3 = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    return stack_heights()[r3.name] + drum_height(r3)


def r4_top_z() -> float:
    r4 = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX + 1]
    return stack_heights()[r4.name] + drum_height(r4)


def r5_top_z() -> float:
    r5 = cfg.DRUMS[-1]
    return stack_heights()[r5.name] + drum_height(r5)


def shamash_seat_z() -> float:
    """Where the shamash washer sits: R5's top, or the dome's flat crown if the dome is enabled."""
    return r5_top_z() + (dome_crown_height() if cfg.DOME_ENABLED else 0.0)
