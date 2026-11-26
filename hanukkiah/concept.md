# Agam "Fire and Water" Hanukkiah: Concept and Spec (minimal version)

This file turns Yaacov Agam's *Fire and Water* fountain (Dizengoff Square) into a hanukkiah that the girls can paint and that is safe to light. The model session takes its requirements from **§5 (Spec)** and **§6 (Motifs)**. The stack is 5 pleated rings R1-R5 on a goblet foot. Its proportions now follow the style sketch (`research/user-reference-agam-menorah.png`) rather than the fountain's own ratios (`research/fountain.md`). Ratios used (tooth-tip Ø / main Ø, height / H, with H = main Ø / 1.54):

| Ring | Ø ratio | Height ratio |
|---|---|---|
| R1 | 0.33 | 0.154 |
| R2 | 0.62 | 0.265 |
| R3 | 1.00 | 0.376 |
| R4 | 0.38 | 0.154 |
| R5 (white top drum) | 0.20 | 0.171 |

There is no dome.

**User decisions (final):**
1. The piece looks **as much as possible like the sculpture**. The only physical additions are the candle holders, and they are small and thin: **11 mm visible above R3**, no pipes, no printed collars.
2. 8 candles in a **circle** at 45°, all at one height, standing on **R3's top step** at **r 66**, inside its outline.
3. The **shamash** is the same small cup at the **top centre**, on R5's top. R5 is a white drum; there is no dome.
4. **No dreidel object, no pool, no polymorph relief band.** The goblet foot is part of the style, and stability needs it with ballast (§3).
5. **Everything printed in PETG.**

---

## 1. Halachic notes that shape the design

* **Circle:** the Rema (OC 671:4) prefers a straight row, because lights in a circle look like one fire (*כמדורה*).
  - Poskim who allow a circle (e.g. Pri Chadash, cited in the Mishna Berura) require each light to be **clearly separate**.
  - That is the design rule here: wide, even spacing, separate cups, flames that never touch.
  - The user knows a row is the standard; this is decided.
* **Minimum flame spacing: 40 mm centre to centre** (we have **50.5 mm**). Why 40:
  - The halachic floor for separate lights is about a fingerbreadth (~20 mm, Mishna Berura on 671:4). In a circle we take double that, so the lights read as 8 separate flames from any side.
  - A Hanukkah candle flame is ~10-12 mm wide and ~25-30 mm tall, and leans in a draught. Below ~30 mm between axes, neighbouring flames can lean into each other, merge, and soften or bend each other's candles. At 40 mm or more there is always ≥ 25 mm of air between flame edges.
* **Equal height:** all 8 cup rims at the same Z, all cups identical, all candles vertical.
* **Shamash distinct:** alone at the centre top, **38 mm higher** than the ring of 8. The minimum is 20 mm.
* **Burn time:** standard Hanukkah candles (~45 min) cover the required 30 minutes after nightfall (SA OC 672:2).
* **Real flames only:** electric/LED lights do not fulfil the mitzvah according to most poskim.

---

## 2. Concept: the stack, with 8 small cups on R3's step and one on top

### 2.1 What actually limits the holder

The flame always sits **above** its cup rim:
- At the start it is ~100 mm above the rim (a full candle).
- At the very end it is about level with the rim (the wick drowns in the cup).

So the only plastic that ever sees a flame from the side is plastic that rises **above the rim** near a cup, and only in the **last ~5 minutes** of each candle. Here that is **R4**, and R5 higher up. R3's step is below every flame and is shielded by the metal cup and washer. The real constraint is the **side distance to R4**, not the rim height.

| Layout | Visible above R3 | Flame axis → R4 tooth tip | R4 above rim | R4 surface at end of burn (est.) | Verdict |
|---|---|---|---|---|---|
| Old: Ø16 tube + cup | 28 mm | 13 mm | below | below the flame | safe, but reads as pipes ✗ |
| Small cup at r 81, R4 0.62 (previous version) | 11 mm | 25 mm | +7 | ~55-60 °C | ✔ but cups sat on the very edge |
| **Small cup at r 66, R4 0.38 × 18 mm (current)** | **11 mm** | **31.8 mm** | **+7** | **~45 °C** | ✔ **chosen**, confirm in the test burn |

