"""Compact painting bands: each ring side as one continuous strip, shrunk to fit a landscape page.

Reuses maps.draw_face_set (face colours, motif shapes, paint numbers) so a band shows exactly what
the 1:1 maps show, only smaller and in one piece. Labels are enlarged so they stay readable after
the band is scaled down on the page.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

import config as cfg  # noqa: E402
import fountain  # noqa: E402
import maps  # noqa: E402
import paint_program as program  # noqa: E402

PRINTED_LABEL_MM = 2.3  # paint numbers and scale text, as printed
PRINTED_SMALL_MM = 1.9  # tooth numbers
TOP_ROOM_PRINTED = 7.0  # printed mm above the band: degrees and FRONT
BOTTOM_ROOM_PRINTED = 7.5  # printed mm below: tooth numbers and the START arrow
DEGREE_STEP = 45
TOOTH_LABEL_STEP = 5
RED = "#c2283f"


def ring_geometry(ring_name: str) -> tuple[float, float]:
    """(circumference at the tooth tips, height) in mm."""
    drum = program.drum_by_name(ring_name)
    return 2 * math.pi * fountain.drum_diameter(drum) / 2, fountain.drum_height(drum)


def band_scale(ring_name: str, page_width_mm: float) -> float:
    circumference, _ = ring_geometry(ring_name)
    return min(1.0, page_width_mm / (circumference + 2 * maps.MARGIN))


def draw_band_scales(ax, strip: maps.Strip, ring_name: str, scale: float) -> None:
    big, small = PRINTED_LABEL_MM / scale, PRINTED_SMALL_MM / scale
    top, bottom = strip.top, strip.top + strip.height
    for degrees in range(0, 360, DEGREE_STEP):
        x = strip.x(strip.s(degrees))
        ax.plot([x, x], [top - big * 0.5, top], color="#222", lw=maps.LINE * 2)
        if degrees == 0:  # the FRONT marker labels the front
            continue
        ax.text(x, top - big * 0.7, f"{degrees}°", ha="center", va="bottom", fontsize=maps.text_size(big))
    x = strip.x(strip.s(0.0))
    ax.add_patch(Polygon([(x - big, top - big * 2.6), (x + big, top - big * 2.6), (x, top - big * 1.6)], color=RED))
    ax.text(x + big * 1.3, top - big * 2.1, "FRONT", fontsize=maps.text_size(big), color=RED, weight="bold", va="center")
    for k in range(0, program.teeth_of(ring_name), TOOTH_LABEL_STEP):
        for x0, _ in strip.spans(*program.face_span(ring_name, "left", k)):
            ax.text(x0, bottom + small * 0.3, f"t{k}", va="top", fontsize=maps.text_size(small), color="#444")
    if cfg.START_ARROWS_ENABLED:  # the engraved arrow sits on the ring's seam, inside the first whole tooth
        x, y = strip.x(strip.s(cfg.SEAM_DEG)), bottom + small * 2.6
        ax.add_patch(Polygon([(x, y - big * 0.5), (x + big * 1.6, y), (x, y + big * 0.5)], color=RED))
        ax.text(x + big * 2.0, y, "START arrow", fontsize=maps.text_size(big), color=RED, weight="bold", va="center")


def draw_band(ring_name: str, side: str, scale: float, out_path: Path) -> tuple[float, float]:
    """Writes one band SVG; returns its (width, height) in printed mm."""
    circumference, height = ring_geometry(ring_name)
    top_room, bottom_room = TOP_ROOM_PRINTED / scale, BOTTOM_ROOM_PRINTED / scale
    width, total = circumference + 2 * maps.MARGIN, top_room + height + bottom_room
    fig = plt.figure(figsize=(width / 25.4, total / 25.4))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, width)
    ax.set_ylim(total, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    strip = maps.Strip(circumference, 0.0, circumference, top_room, height)
    with cut_at(seam_tooth_start(ring_name)):
        with enlarged_numbers(scale):
            maps.draw_face_set(ax, strip, ring_name, side)
        draw_band_scales(ax, strip, ring_name, scale)
    ax.add_patch(Rectangle((maps.MARGIN, strip.top), circumference, height, facecolor="none", edgecolor="#000", lw=maps.LINE * 2))
    plt.rcParams["svg.fonttype"] = "none"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    return width * scale, total * scale


def seam_tooth_start(ring_name: str) -> float:
    """Start of the tooth that holds the seam, so a band begins and ends on whole faces."""
    teeth = program.teeth_of(ring_name)
    pitch = 360.0 / teeth
    for k in range(teeth):
        start = program.tooth_start(ring_name, k)
        if (cfg.SEAM_DEG - start) % 360.0 < pitch - 1e-9:
            return start % 360.0
    raise ValueError(f"no tooth of {ring_name} holds the seam at {cfg.SEAM_DEG} deg")


class cut_at:  # noqa: N801 - context manager
    """Temporarily unrolls maps' strips from another angle (maps.Strip reads maps.SEAM_DEG)."""

    def __init__(self, degrees: float):
        self.degrees, self.saved = degrees, maps.SEAM_DEG

    def __enter__(self):
        maps.SEAM_DEG = self.degrees
        return self

    def __exit__(self, *_):
        maps.SEAM_DEG = self.saved
        return False


class enlarged_numbers:  # noqa: N801 - used as a context manager, reads like a phrase
    """Temporarily scales maps' text so the paint numbers print at PRINTED_LABEL_MM."""

    def __init__(self, scale: float):
        self.factor = max(1.0, PRINTED_LABEL_MM / (2.0 * scale))
        self.saved = (maps.text_size, maps.LABEL_FROM_TOP)

    def __enter__(self):
        original = self.saved[0]
        maps.text_size = lambda mm: original(mm * self.factor)
        maps.LABEL_FROM_TOP = self.saved[1] * self.factor
        return self

    def __exit__(self, *_):
        maps.text_size, maps.LABEL_FROM_TOP = self.saved
        return False
