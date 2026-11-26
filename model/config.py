"""All dimensions of the Agam "Fire and Water" hanukkiah model, in millimetres.

Change values here, then run `python build.py` to regenerate STL/3MF and previews.

Source of truth: hanukkiah/concept.md (minimal version) §2-§6 and research/fountain.md.
The piece is the sculpture itself: plinth disc, stem, five pleated rings R1-R5 and a small
dome. The only additions are 8 small tap holes in R3's top step and one in the flattened
dome crown (small metal cups on stainless washers screw in, concept §2.2/§5), five flat
emblems in R3's stripes, and the "colouring book" paint-guide relief.
"""

import math
from dataclasses import dataclass
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Drum:
    """One pleated ring, bottom to top. Ratios from concept.md (research §6):
    tooth-tip diameter / main diameter, and height / H where H = main diameter / 1.54."""

    name: str
    diameter_ratio: float
    height_ratio_h: float


# --- Overall scale ----------------------------------------------------------------
MAIN_DIAMETER = 180.0  # R3 tooth tips; every ring scales with it
H_PER_MAIN = 1 / 1.54  # sculpture height H = main diameter / 1.54

DRUMS: tuple[Drum, ...] = (
    # Proportions from the style sketch (research/user-reference-agam-menorah.png, Dana Barlev),
    # measured with the main ring at 180: R1 59 x 18, R2 111 x 31, R3 180 x 44, R4 68 x 21,
    # R5 35 x 20 (white, holds the shamash). The fountain's own ratios were 0.36/0.68/1/0.68/0.36.
    Drum("drum1_R1", 0.33, 0.154),
    Drum("drum2_R2", 0.62, 0.265),
    Drum("drum3_R3", 1.00, 0.376),
    Drum("drum4_R4", 0.38, 0.154),  # 18 tall (sketch ~21): rises 7 mm above the rims, concept §5 limit
    Drum("drum5_R5_dome", 0.20, 0.171),
)
CANDLE_DRUM_INDEX = 2  # R3 carries the 8 cup holes and the emblems

STEM_DIAMETER_RATIO, STEM_HEIGHT_RATIO_H = 0.25, 0.046
DOME_DIAMETER_RATIO, DOME_HEIGHT_RATIO_H = 0.20, 0.078  # half-ellipsoid on R5

# --- Plinth disc (stability, concept §3: tips at 46 deg) -------------------------------
# Goblet foot, measured from the style sketch (main ring = 180): base disc Ø 103 x 14.5 (just
# under R2's width; we use R2's width, 112, for stability), a concave neck ~20 tall with a Ø 22 waist; foot height ~20 % of the total.
# build.py checks the tip angle with 9 lit candles (STABILITY_*).
PLINTH_DIAMETER = 112.0  # = R2's width (sketch ~103 tips at ~31 deg: too wobbly)
PLINTH_HEIGHT = 14.5
PLINTH_EDGE_ROUND = 4.0
FOOT_STEM_HEIGHT = 20.0
FOOT_STEM_WAIST_DIAMETER = 22.0  # narrowest point of the concave neck
FOOT_STEM_TOP_DIAMETER = 30.0  # where R1 sits; the flare stays under 45 deg so it prints unsupported
FOOT_STEM_BOTTOM_DIAMETER = 42.0
R3_GAP_HUB = (40.0, 0.0)  # (diameter, height) of a hub between R2 and R3; 0 = R3 sits straight on R2 (user)
BALLAST_POCKETS = 8  # underside pockets, each for a stack of 4 M10 washers
BALLAST_POCKET_DIAMETER = 21.0  # M10 washer OD 20 + clearance
BALLAST_POCKET_DEPTH = 8.5
BALLAST_POCKET_RADIUS = 38.0

# --- Saw-tooth (pleat) profile -------------------------------------------------------
TOOTH_PITCH = 7.0  # arc length between tooth tips on every ring (paintable stripes)
TOOTH_LEAN = 0.5  # symmetric V
# Sharper pleats than the fountain's ~90 deg, so each picture shows alone: with a 70 deg V the
# faces of the other set turn away (are hidden) once you stand more than 35 deg to one side.
# The tooth tips (and so the silhouette) stay where they were; only the valleys get deeper.
TOOTH_INCLUDED_ANGLE = 70.0
TOOTH_DEPTH_RATIO = TOOTH_LEAN / math.tan(math.radians(TOOTH_INCLUDED_ANGLE / 2))  # depth = ratio x pitch
TOOTH_TIP_FLAT = 0.4

# --- Spine (central D-shaft, keys every part's rotation) -------------------------
SPINE_DIAMETER = 10.0
SPINE_FLAT = 1.0
SPINE_BASE_DEPTH = 9.4  # into the plinth+stem part (1 mm floor left)
SPINE_TOP_DEPTH = 4.0  # into R5 from below (stays clear of the shamash stud hole above it)
JOINT_CLEAR = 0.40  # printed peg/hole fits, room for 2 coats of paint

