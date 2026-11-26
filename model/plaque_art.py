"""2D artwork of the name ring, in ring mm (u = arc length from the centre, v = height).

Top line: the wordmark of submission/logo.py ("חנוכיית אש ומים": line letters with coloured dots),
letters spaced a little wider than the logo so each dot can be its own printed piece.
Under it: "מחווה לאמן יעקב אגם", each letter its own piece too.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "submission"))
import logo  # noqa: E402  (glyphs and dot colours)

FONT = HERE / "fonts" / "SecularOne-Regular.ttf"
WORDS = ["חנוכיית", "אש", "ומים"]

SCALE = 0.07  # mm per logo unit: letters 7 mm tall
LETTER_GAP = 36.0  # logo units (logo: 26); wider so neighbouring dots and their pockets stay apart
WORD_GAP = 70.0
STROKE_MM = 1.0
MITRE_LIMIT = 1.6  # sharp joins (the peak of מ) are cut flat so they stay under their dot
DOT_MM = 0.85  # dot radius: Ø 1.7
WORDMARK_BOTTOM = 8.1  # the name on top, the tribute line under it

SUBTITLE = "מחווה לאמן יעקב אגם"
SUBTITLE_SIZE = 5.6  # font size in mm (capital height about 3.9)
SUBTITLE_BASELINE = 2.1

COLOUR_NAMES = {"#e4432f": "red", "#f6d21c": "yellow", "#1fa3a8": "teal", "#6a5ea8": "purple", "#6bb7e6": "sky",
                "#1b7f3e": "green", "#a81f2a": "brick", "#4f63b0": "blue", "#cfa3d1": "lilac", "#f39a1e": "orange"}


def path_points(d: str) -> list[list[tuple[float, float]]]:
    """Absolute M/L/H/V/Q/Z path data (as in logo.GLYPHS) to polylines; Q curves sampled."""
    tokens = re.findall(r"[MLHVQZ]|-?\d+(?:\.\d+)?", d)
    lines, current, index, command = [], [], 0, ""
    while index < len(tokens):
        if tokens[index].isalpha():
            command, index = tokens[index], index + 1
        if command == "Z":
            current.append(current[0])
            continue
        x, y = current[-1] if current else (0.0, 0.0)
        if command in "ML":
            point = (float(tokens[index]), float(tokens[index + 1]))
            index += 2
            if command == "M" and current:
                lines.append(current)
            current = [point] if command == "M" else current + [point]
        elif command in "HV":
            value, index = float(tokens[index]), index + 1
            current = current + [(value, y) if command == "H" else (x, value)]
        elif command == "Q":
            cx, cy, ex, ey = (float(t) for t in tokens[index:index + 4])
            index += 4
            current = current + [((1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * ex,
                                  (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * ey) for t in np.linspace(0.1, 1, 10)]
    return lines + [current]


def layout() -> tuple[list[tuple[str, float]], list[float], float]:
    """Letters right to left with this ring's gaps: (letter, left x) pairs, separator x's, total width."""
    placed, separators, x = [], [], 0.0
    for index, word in enumerate(WORDS):
        if index:
            separators.append(x + WORD_GAP / 2)
            x += WORD_GAP
        for position, letter in enumerate(word):
            x += LETTER_GAP if position else 0.0
            width = logo.GLYPHS[letter][0]
            placed.append((letter, x, width))
            x += width
    return [(letter, x - left - width) for letter, left, width in placed], [x - s for s in separators], x


def to_ring(x_unit: float, y_unit: float, total: float) -> tuple[float, float]:
    return (x_unit - total / 2) * SCALE, WORDMARK_BOTTOM + (logo.CAP - y_unit) * SCALE


def wordmark() -> tuple[list[tuple[Polygon, list[tuple[Polygon, str]]]], list[tuple[Polygon, str]]]:
    """Each letter with the dots on its ends (printed as one piece), and the loose dots between words."""
    placed, separators, total = layout()
    letters, colours = [], iter(logo.DOT_COLOURS * 10)
    for letter, left in placed:
        _, paths, points = logo.GLYPHS[letter]
        strokes = [LineString([to_ring(left + px, py, total) for px, py in line]).buffer(STROKE_MM / 2, cap_style="flat", join_style="mitre", mitre_limit=MITRE_LIMIT)
                   for d in paths for line in path_points(d)]
        own_dots = [(Point(*to_ring(left + px, py, total)).buffer(DOT_MM, 32), next(colours)) for px, py in points]
        letters.append((unary_union(strokes), own_dots))
    loose = [(Point(*to_ring(x, logo.CAP / 2, total)).buffer(DOT_MM, 32), next(colours))
             for x in [*separators, -WORD_GAP / 2, total + WORD_GAP / 2]]
    return letters, loose


def tribute_letters() -> list[Polygon]:
    """The tribute line (matplotlib lays Hebrew out right to left), centred; one shape per letter part."""
    path = TextPath((0, 0), SUBTITLE, size=SUBTITLE_SIZE, prop=FontProperties(fname=str(FONT)))
    text = Polygon()
    for ring in path.to_polygons():
        if len(ring) >= 3:
            text = text.symmetric_difference(Polygon(ring).buffer(0))
    minx, _, maxx, _ = text.bounds
    text = affinity.translate(text, -(minx + maxx) / 2, SUBTITLE_BASELINE)
    parts = list(text.geoms) if hasattr(text, "geoms") else [text]
    return sorted(parts, key=lambda part: -part.bounds[0])  # right to left, in reading order
