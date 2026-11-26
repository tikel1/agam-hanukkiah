"""Faceted motifs (user, on the test-cut maps: "avoid loose ends, every shape should go across the
whole face").

A motif drawn freely over the pleats leaves slivers: faces where a curve or a tip starts or ends in the
middle of the face. Here a motif is rebuilt on the tooth grid of the picture so that every corner sits
on a ridge (a tooth edge) and every piece crosses its face from ridge to ridge:

* Each face is cut by a vertical line just inside each of its two ridges (SAMPLE_INSET), giving
  intervals (where it is painted). Sampling inside the face, not on the ridge, keeps steps that fall
  on a ridge (a dreidel's handle one face wide stays a handle).
* Inside each face, matching intervals on its two ridges are joined by straight top and bottom edges,
  so each piece is a strip (a trapezoid) with no corner inside the face.
* One interval meeting several (a fork, like a star's points): the single interval is split, the parts
  touching at a point on that ridge, so the white notch between them starts on the ridge.
* An interval with nothing on the other ridge: a small one (a tip) runs to a point on the next ridge;
  a large one (the end of a wide shape) stops square on its own ridge.

Coordinates are the unrolled picture: x mm along the ring, z mm up.
"""

from __future__ import annotations

import math

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

POINT_RATIO = 0.1  # an interval shorter than this share of the motif's height is the shape closing on that ridge: a point
TIP_RATIO = 0.3  # an end interval shorter than this share of the motif's height is a tip (runs to a point)
OVERLAP = 0.02  # mm: pieces reach just past their ridges, never exactly on them (GEOS overlay fails on coincident edges)
SAMPLE_INSET = 0.01  # of a face: where each face is sampled, just inside its ridges
MIN_INTERVAL = 0.05  # mm: shorter cuts are points (a tangent or a vertex on the ridge)

Interval = tuple[float, float]


def intervals_at(geometry, x: float) -> list[Interval]:
    """Where the vertical line at x crosses the motif, bottom to top (touching pieces merged)."""
    lo, bottom, hi, top = geometry.bounds
    if not lo <= x <= hi:
        return []
    cut = geometry.intersection(LineString([(x, bottom - 1.0), (x, top + 1.0)]))
    parts = getattr(cut, "geoms", [cut])
    spans = sorted((min(p.coords[0][1], p.coords[-1][1]), max(p.coords[0][1], p.coords[-1][1])) for p in parts if p.geom_type == "LineString" and not p.is_empty)
    merged: list[Interval] = []
    for start, end in spans:
        if merged and start <= merged[-1][1] + MIN_INTERVAL:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def split(interval: Interval, targets: list[Interval]) -> list[Interval]:
    """`interval` cut into len(targets) touching parts, sized like the targets."""
    total = sum(max(t[1] - t[0], MIN_INTERVAL) for t in targets)
    parts, start = [], interval[0]
    for target in targets:
        end = start + (interval[1] - interval[0]) * max(target[1] - target[0], MIN_INTERVAL) / total
        parts.append((start, end))
        start = end
    return parts


def pair_up(left: list[Interval], right: list[Interval], tip: float) -> list[tuple[Interval | None, Interval | None]]:
    """Which interval on the left ridge joins which on the right (None: the piece ends on that side)."""
    if len(left) == len(right):
        return list(zip(left, right))
    if not left or not right:  # the motif ends in this face: tips run to a point, wide ends stop on the ridge
        tips = [i for i in (left or right) if i[1] - i[0] < tip]
        return [(i, None) if left else (None, i) for i in tips]
    if len(left) == 1:
        return list(zip(split(left[0], right), right))
    if len(right) == 1:
        return list(zip(left, split(right[0], left)))
    pairs = list(zip(left, right))  # rare: pair in order, extra intervals run to a point
    extra = left[len(right):] if len(left) > len(right) else right[len(left):]
    return pairs + [((i, None) if len(left) > len(right) else (None, i)) for i in extra]


def closed(interval: Interval, smallest: float) -> Interval:
    """A sliver where the shape just reaches a ridge (a disc's side) becomes a point on that ridge."""
    if interval[1] - interval[0] >= smallest:
        return interval
    middle = (interval[0] + interval[1]) / 2
    return (middle, middle)


def strip_piece(x0: float, x1: float, left: Interval | None, right: Interval | None) -> Polygon:
    """One piece across a face: straight edges from ridge to ridge (a point where a side is None)."""
    if left is None:
        middle = (right[0] + right[1]) / 2
        left = (middle, middle)
    if right is None:
        middle = (left[0] + left[1]) / 2
        right = (middle, middle)
    a, b = x0 - OVERLAP, x1 + OVERLAP
    return Polygon([(a, left[0]), (b, right[0]), (b, right[1]), (a, left[1])])


RIDGE_TOLERANCE = 0.02  # of a face: a corner this close to a ridge sits on it


def corners_on_ridges(geometry, first_ridge: float, pitch: float) -> bool:
    """True when every corner of the outline already sits on a ridge (nothing to rebuild)."""
    polygons = getattr(geometry, "geoms", [geometry])
    xs = [x for polygon in polygons for x, _ in polygon.exterior.coords] + [
        x for polygon in polygons for ring in polygon.interiors for x, _ in ring.coords
    ]
    offsets = [((x - first_ridge) / pitch) % 1.0 for x in xs]
    return all(min(offset, 1.0 - offset) < RIDGE_TOLERANCE for offset in offsets)


def facet(geometry, first_ridge: float, pitch: float, motif_height: float):
    """The motif rebuilt so each piece spans its whole face (see the module notes)."""
    if corners_on_ridges(geometry, first_ridge, pitch):
        return geometry  # already made of whole-face pieces (a Magen David sized to the grid)
    lo, _, hi, _ = geometry.bounds
    tip = TIP_RATIO * motif_height
    start = math.floor((lo - first_ridge) / pitch)
    end = math.ceil((hi - first_ridge) / pitch)
    ridges = [first_ridge + k * pitch for k in range(start, end + 1)]
    inset = SAMPLE_INSET * pitch
    pieces = []
    for x0, x1 in zip(ridges, ridges[1:]):
        left, right = (
            [closed(i, POINT_RATIO * motif_height) for i in intervals_at(geometry, x)] for x in (x0 + inset, x1 - inset)
        )
        for a, b in pair_up(left, right, tip):
            pieces.append(strip_piece(x0, x1, a, b))
    return unary_union([p for p in pieces if p.area > 1e-6])
