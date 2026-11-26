"""Copied from research/fountain_colour_program.py (2026-11-08). The real fountain's colour program (research/fountain-colour-program.md), as data plus a check.

Stand-alone (no build123d). It holds:
* PAINTS: the original 1986 colours (normalised from photos).
* SECTORS: per ring, per face side, (start_deg, end_deg, paint) in FOUNTAIN angles. 0 = the
  centre of the side seen in the 1986 reference photo; degrees increase counter-clockwise seen
  from above (= left to right for someone facing that side), as in model/paint_program.py.
* ROTATION: fountain angle + ROTATION = model concept angle (puts the fountain's own disc on
  the model's DISC_ANGLE 180 and its "+" near CROSS_ANGLE 225).
* faces(ring, side, teeth): the per-face paint list, ready for config.Stripes(colours, run=1).

Run `python fountain_colour_program.py` to print the program, check that the emblems
contrast with the stripes under them, and write fountain_colour_program.svg / .json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_DIAMETER = 180.0
TOOTH_PITCH = 7.0
TOOTH_LEAN = 0.5
ROTATION = 207.0  # fountain disc 1 (fountain -27 deg) -> model 180 deg; "+" 1 (+24) -> 231

PAINTS = {  # name: (hex, nearest Amsterdam Standard acrylic, nearest Posca) - check on a swatch
    "white": ("#F4F1E4", "105 Titanium white", "White"),
    "yellow": ("#F2C94C", "269 Azo yellow medium", "Sunshine Yellow"),
    "orange": ("#E8893F", "276 Azo orange + white", "Light Orange"),
    "coral": ("#E8655C", "315 Pyrrole red + white", "Coral Pink"),
    "brick": ("#A8322A", "399 Naphthol red deep", "Red + touch of Brown"),
    "rose": ("#DC8A86", "330 Persian rose + white", "Salmon Pink"),
    "lilac": ("#9A8CC0", "568 Permanent blue violet + white", "Lavender"),
    "periwinkle": ("#7484C4", "504 Ultramarine + 568 + white", "Light Blue + Lavender"),
    "light_blue": ("#A3C1E0", "551 Sky blue light", "Light Blue"),
    "blue": ("#3E5FB0", "504 Ultramarine", "Blue"),
    "navy": ("#2B2F6B", "504 Ultramarine + 566 Prussian blue", "Navy Blue"),
    "mint": ("#A8DDB5", "660 Turquoise green light + white", "Mint"),
    "teal": ("#3E8F7C", "661 Turquoise green", "Emerald Green"),
    "green": ("#4E9E5E", "618 Permanent green light + touch of blue", "Green"),
    "grey": ("#A9B3B6", "710 Neutral grey + white", "Light Grey"),
}

# (start, end, paint), fountain angles; each list covers -90 .. 270 with no gaps.
SECTORS: dict[str, dict[str, list[tuple[float, float, str]]]] = {
    "drum5_R5_dome": {  # same in both halves (1986 photo + 2012-2014 photos agree)
        "right": [(-90, -50, "light_blue"), (-50, 90, "white"), (90, 130, "light_blue"), (130, 270, "white")],
        "left": [(-90, -10, "lilac"), (-10, 34, "yellow"), (34, 90, "orange"),
                 (90, 170, "lilac"), (170, 214, "yellow"), (214, 270, "orange")],
    },
    "drum4_R4": {
        "right": [(-90, -28, "coral"), (-28, 14, "rose"), (14, 90, "white"),
                  (90, 140, "coral"), (140, 190, "lilac"), (190, 270, "white")],
        "left": [(-90, 14, "white"), (14, 39, "mint"), (39, 90, "teal"),
                 (90, 190, "white"), (190, 230, "teal"), (230, 270, "mint")],
    },
    "drum3_R3": {
        "right": [(-90, -11, "white"), (-11, 2, "lilac"), (2, 90, "periwinkle"),
                  (90, 180, "white"), (180, 200, "light_blue"), (200, 234, "teal"), (234, 270, "blue")],
        "left": [(-90, -21, "yellow"), (-21, -11, "lilac"), (-11, 35, "rose"), (35, 54, "orange"), (54, 90, "yellow"),
                 (90, 159, "yellow"), (159, 180, "rose"), (180, 215, "coral"), (215, 270, "orange")],
    },
    "drum2_R2": {
        "right": [(-90, -53, "orange"), (-53, -8, "brick"), (-8, 90, "white"),
                  (90, 135, "brick"), (135, 200, "white"), (200, 270, "blue")],
        "left": [(-90, -8, "white"), (-8, 90, "navy"),
                 (90, 135, "white"), (135, 200, "navy"), (200, 270, "blue")],
    },
    "drum1_R1": {
        "right": [(-90, -30, "brick"), (-30, 30, "white"), (30, 90, "grey"),
                  (90, 150, "brick"), (150, 210, "white"), (210, 270, "grey")],
        "left": [(-90, -30, "white"), (-30, 30, "green"), (30, 90, "white"),
                 (90, 150, "white"), (150, 210, "green"), (210, 270, "white")],
    },
}
DIAMETER_RATIO = {"drum1_R1": 0.36, "drum2_R2": 0.68, "drum3_R3": 1.00, "drum4_R4": 0.62, "drum5_R5_dome": 0.36}

# Model emblems (config.py angles), with the paint each one gets here.
EMBLEMS = {
    "word": (0.0, 44.0, ("blue",)),          # HANUKKAH: user addition, blue
    "star": (90.0, 9.0, ("green",)),         # Magen David: user addition, green
    "dreidel": (270.0, 8.0, ("orange",)),  # user addition, orange silhouette (no letter, user 2026-11-08)
    "disc": (180.0, 8.0, ("orange", "orange")),    # the fountain's own disc 1 (1986: yellow + marigold halves, no bar)
    "cross": (225.0, 7.0, ("mint",)),        # the fountain's own "+" (2012: pink on side 1, mint on side 2)
}
OTHER = {"STEM_COLOURS": ("grey",), "PLINTH_PAINT": "blue", "DOME_PAINT": "white", "TOPS": "white"}


def _gradient(steps_left: tuple[str, ...], steps_right: tuple[str, ...]) -> dict[str, list]:
    """Both halves get the same hue walk, one colour per 180/len degrees (no white faces)."""
    def walk(steps: tuple[str, ...]) -> list[tuple[float, float, str]]:
        width = 180.0 / len(steps)
        return [(-90 + h * 180 + i * width, -90 + h * 180 + (i + 1) * width, c)
                for h in (0, 1) for i, c in enumerate(steps)]
    return {"left": walk(steps_left), "right": walk(steps_right)}


# Variant "sketch": the fountain's own colours, arranged the way the Dana Barlev concept sketch
# (research/user-reference-agam-menorah.png, style direction only) uses them at this scale:
# lower drums as continuous gradients with no white, R3/R4 unchanged (colour / white alternation),
# a plain white top drum, and a white stem and foot. Left faces run one step ahead of the right
# faces, so the two pictures differ and head-on the gradient looks smooth.
SKETCH_OVERRIDES: dict[str, dict[str, list]] = {
    "drum5_R5_dome": {"left": [(-90, 270, "white")], "right": [(-90, 270, "white")]},
    "drum2_R2": _gradient(("coral", "brick", "navy", "blue", "light_blue", "orange"),
                          ("orange", "coral", "brick", "navy", "blue", "light_blue")),
    "drum1_R1": _gradient(("coral", "orange", "yellow", "green", "teal", "brick"),
                          ("brick", "coral", "orange", "yellow", "green", "teal")),
}
SKETCH_OTHER = {"STEM_COLOURS": ("white",), "PLINTH_PAINT": "white", "DOME_PAINT": "white", "TOPS": "white"}
VARIANT = "fountain"  # or "sketch"


def sectors(ring: str, variant: str | None = None) -> dict[str, list]:
    variant = variant or VARIANT
    if variant == "sketch" and ring in SKETCH_OVERRIDES:
        return SKETCH_OVERRIDES[ring]
    return SECTORS[ring]


def tooth_count(tip_diameter: float) -> int:
    return max(6, round(math.pi * tip_diameter / TOOTH_PITCH))


def front_tooth(teeth: int) -> int:
    pitch = 2 * math.pi / teeth
    return int(math.floor((math.radians(-90) % (2 * math.pi)) / pitch))


def face_centre_concept(teeth: int, side: str, k: int) -> float:
    """Concept angle of the middle of face k (mirrors paint_program.face_span)."""
    pitch = 360.0 / teeth
    start = ((k + front_tooth(teeth)) % teeth) * pitch
    split = start + TOOTH_LEAN * pitch
    lo, hi = (start, split) if side == "left" else (split, start + pitch)
    return ((lo + hi) / 2 + 90.0) % 360.0


def paint_at(ring: str, side: str, fountain_deg: float, variant: str | None = None) -> str:
    a = (fountain_deg + 90.0) % 360.0 - 90.0  # into -90 .. 270
    for start, end, name in sectors(ring, variant)[side]:
        if start <= a < end:
            return name
    raise ValueError(f"{ring} {side}: no sector covers {a:.1f} deg")


def faces(ring: str, side: str, teeth: int, variant: str | None = None) -> tuple[str, ...]:
    """Paint of face k = 0 .. teeth-1, for config.Stripes(colours=..., run=1)."""
    return tuple(paint_at(ring, side, face_centre_concept(teeth, side, k) - ROTATION, variant) for k in range(teeth))


def check_sectors() -> list[str]:
    problems = []
    for variant in ("fountain", "sketch"):
        for ring in SECTORS:
            for side, secs in sectors(ring, variant).items():
                edges = [s for s, _, _ in secs] + [secs[-1][1]]
                if edges[0] != -90 or abs(edges[-1] - 270) > 1e-9 or any(abs(a[1] - b[0]) > 1e-9 for a, b in zip(secs, secs[1:])):
                    problems.append(f"{variant} {ring} {side}: sectors must tile -90..270")
                problems += [f"{variant} {ring} {side}: unknown paint {n}" for _, _, n in secs if n not in PAINTS]
    return problems


def luminance(hex_: str) -> float:
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(PAINTS[a][0]), luminance(PAINTS[b][0])), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def emblem_report(teeth3: int) -> list[str]:
    lines = []
    for name, (angle, half, paints) in EMBLEMS.items():
        under = set()
        for side in ("left", "right"):
            for deg in range(int(angle - half), int(angle + half) + 1):
                under.add(paint_at("drum3_R3", side, deg - ROTATION))
        worst = min(contrast(paints[0], u) for u in under)
        lines.append(f"{name:8s} {paints[0]:7s} on {sorted(under)}  worst contrast {worst:.2f}")
    return lines


def svg(tables: dict[str, dict[str, tuple[str, ...]]]) -> str:
    fw, rh, cx = 8, 24, 560
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 470" font-family="Arial" font-size="12">',
           '<rect width="1200" height="470" fill="#fff"/>',
           '<text x="10" y="20" font-size="15" font-weight="bold">Fountain colour program, rings unrolled from the model front (k = 0), left to right</text>',
           '<text x="10" y="38" fill="#555">Upper row LEFT faces, lower row RIGHT faces. Fountain angle = model angle - 207.</text>']
    y = 55
    for ring in ("drum5_R5_dome", "drum4_R4", "drum3_R3", "drum2_R2", "drum1_R1"):
        t = len(tables[ring]["left"])
        out.append(f'<text x="10" y="{y + 20}">{ring.split("_")[1]} ({t})</text>')
        for kr in range(-(t // 2), t - t // 2):
            k = kr % t
            x = cx + kr * fw
            for row, side in enumerate(("left", "right")):
                out.append(f'<rect x="{x}" y="{y + row * rh}" width="{fw}" height="{rh}" fill="{PAINTS[tables[ring][side][k]][0]}" stroke="#ddd" stroke-width="0.3"/>')
        y += 2 * rh + 16
    out.append(f'<line x1="{cx + fw / 2}" y1="48" x2="{cx + fw / 2}" y2="{y}" stroke="#333" stroke-dasharray="3 3"/>')
    out.append(f'<text x="{cx + 8}" y="{y + 12}">FRONT (HANUKKAH)</text>')
    y += 34
    for i, (name, (hex_, _, _)) in enumerate(PAINTS.items()):
        x = 10 + (i % 8) * 148
        yy = y + (i // 8) * 30
        out += [f'<rect x="{x}" y="{yy}" width="22" height="22" fill="{hex_}" stroke="#999"/>',
                f'<text x="{x + 27}" y="{yy + 15}">{name} {hex_}</text>']
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    problems = check_sectors()
    if problems:
        raise SystemExit("\n".join(problems))
    out = {"rotation": ROTATION, "paints": {k: v[0] for k, v in PAINTS.items()},
           "emblems": {k: v[2] for k, v in EMBLEMS.items()}, "variants": {}}
    for variant, other in (("fountain", OTHER), ("sketch", SKETCH_OTHER)):
        tables = {}
        for ring, ratio in DIAMETER_RATIO.items():
            teeth = tooth_count(ratio * MAIN_DIAMETER)
            tables[ring] = {side: faces(ring, side, teeth, variant) for side in ("left", "right")}
            print(f"{variant:8s} {ring:15s} {teeth:3d} teeth  front L={tables[ring]['left'][0]:10s} R={tables[ring]['right'][0]}")
        out["variants"][variant] = {"faces": tables, "other": other}
        suffix = "" if variant == "fountain" else "_sketch"
        (HERE / f"fountain_colour_program{suffix}.svg").write_text(svg(tables), encoding="utf-8")
    print("\n".join(emblem_report(81)))
    (HERE / "fountain_colour_program.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote fountain_colour_program.json, .svg and _sketch.svg")


if __name__ == "__main__":
    main()