How the estimate works:
- A thin Hanukkah candle releases ~50 W, ~15% of it as radiation.
- At 31.8 mm that is ~0.6 kW/m² on the nearest R4 tooth, for ~5 min. That warms painted PETG by ~20 K.
- At 25 mm it is ~1 kW/m² (~30 K). PETG softens from ~70 °C.
- **The test burn (§3) is the real check.**

The narrow R4 of the sketch proportions (tip r 34.2) is what makes r 66 safe. R4 is kept at **18 mm tall** (sketch ~21), so it rises only 7 mm above the rims. **Do not make R4 taller or wider without re-checking §5 rule 3.**

### 2.2 The holder (same for all 9)
* **Cup:** a closed-bottom brass or aluminium menorah cup.
  - **OD 12** (≤ 13), ID to fit your candles (~10.5), **10 mm tall**.
  - Flat bottom with a **threaded stud, M4 × 8-10**. Sold as "candle cup with screw / bobeche cup with stud".
  - The **shamash stud must be ≤ 8 mm**, because R5 is short and the spine comes up from below.
* **Heat-shield washer:** **stainless, Ø 16 × 1**, with a hole for the stud.
  - It sits between the cup and the PETG, so the hot cup bottom never touches plastic, and it catches drips.
* **In the print:** one plain **tap hole** per cup (M4: Ø 3.4, depth 10; shamash depth 8).
  - The stud self-taps into the PETG. No insert: a brass insert would carry heat into the plastic.
  - The ring holes sit over R3's tooth tips, turned 2.25° (R3 has 80 teeth). The hole wall is ≥ 3 mm everywhere.
* **No printed collars** round the cups, even though the sketch shows them. PETG 2-4 mm from a hot cup wall, at the height where the last flame burns, is not safe.

### 2.3 Layout (R3 = Ø 180, H = 116.9)

```
SIDE VIEW                              S          <- shamash cup on R5's top, rim Z 180.4
                                     [R5]         white drum Ø36 x 20, Z 149.4-169.4
                                  [  R4  ]        Ø68 x 18, Z 131.4-149.4 (7 mm above the rims)
              u     u                    u     u  <- small cups at r 66, rims Z 142.4 (R3 top + 11)
     [‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾]  <- R3 Ø180 x 44, 8 tap holes
     [                         R3                            ]
                          [ hub ]                 shadow gap, Ø40 x 4
               [               R2               ] Ø112 x 31
                         [    R1    ]             Ø59 x 18
                            )    (                goblet neck, waist Ø22, 20 tall
                 [========  foot Ø112 x 14.5  ========]   8 ballast pockets

TOP VIEW
                     o
              o     .--.     o            o = cup Ø12 on washer Ø16, r 66, 45° steps
                   (R4 S)                 R4 tip r 34.2, R5 r 18
           o        '--'        o         R3 tip r 90: washers end at r 74
              o              o
                     o                    chord 2·66·sin 22.5° = 50.5 mm
```

---

## 3. Heat, fire safety and stability

**Material (decided): everything printed in PETG.**
- Glass transition ~80 °C; it softens under load from ~70 °C.
- Printed plastic is **not fire-resistant**: PETG burns. It is safe only within these limits.

### Candles and metal parts
* **Standard thin Hanukkah candles only** (in Israel ~9.5-10.5 mm at the base, ~10 cm long). **Measure your box.** **No tealights, no oil cups.**
* **9 small closed-bottom metal cups with a stud** and **9 stainless washers Ø 16 × 1** (§2.2). **Buy them first and measure them.** The modeller sets the holes from the stud.

### Flame-to-plastic distances (checked independently against the model)
Cups at r 66, ring rims at Z 142.4, shamash rim at Z 180.4.

