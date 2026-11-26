"""2D artwork for the painted motifs (colour_types.Motif). No relief: the motifs are painted on
one face set only, so the pleats stay pure and each picture vanishes from the other side.

`motif_zones(motif, height)` returns the motif's colour zones as build123d sketches in mm,
centred on the origin, `height` tall (before the motif's horizontal stretch).
"""

from __future__ import annotations

from build123d import Circle, Polygon, Pos, Rectangle, Sketch, Text

import colour_types as ct
import config as cfg
import relief


def glyph(letter: str, height: float) -> Sketch:
    """One SecularOne glyph, `height` tall, centred on the origin."""
    probe = Text(letter, 10, font_path=cfg.FONT_FILE)
    text = Text(letter, 10 * height / probe.bounding_box().size.Y, font_path=cfg.FONT_FILE)
    box = text.bounding_box()
    return Pos(-box.center().X, -box.center().Y) * text


def text_line(word: str, cap_height: float, right_to_left: bool = False) -> Sketch:
    """A word placed letter by letter (from the right for Hebrew), centred on the origin, so no
    CAD engine can reorder or mirror it."""
    probe = Text("H", 10, font_path=cfg.FONT_FILE)
    font_size = 10 * cap_height / probe.bounding_box().size.Y
    glyphs = []
    for letter in word:
        shape = Text(letter, font_size, font_path=cfg.FONT_FILE)
        box = shape.bounding_box()
        glyphs.append((Pos(-box.center().X, -box.center().Y) * shape, box.size.X))
    gap = cap_height * cfg.TEXT_LETTER_GAP_RATIO
    total = sum(width for _, width in glyphs) + gap * (len(glyphs) - 1)
    direction = -1 if right_to_left else 1
    edge = -direction * total / 2
    placed = Sketch()
    for shape, width in glyphs:
        placed = placed + Pos(edge + direction * width / 2, 0) * shape
        edge += direction * (width + gap)
    return placed


def text_block(text: str, lines: int, height: float) -> Sketch:
    """The text split into `lines` lines that together fill `height`."""
    words = [text[i * len(text) // lines : (i + 1) * len(text) // lines] for i in range(lines)]
    gap = height * cfg.TEXT_LINE_GAP_RATIO
    cap = (height - gap * (lines - 1)) / lines
    block = Sketch()
    for number, word in enumerate(words):
        y = height / 2 - cap / 2 - number * (cap + gap)
        block = block + Pos(0, y) * text_line(word, cap, cfg.WORD_RIGHT_TO_LEFT)
    return block


def dreidel(height: float) -> tuple[Sketch, Sketch]:
    """Silhouette (handle, body, point) and the letter on the body (None if DREIDEL_LETTER is empty)."""
    handle_w, handle_h = (v * height for v in cfg.DREIDEL_HANDLE)
    body_w, body_h = (v * height for v in cfg.DREIDEL_BODY)
    point_w, point_h = (v * height for v in cfg.DREIDEL_POINT)
    bottom = -height / 2
    body_bottom = bottom + point_h
    body_top = body_bottom + body_h
    point = Polygon((-point_w / 2, body_bottom + 0.01), (0, bottom), (point_w / 2, body_bottom + 0.01), align=None)
    body = Pos(0, body_bottom + body_h / 2) * Rectangle(body_w, body_h)
    handle = Pos(0, body_top + handle_h / 2) * Rectangle(handle_w, handle_h + 0.01)
    silhouette = Sketch() + point + body + handle
    if not cfg.DREIDEL_LETTER:
        return silhouette, None
    letter = Pos(0, body_bottom + body_h / 2) * glyph(cfg.DREIDEL_LETTER, body_h * cfg.DREIDEL_LETTER_RATIO)
    return silhouette, letter


def jam_dot(height: float) -> Sketch:
    """The sufganiyah's jam: a six-cornered dot two faces wide, high on the dough. Its corners sit one
    face either side of the centre and on it (the sufganiyah is stretched to DISC_HALF_FACES faces each
    side, so one face is radius / DISC_HALF_FACES here), so each half crosses one whole face."""
    radius = height / 2
    face = radius / cfg.DISC_HALF_FACES
    centre = cfg.JAM_CENTRE_RATIO * radius
    side, middle = (r * radius for r in cfg.JAM_HALF_HEIGHTS)
    corners = ((-face, centre - side), (0, centre - middle), (face, centre - side), (face, centre + side), (0, centre + middle), (-face, centre + side))
    return Sketch() + Polygon(*corners, align=None)


def motif_zones(motif: ct.Motif, height: float) -> list[tuple[Sketch, str]]:
    """Colour zones of a motif (later zones paint over earlier ones)."""
    if motif.shape == "text":
        return [(text_block(motif.text, motif.lines, height), motif.inks[0])]
    if motif.shape == "star":
        return [(relief.solid_hexagram(height), motif.inks[0])]
    if motif.shape == "disc":
        return [(Sketch() + Circle(height / 2), motif.inks[0])]
    if motif.shape == "sufganiyah":
        return [(Sketch() + Circle(height / 2), motif.inks[0]), (jam_dot(height), motif.inks[1])]
    if motif.shape == "disc_bar":
        bar = Sketch() + Rectangle(height * cfg.DISC_BAR_RATIO, height) & Circle(height / 2)
        return [(Sketch() + Circle(height / 2), motif.inks[0]), (bar, motif.inks[1])]
    if motif.shape == "square":
        return [(Sketch() + Rectangle(height, height), motif.inks[0])]
    if motif.shape == "cross":
        arm = height * cfg.CROSS_ARM_RATIO
        return [(Sketch() + Rectangle(height, arm) + Rectangle(arm, height), motif.inks[0])]
    if motif.shape == "dreidel":
        silhouette, letter = dreidel(height)
        if letter is None:
            return [(silhouette, motif.inks[0])]
        if len(motif.inks) < 2:
            raise ValueError(f"dreidel at {motif.centre_deg}: DREIDEL_LETTER is set, so it needs a second ink for the letter")
        return [(silhouette, motif.inks[0]), (letter, motif.inks[1])]
    raise ValueError(f"Unknown motif shape {motif.shape!r} (text, star, disc, sufganiyah, disc_bar, cross, dreidel)")
