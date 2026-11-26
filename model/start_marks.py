"""Engraved start arrows (user, after the first painted test ring).

Each pleated ring gets one small arrow sunk START_ARROW_DEPTH into its flat top face and
one into its flat bottom face, just inside the pleat roots. The arrow's tail sits on the seam
angle where every painting map starts (config SEAM_DEG), and the arrow points the way the map
runs: counter-clockwise seen from above, so left to right as you face the ring. It is sunk,
not raised, so it never shows from the side and does not compete with the cup-seat rings.
"""

from __future__ import annotations

import math

from build123d import Part, Plane, Polygon, extrude

import config as cfg


def arrow_outline(radius: float, seam_deg: float) -> list[tuple[float, float]]:
    """Plan points of the arrow: tail on the seam radial, pointing counter-clockwise."""
    length, width, shaft = cfg.START_ARROW_LENGTH, cfg.START_ARROW_WIDTH, cfg.START_ARROW_SHAFT
    head = length * cfg.START_ARROW_HEAD_RATIO
    world = math.radians(seam_deg - 90.0)  # concept 0 = front (-Y)
    radial = (math.cos(world), math.sin(world))
    tangent = (-radial[1], radial[0])  # counter-clockwise seen from above
    local = [
        (0.0, -shaft / 2), (length - head, -shaft / 2), (length - head, -width / 2), (length, 0.0),
        (length - head, width / 2), (length - head, shaft / 2), (0.0, shaft / 2),
    ]
    return [
        (radius * radial[0] + along * tangent[0] + across * radial[0],
         radius * radial[1] + along * tangent[1] + across * radial[1])
        for along, across in local
    ]


def arrow_radius(tip_radius: float) -> float:
    """Arrow centre line: just inside the pleat roots, clear of the paint lip on the top edge."""
    root = tip_radius - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    return root - cfg.START_ARROW_EDGE_INSET - cfg.START_ARROW_WIDTH / 2


def arrow_cutters(tip_radius: float, height: float) -> list[Part]:
    """The two arrow-shaped pockets (top and bottom face) of a ring `height` tall, print orientation.
    Extruded along +Z explicitly: the outline winds clockwise, so a default extrude would go down."""
    points = arrow_outline(arrow_radius(tip_radius), cfg.SEAM_DEG)
    depth = cfg.START_ARROW_DEPTH
    bottom = extrude(Plane.XY.offset(-1.0) * Polygon(*points, align=None), amount=depth + 1.0, dir=(0, 0, 1))
    top = extrude(Plane.XY.offset(height - depth) * Polygon(*points, align=None), amount=depth + 1.0, dir=(0, 0, 1))
    return [bottom, top]


def engrave(part: Part, tip_radius: float, height: float) -> Part:
    """`part` with both start arrows sunk in (no-op when START_ARROWS_ENABLED is off)."""
    if not cfg.START_ARROWS_ENABLED:
        return part
    for cutter in arrow_cutters(tip_radius, height):
        part = part - cutter
    return part
