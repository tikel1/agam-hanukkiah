"""2D props in the film's language: straight lines, slight slants, flat palette colours, dots at the ends.

Every prop is a function returning SVG markup in screen pixels.
"""

from __future__ import annotations

import math

from style import DOTS, F, INK, PAPER, SPECTRUM, mix

SMALL_FONT = 'font-family="Secular One"'
SHOW_CREDITS = False


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>'


def dot(x, y, r, fill):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"/>'


def line(x0, y0, x1, y1, colour=INK, width=6, extra=""):
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linecap="butt"{extra}/>')


def rotated(svg: str, angle: float, cx: float, cy: float) -> str:
    return f'<g transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})">{svg}</g>'


def brush(tip_x: float, tip_y: float, angle: float = 0.0, colour: str = F["coral"], scale: float = 1.0) -> str:
    """Flat brush pointing down, its painted tip at (tip_x, tip_y). angle tilts it about the tip."""
    s = scale
    body = (rect(tip_x - 30 * s, tip_y - 70 * s, 60 * s, 70 * s, colour)                    # bristles
            + rect(tip_x - 34 * s, tip_y - 130 * s, 68 * s, 60 * s, "#C9CED0")             # ferrule
            + line(tip_x - 34 * s, tip_y - 112 * s, tip_x + 34 * s, tip_y - 112 * s, "#A9B3B6", 4 * s)
            + f'<polygon points="{tip_x - 26 * s:.1f},{tip_y - 130 * s:.1f} {tip_x + 26 * s:.1f},{tip_y - 130 * s:.1f} '
              f'{tip_x + 14 * s:.1f},{tip_y - 470 * s:.1f} {tip_x - 14 * s:.1f},{tip_y - 470 * s:.1f}" fill="{INK}"/>'
            + dot(tip_x, tip_y - 470 * s, 16 * s, DOTS[1]))
    return rotated(body, angle, tip_x, tip_y)


def pencil(tip_x: float, tip_y: float, angle: float = 0.0, colour: str = INK, scale: float = 1.0) -> str:
    s = scale
    body = (f'<polygon points="{tip_x:.1f},{tip_y:.1f} {tip_x - 18 * s:.1f},{tip_y - 52 * s:.1f} '
            f'{tip_x + 18 * s:.1f},{tip_y - 52 * s:.1f}" fill="#F1D9A8"/>'
            + f'<polygon points="{tip_x:.1f},{tip_y:.1f} {tip_x - 6 * s:.1f},{tip_y - 17 * s:.1f} '
              f'{tip_x + 6 * s:.1f},{tip_y - 17 * s:.1f}" fill="{colour}"/>'
            + rect(tip_x - 18 * s, tip_y - 420 * s, 36 * s, 368 * s, colour)
            + rect(tip_x - 18 * s, tip_y - 452 * s, 36 * s, 32 * s, F["rose"]))
    return rotated(body, angle, tip_x, tip_y)


def credit(text: str, x: float, y: float, colour: str = INK, vertical: bool = True, size: int = 22,
           anchor: str = "start") -> str:
    """Photo credit along the photo's edge. Off (user 26.11: a school film, not published); sources are in
    photos/credits.md. Set SHOW_CREDITS = True to put them back on screen."""
    if not SHOW_CREDITS:
        return ""
    if vertical:
        x += size  # the glyphs sit to the left of the baseline once turned, so keep them off the frame
    tf = f' transform="rotate(-90 {x:.1f} {y:.1f})"' if vertical else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" {SMALL_FONT} font-size="{size}" fill="{colour}" opacity="0.7" '
            f'text-anchor="{anchor}" direction="ltr"{tf}>{text}</text>')


def stripe_frame(x: float, y: float, w: float, h: float, band: float = 26, stripe: float = 13,
                 offset: int = 0, white: str = PAPER) -> str:
    """A frame made of spectrum stripes alternating with white: Agam's colour rhythm as a border."""
    out = []
    k = offset
    # top and bottom bands: vertical stripes
    for yy in (y, y + h - band):
        xx = x
        while xx < x + w - 0.1:
            ww = min(stripe, x + w - xx)
            out.append(rect(xx, yy, ww, band, SPECTRUM[k % 12] if (k % 2 == 0) else white))
            xx += stripe
            k += 1
    # side bands: horizontal stripes
    for xx in (x, x + w - band):
        yy = y + band
        while yy < y + h - band - 0.1:
            hh = min(stripe, y + h - band - yy)
            out.append(rect(xx, yy, band, hh, SPECTRUM[k % 12] if (k % 2 == 0) else white))
            yy += stripe
            k += 1
    return "".join(out)


