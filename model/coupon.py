"""Test coupon: a COUPON_SPAN_DEG arc of R3 at full height, cut from the real R3 part, so it has
the same pleats, guide relief, one cup seat (stud hole + locating ring) and, painted, a few
HANUKKAH letters on the right faces and part of the Magen David on the left faces. It stands on
R3's flat bottom and is hollowed from below (thin walls, a solid boss round the stud hole) to
print in about an hour without supports.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import Cylinder, Part, Polygon, Pos, extrude

import config as cfg
import fountain
import hanukkiah
import profiles


def wedge(start_deg: float, end_deg: float, radius: float, height: float, z: float = 0.0) -> Part:
    """Plan wedge between two concept angles (0 = front), extruded."""
    steps = 48
    points = [(0.0, 0.0)]
    for i in range(steps + 1):
        world = math.radians(-90 + start_deg + (end_deg - start_deg) * i / steps)
        points.append((radius * math.cos(world), radius * math.sin(world)))
    return Pos(0, 0, z) * extrude(Polygon(*points, align=None), amount=height)


@dataclass(frozen=True)
class Coupon:
    """One test cut of R3: its file stem, the arc it covers and what its map should say to check."""

    name: str
    centre_deg: float
    span_deg: float
    check: str


MAIN = Coupon("test_coupon_R3", cfg.COUPON_CENTRE_DEG, cfg.COUPON_SPAN_DEG,
              "Check from 40° left (the Magen David) and 40° right (HANUKKAH) before painting the big ring.")
STAR = Coupon("test_star_R3", cfg.STAR_COUPON_CENTRE_DEG, cfg.STAR_COUPON_SPAN_DEG,
              "The whole Magen David (picture A) at full size. Check it from 40° left before painting the big ring.")
COUPONS = (MAIN, STAR)


def coupon_range(spec: Coupon = MAIN) -> tuple[float, float]:
    return spec.centre_deg - spec.span_deg / 2, spec.centre_deg + spec.span_deg / 2


def coupon_part(r3: Part | None = None, spec: Coupon = MAIN) -> Part:
    """The coupon in R3's own frame (print orientation, bottom at z = 0)."""
    r3 = r3 if r3 is not None else hanukkiah.r3_part()
    drum = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    height = fountain.drum_height(drum)
    tip = fountain.drum_diameter(drum) / 2
    root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    lo, hi = coupon_range(spec)
    inner = cfg.COUPON_INNER_RADIUS
    piece = r3 & (wedge(lo, hi, tip + 5, height + 5, -1) - Pos(0, 0, -1) * Cylinder(inner, height + 5, align=profiles.BOTTOM))
    wall = cfg.COUPON_WALL
    shrink = math.degrees(wall / inner)
    pocket = wedge(lo + shrink, hi - shrink, root - wall, height - cfg.COUPON_TOP_SKIN, -1) - Pos(0, 0, -1) * Cylinder(inner + wall, height + 5, align=profiles.BOTTOM)
    seat = cup_seat_in_coupon(spec)
    if seat is not None:  # solid boss under the cup seat, for the stud to bite into
        pocket = pocket - Pos(seat[0], seat[1], -2) * Cylinder(cfg.STUD_HOLE_D / 2 + cfg.COUPON_WALL + 2.0, height + 5, align=profiles.BOTTOM)
    return piece - pocket


def cup_seat_in_coupon(spec: Coupon = MAIN) -> tuple[float, float] | None:
    lo, hi = coupon_range(spec)
    for x, y in hanukkiah.candle_positions():
        angle = (math.degrees(math.atan2(y, x)) + 90 + 180) % 360 - 180
        if lo < angle < hi:
            return x, y
    return None
