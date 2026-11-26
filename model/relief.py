"""2D artwork helpers for the emblems: outline bands and the interlaced Magen David."""

from __future__ import annotations

import math

from build123d import Kind, Polygon, Sketch, offset

import config as cfg


def outline_of(shape: Sketch, width: float = cfg.RIDGE_WIDTH) -> Sketch:
    """A band `width` wide just inside the edge of `shape` (for raised outlines).
    Sharp-cornered inset first; glyphs like ג need the rounded (ARC) inset instead."""
    try:
        return shape - offset(shape, amount=-width, kind=Kind.INTERSECTION)
    except RuntimeError:
        return shape - offset(shape, amount=-width, kind=Kind.ARC)


def regular_polygon(radius: float, sides: int, start_deg: float) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(math.radians(start_deg + 360 * k / sides)), radius * math.sin(math.radians(start_deg + 360 * k / sides)))
        for k in range(sides)
    ]


def _triangle_band(radius: float, band: float, start_deg: float) -> Sketch:
    inner_radius = radius - 2 * band  # a triangle band of width `band` has its inner triangle at r - 2*band
    outer = Sketch() + Polygon(*regular_polygon(radius, 3, start_deg), align=None)
    if inner_radius <= 0.2:
        return outer
    return outer - Polygon(*regular_polygon(inner_radius, 3, start_deg), align=None)


def magen_david(size: float, band: float, gap: float) -> Sketch:
    """Interlaced Magen David: two triangle bands crossing over and under in turn. At every
    crossing the lower band stops `gap` short of the upper one, so each band segment is its
    own painting zone (concept §6.3: 3 mm band, 1 mm gap)."""
    radius = size / 2
    up, down = _triangle_band(radius, band, 90), _triangle_band(radius, band, -90)
    if gap <= 0:
        return up + down
    up_grown = _triangle_band(radius + 2 * gap, band + 2 * gap, 90)
    down_grown = _triangle_band(radius + 2 * gap, band + 2 * gap, -90)
    reach = size * 2
    for k in range(6):  # crossings sit at 0, 60, ... 300 deg
        center = math.radians(60 * k)
        wedge = Polygon(
            (0, 0),
            (reach * math.cos(center - math.radians(30)), reach * math.sin(center - math.radians(30))),
            (reach * math.cos(center + math.radians(30)), reach * math.sin(center + math.radians(30))),
            align=None,
        )
        if k % 2 == 0:
            down = down - (up_grown & wedge)
        else:
            up = up - (down_grown & wedge)
    return up + down


def solid_hexagram(size: float) -> Sketch:
    """Filled Magen David: two solid triangles, `size` point to point."""
    radius = size / 2
    return Sketch() + Polygon(*regular_polygon(radius, 3, 90), align=None) + Polygon(*regular_polygon(radius, 3, -90), align=None)
