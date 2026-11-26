"""Key frames, beats 6-10: the AI, the design (tribute + hidden Hanukkah), printing, painting, the tribute."""

from __future__ import annotations

import math

import ai
import models
import props as P
from frames_a import FAN_A, FAN_B, frame
from geom import Camera, Picture, Pleats, box, draw_groups, ellipse_xz, flame, spool_3d
from style import DOTS, F, GOLD, GROUND, INK, NIGHT, PAPER, SPECTRUM, TITLE_TOP, dot_rule, mix, small_line, title

PH = "../photos/treated/"
OWN = "../photos/own/"
TRIBUTE = PH + "agam_tribute.jpg"
CREDIT_TRIBUTE = "Photo: Agam at the fountain (source to confirm, press photo)"


def _hk_cam(**kw):
    base = dict(yaw=-10, pitch=9, zoom=1.12, target=(0, 330, 0), cx=540, cy=1030)
    base.update(kw)
    return Camera(**base)


def wire_ring(cam: Camera, radius: float, y0: float, y1: float, colour: str = F["light_blue"]) -> str:
    """Construction drawing of a ring: top and bottom circles and eight uprights, a dot at each joint."""
    out = []
    for y in (y0, y1):
        pts = [cam.project(radius * math.sin(a), y, radius * math.cos(a))[:2]
               for a in (k * 2 * math.pi / 64 for k in range(65))]
        out.append('<polyline points="' + " ".join(f"{x:.1f},{yy:.1f}" for x, yy in pts) +
                   f'" fill="none" stroke="{colour}" stroke-width="3" stroke-dasharray="10 8"/>')
    for k in range(8):
        a = k * math.pi / 4
        p0 = cam.project(radius * math.sin(a), y0, radius * math.cos(a))
        p1 = cam.project(radius * math.sin(a), y1, radius * math.cos(a))
        out.append(P.line(p0[0], p0[1], p1[0], p1[1], colour, 3))
        out.append(P.dot(p1[0], p1[1], 8, DOTS[k]))
    return "".join(out)


