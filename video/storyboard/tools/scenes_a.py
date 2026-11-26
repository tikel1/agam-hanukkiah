"""Key frames for scenes 1-6. Each scene returns {frame_id: svg_body} and a sample subtitle."""

from __future__ import annotations

from shapes import (basin, circle, clip_group, flame, hand, ny_menorah, person, poly, rect, ring_stack,
                    stack_height, stripes, water_jets)
from style import (ASSET, DOTS, FOUNTAIN as F, H, NAVY, NAVY_D, PAPER, SPECTRUM, W, WHITE, digits, label, title)

BAND = [F["blue"], F["yellow"], F["coral"], F["teal"], F["lilac"], F["orange"], F["light_blue"], F["green"]]


def scene01() -> dict:
    head = title(["יעקב", "אגם"], 1000, 110)
    field_a = stripes(0, 330, 1150, 520, BAND, 54, white=PAPER, skew=60)
    a = field_a + hand(1330, 520, -8, 1.0) + head
    field_b = stripes(0, 330, W, 520, BAND, 54, white=PAPER, skew=60)
    disc = clip_group('<circle cx="960" cy="590" r="250"/>', rect(700, 340, 520, 500, F["coral"]))
    b = field_b + disc + circle(960, 590, 250, F["coral"]) + hand(1500, 560, -8, 0.9) + head
    return {"a": a, "b": b, "sub": "קוראים לו יעקב אגם. הוא היה אמן ישראלי."}


def _polymorph(f: float, x0: float = 260, y0: float = 340, width: float = 1400, height: float = 470) -> str:
    """Folded sheet seen from an angle: f = share of the A (red) faces that is visible."""
    period, out, x = 116.0, [], x0
    reds, blues = [F["coral"], F["brick"]], [F["blue"], F["periwinkle"]]
    n = 0
    while x < x0 + width:
        wa, wb = period * f, period * (1 - f)
        skew = 26
        for wid, col in ((wa, reds[n % 2]), (wb, blues[n % 2])):
            if wid > 0.5:
                out.append(poly([(x, y0), (x + wid, y0 + 8), (x + wid, y0 + height - 8), (x, y0 + height)], col))
                x += wid
        n += 1
        out.append(rect(x - 3, y0 + 4, 6, height - 8, WHITE))
    return "".join(out)


def _eye(x: float) -> str:
    arc = "".join(circle(430 + i * 105, 868 - 18 * (1 - ((i - 5.5) / 5.5) ** 2), 6, DOTS[i % 10]) for i in range(12))
    return arc + poly([(x - 34, 896), (x + 34, 896), (x, 846)], NAVY_D) + circle(x, 826, 16, NAVY_D)


def scene02() -> dict:
    head = title(["פולימורף"], 960, 90, cap=140)
    sub = "מצד אחד רואים תמונה אחת. מהצד השני, תמונה אחרת."
    return {"a": _polymorph(1.0) + _eye(430) + head, "b": _polymorph(0.0) + _eye(1490) + head,
            "c": _polymorph(0.5) + _eye(960) + head, "sub": sub}


def _fountain(phases: list[float], flame_args: tuple, jets: tuple, top: float = 330, cx: float = 960) -> str:
    stack = ring_stack(cx, top, phases=phases, scale=1.06)
    base = top + stack_height(1.06)
    wet = water_jets(cx, base - 30, *jets) + basin(cx, base + 6, 1060)
    return wet + stack + flame(cx, top + 6, *flame_args)


def scene03() -> dict:
    head = title(["אש", "ומים"], 960, 70, cap=130)
    full = ring_stack(960, 230, scale=1.1) + basin(960, 820, 1100)
    slide = ring_stack(960, 230, scale=1.1, offsets=[-640, 560, 0, -520, 700]) + basin(960, 820, 1100)
    return {"a": full + head, "b": slide + head, "sub": 'בכיכר דיזנגוף יש מזרקה שלו. קוראים לה "אש ומים".'}


def scene04() -> dict:
    year = digits("1986", 1640, 90, cap=100)
    a = _fountain([0, 40, 80, 40, 0], (130, 70, 6), (700, 330), top=300) + year
    b = _fountain([30, 10, 55, 90, 20], (190, 84, -16), (700, 450), top=300) + year
    return {"a": a, "b": b, "sub": "הטבעות סבבו, המים קפצו, ומלמעלה עלתה להבת אש."}


def _candles(cx: float, base: float, lit: int, raise_shamash: bool = True) -> str:
    out = []
    for i in range(9):
        x = cx + (i - 4) * 120
        sham = i == 4
        top = base - (250 if sham else 160)
        out.append(rect(x - 20, top, 40, base - top, F["blue"] if not sham else F["periwinkle"]))
        out.append(rect(x - 30, base - 18, 60, 18, F["yellow"]))
        if i < lit or sham:
            out.append(flame(x, top - 6, 78 if sham else 66, 38, lean=5 if i % 2 else -5))
    return "".join(out)


def scene05() -> dict:
    head = title(["חנוכה"], 960, 80, cap=140)
    trail = "".join(circle(560 + i * 62, 520 - 90 * ((i - 3) / 3) ** 2 + 60, 12 + (i % 3) * 3, DOTS[i % 10]) for i in range(7))
    src = (ring_stack(380, 520, scale=0.62, visible=2) + flame(380, 526, 230, 120))
    a = src + trail + _candles(1190, 800, lit=9) + head
    people = person(700, 840, 90, F["periwinkle"]) + person(760, 840, 70, F["coral"]) + person(1180, 840, 85, F["teal"])
    b = ny_menorah(960, 840, 520) + people + label("החנוכייה הגדולה בעולם, ניו יורק", 960, 290, 54) + head
    return {"a": a, "b": b, "sub": "רצינו לקחת את האש מהמזרקה ולהפוך אותה לנרות."}


def _notebook(fill_w: float, dots_out: bool, palette: bool = True) -> str:
    cover = rect(520, 250, 880, 630, F["periwinkle"])
    page = rect(560, 272, 800, 586, WHITE)
    spiral = "".join(circle(548, 300 + i * 40, 11, F["light_blue"]) for i in range(14))
    ink = clip_group('<rect x="560" y="272" width="800" height="586"/>',
                     stripes(600, 272, fill_w, 586, SPECTRUM, 40, white=WHITE))
    pal = "".join(circle(1560 + (i % 3) * 64, 330 + (i // 3) * 70, 22, c) for i, c in enumerate(list(F.values())[:15]))
    if dots_out:
        pal = "".join(circle(1560 + (i % 3) * 64 - i * 18, 330 + (i // 3) * 70 + (i % 4) * 22, 22, c)
                      for i, c in enumerate(list(F.values())[:15]))
    return cover + page + spiral + ink + (pal if palette else "")


def scene06() -> dict:
    head = title(["ללמוד"], 700, 80, cap=130)
    note = label("ככה התחלנו:", 1250, 170, 56)
    rings = "".join(rect(1470 + 0, 300 + i * 78, 300, 52, WHITE) + stripes(1476, 306 + i * 78, 288, 40,
                    [SPECTRUM[(i * 3 + k) % 12] for k in range(3)], 24, white=WHITE) for i in range(5))
    return {"a": _notebook(360, False) + head + note, "b": _notebook(760, False, palette=False) + rings + head + note,
            "sub": "קראנו על אגם, הסתכלנו בצבעים שלו, וחקרנו איך המזרקה עובדת."}