| Plastic | Height vs the ring cup rims | Distance from a candle axis | OK? |
|---|---|---|---|
| Anything **above** a candle (cylinder r 15, up to 250 mm) | — | none | ✔ |
| **R4** (tip r 34.2, top Z 149.4) | up to **7 mm above** | **31.8 mm** | ✔ (≥ 25), end of burn only, test-burn check |
| **R5** (tip r 18, Z 149.4-169.4) | 7-27 mm above | **48 mm** | ✔ (≥ 40) |
| **R3** step | 11 mm below the rim, under washer + cup | under the cup | ✔ shielded |
| Neighbouring flame | — | **50.5 mm** | ✔ (≥ 40) |
| **Shamash flame** → plastic | nothing above it. R5's top is 11 mm below its rim, under washer + cup | — | ✔ |
| Shamash ↔ candle flames | 38 mm higher, 66 mm apart | | ✔ |

Rules for the model:
- No plastic above any cup.
- R4 rises ≤ 7 above the rims, and `CANDLE_RING_R − R4_tip_r ≥ 25`.
- `CANDLE_RING_R − R5_tip_r ≥ 40`.

### Drips
The cups hold most of the wax, and the washers catch the rest. There is no drip lip. Wax that reaches R3's step pops off PETG when cold. R3's top stays **white PETG, unpainted**.

### Filament
| Part | Material |
|---|---|
| **All printed parts** | **PETG** (decided). Print R3, R4 and R5 with ≥ 4 perimeters and 20-30% infill so the tap holes hold. Print the foot solid |

### Stability: the goblet foot needs its ballast
| Base | Tips at | Verdict |
|---|---|---|
| Stem only | 21° | ✗ too wobbly for a table with kids |
| Sketch foot Ø 103, with ballast | ~31° | ✗ marginal |
| Foot Ø 112, **no ballast** | **32°** | ✗ marginal |
| **Foot Ø 112 + 32 M10 washers** (4 in each of 8 pockets, glued) | **36°** | ✔ acceptable: well over the 10° of ASTM F2601, but below the 46° the minimal version had |

The new stack is taller (centre of mass ~78 mm up), so the **ballast is required, not optional**. The **metal tray** in house rule 2 matters more now. If the print feels light, add more washers or steel shot.

### Paint
- Water-based acrylic or Posca.
- No spray or solvent varnish near the cups.
- Nothing painted on R3's top, R5's top or within 5 mm of any hole.

### House rules
1. An adult lights and **stays in the room** until every candle is out.
2. Stand it on a **metal tray or tile (Ø ≥ 200)**, away from curtains, hair and sleeves.
3. **Test burn before Hanukkah** (before painting is fine): all 8 candles plus the shamash, burned to the end, indoors with no draught.
   - In the last 10 minutes, check R4's teeth facing each cup, and the plastic round each washer. With an IR thermometer, **≤ 60 °C is good and over 70 °C fails**.
   - Without a thermometer: warm to the touch is fine; too hot to hold a finger on fails.
   - After it cools, check R4's teeth, R3's top and R5's top for sag, gloss change, bubbles or smell. Every cup must still be screwed tight.
   - **If it fails, no reprint:** put a **5 mm stainless spacer** (or a stack of washers) under each ring cup. R4 is then only ~2 mm above the rims (16 mm visible). Test again.
4. Let it cool for 10 min before moving it.

---

## 4. Layout numbers (R3 = Ø 180)

| Part | Tooth-tip Ø | Z bottom → top |
|---|---|---|
| Foot disc (8 ballast pockets) | 112 | 0 → 14.5 |
| Goblet neck (waist Ø 22) | 42 → 30 | 14.5 → 34.5 |
| R1 | 59 | 34.5 → 52.5 |
| R2 | 112 | 52.5 → 83.5 |
| Hub (shadow gap) | 40 | 83.5 → 87.5 |
| R3 (80 teeth) | **180** | 87.5 → 131.4 |
| 8 washers + cups on R3's top, at **r 66** | 16 / 12 | 131.4 → 142.4 (1 + 10) |
| **Ring cup rims** | — | **142.4** (R3 top + 11; R4 top − 7) |
| R4 | **68** (ratio 0.38) | 131.4 → 149.4 |
| R5 (white drum) | 36 | 149.4 → 169.4 |
| Shamash washer + cup | 16 / 12 | 169.4 → 180.4 |
| **Shamash cup rim** | — | **180.4** (38 above the ring) |
| Overall | **Ø 180 × ~180** with cups, without candles | |

