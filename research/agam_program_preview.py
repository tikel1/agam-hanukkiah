"""Preview of the recommended Agam colour program (research/agam-palettes.md section 5).

Stand-alone: no build123d needed. It mirrors model/paint_program.stripe_colour() and the
tooth count rule in model/profiles.tooth_count(), then writes agam_program_preview.svg:
each ring unrolled from the front (face k = 0 at concept angle 0, counter-clockwise =
left to right for someone facing the ring), left faces on the upper row and right faces on
the lower row, plus the emblem positions on R3.

Run:  python agam_program_preview.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

OUT = Path(__file__).resolve().parent / "agam_program_preview.svg"
MAIN_DIAMETER = 180.0
TOOTH_PITCH = 7.0

PAINTS = {  # name -> hex (section 5.1)
    "yellow": "#FFD200",
    "marigold": "#FFA000",
    "orange": "#FF6A13",
    "red": "#E1251B",
    "pink": "#E6338A",
    "violet": "#6E3FA3",
    "cobalt": "#1F4FB4",
    "sky": "#2FA3E6",
    "turquoise": "#00A79D",
    "green": "#22A04B",
    "lime": "#9BCB3C",
    "white": "#F7F5EE",
}
WHEEL_11 = ("yellow", "marigold", "orange", "red", "pink", "violet", "cobalt", "sky", "turquoise", "green", "lime")
WHEEL_10 = ("yellow", "orange", "red", "pink", "violet", "cobalt", "sky", "turquoise", "green", "lime")
WHEEL_9_R3 = ("yellow", "marigold", "orange", "red", "pink", "violet", "cobalt", "turquoise", "lime")
COMPLEMENT = {
    "yellow": "violet", "violet": "yellow", "marigold": "cobalt", "cobalt": "marigold",
    "orange": "sky", "sky": "orange", "red": "green", "green": "red", "pink": "lime",
    "lime": "pink", "turquoise": "red", "white": "white",
}


@dataclass(frozen=True)
class Stripes:
    colours: tuple[str, ...]
    run: int = 1
    offset: int = 0
    complement: bool = False


@dataclass(frozen=True)
class Ring:
    name: str
    diameter_ratio: float
    left: Stripes
    right: Stripes


RINGS = (
    Ring("drum5_R5_dome", 0.372, left=Stripes(WHEEL_10, run=3, offset=4), right=Stripes(("white",))),
    Ring("drum4_R4", 0.62, left=Stripes(WHEEL_10, run=5, offset=12, complement=True), right=Stripes(WHEEL_10, run=5, offset=12)),
    Ring("drum3_R3", 1.00, left=Stripes(("white",)), right=Stripes(WHEEL_9_R3, run=9, offset=4)),
    Ring("drum2_R2", 0.68, left=Stripes(WHEEL_11, run=5, offset=32, complement=True), right=Stripes(WHEEL_11, run=5, offset=32)),
    Ring("drum1_R1", 0.372, left=Stripes(WHEEL_10, run=3, offset=22), right=Stripes(("white",))),
)
EMBLEMS_R3 = (  # (label, concept angle, half-width deg, colours)
    ("HANUKKAH", 0.0, 44.0, "cobalt"),
    ("star", 90.0, 8.5, "cobalt"),
    ("disc+bar", 180.0, 8.0, "orange + cobalt bar"),
    ("+", 225.0, 7.0, "pink"),
    ("dreidel", 270.0, 6.0, "orange + white gimel"),
)


def tooth_count(tip_diameter: float) -> int:
    return max(6, round(math.pi * tip_diameter / TOOTH_PITCH))


def stripe_colour(stripes: Stripes, k: int) -> str:
    colour = stripes.colours[((k + stripes.offset) // stripes.run) % len(stripes.colours)]
    return COMPLEMENT[colour] if stripes.complement else colour


def seam_ok(stripes: Stripes, teeth: int) -> bool:
    """The sequence closes without a jump where face teeth-1 meets face 0 (the front)."""
    period = stripes.run * len(stripes.colours)
    return len(stripes.colours) == 1 or teeth % period == 0


def svg() -> str:
    face_w, row_h, x0 = 8, 26, 150
    width = x0 + 81 * 2 * face_w // 2 * 2 + 40
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 560" font-family="Arial" font-size="12">',
             f'<rect width="{width}" height="560" fill="#ffffff"/>',
             '<text x="10" y="20" font-size="15" font-weight="bold">Recommended Agam colour program, rings unrolled from the front (k=0), left to right</text>',
             '<text x="10" y="38" fill="#555">Upper row = LEFT faces, lower row = RIGHT faces. Each ring is centred so the front sits under the marker.</text>']
    y = 60
    centre_x = x0 + 81 * face_w // 2
    for ring in RINGS:
        teeth = tooth_count(ring.diameter_ratio * MAIN_DIAMETER)
        parts.append(f'<text x="10" y="{y + 22}">{ring.name.split("_")[1]}  {teeth} teeth</text>')
        start = centre_x - teeth * face_w // 2
        for k_rel in range(-(teeth // 2), teeth - teeth // 2):
            k = k_rel % teeth
            x = centre_x + k_rel * face_w - face_w // 2
            for row, side in enumerate(("left", "right")):
                colour = stripe_colour(getattr(ring, side), k)
                parts.append(f'<rect x="{x}" y="{y + row * row_h}" width="{face_w}" height="{row_h}" fill="{PAINTS[colour]}" stroke="#e0e0e0" stroke-width="0.3"/>')
        for side in ("left", "right"):
            if not seam_ok(getattr(ring, side), teeth):
                parts.append(f'<text x="{start}" y="{y - 3}" fill="#c00">seam jump at the front ({side})</text>')
        y += 2 * row_h + 22
    parts.append(f'<line x1="{centre_x}" y1="50" x2="{centre_x}" y2="{y}" stroke="#333" stroke-dasharray="3 3"/>')
    parts.append(f'<text x="{centre_x + 4}" y="{y + 12}">FRONT (0 deg)</text>')
    y += 40
    parts.append(f'<text x="10" y="{y}" font-weight="bold">R3 emblems (no outlines): </text>')
    for i, (label, angle, _, colours) in enumerate(EMBLEMS_R3):
        parts.append(f'<text x="200" y="{y + i * 16}">{label} at {angle:.0f} deg: {colours}</text>')
    y += 5 * 16 + 10
    for i, (name, hex_) in enumerate(PAINTS.items()):
        x = 10 + i * 100
        parts.append(f'<rect x="{x}" y="{y}" width="24" height="24" fill="{hex_}" stroke="#999"/>')
        parts.append(f'<text x="{x + 28}" y="{y + 16}">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    for ring in RINGS:
        teeth = tooth_count(ring.diameter_ratio * MAIN_DIAMETER)
        front = {side: stripe_colour(getattr(ring, side), 0) for side in ("left", "right")}
        seams = {side: seam_ok(getattr(ring, side), teeth) for side in ("left", "right")}
        print(f"{ring.name:15s} teeth {teeth:3d}  front L={front['left']:9s} R={front['right']:9s} seams {seams}")
    r3 = RINGS[2]
    teeth3 = tooth_count(MAIN_DIAMETER)
    for label, angle, half, _ in EMBLEMS_R3:
        lo = math.floor((angle - half) / 360 * teeth3)
        hi = math.ceil((angle + half) / 360 * teeth3)
        under = sorted({stripe_colour(r3.right, k % teeth3) for k in range(lo, hi + 1)})
        print(f"R3 {label:9s} right faces underneath: {under}")
    OUT.write_text(svg(), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