def tape(cx: float, cy: float, w: float, h: float, angle: float, colour: str = "#F2E6B8") -> str:
    return rotated(rect(cx - w / 2, cy - h / 2, w, h, colour, ' opacity="0.85"'), angle, cx, cy)


def eye_track(cx: float, y: float, width: float, position: float, label_left: str = "", label_right: str = "") -> str:
    """Angle indicator under a polymorph: a dotted arc and an eye-dot at position -1..1 (left..right)."""
    out = []
    n = 15
    for i in range(n):
        t = i / (n - 1) * 2 - 1
        px, py = cx + t * width / 2, y + (t * t) * 26
        out.append(dot(px, py, 5, mix(INK, PAPER, 0.55)))
    px, py = cx + position * width / 2, y + position * position * 26
    out.append(dot(px, py, 20, INK))
    out.append(dot(px, py, 8, PAPER))
    # sight line to the subject
    out.append(line(px, py - 22, cx + (px - cx) * 0.3, y - 150, INK, 3, ' stroke-dasharray="2 12" opacity="0.6"'))
    return "".join(out)


def ghost(svg: str, dx: float, dy: float, opacities=(0.10, 0.18, 0.28)) -> str:
    """Motion trail: copies of a shape behind it (stand-in for the engine's motion blur)."""
    n = len(opacities)
    return "".join(f'<g transform="translate({dx * (n - k):.1f},{dy * (n - k):.1f})" opacity="{o}">{svg}</g>'
                   for k, o in enumerate(opacities))


def dotted_arc(x0, y0, x1, y1, bow: float, colour_offset: int = 0, n: int = 12, r: float = 6) -> str:
    """Trajectory drawn as a row of logo dots on a quadratic arc."""
    mx, my = (x0 + x1) / 2 + bow, (y0 + y1) / 2 - abs(bow) * 0.4
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1
        out.append(dot(x, y, r * (0.55 + 0.45 * t), DOTS[(i + colour_offset) % len(DOTS)]))
    return "".join(out)


def phone(x: float, y: float, w: float, h: float, body: str = INK, screen_svg: str = "", clip_id: str = "ph",
          defs: list | None = None) -> str:
    """Phone made of straight lines, a slight slant on the speaker slot like the museum letters."""
    pad, top, bottom = w * 0.045, h * 0.07, h * 0.06
    sx, sy, sw, sh = x + pad, y + top, w - 2 * pad, h - top - bottom
    if defs is not None:
        defs.append(f'<clipPath id="{clip_id}"><rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}"/></clipPath>')
    return (rect(x, y, w, h, body, f' rx="{w * 0.07:.1f}"')
            + f'<g clip-path="url(#{clip_id})">{screen_svg}</g>'
            + line(x + w * 0.4, y + top * 0.5, x + w * 0.6, y + top * 0.42, PAPER, 6)
            + dot(x + w * 0.68, y + top * 0.46, 7, DOTS[2]))


def print_head(cx: float, y: float, scale: float = 1.0) -> str:
    s = scale
    return (rect(cx - 900, y - 64 * s, 1800, 22 * s, "#C9CED0")                      # gantry rail
            + rect(cx - 70 * s, y - 110 * s, 140 * s, 80 * s, INK)
            + f'<polygon points="{cx - 30 * s:.1f},{y - 30 * s:.1f} {cx + 30 * s:.1f},{y - 30 * s:.1f} '
              f'{cx + 8 * s:.1f},{y:.1f} {cx - 8 * s:.1f},{y:.1f}" fill="{F["grey"]}"/>'
            + dot(cx, y + 2, 7 * s, DOTS[0])
            + dot(cx + 48 * s, y - 92 * s, 8 * s, DOTS[2]))


