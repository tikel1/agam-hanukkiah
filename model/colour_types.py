"""Building blocks of the colour program (colour_program.py). No colours live here.

Every pleat has a LEFT face (turned to your left as you face the ring, seen from the left)
and a RIGHT face. Each face set carries its own complete picture (Agam's polymorph):
a ground of stripes, optionally with big flat motifs painted across many pleats. From the
left you see the left picture, from the right the right picture, head-on the two interleaved.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Paint:
    number: int  # the number painted on the maps and used in painting/guide.md
    name: str
    hex: str


@dataclass(frozen=True)
class Stripes:
    """One colour per pleat face: face k gets colours[((k + offset) // run) % len(colours)]."""

    colours: tuple[str, ...]
    run: int = 1  # faces per colour (a run of 3+ reads as a gradient)
    offset: int = 0  # shifts the sequence
    complement: bool = False  # paint each colour's COMPLEMENT instead


@dataclass(frozen=True)
class Sector:
    span_deg: float  # how much of the ring this sector covers
    stripes: Stripes  # face index counts from the sector's first tooth


@dataclass(frozen=True)
class Sectors:
    """The ring split into consecutive sectors (a 'colour journey' round the ring), the first
    starting at start_deg (concept angle: 0 = front, counter-clockwise seen from above)."""

    start_deg: float
    sectors: tuple[Sector, ...]


@dataclass(frozen=True)
class Motif:
    """A big flat shape painted on one face set only, across many pleats (no relief).
    shape: "text" (text, lines), "columns" (text in face-column letters, snapped to whole tooth faces, column_letters.py),
    "star" (Magen David), "disc", "sufganiyah" (ellipse + jam dot), "disc_bar", "square", "cross", "dreidel", "band" (a full-height ground patch, e.g. white
    behind a word)."""

    shape: str
    centre_deg: float  # concept angle of its centre
    inks: tuple[str, ...]  # one per zone (disc_bar: disc, bar; dreidel: body, letter)
    height_fraction: float = 0.8  # of the ring height
    text: str = ""
    lines: int = 1  # text split over this many lines
    stretch: float = 1.4  # horizontal stretch on the unrolled ring, to offset the side-on view
    width_deg: float = 0.0  # "band" only: how much of the ring it spans (full height)


@dataclass(frozen=True)
class FaceSet:
    ground: Stripes | Sectors
    motifs: tuple[Motif, ...] = ()


@dataclass(frozen=True)
class RingPaint:
    """Pictures for one ring's pleated side. Top faces always stay white PETG."""

    left: FaceSet
    right: FaceSet