Relative values are what matter:
- Ring rims = R3 top + 11.
- R4 top = rims + 7.
- Shamash = R5 top + 11.

---

## 5. Spec for the modeller (matches `model/config.py`)

```
MAIN_DIAMETER    = 180.0  # all rings scale with it
DRUMS            = R1 0.33/0.154, R2 0.62/0.265, R3 1.00/0.376, R4 0.38/0.154 (18 mm), R5 0.20/0.171; no dome
CUP_OD           = 12.0   # bought metal cup, measure (<= 13)
CUP_HEIGHT       = 10.0   # visible cup, rim to bottom
WASHER_D, WASHER_T = 16.0, 1.0   # stainless heat-shield washer under each cup
HOLDER_VISIBLE   = WASHER_T + CUP_HEIGHT   # 11.0 above the seat
STUD_HOLE_D      = 3.4    # tap hole for an M4 stud; measure the stud
STUD_HOLE_DEPTH  = 10.0   # ring; shamash 8.0 (>= 1.5 PETG above the spine end); no inserts
HOLE_WALL_MIN    = 3.0    # cups turned onto R3 tooth tips (80 teeth, +2.25 deg)
CANDLE_COUNT     = 8
CANDLE_RING_R    = 66.0   # >= R4_tip_r + 25 (31.8); >= R5_tip_r + 40 (48); chord 50.5
CANDLE_ANGLE0    = 0.0    # step 45 deg, 0 = front
RING_CUP_RIM     = R3_top + 11   # Z 142.4 = R4_top - 7
SHAMASH          = stud hole on the axis in R5's flat top; rim = R5_top + 11 (Z 180.4, >= ring + 20)
DRIP_LIP         = none
FOOT             = goblet: disc Ø 112 x 14.5 + neck 20 (waist Ø 22), printed solid, 8 pockets x 4 M10 washers
STABILITY_MIN    = 35 deg with ballast (model: 36)
```

### Parts
| # | Part | Qty | Size (approx) | Material | Print / notes |
|---|---|---|---|---|---|
| 1 | **Foot + neck** with 8 ballast pockets | 1 | Ø 112 × 34.5 | PETG | Solid infill; 32 M10 washers glued in |
| 2 | R1 | 1 | Ø 60 × 18 | PETG | Upright |
| 3 | R2 with the shadow-gap hub | 1 | Ø 112 × 35 | PETG | Upright |
| 4 | **R3** with 8 tap holes at r 66 | 1 | Ø 181 × 45 | **PETG** | Upright, no supports, ≥ 4 perimeters. Fits a 220 bed |
| 5 | **R4** (0.38 × 18) | 1 | Ø 69 × 18.6 | **PETG** | Upright |
| 6 | **R5** with the shamash tap hole | 1 | Ø 37 × 21 | **PETG** | Upright |
| 7 | Spine | 1 | D 10 × 131, keyed | PETG | Through all rings; 4 mm into R5 |
| — | Metal: 9 cups Ø 12 × 10 with M4 stud (shamash stud ≤ 8), 9 stainless washers Ø 16 × 1, 32 M10 washers | | | bought | |

### Hard requirements
1. 8 cup rims at the same Z, on one circle, at 45° steps; candles vertical.
2. Chord between neighbours ≥ 40 mm (design: 50.5).
3. No plastic above any candle. From each candle axis:
   - ≥ 25 mm to R4's tooth tips, which rise ≤ 7 mm above the rim (design: 31.8).
   - ≥ 40 mm to any other plastic higher than the rim (R5, design: 48).
4. Shamash alone at the centre top, cup rim ≥ 20 mm above the ring (design: 38).
5. Metal at every flame: cup + stainless washer on all 9. No plastic touches a cup, and no printed collars. Everything printed in PETG.
6. Nothing outside R3's tooth tips in top view. Holders rise 11 mm, straight up.
7. Every part fits 220 × 220 and prints without supports.
8. Tips at ≥ 35° with ballast. The ballast is part of the build.
9. Nothing painted within ~5 mm of any hole.

---

## 6. Motifs: five shapes embossed in R3's pleats