# --- Candle holders (concept §2.2/§5): bought cup with a threaded stud on a washer -----
# BUY AND MEASURE FIRST, then update. Same holder on all 9.
CUP_OD = 12.0  # closed-bottom brass/aluminium menorah cup (<= 13)
CUP_HEIGHT = 10.0  # visible cup, rim to bottom
CUP_INNER_DEPTH = 9.0  # how far a candle sinks in (renders only)
WASHER_D, WASHER_T = 16.0, 1.0  # stainless heat-shield washer under each cup
STUD_HOLE_D = 3.4  # self-tapping hole for an M4 stud (M3: 2.5); measure the stud
STUD_HOLE_DEPTH = 10.0  # plain hole, no insert (brass would carry heat into the PETG)
HOLE_WALL_MIN = 3.0  # stud hole to the nearest outside surface
SEAT_CLEARANCE = 1.0  # no relief (lip, step circles) within this of a washer's edge: it sits flat
DOME_ENABLED = False  # user: no dome; the shamash cup sits straight on R5's top centre
DOME_CROWN_FLAT_D = 16.0  # (dome only) crown cut flat to seat the shamash washer
SHAMASH_STUD_HOLE_DEPTH = 8.0  # M4 x 8 stud; R5 is only 14.4 tall and the spine comes up from below
MIN_FLOOR_ABOVE_SPINE = 1.5  # PETG between the spine's end and the shamash stud hole

# --- Candle layout --------------------------------------------------------------------
CANDLE_COUNT = 8
CANDLE_RING_RADIUS = 66.0  # moved in from 81 (user): R4 teeth 31.8 mm away, R5 48, chord 50.5
CANDLE_ANGLE_OFFSET = 0.0  # deg; 0 = front (-Y), then counter-clockwise seen from above
CANDLE_ON_TOOTH_TIP = True  # turn the cups by up to half a tooth so each sits over a tooth tip
# (R3's tooth count is rounded to a multiple of CANDLE_COUNT so all 8 can): the deep valleys of the
# 70 deg pleats would otherwise come too close to a stud hole.
HOLDER_VISIBLE = WASHER_T + CUP_HEIGHT  # 11 mm: ring rims = R3 top + this, shamash = dome crown + this

# --- Safety rules (concept §1, §3, §5) ------------------------------------------------
MIN_AXIS_TO_R4_TIPS = 25.0  # concept §5: R4 teeth this far from each flame, if R4 rises <= MAX_R4_RISE
MAX_R4_RISE = 7.0  # mm R4 may rise above the cup rims under the 25 mm rule
MIN_AXIS_TO_HIGHER_PLASTIC = 40.0  # R5, dome
MIN_SHAMASH_ABOVE_RING = 20.0
MIN_FLAME_SPACING = 40.0
MAX_HOLDER_VISIBLE = 11.0
# Stability (concept §3): tip angle = atan(foot radius / height of the centre of mass), counted
# with 9 cups, washers and fresh lit candles. Concept §3: stem alone 21 deg = too wobbly, R1 as a
# foot 31 deg = marginal, >= 46 deg = fine; ASTM F2601 tests candle holders at 10 deg.
STABILITY_MIN_TIP_DEG = 35.0
PETG_DENSITY = 1.27  # g/cm3
PRINT_SHELL_MM = 1.4  # walls + top/bottom skins, as a solid layer this thick under the whole surface
PRINT_INFILL = 0.15  # the rest of each part
FOOT_INFILL = 1.0  # print the foot solid (100 % infill): its weight sits lowest and steadies the piece
CUP_MASS_G, WASHER_MASS_G, CANDLE_MASS_G = 4.0, 2.0, 6.0  # brass cup, stainless washer, new candle
BALLAST_WASHER_MASS_G = 17.0  # per pocket: 4 stacked M10 washers (DIN 125, Ø 20 x 2, ~4.3 g each)

# --- Paint guides: "colouring book" relief --------------------------------------------
RIDGE_WIDTH = 0.8  # raised dams between colour zones (2 lines at a 0.4 nozzle)
RIDGE_HEIGHT = 0.6

