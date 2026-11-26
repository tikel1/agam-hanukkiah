"""contact_sheet.png (every key frame in film order, with time and beat) and colour_script.png (the film's
colour along its 128 seconds: ground band, dominant colours per key frame, act names).

Usage: python sheets.py   (after build.py)
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import frames
from style import BOARD, ENGINE, INK, PAPER

FR = BOARD / "frames"
FONT = str(ENGINE / "assets" / "fonts" / "SecularOne-Regular.ttf")
DURATION = 129.5
BEATS = [  # start second, label (English, so PIL needs no right-to-left shaping)
    (0, "1 Hello"), (6.5, "2 Works that change"), (23, "3 Fire and Water"), (38, "4 Fire to Hanukkah"),
    (55.5, "5 Learning"), (62.5, "6 AI"), (78.5, "7 The design"), (97, "8 Print"), (103, "9 Paint"),
    (112, "10 Tribute"),
]
ACTS = [(0, 23, "DAY: paper + spectrum"), (23, 38, "WATER: sky, cream"), (38, 55.5, "FIRE: amber"),
        (55.5, 62.5, "PAPER"), (62.5, 78.5, "SCREEN: navy"), (78.5, 112, "COLOUR: paper, studio"),
        (112, 129.5, "NIGHT: navy + candle gold")]


def seconds(t: str) -> float:
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def contact_sheet(items: list[dict]) -> None:
    tw, th, gap, cols = 300, 533, 22, 9
    rows = (len(items) + cols - 1) // cols
    top = 120
    sheet = Image.new("RGB", (cols * (tw + gap) + gap, top + rows * (th + 70 + gap) + gap), "#D9D6CC")
    d = ImageDraw.Draw(sheet)
    d.text((gap, 34), "Fire and Water: v2 storyboard, 36 key frames, 1080x1920, one continuous take", font=font(44),
           fill=INK)
    for i, f in enumerate(items):
        x = gap + (i % cols) * (tw + gap)
        y = top + (i // cols) * (th + 70 + gap)
        im = Image.open(FR / f"{f['name']}.png").convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (x, y))
        beat = int(f["name"][1:3])
        d.rectangle((x, y + th, x + tw, y + th + 58), fill=INK)
        d.text((x + 12, y + th + 8), f"{f['name']}", font=font(28), fill=PAPER)
        d.text((x + tw - 12, y + th + 8), f["time"], font=font(28), fill="#F2C94C", anchor="ra")
        del beat
    sheet.save(BOARD / "contact_sheet.png")


def dominant(path: Path, bg: str, k: int = 5) -> list[tuple]:
    """The frame's accent colours: pixels snapped to the film palette (ground excluded), most area first."""
    from style import F, FLAME, GOLD, INK as _INK, NIGHT
    palette = list(dict.fromkeys(list(F.values()) + list(FLAME.values()) + [GOLD, _INK, NIGHT, "#FFFFFF"]))
    rgb = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in palette]
    ground = tuple(int(bg[i:i + 2], 16) for i in (1, 3, 5))
    im = Image.open(path).convert("RGB").resize((108, 170))
    counts: dict = {}
    for px in im.getdata():
        if sum((a - b) ** 2 for a, b in zip(px, ground)) < 300:
            continue
        best = min(range(len(rgb)), key=lambda i: sum((a - b) ** 2 for a, b in zip(px, rgb[i])))
        if sum((a - b) ** 2 for a, b in zip(px, rgb[best])) < 1800:
            counts[best] = counts.get(best, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:k]
    return [(rgb[i], n) for i, n in top]


def colour_script(items: list[dict]) -> None:
    W, H, left, right = 3000, 900, 40, 40
    span = W - left - right
    x_of = lambda t: left + span * t / DURATION
    img = Image.new("RGB", (W, H), "#D9D6CC")
    d = ImageDraw.Draw(img)
    d.text((left, 24), "Colour script: one take from day paper to candle night (seconds 0-129.5)", font=font(40), fill=INK)
    times = [seconds(f["time"]) for f in items]
    # ground band: each key frame's background colour until the next key frame
    for i, f in enumerate(items):
        t0 = 0 if i == 0 else (times[i - 1] + times[i]) / 2
        t1 = DURATION if i == len(items) - 1 else (times[i] + times[i + 1]) / 2
        d.rectangle((x_of(t0), 330, x_of(t1), 470), fill=f["bg"])
    # dominant colours of each key frame, stacked under its time
    for i, f in enumerate(items):
        cols = [c for c, n in dominant(FR / f"{f['name']}.png", f["bg"]) if n > 40][:5]
        x = x_of(times[i])
        for j, c in enumerate(cols):
            d.rectangle((x - 30, 500 + j * 52, x + 30, 548 + j * 52), fill=c)
    # thumbnails above, at their times
    for i, f in enumerate(items):
        x = x_of(times[i])
        th = Image.open(FR / f"{f['name']}.png").convert("RGB").resize((90, 160), Image.LANCZOS)
        img.paste(th, (int(x - 45), 100 + (i % 2) * 60))
        d.line((x, 260 + (i % 2) * 60, x, 330), fill=INK, width=2)
    for t, label in BEATS:
        d.line((x_of(t), 470, x_of(t), 790), fill=INK, width=3)
        d.text((x_of(t) + 8, 770), label, font=font(26), fill=INK)
    for t0, t1, label in ACTS:
        d.rectangle((x_of(t0) + 2, 830, x_of(t1) - 2, 880), fill=INK)
        d.text((x_of(t0) + 12, 838), label, font=font(26), fill=PAPER)
    img.save(BOARD / "colour_script.png")


def main() -> None:
    items = frames.ALL()
    contact_sheet(items)
    colour_script(items)
    print("wrote contact_sheet.png and colour_script.png")


if __name__ == "__main__":
    main()