### 6.1 Idea
On the fountain, R3's face is a run of **vertical stripes** (one per pleat face) with a few **flat emblems** in them: round discs and a "+" (`research/user-reference-motifs.png`). Here **three emblems are Hanukkah motifs** and **two stay Agam's own**. They are graphics only. There is **no plaque or tile**: each shape is embossed straight onto the pleats, so it is sliced into narrow vertical strips by the teeth, and the ring's stripes run all around and between the shapes.

### 6.2 Placement (R3 only; R1, R2, R4, R5 carry stripes only)

| Angle (0° = front) | Motif | Size (R3 is 34 mm tall) |
|---|---|---|
| **0°** (front) | **"חנוכה"** | word ~80 mm wide (≈ ±25°); letters **14 mm**, stroke ≥ 2.4, Secular One |
| **90°** | **Magen David**, outline: two interlaced triangles | 24 mm point to point, band 2.5 mm |
| **180°** (back) | **Agam disc** with a vertical bar (as on the fountain) | Ø 24, bar 5 |
| **225°** | **Agam "+"** | 22 mm, arms 7 |
| **270°** | **Dreidel**: flat silhouette with **ג** | 26 tall: handle 4 × 5, body 16 × 13, point 16 × 8; letter 10 mm |

* 5 motifs in all, each under a candle position, so they read as part of the ring's rhythm. Everything else is stripes.
* Keep each motif ≥ 4 mm from R3's top and bottom edges.

### 6.3 How a motif is built (as in the current model)
* **Fill:** inside the shape, the pleat surface is raised **0.6 mm** (offset along the pleat faces). The teeth stay visible, so the shape is cut into strips, one per pleat face.
* **Outline:** a ridge **0.8 mm wide, 1.0 mm high** runs round every shape, and round inner parts that take a second colour (the bar on the disc, the ג on the dreidel). It is the paint stop. Stripes end at the ridge.
* **No tile, no valley filling, no plaque.** Nothing extends beyond the tooth tips by more than the 1.0 mm ridge.
* **Printability:** the relief follows the vertical pleat faces, so no overhang beyond 1.0 mm. No supports.
* **Minimums:** features ≥ 10 mm, strokes ≥ 2 mm (Hebrew letters 2.4 mm), gaps ≥ 1.5 mm.
* **Text:** place the 5 letters individually so that CAD engines that do not reorder Hebrew cannot mirror the word. Check in a render that it reads ח-נ-ו-כ-ה from the right.

### 6.4 Colour plan (`painting/guide.md` §3.3 and §5 are the master)
Palette: 1 yellow, 2 orange, 3 red, 4 pink, 5 sky blue, 6 turquoise (mint = 6 + white), 7 green, 8 cobalt, 9 navy, 10 white, 11 lilac.

Each motif sits on the R3 slice (45° sector) whose stripes contrast with it. The fill is one colour, and the outline ridge is navy or the fill colour.

| Motif | Stripes around it (R3 slice) | Fill | Outline / inner detail |
|---|---|---|---|
| **"חנוכה"** (0°) | **8 cobalt / dark blue** front sector | letters **1 yellow** | ridge **9 navy** |
| Magen David (90°) | 3 red | **1 yellow** | ridge 9 navy |
| Agam disc (180°) | 6 turquoise | **3 red** | bar 9 navy |
| Agam "+" (225°) | 9 navy | **4 pink** | ridge 4 pink or 10 white |
| Dreidel (270°) | 5 sky blue | body **2 orange** | handle and point 11 lilac, ג 10 white |
| R3 step, dome crown | — | **unpainted** (grey steel) | |
| Dome | 10 white or 5 sky blue | | |
| Plinth disc | 9 navy or grey | | |
| Metal cups and washers | not painted | | |

**Painting order:** stripes ring by ring, stopping at the motif ridges → motif fills strip by strip → outline ridges and small details with a fine Posca (PC-3M) → touch-ups by a grown-up.

---

## 7. Dropped (kept for reference)
Pool, polymorph band, dreidel shamash holder and printed candle bosses were tried in earlier versions and are out at the user's request. If a pool ever returns, it is decorative only: it lies under R3 and below every flame.