def notebook(x: float, y: float, w: float, h: float, rules: bool = True) -> str:
    """Standing notebook page: white sheet, light blue rules, a coral margin, a spiral of line-and-dot rings."""
    out = [rect(x + 14, y + 16, w, h, mix(INK, PAPER, 0.85)), rect(x, y, w, h, "#FFFFFF")]
    if rules:
        yy = y + 150
        while yy < y + h - 40:
            out.append(line(x + 30, yy, x + w - 30, yy, F["light_blue"], 3))
            yy += 58
        out.append(line(x + w - 110, y + 20, x + w - 110, y + h - 20, F["coral"], 3))
    for k in range(int((w - 80) // 62) + 1):
        cx = x + 50 + k * 62
        out.append(line(cx, y - 34, cx, y + 26, INK, 6))
        out.append(dot(cx, y - 34, 9, DOTS[k % len(DOTS)]))
    return "".join(out)


def timeline_bar(x: float, y: float, w: float, progress: float, dark: bool = True) -> str:
    """Player timeline as a row of logo dots, the played part in colour."""
    n = 24
    out = []
    for i in range(n):
        t = i / (n - 1)
        colour = DOTS[i % len(DOTS)] if t <= progress else (mix(PAPER, INK, 0.6) if dark else mix(INK, PAPER, 0.7))
        out.append(dot(x + t * w, y, 6, colour))
    out.append(dot(x + progress * w, y, 14, PAPER if dark else INK))
    return "".join(out)


def counter_dots(cx: float, y: float, filled: int, total: int = 40, colour_shift: int = 0) -> str:
    """A row of dots that fills as stripes are painted (408 is said aloud, the dots show the work)."""
    out = []
    per_row = 20
    for i in range(total):
        r, c = divmod(i, per_row)
        x = cx + (c - (per_row - 1) / 2) * 34
        colour = SPECTRUM[(i + colour_shift) % 12] if i < filled else mix(INK, PAPER, 0.8)
        out.append(dot(x, y + r * 34, 10, colour))
    return "".join(out)


def sparkle(cx: float, cy: float, r: float, colour: str = F["yellow"]) -> str:
    """Line-and-dot spark: four short straight strokes with dots, for the idea moment."""
    out = []
    for k in range(8):
        a = math.radians(k * 45)
        r0, r1 = r * 0.45, r * (1.0 if k % 2 == 0 else 0.7)
        out.append(line(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                        INK, 5))
        out.append(dot(cx + r1 * math.cos(a), cy + r1 * math.sin(a), 8, DOTS[k % len(DOTS)]))
    return "".join(out)


def photo_card(x: float, y: float, w: float, h: float, href: str, defs: list, open_: float = 1.0,
               band: float = 26, stripe: float = 13, offset: int = 0, clip_id: str = "card",
               slice_: str = "xMidYMid slice", white: str = PAPER) -> str:
    """A real photo, untouched, inside a stripe frame. open_ < 1 draws the pleated curtain (the opening's
    stripes, folded up) still covering both sides: the curtain is the transition, never the photo."""
    from geom import Camera, Pleats, draw_groups
    defs.append(f'<clipPath id="{clip_id}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath>')
    out = [P_shadow(x, y, w, h),
           f'<image href="{href}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
           f'preserveAspectRatio="{slice_}" clip-path="url(#{clip_id})"/>']
    if open_ < 1.0:
        side = (1 - open_) * w / 2
        n = 9
        for sign in (-1, 1):
            cx = x + side / 2 if sign < 0 else x + w - side / 2
            cam = Camera(target=(0, h / 2, 0), cx=cx, cy=y + h / 2)
            colours = SPECTRUM[offset:] + SPECTRUM[:offset]
            sheet = Pleats(pleats=n, length=side, height=h, skin_a=lambda i, c=colours: c[i % 12],
                           skin_b=PAPER, depth_ratio=0.9 + 2.2 * (1 - open_))
            out.append(f'<g clip-path="url(#{clip_id})">' + draw_groups(cam, [sheet], defs) + "</g>")
    out.append(stripe_frame(x - band, y - band, w + 2 * band, h + 2 * band, band, stripe, offset, white))
    return "".join(out)


def P_shadow(x, y, w, h):
    return rect(x + 16, y + 20, w, h, INK, ' opacity="0.12"')


def marker(tip_x: float, tip_y: float, angle: float = 0.0, colour: str = F["coral"], scale: float = 1.0) -> str:
    """Paint marker as in our photo: black barrel, white band, a colour ring at the end, a colour tip.
    Points down; (tip_x, tip_y) is the tip; angle tilts it about the tip."""
    s = scale
    barrel = "#1F2128"
    body = (f'<polygon points="{tip_x - 9 * s:.1f},{tip_y - 22 * s:.1f} {tip_x + 9 * s:.1f},{tip_y - 22 * s:.1f} '
            f'{tip_x + 5 * s:.1f},{tip_y:.1f} {tip_x - 5 * s:.1f},{tip_y:.1f}" fill="{colour}"/>'          # nib
            + rect(tip_x - 20 * s, tip_y - 70 * s, 40 * s, 48 * s, "#E9E7E1")                          # grip cone
            + rect(tip_x - 24 * s, tip_y - 420 * s, 48 * s, 350 * s, barrel)                            # barrel
            + rect(tip_x - 24 * s, tip_y - 330 * s, 48 * s, 26 * s, "#F4F1E4")                          # white band
            + rect(tip_x - 24 * s, tip_y - 300 * s, 48 * s, 10 * s, colour)                             # colour ring
            + rect(tip_x - 24 * s, tip_y - 446 * s, 48 * s, 26 * s, colour))                            # end cap
    return rotated(body, angle, tip_x, tip_y)


def spool(cx: float, cy: float, r: float, filament: str = "#FBFAF6") -> str:
    """A filament spool seen from the side: a disc of wound white filament, grey flange ring, dark hub."""
    out = [dot(cx, cy, r, "#B9BEC2"), dot(cx, cy, r * 0.9, filament)]
    for k in range(1, 5):
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * (0.9 - k * 0.1):.1f}" fill="none" '
                   f'stroke="{mix(filament, INK, 0.08)}" stroke-width="2"/>')
    out += [dot(cx, cy, r * 0.42, "#B9BEC2"), dot(cx, cy, r * 0.22, "#2A2D33")]
    return "".join(out)


