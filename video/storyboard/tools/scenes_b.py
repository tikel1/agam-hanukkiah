"""Key frames for scenes 7-11."""

from __future__ import annotations

from shapes import (brush, circle, clip_group, flame, flat_hanukkiah, hand, poly, rect, recycle, ring,
                    ring_close_up, ring_stack, stripes)
from style import (ASSET, DOTS, FOUNTAIN as F, H, NAVY, NAVY_D, PAPER, SPECTRUM, W, WHITE, digits, label, title)

BAND = [F["blue"], F["yellow"], F["coral"], F["teal"], F["lilac"], F["orange"], F["light_blue"], F["green"]]


def _img(href: str, x: float, y: float, w: float, h: float, extra: str = "") -> str:
    return f'<image href="{ASSET}/{href}" x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>'


def _disc(href: str, cx: float, cy: float, r: float, iw: float, ih: float, shift: float = 0) -> str:
    img = _img(href, cx - iw / 2 + shift, cy - ih / 2, iw, ih)
    return circle(cx, cy, r + 14, WHITE) + clip_group(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>', img)


def scene07() -> dict:
    head = title(["בינה"], 1180, 80, cap=130)
    note = label("מלאכותית בנתה:", 800, 170, 54)
    chips = label("דגמים  ·  צבעים  ·  לוגו", 960, 872, 46)
    pale = ["#CFCBBE", "#E6E3D8"]
    a = flat_hanukkiah(960, 250, 0.62, mono=pale) + head + note + chips
    sheet = (rect(250, 420, 330, 300, WHITE) + stripes(262, 432, 306, 276, SPECTRUM, 34, white=WHITE))
    mark = title(["אש", "ומים"], 1560, 480, cap=70)
    b = (sheet + flat_hanukkiah(960, 250, 0.62) + mark + circle(1560, 640, 12, F["coral"])
         + head + note + chips)
    return {"a": a, "b": b, "sub": "ביקשנו עזרה מבינה מלאכותית. היא בנתה לנו את כל הדגמים."}


def _panel(side: str, caption_dots: float) -> str:
    arc = "".join(circle(560 + i * 80, 878 - 14 * (1 - ((i - 5.5) / 5.5) ** 2), 6, DOTS[i % 10]) for i in range(12))
    eye = poly([(caption_dots - 30, 904), (caption_dots + 30, 904), (caption_dots, 860)], NAVY_D)
    return ring_close_up(960, 330, 1000, 300, side) + arc + eye


def scene08() -> dict:
    sub = "מצד אחד מגן דוד וסביבון. מהצד השני סופגנייה!"
    return {"a": _panel("left", 560), "b": _panel("right", 1360), "c": _panel("back", 960), "sub": sub}


def _printer(cx: float, nozzle_y: float) -> str:
    return (rect(cx - 520, 190, 36, 600, F["periwinkle"]) + rect(cx + 484, 190, 36, 600, F["periwinkle"])
            + rect(cx - 520, nozzle_y - 90, 1040, 34, F["blue"])
            + rect(cx - 30, nozzle_y - 56, 60, 30, F["blue"])
            + poly([(cx - 30, nozzle_y - 26), (cx + 30, nozzle_y - 26), (cx, nozzle_y + 4)], F["orange"])
            + rect(cx - 600, 790, 1200, 40, F["grey"]))


def _bottle(x: float, y: float) -> str:
    """Flat used-plastic bottle: 'the plastic was already in use'."""
    return (rect(x - 14, y - 150, 28, 44, F["light_blue"]) + poly([(x - 14, y - 106), (x + 14, y - 106), (x + 44, y - 60),
            (x + 44, y + 80), (x - 44, y + 80), (x - 44, y - 60)], F["light_blue"]) + rect(x - 44, y - 10, 88, 40, F["mint"]))


def scene09() -> dict:
    head = title(["הדפסה"], 960, 60, cap=120)
    cols = [F["coral"], F["yellow"], F["teal"], F["blue"]]
    mark = recycle(1580, 470, 140, [F["green"], F["teal"], F["mint"]])
    a = (_printer(800, 640) + ring(800, 600, 640, 190, cols, 30, teeth=18, layers=0.55) + head + mark)
    b = (ring_stack(800, 370, scale=0.8, layers=1.0) + rect(200, 790, 1200, 40, F["grey"]) + head + mark
         + label("פלסטיק ממוחזר", 1580, 720, 46) + _bottle(1300, 520))
    return {"a": a, "b": b, "sub": "הדפסנו הכול במדפסת תלת־ממד, מפלסטיק ממוחזר."}


def scene10() -> dict:
    head = digits("408", 960, 70, cap=130)
    note = label("פאות צבועות ביד", 960, 270, 56)
    card = rect(560, 330, 800, 520, WHITE) + clip_group('<rect x="560" y="330" width="800" height="520"/>',
                                                         stripes(560, 330, 420, 520, SPECTRUM, 42, white=WHITE))
    a = (card + brush(960, 600, 8) + hand(1400, 460, 0, 1.0) + hand(430, 800, 6, 0.8, flip=True) + head + note)
    b = flat_hanukkiah(960, 300, 0.58) + head + note
    return {"a": a, "b": b, "sub": "צבענו ביד, פס אחרי פס, והרכבנו הכול."}


NIGHT_TIPS = [(392, 212), (471, 206), (503, 216), (712, 204), (680, 218), (888, 216), (943, 206), (1002, 211), (698, 28)]


def _inset() -> str:
    """The only 3D render in the video: framed, small, as 'the real result'."""
    view = (f'<svg x="70" y="700" width="260" height="300" viewBox="250 10 900 1040">'
            f'<image href="{ASSET}/own-shots/night_front.png" width="1400" height="1400" '
            f'style="filter:brightness(2.6) saturate(1.2)"/></svg>')
    return rect(58, 688, 284, 324, WHITE) + view


def scene11() -> dict:
    panel = rect(1040, 0, 880, H, PAPER) + stripes(1040, 0, 64, H, BAND, 32)
    head = title(["חנוכיית"], 1500, 140, cap=100) + title(["אש", "ומים"], 1500, 330, cap=100)
    names = (label("נעמי קפלן ב'1", 1500, 610, 54) + label("ליבי קפלן ד'1", 1500, 690, 54)
             + label("בית ספר כצנלסון, גבעתיים", 1500, 780, 42))
    base = rect(0, 0, 1040, H, "#232c5e")
    names += recycle(1500, 870, 34, [F["green"], F["teal"], F["mint"]])
    dots = "".join(circle(120 + i * 190, 80 + (i % 3) * 30, 14, DOTS[i % 10]) for i in range(10))
    lit = lambda k: flat_hanukkiah(520, 90, 0.78, lit=True, flick=k, mono=None)
    a = base + lit(0.0) + _inset() + panel + head + names
    b = base + lit(1.0) + _inset() + panel + head + names + dots
    return {"a": a, "b": b, "sub": 'וכך נולדה חנוכיית "אש ומים". חג חנוכה שמח!'}
