"""Key frames, beats 1-5: hello, the works that change, the fountain, from fire to Hanukkah, learning."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

import models
import props as P
from geom import Camera, PhotoSkin, Picture, Pleats, draw_groups, flame
from style import (DOTS, F, GROUND, INK, PAPER, SPECTRUM, TITLE_TOP, dot_rule, mix, small_line, title)

PH = "../photos/treated/"
# Real photos are shown untouched (crop only), inside a stripe frame; see props.photo_card.
AGAM = PH + "agam_portrait.jpg"
AGAM_1991 = PH + "agam_portrait_face.jpg"   # Agam only as an older man (user 26.11)
CIRCLES = PH + "work_circles.jpg"
WALL = PH + "work_wall.jpg"
FOUNTAIN_PHOTO = PH + "fountain_2010.jpg"
NYC = PH + "menorah_nyc.jpg"
TRIBUTE = PH + "agam_tribute.jpg"
# Kan 11 archive clips (stills stand in for the moving clip in the key frames): v2/storyboard/footage/
KAN_DAY = "../footage/kan_fountain_day.png"
KAN_FIRE = "../footage/kan_fire_on_water.png"

CREDIT = {
    "kaprov": "Photo: Edward Kaprov, CC BY-SA 3.0",
    "batkin": "Photo: Stanley Batkin, CC BY-SA 3.0",
    "sheba": "Agam at Sheba. Photo: Talmoryair, CC BY 3.0",
    "museum": "Agam Museum. Photo: Yaakov (Wikimedia), CC0",
    "teicher": "Photo: Dr. Avishai Teicher, PikiWiki, CC BY 2.5",
    "chabad": "Photo: Chabad Lubavitch, CC BY 2.0",
}


def frame(name, time, body, defs, bg=PAPER, sub=None, dark=False):
    return {"name": name, "time": time, "body": body, "defs": defs, "bg": bg, "sub": sub, "dark": dark}


def stripe(i: int) -> str:
    return SPECTRUM[i % 12]


def flat_image(img: Image.Image, href: str) -> str:
    return href


def _picture(cols: int, rows: int, ground, shape) -> Picture:
    """Picture one column per pleat: ground(col) colour, then shape(draw, cols, rows) on top."""
    scale = 40
    img = Image.new("RGB", (cols * scale, rows))
    d = ImageDraw.Draw(img)
    for c in range(cols):
        d.rectangle((c * scale, 0, (c + 1) * scale, rows), fill=ground(c))
    shape(d, cols * scale, rows)
    small = Image.new("RGB", (cols, rows))
    for c in range(cols):
        small.paste(img.crop((c * scale + scale // 2, 0, c * scale + scale // 2 + 1, rows)), (c, 0))
    return Picture(small)


FAN_COLS = 26
WARM = [F["yellow"], F["orange"], F["yellow"], F["coral"]]
COOL = [F["blue"], F["light_blue"], F["periwinkle"], F["light_blue"]]
FAN_A = _picture(FAN_COLS, 240, lambda c: WARM[c % 4],
                 lambda d, w, h: d.ellipse((w / 2 - 300, h / 2 - 72, w / 2 + 300, h / 2 + 72), fill=F["coral"]))
FAN_B = _picture(FAN_COLS, 240, lambda c: COOL[c % 4],
                 lambda d, w, h: (d.rectangle((w / 2 - 70, h / 2 - 78, w / 2 + 70, h / 2 + 78), fill=F["green"]),
                                  d.rectangle((w / 2 - 230, h / 2 - 24, w / 2 + 230, h / 2 + 24), fill=F["green"])))


# ---- beat 1 -----------------------------------------------------------------------------------------------
def b01_1():
    defs: list = []
    cam = Camera(target=(0, 615, 0), cx=540, cy=845)
    # written like Hebrew, right to left: the right stripes are done, two brushes are still drawing
    progress = [0.0, 0.0, 0.0, 0.1, 0.26, 0.42, 0.6, 0.77, 0.9, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    n = len(progress)
    sheet = Pleats(pleats=n, length=936, height=1230, base=0, skin_a=lambda i: stripe(n - 1 - i), skin_b=PAPER,
                   shaded=False, reveal=lambda i: progress[i], depth_ratio=0.0001)
    body = draw_groups(cam, [sheet], defs)
    pitch = 936 / n
    for i, ang in ((4, -16), (7, 12)):
        x = 72 + (i + 0.25) * pitch
        body += P.marker(x, 230 + 1230 * progress[i], angle=ang, colour=stripe(n - 1 - i), scale=1.0)
    return frame("b01_1", "0:01.5", body, defs, sub=["שלום! אנחנו ליבי ונעמי,", "ואנחנו מאוד אוהבות אמנות."])


def b01_2():
    defs: list = []
    body = P.photo_card(150, 650, 780, 790, AGAM, defs, open_=0.64, clip_id="c012")
    body += P.credit(CREDIT["kaprov"], 966, 1440)
    body += title(["יעקב"], 540, TITLE_TOP - 10, cap=140) + title(["אגם"], 540, TITLE_TOP + 180, cap=140, dot_offset=4)
    return frame("b01_2", "0:05.5", body, defs, sub=["תכירו את", "יעקב אגם!"])


# ---- beat 2 -----------------------------------------------------------------------------------------------
def b02_1():
    defs: list = []
    body = P.photo_card(150, -540, 780, 790, AGAM, defs, clip_id="c021a")
    body += P.photo_card(250, 380, 580, 560, CIRCLES, defs, offset=4, clip_id="c021b")
    body += P.photo_placeholder(150, 1030, 780, 410, "הבנות במוזיאון אגם", defs, offset=8, clip_id="c021c")
    for k in range(9):
        body += P.dot(1040, 520 + k * 46, 14 if k == 3 else 7, DOTS[k] if k == 3 else mix(INK, PAPER, 0.6))
    return frame("b02_1", "0:10", body, defs, sub=["ואחד ממייסדי", "האמנות הקינטית."])


def b02_2():
    """Kinetic art in one sentence: the title builds, and our own drawing in his style turns as the eye walks by."""
    defs: list = []
    body = P.stripe_frame(120, 640, 840, 760, 22, 11, offset=7)
    body += f'<rect x="142" y="662" width="796" height="716" fill="{PAPER}"/>'
    body += _fan(14, 0.65, defs, length=700, height=600, cy=1020, base_y=300)
    body += P.eye_track(540, 1440, 620, 0.35)
    body += title(["אמנות"], 540, TITLE_TOP - 20, cap=130) + title(["קינטית"], 540, TITLE_TOP + 160, cap=130, dot_offset=5)
    return frame("b02_2", "0:12", body, defs, sub=["זו אמנות שזזה,", "או שמשתנה כשזזים לידה."])


def _fan(yaw, depth, defs, length=900, height=760, pitch=10.0, cx=540, cy=1000, bend=0.0, base_y=380):
    cam = Camera(yaw=yaw, pitch=pitch, target=(0, base_y, 0), cx=cx, cy=cy)
    sheet = Pleats(pleats=FAN_COLS, length=length, height=height, skin_a=FAN_A, skin_b=FAN_B, depth_ratio=depth,
                   bend=bend, back=mix(F["white"], INK, 0.12))
    return draw_groups(cam, [sheet], defs)


def b02_3():
    defs: list = []
    # the fold travels across the sheet: the right half is already folded, the left half still flat
    cam = Camera(yaw=0, pitch=14, target=(0, 380, 0), cx=540, cy=1000)
    half = FAN_COLS // 2

    class Shift(Picture):
        def __init__(self, base, offset):
            self.base, self.offset = base, offset

        def runs(self, col):
            return self.base.runs(col + self.offset)
    flat = Pleats(pleats=half, length=460, height=760, skin_a=FAN_A, skin_b=FAN_A, depth_ratio=0.0001,
                  centre=(-230 - 120, 0, 0))
    folded = Pleats(pleats=half, length=300, height=760, skin_a=Shift(FAN_A, half), skin_b=Shift(FAN_B, half),
                    depth_ratio=1.25, centre=(30, 0, 0))
    body = draw_groups(cam, [flat, folded], defs)
    body += P.dotted_arc(150, 1450, 900, 1450, 0, n=14)
    return frame("b02_3", "0:15", body, defs, sub=["הסוד שלו:", "קפלים, כמו במניפה."])


def b02_4():
    defs: list = []
    body = _fan(-36, 0.65, defs)
    body += P.eye_track(540, 1440, 640, -0.85)
    return frame("b02_4", "0:17.5", body, defs, sub=["על צד אחד", "תמונה אחת,"])


def b02_5():
    defs: list = []
    body = _fan(36, 0.65, defs)
    body += P.eye_track(540, 1440, 640, 0.85)
    return frame("b02_5", "0:20", body, defs, sub=["ועל הצד השני,", "תמונה אחרת."])


def b02_6():
    defs: list = []
    body = _fan(0, 0.65, defs, length=1300, height=420, pitch=12, cy=1210, bend=0.62, base_y=200)
    return frame("b02_6", "0:21.5", body, defs, sub=["כל צעד,", "ציור חדש!"])


# ---- beat 3 -----------------------------------------------------------------------------------------------
def _f_cam(**kw):
    base = dict(yaw=0, pitch=5, zoom=1.0, target=(0, 430, 0), cx=540, cy=1020)
    base.update(kw)
    return Camera(**base)


def b03_1():
    defs: list = []
    body = P.photo_card(130, 620, 820, 585, KAN_DAY, defs, open_=0.86, offset=2, clip_id="c031")
    body += P.video_tag(130, 620, 820, "כאן 11")
    body += P.credit(CREDIT["teicher"], 952, 1320)
    ring_cam = Camera(pitch=10, zoom=0.62, target=(0, 0, 0), cx=540, cy=1405)
    body += models.ellipse_xz(ring_cam, 0, 0, 0, 640, mix(F["light_blue"], PAPER, 0.15))
    ring = Pleats(pleats=72, length=2 * math.pi * 410, height=138, base=8, bend=1.0, skin_a=models.spectrum_from(0, 72),
                  skin_b=F["white"], cap="#F4F1E4", depth_ratio=0.6)
    body += draw_groups(ring_cam, [ring], defs)
    body += title(["אש", "ומים"], 540, TITLE_TOP)
    body += small_line("1986", 540, TITLE_TOP + 240, size=52, rtl=False)
    return frame("b03_1", "0:25", body, defs, bg=GROUND["sky"],
                 sub=["ויש לו יצירה גדולה, בכיכר דיזנגוף", "בתל אביב: המזרקה \"אש ומים\"."])


def b03_2():
    defs: list = []
    cam = _f_cam()
    falling = models.fountain(Camera(**{**cam.__dict__}), [], rings=5, drop={4: 300}, pool=False)
    body = models.fountain(cam, defs, rings=4)
    top_only = []
    ring = models.FOUNTAIN_RINGS[4]
    r5 = Pleats(pleats=ring[0], length=2 * math.pi * ring[1], height=ring[2], base=ring[3] + 300, bend=1.0,
                skin_a=models.spectrum_from(ring[4], ring[0]), skin_b=F["white"], cap="#F4F1E4", depth_ratio=0.6)
    ghost = draw_groups(cam, [Pleats(**{**r5.__dict__, "base": ring[3] + 420})], top_only)
    body += P.ghost(ghost, 0, -40, (0.06, 0.12, 0.2))
    body += draw_groups(cam, [r5], defs)
    body += "".join(P.dot(540, 330 + k * 34, 5, DOTS[k % 10]) for k in range(5))
    del falling
    return frame("b03_2", "0:29", body, defs, bg=GROUND["sky"], sub=["היו בה חמש טבעות ענקיות,", "עם פאות משוננות."])


def b03_3():
    defs: list = []
    body = models.fountain(_f_cam(), defs, spin=14, water=1.0, fire=1.0)
    return frame("b03_3", "0:33", body, defs, bg=GROUND["memory"],
                 sub=["פעם, הטבעות שבאמצע הסתובבו לאט,", "המים רקדו, ולמעלה בערה אש."])


def b03_4():
    defs: list = []
    body = models.fountain(_f_cam(zoom=1.12, target=(0, 640, 0), cy=1080), defs, spin=22, water=1.35, fire=1.55)
    return frame("b03_4", "0:37", body, defs, bg=GROUND["memory"], sub=["אש ומים,", "ביחד!"])


# ---- beat 4 -----------------------------------------------------------------------------------------------
def light_rings(cx, cy, radii, alpha=1.0):
    out = []
    for k, r in enumerate(radii):
        n = int(2 * math.pi * r / 46)
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.2
            out.append(P.dot(cx + r * math.cos(a), cy + r * math.sin(a), 7 + k, DOTS[(i + k * 3) % 10]))
    return f'<g opacity="{alpha}">' + "".join(out) + "</g>"


def b04_1():
    defs: list = []
    cam = Camera(pitch=8, zoom=1.6, target=(0, 690, 0), cx=540, cy=1600)
    body = light_rings(540, 1000, (330, 450, 590), 0.9)
    body += models.fountain(cam, defs, spin=30, rings=5, pool=False)
    body += flame(540, 1450, 1180, 640)
    # the real flame on the water, 1986 (Kan 11 archive), framed; it dissolves into our drawn flame behind it
    body += P.photo_card(150, 600, 780, 632, KAN_FIRE, defs, offset=1, clip_id="c041")
    body += P.video_tag(150, 600, 780, "כאן 11 · 1986")
    body += title(["חנוכה"], 540, TITLE_TOP)
    return frame("b04_1", "0:39.5", body, defs, bg=GROUND["amber"], sub=["והאש הזאת הזכירה לנו את חנוכה,", "חג האור!"])


def b04_2():
    defs: list = []
    body = light_rings(540, 1040, (380, 520), 0.55)
    body += P.photo_card(200, 600, 680, 840, NYC, defs, offset=0, clip_id="c042")
    body += P.credit(CREDIT["chabad"], 912, 1440)
    body += title(["ניו", "יורק"], 540, TITLE_TOP - 10)
    body += small_line("הגדולה בעולם", 540, TITLE_TOP + 225, size=50)
    return frame("b04_2", "0:44.5", body, defs, bg=GROUND["amber"],
                 sub=["וגם אגם עצמו עיצב חנוכייה, בניו יורק.", "היא נחשבת לגדולה בעולם."])


def b04_3():
    """Half a second of quiet, the light dims, a real photo of Agam rises in the upper half. The music dips."""
    defs: list = []
    body = light_rings(540, 1260, (300, 420), 0.25)
    body += flame(540, 1440, 300, 160)
    body += P.photo_card(230, 250, 620, 800, TRIBUTE, defs, offset=0, clip_id="c043")
    body += small_line("1928–2026", 540, 1150, size=50, rtl=False)
    return frame("b04_3", "0:49.5", body, defs, bg=mix(GROUND["amber"], GROUND["memory"], 0.7),
                 sub=["ביוני השנה, יעקב אגם הלך לעולמו,", "ורצינו לעשות לו מחווה."])


def b04_4():
    """The idea: the fountain's own flame splits into eight on its wide ring and one on top. The fountain turns
    into a hanukkiah in front of our eyes."""
    defs: list = []
    cam = Camera(pitch=12, zoom=0.92, target=(0, 420, 0), cx=540, cy=1110)
    body = light_rings(540, 620, (170, 240), 0.45)
    body += models.fountain(cam, defs, rings=5, pool=True)
    sx, sy, _ = cam.project(0, 732, 0)
    body += P.sparkle(sx, sy - 330, 60)
    landed = [1.0, 1.0, 0.8, 1.0, 0.62, 1.0, 0.45, 0.9]
    ring_y = models.FOUNTAIN_RINGS[2][3] + models.FOUNTAIN_RINGS[2][2]
    spots = []
    for k in range(8):
        phi = math.radians(-157.5 + k * 45)
        x, y, depth = cam.project(350 * math.sin(phi), ring_y, 350 * math.cos(phi))
        spots.append((depth, k, x, y))
    for depth, k, x, y in sorted(spots):
        body += P.dotted_arc(sx, sy - 160, x, y - 20, (x - 540) * 0.5, colour_offset=k, n=12, r=5)
        t = landed[k]
        bow = (x - 540) * 0.5
        mx, my = (sx + x) / 2 + bow, (sy - 160 + y - 20) / 2 - abs(bow) * 0.4
        fx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * x
        fy = (1 - t) ** 2 * (sy - 160) + 2 * (1 - t) * t * my + t * t * (y - 20)
        body += flame(fx, fy + 18, 80, 38)
    body += flame(sx, sy, 170, 80, glow=True)
    return frame("b04_4", "0:54", body, defs, bg=GROUND["memory"],
                 sub=["ואז עלה לנו רעיון: להפוך", "את המזרקה שלו לחנוכייה!"])


# ---- beat 5 -----------------------------------------------------------------------------------------------
def _page(defs, photo=True):
    body = P.notebook(110, 330, 860, 1130)
    if photo:
        cam = Camera(yaw=0, target=(0, 0, 0), cx=0, cy=0)
        x, y, w, h = 170, 420, 400, 351
        body += P.rect(x - 14, y - 14, w + 28, h + 28, "#FFFFFF", ' stroke="#E3E0D6" stroke-width="2"')
        body += f'<image href="{AGAM_1991}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
        body += P.tape(x + 30, y - 6, 120, 34, -12) + P.tape(x + w - 20, y + h + 4, 120, 34, -8)
        body += P.credit(CREDIT["batkin"], x + w + 28, y + h, vertical=True, size=18)
        for k in range(5):
            body += P.line(640, 470 + k * 58, 900 - (k % 3) * 60, 470 + k * 58, INK, 6)
            body += P.dot(640, 470 + k * 58, 8, DOTS[(k * 3) % 10])
        del cam
    return body


def b05_1():
    defs: list = []
    body = _page(defs)
    for k in range(9):
        y = 1010 - [0, 120, 40, 260, 0, 180, 60, 300, 20][k]
        body += P.dot(260 + k * 70, y, 22, DOTS[k])
        if y < 1000:
            body += P.dotted_arc(260 + k * 70, y - 260, 260 + k * 70, y - 30, 0, colour_offset=k, n=5, r=4)
    return frame("b05_1", "0:56", body, defs, bg="#E6E2D6", sub=["קודם כול,", "ישבנו ללמוד."])


def b05_2():
    """Reading about him: real photos of his works taped into the notebook, one under the other, untouched."""
    defs: list = []
    body = _page(defs)
    cards = [(PH + "work_circles.jpg", 170, 860, 330, 380, -3), (PH + "work_polymorph.jpg", 560, 830, 330, 450, 4),
             (PH + "work_wall.jpg", 300, 1250, 520, 200, -2)]
    for k, (href, x, y, w, h, ang) in enumerate(cards):
        card = (P.rect(x - 12, y - 12, w + 24, h + 24, "#FFFFFF", ' stroke="#E3E0D6" stroke-width="2"')
                + f'<image href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
                + P.tape(x + w / 2, y - 8, 130, 34, -6 + k * 5))
        body += P.rotated(card, ang, x + w / 2, y + h / 2)
    return frame("b05_2", "1:00", body, defs, bg="#E6E2D6",
                 sub=["קראנו על אגם, ולמדנו על הסגנון", "המיוחד שלו, שאין עוד אחד כמוהו."])


FRAMES = [b01_1, b01_2, b02_1, b02_2, b02_3, b02_4, b02_5, b02_6, b03_1, b03_2, b03_3, b03_4, b04_1, b04_2, b04_3,
          b04_4, b05_1, b05_2]