# ---- beat 6 -----------------------------------------------------------------------------------------------
def b06_1():
    """The notebook page becomes a phone screen, and Claude climbs out of it and waves."""
    defs: list = [ai.GLOW_DEFS]
    screen = (P.rect(0, 0, 1080, 1920, "#FFFFFF")
              + "".join(P.rect(330 + k * 46, 1020, 46, 300, SPECTRUM[(k // 2) % 12] if k % 2 == 0 else "#FFFFFF")
                        for k in range(9))
              + "".join(P.line(300, 860 + k * 58, 780, 860 + k * 58, F["light_blue"], 3) for k in range(3)))
    body = ai.data_rain(5)
    body += f'<g filter="url(#glow)"><rect x="270" y="720" width="540" height="720" rx="40" fill="none" stroke="{ai.HOLO}" stroke-width="6"/></g>'
    body += P.phone(270, 720, 540, 720, INK, screen, "ph061", defs)
    body += ai.claude(560, 732, 1.1, "wave")
    body += title(["AI"], 540, TITLE_TOP + 30, cap=190, ink=PAPER, rtl=False)
    return frame("b06_1", "1:03.5", body, defs, bg=GROUND["screen"], sub=["ואז הגיע", "תור ה־AI."], dark=True)


def b06_2():
    """Inside the screen: a hologram table. Claude's beam builds the model ring by ring, still glowing wireframe on top."""
    defs: list = [ai.GLOW_DEFS]
    cam = _hk_cam(pitch=14, zoom=0.84, cy=1160, target=(0, 300, 0), cx=620)
    body = ai.data_rain(11) + ai.holo_floor(cam)
    rings = models.hanukkiah_rings(white=True)
    body += models.cylinder(cam, 0, 0, 34, 0, 230, "#E9E6DC", "#F4F1E4") + models.cylinder(cam, 0, 34, 95, 0, 58, "#E9E6DC", "#F4F1E4")
    body += draw_groups(cam, rings[:3], defs)
    body += ai.holo_ring(cam, 185, 385 + 70, 449 + 70)
    body += ai.holo_ring(cam, 105, 449 + 190, 505 + 190, F["mint"], uprights=10)
    hx, hy = ai.hand_point(180, 1340, 1.1, "wave")
    tx, ty, _ = cam.project(0, 500, 0)
    body += ai.beam(hx, hy, tx, ty, 90)
    body += ai.claude(180, 1340, 1.1, "wave")
    inner = P.photo_placeholder(90, 250, 400, 300, "הבנות מול המחשב", defs, dark=True, offset=4, clip_id="c062")
    body += ai.holo_panel(90, 250, 400, 300, inner)
    return frame("b06_2", "1:07", body, defs, bg=GROUND["screen"],
                 sub=["ביקשנו ממנו עזרה, והוא בנה לנו", "דגמים בתלת־ממד לכל החלקים."], dark=True)


def b06_3():
    """The colour wave climbs the model behind a glowing scan ring; the colouring map floats on a holo screen."""
    defs: list = [ai.GLOW_DEFS]
    cam = _hk_cam(pitch=10, zoom=0.9, cy=920, target=(0, 300, 0), cx=600)
    body = ai.data_rain(17) + ai.holo_floor(cam, 560)
    body += models.hanukkiah(cam, defs, painted=0.66, candles=False)
    body += ai.scan_ring(cam, 400, 0.66 * 505)
    defs.append('<clipPath id="map063"><rect x="150" y="1240" width="820" height="200"/></clipPath>')
    inner = (f'<rect x="150" y="1240" width="820" height="200" fill="{mix(INK, ai.HOLO, 0.15)}"/>'
             f'<image href="{OWN}map_R3_A_band.png" x="-160" y="1250" width="2440" height="283" opacity="0.92" '
             f'preserveAspectRatio="none" clip-path="url(#map063)"/>')
    body += ai.holo_panel(150, 1240, 820, 200, inner)
    body += ai.claude(150, 1120, 0.8, "point", yaw=-40)
    return frame("b06_3", "1:12", body, defs, bg=GROUND["screen"],
                 sub=["הוא גם הראה לנו", "איך החנוכייה תיראה בסוף,"], dark=True)


def b06_4():
    """The wink: everything was a film on a small phone. Claude stands beside it and winks."""
    defs: list = [ai.GLOW_DEFS]
    screen = (P.rect(0, 0, 1080, 1920, PAPER)
              + '<image href="b07_1.png" x="410" y="560" width="360" height="640" preserveAspectRatio="xMidYMid slice"/>')
    body = ai.data_rain(23)
    body += f'<g filter="url(#glow)"><rect x="380" y="470" width="420" height="860" rx="30" fill="none" stroke="{ai.HOLO}" stroke-width="6"/></g>'
    body += P.phone(380, 470, 420, 860, INK, screen, "ph064", defs)
    body += P.timeline_bar(430, 1290 - 40, 320, 0.58)
    body += ai.claude(220, 1330, 1.25, "wink", yaw=-30)
    for x, y in ((900, 560), (930, 1220), (150, 640)):
        body += P.sparkle(x, y, 40)
    return frame("b06_4", "1:16.5", body, defs, bg=GROUND["screen"],
                 sub=["ואפילו הסרט הזה, שאתם רואים עכשיו,", "נעשה בעזרת AI!"], dark=True)


# ---- beat 7 -----------------------------------------------------------------------------------------------
def b07_1():
    defs: list = []
    cam = _hk_cam(yaw=-40, pitch=7, zoom=1.18, cy=1060, target=(0, 340, 0))
    ghost = models.fountain(Camera(**{**cam.__dict__, "zoom": 0.92, "cy": 1080, "target": (0, 420, 0)}), [],
                            silhouette=mix(F["light_blue"], PAPER, 0.45), pool=False)
    body = ghost + models.hanukkiah(cam, defs)
    for y in (cam.project(0, 310, 0)[1],):
        body += P.line(70, y, 200, y, INK, 3, ' stroke-dasharray="4 10"') + P.line(880, y, 1010, y, INK, 3, ' stroke-dasharray="4 10"')
    return frame("b07_1", "1:22", body, defs, sub=["חמש טבעות עם פאות משוננות,", "כמו שלה."])


def _r3_close(yaw, spin=0.0, zoom=2.5, cy=1080, pitch=5, aim=0.0):
    """Close on R3. aim = the ring angle (degrees, after spin) the camera centres on: the picture being read."""
    phi_c = math.radians(aim)
    target = (models.R3_RADIUS * math.sin(phi_c), 310, models.R3_RADIUS * math.cos(phi_c))
    return Camera(yaw=yaw, pitch=pitch, zoom=zoom, target=target, cx=540, cy=cy), spin


def b07_2():
    defs: list = []
    cam, spin = _r3_close(0, zoom=2.2, cy=1190, pitch=3)
    body = models.hanukkiah(cam, defs, spin=spin, candles=False)
    body += title(["מה", "מסתתר?"], 540, TITLE_TOP + 20, cap=112)
    return frame("b07_2", "1:25.5", body, defs, sub=["ובתוך הפאות, הסתרנו", "סמלים של חג החנוכה."])


def b07_3():
    defs: list = []
    cam, _ = _r3_close(-62, zoom=2.9, pitch=3, aim=-20)
    body = models.hanukkiah(cam, defs, spin=-20, candles=False)
    body += P.eye_track(540, 1440, 600, -0.85)
    return frame("b07_3", "1:28.5", body, defs, sub=["מצד אחד מתגלים", "מגן דוד וסביבון,"])


def b07_4():
    defs: list = []
    cam, _ = _r3_close(62, zoom=2.9, pitch=3, aim=22)
    body = models.hanukkiah(cam, defs, spin=22, candles=False)
    body += P.eye_track(540, 1440, 600, 0.85)
    return frame("b07_4", "1:31", body, defs, sub=["ומהצד השני,", "המילה חנוכה וסופגנייה."])


def b07_5():
    defs: list = []
    fan_cam = Camera(yaw=12, pitch=10, target=(0, 230, 0), cx=540, cy=560)
    body = draw_groups(fan_cam, [Pleats(pleats=26, length=760, height=460, skin_a=FAN_A, skin_b=FAN_B)], defs)
    body += dot_rule(540, 905, 900, n=25, r=6)
    cam, _ = _r3_close(12, zoom=1.9, cy=1230)
    body += models.hanukkiah(cam, defs, candles=False)
    body += f'<rect x="0" y="905" width="1080" height="12" fill="{PAPER}" opacity="0"/>'
    return frame("b07_5", "1:35", body, defs, sub=["כל פעם שזזים, מגלים משהו אחר,", "בדיוק כמו באמנות הקינטית של אגם!"])


# ---- beat 8 -----------------------------------------------------------------------------------------------
STUDIO = "#DCE2E6"   # workshop grey-blue: white prints and white rings must read on it


def b08_1():
    defs: list = []
    cam = _hk_cam(yaw=-14, pitch=12, zoom=0.95, cy=1150, target=(0, 300, 0))
    offsets = {"R1": -10, "R2": 50, "R3": 140, "R4": 270, "R5": 380}
    body = models.hanukkiah(cam, defs, white=True, candles=False, offset_y=offsets)
    axis = "".join(P.dot(540, 330 + k * 40, 5, DOTS[k % 10]) for k in range(28))
    body = axis + body
    return frame("b08_1", "1:38", body, defs, bg=STUDIO, sub=["ועכשיו,", "מהמחשב לעולם האמיתי:"])


def a1_printer_3d(cam: Camera, defs: list, done: float) -> str:
    """Our printer in the style of the Bambu Lab A1 (a bed slinger, not an exact model), in the film's flat 3D:
    grey base with a small screen, dark textured bed slid back, arch frame, X gantry, light toolhead with a green
    light, the white spool on top feeding a white tube to the toolhead. The big ring grows on the bed in white."""
    R, H = models.R3_RADIUS, 150 * done
    zg = 150                                   # gantry plane: the bed has slid back so the nozzle is at the ring front
    bz = zg - R                                # bed (and ring) centre
    frame_c, rail, light, dark = "#3A3E46", "#B9BEC2", "#E5E8EA", "#2A2D33"
    out = [box(cam, -470, 470, -150, -32, -260, 260, "#C9CED0", top="#E1E4E6"),
           box(cam, 250, 380, -125, -62, 260, 264, dark),
           box(cam, 262, 368, -116, -71, 264, 266, mix(F["light_blue"], INK, 0.35)),
           box(cam, -410, 410, -32, 0, bz - 410, bz + 410, dark, top="#34383F")]
    for i in range(-9, 10):
        for j in range(-9, 10):
            x, y, _ = cam.project(i * 42, 1, bz + j * 42)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#4A4F58"/>')
    ring = Pleats(pleats=models.R3_TEETH, length=2 * math.pi * R, height=H, base=0, bend=1.0, centre=(0, 0, bz),
                  skin_a="#FBFAF6", skin_b="#EDEBE4", cap="#F4F1E4", depth_ratio=models.R_DEPTH)
    out.append(draw_groups(cam, [ring], defs))
    for k in range(1, 10):
        y = H * k / 10
        pts = [cam.project(R * 1.02 * math.sin(t), y, bz + R * 1.02 * math.cos(t))[:2]
               for t in (j * math.pi / 40 - math.pi / 2 for j in range(41))]
        out.append('<polyline points="' + " ".join(f"{x:.1f},{yy:.1f}" for x, yy in pts) +
                   f'" fill="none" stroke="{mix("#FBFAF6", INK, 0.1)}" stroke-width="2"/>')
    top = 700
    out += [box(cam, -520, -470, -150, top, zg - 40, zg + 40, frame_c),
            box(cam, 470, 520, -150, top, zg - 40, zg + 40, frame_c),
            box(cam, -520, 520, top, top + 48, zg - 40, zg + 40, frame_c),
            box(cam, -470, 470, H + 150, H + 182, zg - 34, zg + 2, rail)]
    hx = 60
    out += [box(cam, hx - 74, hx + 74, H + 34, H + 210, zg - 10, zg + 104, light, front="#F2F3F4"),
            box(cam, hx - 74, hx + 74, H + 186, H + 210, zg - 10, zg + 104, "#C9CED0"),
            box(cam, hx - 12, hx + 12, H + 2, H + 34, zg + 30, zg + 54, dark)]
    gx, gy, _ = cam.project(hx + 40, H + 150, zg + 104)
    out.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7" fill="{F["green"]}"/>')
    nx, ny, _ = cam.project(hx, H + 2, zg + 42)
    out.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{DOTS[9]}"/>')
    out.append(box(cam, -30, 30, top + 48, top + 110, zg - 20, zg + 20, frame_c))        # spool holder
    out.append(spool_3d(cam, 0, top + 200, zg, 120, 90))
    sx, sy, _ = cam.project(60, top + 210, zg)
    tx, ty, _ = cam.project(hx, H + 210, zg + 50)
    out.append(f'<path d="M{sx:.1f},{sy:.1f} C{sx + 260:.1f},{sy - 40:.1f} {tx + 220:.1f},{ty - 260:.1f} {tx:.1f},{ty:.1f}" '
               f'stroke="#9EA4A9" stroke-width="13" fill="none"/>'
               f'<path d="M{sx:.1f},{sy:.1f} C{sx + 260:.1f},{sy - 40:.1f} {tx + 220:.1f},{ty - 260:.1f} {tx:.1f},{ty:.1f}" '
               f'stroke="#FBFAF6" stroke-width="7" fill="none"/>')
    return "".join(out)


def b08_2():
    defs: list = []
    cam = Camera(yaw=-28, pitch=13, zoom=0.86, target=(0, 300, 0), cx=540, cy=1030)
    body = a1_printer_3d(cam, defs, 0.72)
    return frame("b08_2", "1:41", body, defs, bg=STUDIO,
                 sub=["הדפסנו את כל החלקים במדפסת", "תלת־ממד, מפלסטיק ממוחזר."])


# ---- beat 9 -----------------------------------------------------------------------------------------------
class PaintedSoFar(Picture):
    """The colouring map applied column by column: painted columns show picture A, the rest are still white."""

    def __init__(self, base: Picture, painted: set):
        self.base, self.painted = base, painted

    def runs(self, col):
        return self.base.runs(col) if col % models.R3_TEETH in self.painted else [(0.0, 1.0, "#FBFAF6")]


def _paint_ring(cam, defs, painted: set, b_painted: set | None = None):
    ring = models.hanukkiah_rings(white=True)[2]
    ring.skin_a = PaintedSoFar(models.PIC_A, painted)
    ring.skin_b = PaintedSoFar(models.PIC_B, b_painted or set())
    return draw_groups(cam, [ring], defs)


def b09_1():
    """A real photo of the girls painting goes here; our acrylic paint markers lie ready along its foot."""
    defs: list = []
    body = P.photo_placeholder(170, 250, 740, 960, "הבנות צובעות", defs, offset=3, clip_id="c091")
    caps = [F["green"], F["blue"], F["lilac"], F["coral"], F["orange"], F["yellow"]]
    for k, c in enumerate(caps):
        body += P.marker(760 - k * 34, 1262 + k * 40, angle=-86 + k * 1.2, colour=c, scale=0.62)
    return frame("b09_1", "1:44", body, defs, bg=STUDIO, sub=["והחלק הכי כיפי?", "לצבוע!"])


def P_poly(points, fill):
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}"/><polygon points="{pts}" fill="none" stroke="#D6D9DB" stroke-width="2"/>'


def P_chart(x, y):
    """The colouring chart on the sheet: numbered swatches in the fountain palette."""
    keys = ["yellow", "orange", "coral", "brick", "rose", "lilac", "periwinkle", "blue", "light_blue", "mint", "teal", "green"]
    out = []
    for k, key in enumerate(keys):
        cx, cy = x + (k % 6) * 46, y + (k // 6) * 46 + (k % 6) * 6
        out.append(f'<rect x="{cx}" y="{cy}" width="36" height="36" fill="{F[key]}"/>')
    for r in range(0):
        out.append(f'<line x1="{x + 330}" y1="{y + 20 + r * 34}" x2="{x + 700 - r * 60}" y2="{y + 60 + r * 34}" '
                   f'stroke="{INK}" stroke-width="5" opacity="0.5"/>')
    return "".join(out)


def b09_2():
    defs: list = []
    cam, _ = _r3_close(-22, zoom=2.0, cy=1150)
    painted = set(range(26, 56))
    body = _paint_ring(cam, defs, painted)
    tx, ty, _ = cam.project(models.R3_RADIUS * math.sin(math.radians(31)), 280, models.R3_RADIUS * math.cos(math.radians(31)))
    body += P.marker(tx, ty, angle=-12, colour=F["yellow"], scale=1.0)
    body += title(["408"], 540, TITLE_TOP - 20, cap=130, rtl=False) + title(["פסים"], 540, TITLE_TOP + 150, cap=110, dot_offset=5)
    body += small_line("צבועים ביד", 540, TITLE_TOP + 330, size=46)
    body += P.counter_dots(540, 760, 23)
    return frame("b09_2", "1:47", body, defs, bg=STUDIO, sub=["צבענו ביד", "ארבע מאות ושמונה פסים."])


def b09_3():
    defs: list = []
    cam = _hk_cam(yaw=-30, pitch=8, zoom=1.12, cy=1110)
    body = models.hanukkiah(cam, defs, offset_y={"R5": 230}, candles=False)
    ring = models.hanukkiah_rings(offset_y={"R5": 330})[4]
    body += P.ghost(draw_groups(cam, [ring], []), 0, -30, (0.06, 0.12))
    return frame("b09_3", "1:50.5", body, defs, bg=STUDIO, sub=["ובסוף הרכבנו הכול, טבעת על טבעת,", "כמו במזרקה."])


# ---- beat 10 ----------------------------------------------------------------------------------------------
def stars(n=60, seed=7, top=200, bottom=1480):
    out, x = [], seed
    for k in range(n):
        x = (x * 1103515245 + 12345) % 2 ** 31
        px, py = 40 + x % 1000, top + (x // 1000) % (bottom - top)
        out.append(P.dot(px, py, 2.5 + (k % 3), mix(NIGHT, DOTS[k % 10], 0.55)))
    return "".join(out)


def b10_1():
    defs: list = []
    cam = _hk_cam(yaw=34, pitch=8, zoom=1.12, cy=1110)
    body = stars() + models.hanukkiah(cam, defs, lit=5, night=True)
    body += title(["חנוכיית"], 540, TITLE_TOP - 20, cap=120, ink=PAPER) + title(["אש", "ומים"], 540, TITLE_TOP + 150, cap=120,
                                                                              ink=PAPER, dot_offset=4)
    return frame("b10_1", "1:53.5", body, defs, bg=NIGHT, sub=["וכך נולדה", "חנוכיית \"אש ומים\"."], dark=True)


def _small_hk(defs, lit, cy=1250, zoom=0.66):
    cam = _hk_cam(yaw=-8, pitch=8, zoom=zoom, cy=cy, target=(0, 330, 0))
    return models.hanukkiah(cam, defs, lit=lit, night=True)


def _tribute_layout(defs, lit, title_on=True):
    body = P.stripe_frame(50, 200, 980, 1255, band=30, stripe=15, white=NIGHT)
    body += P.photo_card(340, 540, 400, 508, TRIBUTE, defs, offset=0, clip_id="c103", white=NIGHT, band=16, stripe=8)
    body += _small_hk(defs, lit, cy=1300, zoom=0.46)
    if title_on:
        body += title(["מחווה"], 540, 250, cap=100, ink=PAPER) + title(["ליעקב", "אגם"], 540, 385, cap=92, ink=PAPER,
                                                                     dot_offset=6)
    return body


def b10_2():
    """The Agam photo from 4.3 returns; the stripes of 1.1 wrap him and our hanukkiah in one frame."""
    defs: list = []
    body = _tribute_layout(defs, 9)
    return frame("b10_2", "1:57", body, defs, bg=NIGHT, sub=["החנוכייה שלנו היא מחווה,", "מתנה קטנה מאיתנו ליעקב אגם,"], dark=True)


def b10_3():
    defs: list = []
    body = _tribute_layout(defs, 8, title_on=False)
    cam = _hk_cam(yaw=-8, pitch=8, zoom=0.46, cy=1300, target=(0, 330, 0))
    sx, sy, _ = cam.project(0, 505 + 24 + 170, 0)
    body += P.dotted_arc(540, 530, sx, sy - 40, 160, n=16, r=6)
    body += flame(sx + 40, sy - 70, 70, 34, glow=True)
    return frame("b10_3", "2:01", body, defs, bg=NIGHT, sub=["כדי שהאש שלו תמשיך לבעור,", "נר אחרי נר."], dark=True)


def b10_4():
    defs: list = []
    body = stars(40)
    body += title(["חג", "שמח!"], 540, TITLE_TOP - 10, cap=140, ink=PAPER)
    cam = _hk_cam(yaw=34, pitch=8, zoom=0.64, cy=900, target=(0, 330, 0))
    body += models.hanukkiah(cam, defs, lit=9, night=True)
    body += dot_rule(540, 1160, 700, n=19, r=5)
    body += small_line("נעמי קפלן ב'1  ·  ליבי קפלן ד'1", 540, 1240, size=50, fill=PAPER)
    body += small_line("בית ספר כצנלסון, גבעתיים", 540, 1305, size=40, fill=mix(PAPER, NIGHT, 0.25))
    body += title(["חנוכיית", "אש", "ומים"], 540, 1360, cap=52, ink=PAPER)  # our logo, drawn in the same letters
    return frame("b10_4", "2:05", body, defs, bg=NIGHT, sub=["חג חנוכה", "שמח!"], dark=True)


FRAMES = [b06_1, b06_2, b06_3, b06_4, b07_1, b07_2, b07_3, b07_4, b07_5, b08_1, b08_2, b09_1, b09_2, b09_3,
          b10_1, b10_2, b10_3, b10_4]