# --- Painted motifs (colour_program.py places them; emblems.py draws them) -------------
FONT_FILE = str(MODEL_DIR / "fonts" / "SecularOne-Regular.ttf")  # SIL OFL, bold sans with Latin + Hebrew
WORD_RIGHT_TO_LEFT = False  # True for a Hebrew word such as "חנוכה" in a text motif
TEXT_LETTER_GAP_RATIO = 0.24  # gap between letters / cap height (generous: each face set shows only half the faces)
TEXT_LINE_GAP_RATIO = 0.10  # gap between lines / motif height
DISC_HALF_FACES = 4  # the disc spans this many tooth faces each side of its centre (a 16-sided round, pointed on the ridges)
JAM_CENTRE_RATIO = 0.45  # the jam dot's centre above the sufganiyah's middle / its half height
JAM_HALF_HEIGHTS = (0.20, 0.35)  # the dot's half height at its sides and at its middle / the sufganiyah's half height
DISC_BAR_RATIO = 5 / 24  # bar width / disc diameter (as on the fountain)
CROSS_ARM_RATIO = 7 / 22  # arm width / cross size
DREIDEL_HANDLE = (3.83 / 26, 5 / 26)  # width, height / dreidel height. The width is exactly one R3 face
# (7.07 mm after the 1.3 stretch at 84% of R3's height), so with the dreidel centred on a face the handle
# fills that face edge to edge and its shoulders step down on the ridges (facets.py)
DREIDEL_BODY = (16 / 26, 13 / 26)
DREIDEL_POINT = (16 / 26, 8 / 26)
DREIDEL_LETTER = ""  # no letter: the dreidel is its silhouette only (user); e.g. "ג" puts one back
DREIDEL_LETTER_RATIO = 0.75  # letter height / body height
COLUMN_BAND_RATIO = 0.30  # HANUKKAH face-column letters (column_letters.py): horizontal band / cap height
COLUMN_LETTER_GAP = 1  # empty tooth faces between letters
COLUMN_K_JOINT_RATIO = 0.4  # K: how tall its arms are where they leave the stem / cap height
COLUMN_DIAGONAL_RATIO = 0.5  # N's diagonal: its height on each face / cap height (edges run straight across each face)
GUIDE_LINE_HEIGHT = 0.3  # subtle raised guide along each motif outline (on its own face set only)
GUIDE_LINE_WIDTH = 0.6
GUIDE_SEAT_CLEARANCE = 0.3  # gap between a washer and its locating ring
GUIDES_ENABLED = True
# Engraved start arrows (start_marks.py): one sunk into the top and one into the bottom of every
# ring, tail on the seam where the painting maps start, pointing the way the maps run.
SEAM_DEG = 157.5  # concept angle where each unrolled ring is cut: between candles, clear of every motif
START_ARROWS_ENABLED = True
START_ARROW_LENGTH = 5.0
START_ARROW_WIDTH = 2.4  # head width
START_ARROW_SHAFT = 1.0
START_ARROW_HEAD_RATIO = 0.45  # head length / arrow length
START_ARROW_DEPTH = 0.4  # sunk, not raised (user)
START_ARROW_EDGE_INSET = 1.2  # from the pleat roots (the top paint lip sits outside this)
# Scaled full test rings of R3 (test_ring.py): rebuilt at each scale with real-size ridges and guides.
TEST_RING_SCALES = (0.5, 0.6, 0.7)
TEST_RING_RENDER_SCALE = 0.6  # maps and renders for this one
TEST_RING_MIN_ZONE = 2.0  # mm: narrowest paint zone (pleat face between ridges); the pitch clamps to keep it
# Test coupon (out/test_coupon_R3.stl): an arc of R3 to print and paint first.
COUPON_CENTRE_DEG = 5.0  # covers the Magen David (left faces, 0), cup 1 and the first HANUKKAH letters
COUPON_SPAN_DEG = 50.0
# Magen David test cut (user): the whole star (green paint runs -13 to +11 deg on R3) with ~6 deg spare each side
STAR_COUPON_CENTRE_DEG = -1.0
STAR_COUPON_SPAN_DEG = 36.0
COUPON_INNER_RADIUS = 55.0  # keeps cup 1's seat (r 66, washer to r 74) and its locating ring
COUPON_WALL = 2.4  # hollowed from below: walls this thick
COUPON_TOP_SKIN = 1.6
MOTIF_ANGLE_TOLERANCE = 3.0  # deg: maps vs model motif centres must agree within this (build check)
MOTIF_ANGLE_SEARCH_MARGIN = 10.0  # deg past a motif's half width (from the maps) where build.py looks for its paint
MOTIF_CURVE_POINTS = 240  # points per outline when a motif is turned into polygons (smooth curves)
STEM_SECTORS = 0  # the fountain's stem is plain steel: no sectors (white PETG)

# --- Colour program: lives in colour_program.py (swap a palette in there) --------------
from colour_types import FaceSet, Motif, Paint, RingPaint, Sector, Sectors, Stripes  # noqa: E402,F401
from colour_program import *  # noqa: E402,F401,F403

# --- Optional decorative pool (OFF: dropped by the user; kept as a parameter) ----------
POOL_ENABLED = False
POOL_DIAMETER = 210.0
POOL_FLOOR = 3.0
POOL_RIM_HEIGHT = 10.0
POOL_RIM_WIDTH = 6.0

# --- Rendering / export ----------------------------------------------------------------
PREVIEW_SIZE = (1400, 1100)
CANDLE_PREVIEW_LENGTH = 60.0  # renders and GLB only (a standard ~10 mm Hanukkah candle)
CANDLE_PREVIEW_DIAMETER = 10.0
FLAME_PREVIEW_HEIGHT = 16.0
GLB_MAX_BYTES = 10_000_000
BED_SIZE = 220.0
STL_TOLERANCE = 0.03
STL_ANGULAR_TOLERANCE = 0.15
