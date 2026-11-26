"""COLOUR PROGRAM: the one source for the painted renders, the flat painting maps (out/maps/),
the GLB export and the painting guide. Change colours here only.

Source: the real Dizengoff fountain, research/fountain-colour-program.md (default "fountain"
variant), whose data is copied into fountain_colours.py: the 1986 palette and, per ring and
face set, sectors in fountain angles (model angle = fountain angle + ROTATION).

R3 carries three motifs (user): HANUKKAH in blue on the RIGHT faces, the Magen David in green and
the dreidel in orange on the LEFT faces; plus the fountain's own disc (red) on the back of the
RIGHT faces. The fountain's "+" is left out.
User rules: only the pleated sides get colour; every top face stays white PETG; no black
(the darkest paint is navy, a clear blue); no outlines and no relief on motifs.
"""

import fountain_colours as fc
from colour_types import FaceSet, Motif, Paint, RingPaint, Sector, Sectors, Stripes

PALETTE_SOURCE = "research/fountain-colour-program.md (1986 shades, default fountain variant)"
# The research turns the fountain by +207 deg to land its own disc on the model; the disc is gone,
# so we turn it by +245 instead: the white stretch of the right faces (fountain 90..180) then sits
# round model +20, where HANUKKAH goes, and the yellow of the left faces under the star and dreidel.
ROTATION = 245.0

PAINTS: tuple[Paint, ...] = tuple(  # numbered as in the research table
    Paint(number, name, fc.PAINTS[name][0])
    for number, name in enumerate(fc.PAINTS, start=1)
) + (Paint(0, "bare", "#F2F1EC"),)  # unpainted white PETG: every top face, washer seats, joints
COMPLEMENT: dict[str, str] = {}  # not used by the fountain program


def fountain_sectors(ring: str, side: str, variant: str = "fountain") -> Sectors:
    """The research sector table for one face set, as model Sectors (one paint per sector)."""
    table = fc.sectors(ring, variant)[side]
    return Sectors(table[0][0] + ROTATION, tuple(Sector(end - start, Stripes((paint,))) for start, end, paint in table))


def ring(name: str, left_motifs: tuple = (), right_motifs: tuple = (), variant: str = "fountain") -> RingPaint:
    return RingPaint(
        left=FaceSet(fountain_sectors(name, "left", variant), left_motifs),
        right=FaceSet(fountain_sectors(name, "right", variant), right_motifs),
    )


# HANUKKAH in face-column letters (user: no small cuts or notches to paint): every column is one whole
# tooth face, blue full height or in horizontal bands. 8 letters + 7 one-face gaps = 32 faces of R3's
# 80 teeth (4.5 deg each); paint_program.motif_shapes checks the span and snaps the start to a tooth edge.
WORD_START_DEG = -9.0  # a tooth edge. Optics (measured): a viewer 40 deg to the LEFT of the front sees
# no right faces at all from about -10 deg onward, so the word stays hidden from there; it reads in
# full as you walk round to the right of the front.
WORD_SPAN_DEG = 144.0  # 32 faces x 4.5 deg
WORD_CENTRE_DEG = WORD_START_DEG + WORD_SPAN_DEG / 2
WORD_BAND_DEG = 183.0  # the white ground under the word: -28.5 to 154.5. The right faces are white there anyway
# except three blue fountain faces just after the word (140-153), which would run into its last H

# The fountain's own disc (user: the back of the right faces was empty, "add a circle as in the
# original"). It sits on the white stretch of the right faces (model 155..234), so it reads from
# about 40 deg to its right, round the back where neither the word nor the star nor the dreidel
# shows. Red, as the disc on the fountain's second half; the three motif colours stay unique.
# Now a sufganiyah (user): a fried-golden ellipse with a red jam dot on top, in place of the plain disc.
DISC_CENTRE_DEG = 211.5  # on a ridge (47 teeth x 4.5), so the faceted ellipse is symmetric
SUFGANIYAH_HEIGHT_RATIO = 0.60  # of R3's height: 8 faces wide and this tall makes a flat ellipse
# The dreidel sits in the middle of a face (180 + half a 4.5 deg tooth), so its narrow handle becomes
# exactly one whole face and its body three (facets.py: every piece spans its whole face).
# Two faces left of 182.25 (user: a small gap between it and the sufganiyah): it ends at 180, the
# sufganiyah starts at 193.5
DREIDEL_CENTRE_DEG = 173.25
SUFGANIYAH_INKS = ("orange", "brick")  # dough, jam

RING_PAINT: dict[str, RingPaint] = {
    # R1, R2: the research's "sketch" variant (fountain colours as continuous gradients, no white
    # sectors), so the lower drums read as rich colour; white shows only as the ridge separators.
    "drum1_R1": ring("drum1_R1", variant="sketch"),
    "drum2_R2": ring("drum2_R2", variant="sketch"),
    # R3: exactly three motifs, each large, painted on one face set only (no outline; fine guide relief only).
    # Right faces (seen from the right): HANUKKAH in blue, one line, on the white stretch of the
    # right-face journey of the fountain. Left faces (seen from the left): the Magen David in green
    # at the front (on yellow) and the dreidel in orange at the back (on yellow). Colour runs all
    # round both face sets as on the fountain; white shows as strips between colours.
    # Optics (previews/test_two_pictures_*): a picture on the right faces at a spot reads from
    # ~40 deg to the right of it, one on the left faces from ~40 deg to the left; head-on they mix.
    "drum3_R3": ring(
        "drum3_R3",
        left_motifs=(
            Motif("star", 0.0, ("green",), height_fraction=0.84, stretch=1.3),
            Motif("dreidel", DREIDEL_CENTRE_DEG, ("orange",), height_fraction=0.84, stretch=1.3),  # silhouette only (user)
        ),
        right_motifs=(
            Motif("band", WORD_CENTRE_DEG, ("white",), width_deg=WORD_BAND_DEG),  # white ground under the word
            Motif("columns", WORD_CENTRE_DEG, ("blue",), text="HANUKKAH", height_fraction=0.70),
            Motif("sufganiyah", DISC_CENTRE_DEG, SUFGANIYAH_INKS, height_fraction=SUFGANIYAH_HEIGHT_RATIO),
        ),
    ),
    "drum4_R4": ring("drum4_R4"),
    "drum5_R5_dome": ring("drum5_R5_dome"),
}
PLINTH_PAINT = "bare"  # the foot is all white (sketch, user ruling)
STEM_PAINT = "bare"
MIN_ZONE_WIDTH = 2.5  # mm: target minimum zone a child paints (maps.py reports anything smaller)