def a1_printer(cx: float, top: float, bed_y: float, width: float, head_x: float, head_y: float,
               bed_shift: float = 0.0) -> tuple[str, str]:
    """A bed-slinger in the style of our Bambu Lab A1 (not an exact model): an arch frame, the spool on top,
    an X gantry with the toolhead, a dark textured bed that slides front to back, the base with a small screen.
    Returns (behind, front): draw the printed part between them."""
    grey, light, dark, frame_c = "#C9CED0", "#E5E8EA", "#2A2D33", "#3A3E46"
    left, right = cx - width / 2, cx + width / 2
    behind = [
        rect(left, top, 46, bed_y - top + 40, frame_c),                       # left upright
        rect(right - 46, top, 46, bed_y - top + 40, frame_c),                 # right upright
        rect(left, top, width, 40, frame_c),                                  # top bar
        spool(cx, top - 70, 92),
        f'<path d="M{cx:.1f},{top - 70:.1f} C{cx + 160:.1f},{top - 40:.1f} {head_x + 40:.1f},{top + 60:.1f} '
        f'{head_x:.1f},{head_y - 120:.1f}" stroke="#FBFAF6" stroke-width="4" fill="none"/>',  # white filament
        rect(left + 46, head_y - 128, width - 92, 26, grey),                  # X gantry bar
        rect(cx - width / 2 + 70 + bed_shift * 0.2, bed_y, width - 140, 22, dark),               # bed plate (textured PEI)
    ]
    n = int((width - 160) / 16.4)
    for k in range(n):
        behind.append(dot(cx - width / 2 + 80 + bed_shift * 0.2 + k * 16.4, bed_y + 11, 1.6, "#4A4F58"))
    front = [
        rect(head_x - 62, head_y - 150, 124, 120, light),                     # toolhead cover
        rect(head_x - 62, head_y - 150, 124, 22, grey),
        dot(head_x + 36, head_y - 92, 6, F["green"]),                         # status light
        f'<polygon points="{head_x - 16:.1f},{head_y - 30:.1f} {head_x + 16:.1f},{head_y - 30:.1f} '
        f'{head_x + 5:.1f},{head_y:.1f} {head_x - 5:.1f},{head_y:.1f}" fill="{dark}"/>',   # hotend nozzle
        dot(head_x, head_y + 2, 4, DOTS[9]),
        rect(cx - width / 2 + 40, bed_y + 22, width - 80, 92, grey),                            # base
        rect(cx - width / 2 + 40, bed_y + 22, width - 80, 14, light),
        rect(cx + 200, bed_y + 52, 110, 46, dark),                            # little screen
        rect(cx + 210, bed_y + 60, 90, 30, mix(F["light_blue"], INK, 0.35)),
    ]
    return "".join(behind), "".join(front)


def photo_placeholder(x: float, y: float, w: float, h: float, label: str, defs: list, dark: bool = False,
                      offset: int = 0, clip_id: str = "ph") -> str:
    """Where a real photo of the girls will go: the same stripe frame as every photo, a quiet hatched field,
    a line-and-dot camera and the label. Swap for props.photo_card(...) when the photo arrives."""
    field = mix(PAPER, INK, 0.07) if not dark else mix(INK, PAPER, 0.12)
    ink = INK if not dark else PAPER
    defs.append(f'<clipPath id="{clip_id}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath>')
    hatch = "".join(f'<line x1="{x + k * 46:.1f}" y1="{y:.1f}" x2="{x + k * 46 - h:.1f}" y2="{y + h:.1f}" '
                    f'stroke="{mix(field, ink, 0.08)}" stroke-width="10"/>' for k in range(int((w + h) / 46) + 2))
    cx, cy = x + w / 2, y + h / 2 - 40
    camera = (rect(cx - 80, cy - 46, 160, 104, "none", f' stroke="{ink}" stroke-width="7"')
              + line(cx - 40, cy - 46, cx - 24, cy - 70, ink, 7) + line(cx - 24, cy - 70, cx + 24, cy - 70, ink, 7)
              + line(cx + 24, cy - 70, cx + 40, cy - 46, ink, 7)
              + f'<circle cx="{cx:.1f}" cy="{cy + 6:.1f}" r="30" fill="none" stroke="{ink}" stroke-width="7"/>'
              + dot(cx, cy + 6, 11, DOTS[(offset + 2) % 10]) + dot(cx + 58, cy - 26, 8, DOTS[offset % 10]))
    text = (f'<text x="{cx:.1f}" y="{cy + 140:.1f}" text-anchor="middle" direction="rtl" {SMALL_FONT} font-size="44" '
            f'fill="{ink}">{label}</text>'
            f'<text x="{cx:.1f}" y="{cy + 192:.1f}" text-anchor="middle" direction="rtl" {SMALL_FONT} font-size="28" '
            f'fill="{ink}" opacity="0.6">כאן תיכנס תמונה אמיתית</text>')
    return (P_shadow(x, y, w, h) + rect(x, y, w, h, field) + f'<g clip-path="url(#{clip_id})">{hatch}</g>'
            + camera + text + stripe_frame(x - 26, y - 26, w + 52, h + 52, 26, 13, offset, PAPER if not dark else INK))


def video_tag(x: float, y: float, w: float, label: str) -> str:
    """Marks a framed card as a moving archive clip (key frames show a still): a small play triangle + source."""
    cx, cy = x + w - 44, y + 40
    return (f'<rect x="{x + w - 190:.1f}" y="{y + 16:.1f}" width="174" height="48" fill="{INK}" opacity="0.78"/>'
            f'<polygon points="{cx - 8:.1f},{cy - 13:.1f} {cx - 8:.1f},{cy + 13:.1f} {cx + 14:.1f},{cy:.1f}" fill="{PAPER}"/>'
            f'<text x="{x + w - 70:.1f}" y="{y + 50:.1f}" text-anchor="end" direction="rtl" {SMALL_FONT} font-size="24" '
            f'fill="{PAPER}">{label}</text>')
