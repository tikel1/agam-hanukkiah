# Fountain colour program: copying the real Dizengoff fountain

Goal: colours **as close as possible to the original fountain**. The only additions:
- **HANUKKAH** in blue
- a **Magen David** in green
- a **dreidel** in orange

Also: no black, white ring tops.

This replaces the cross-work recommendation in `agam-palettes.md` §4–5. Keep that file only as background.

**Data and check:**
- [`fountain_colour_program.py`](fountain_colour_program.py) holds the palette, the sector tables and the rotation. Run it to:
  - check that every sector table covers the whole ring;
  - list the stripes under each emblem;
  - write [`fountain_colour_program.json`](fountain_colour_program.json), the per-face lists for the current tooth counts;
  - write [`fountain_colour_program.svg`](fountain_colour_program.svg), the unrolled preview.

**Confidence tags:**
- **[H]** high: seen directly in the 1986 photo and confirmed by later photos of the same side.
- **[M]** medium: from 2012–2014 photos, translated to the 1986 shades.
- **[L]** low: inferred.

---

## 1. Sources and what they show

| Photo | Date | Use |
|---|---|---|
| [`user-reference-top.png`](user-reference-top.png) | 1980s (fresh original paint) | **Main reference.** Front half of every ring from slightly above. Original shades |
| [PikiWiki 507](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_507_Geography_of_Israel_%D7%9E%D7%96%D7%A8%D7%A7%D7%94_%D7%91%D7%9B%D7%99%D7%9B%D7%A8.JPG) | Jul 2004 | Original paint, other angle, still bright |
| [Telaviv10.jpg](https://commons.wikimedia.org/wiki/File:Telaviv10.jpg), [`refs/pre2011_front_original.jpg`](refs/pre2011_front_original.jpg), [`refs/2010_original_faded_profile.jpg`](refs/2010_original_faded_profile.jpg) | 2006–2010 | Original layout, faded: cream, ochre, olive, brick. **These are faded original colours, not a separate palette.** This corrects fountain.md §4.4 |
| [המזרקה בכיכר דיזינגוף.JPG](https://commons.wikimedia.org/wiki/File:%D7%94%D7%9E%D7%96%D7%A8%D7%A7%D7%94_%D7%91%D7%9B%D7%99%D7%9B%D7%A8_%D7%93%D7%99%D7%96%D7%99%D7%A0%D7%92%D7%95%D7%A3.JPG) | Sep 2012 | **Close-up of R3 pleats.** Shows which face set carries which picture |
| [Dizingoff Square.JPG](https://commons.wikimedia.org/wiki/File:Dizingoff_Square.JPG), [כיכר דיזינגוף 2/3/5](https://commons.wikimedia.org/wiki/File:%D7%9B%D7%99%D7%9B%D7%A8_%D7%93%D7%99%D7%96%D7%99%D7%A0%D7%92%D7%95%D7%A3_3.JPG), [Zina Dizengoff Square](https://commons.wikimedia.org/wiki/File:Zina_Dizengoff_Square_in_Tel_Aviv.JPG), [`refs/2014_front_vivid.jpg`](refs/2014_front_vivid.jpg), [`refs/2013_front_vivid_other_side.jpg`](refs/2013_front_vivid_other_side.jpg) | 2012–2014 repaint | Both sides, several angles. **The repaint kept the original layout sector for sector**, only with stronger shades: salmon → red, periwinkle → cobalt |

**Is there black?** No. The darkest colour on the real fountain is a **dark navy** on R2 (and dark red / brick on R2 and R1). In shade it reads almost black, but it is blue. The program keeps navy `#2B2F6B`, which is clearly blue, not black. If even that is too dark, use `blue` `#3E5FB0`.

**White strips (user photo):** yes. On every ring one face set is **white over large sectors**, and the colours sit on the other face set. That gives the white strips between colours. Where both face sets are coloured (the ends of each sector run), the strips are colour against colour.

---

## 2. How the fountain is laid out

### 2.1 Left and right faces carry two different pictures [H]

The model's face numbering:
- Face k = 0 is at the front. Degrees increase counter-clockwise seen from above, which is left to right as you face the ring.
- Each tooth has a **left** face (clockwise side) and a **right** face (counter-clockwise side).
- At a ring's **left edge** you see only its **right** faces. At its **right edge** you see only its **left** faces.

This explains the user photo and the 2012 close-up:

| Ring | Left edge (= right faces) | Right edge (= left faces) |
|---|---|---|
| **R3** | white | orange → yellow |
| **R4** | solid coral red | solid teal |
| **R2** | orange | navy |
| **R5** | pale blue | white / marigold |

Each ring therefore carries **two complete pictures**, as in an Agamograph:

| Ring | Right-face picture | Left-face picture | Contrast |
|---|---|---|---|
| R5 | pale blue → white | lilac → yellow → orange | |
| R4 | coral → rose → white | white → mint → teal | red vs green: complementary |
| R3 | white → lilac → periwinkle / blue, carrying the big disc | yellow → lilac → rose → orange → yellow | |
| R2 | orange → brick red → white | white → navy | warm vs dark cool |
| R1 | brick red → white → grey | white → green → white | red vs green |

Head-on you see them interleaved. That is the "white strip between colours" look.

### 2.2 Two halves [H for half 1, M for half 2]

Each ring repeats its structure in **two halves of about 180°**, with different colours in each half. On R3, each half runs:
1. white / yellow;
2. the **disc** (half 1: yellow + marigold; half 2: red / teal with a bar);
3. white / lilac or pink;
4. blue / rose or red, with a **"+"** on it (half 1: pink; half 2: mint);
5. a solid end colour (half 1: orange → yellow; half 2: orange, with a cobalt block on the right faces).

In both halves the disc sits about 27–29° left of the half's centre and the "+" about 24–39° right of it.

- Half 1 is exactly what the user photo shows. Fountain angle 0 = the centre of that photo.
- Half 2 comes from the 2013–14 photos of the other side.
- One 2013 photo shows a teal disc with a bar and a cobalt end. That may be half 2 seen from another angle, or a third sector [L].

### 2.3 Fitting the model's emblems

The model has one disc (180°) and one "+" (225°). Rotating the fountain program by **+207°** gives:
- the fountain's half-1 disc (fountain −27°) lands at model 180°;
- its "+" (fountain +24°) lands at model 231°, next to the model's 225°;
- HANUKKAH at the model front falls on half 2's white / yellow / rose stretch, where the fountain has no motif.

Half 2's own disc would land under the word, so it is left out. The fountain's own disc and "+" are not additions, so they stay.

**`ROTATION = 207` (model angle = fountain angle + 207).**

---

## 3. Palette: original 1986 shades

Normalised from the user photo (soft slide colours) and cross-checked against the 2004 and 2012 photos. Acrylic names are the nearest **standard** colours. **Paint a test swatch first.** The 1986 shades are softer than the tubes, so many need a little white.

| Paint (config name) | Hex | Where on the fountain | Amsterdam Standard (nearest) | Posca (nearest) |
|---|---|---|---|---|
| white | `#F4F1E4` | white face sets on every ring | 105 Titanium white | White |
| yellow | `#F2C94C` | R3 left faces, R5, disc | 269 Azo yellow medium | Sunshine Yellow |
| orange | `#E8893F` | R3/R5 ends, R2 left end, disc half; **dreidel** | 276 Azo orange + white | Light Orange |
| coral | `#E8655C` | R4 red, R3 half 2 | 315 Pyrrole red + white | Coral Pink |
| brick | `#A8322A` | R2 and R1 dark red | 399 Naphthol red deep | Red + touch of brown |
| rose | `#DC8A86` | R3 salmon-pink, R4 pink | 330 Persian rose + white | Salmon Pink |
| lilac | `#9A8CC0` | R3, R4, R5 | 568 Permanent blue violet + white | Lavender |
| periwinkle | `#7484C4` | R3 right faces (half 1) | 504 Ultramarine + 568 + white | Light Blue + Lavender |
| light_blue | `#A3C1E0` | R5 right faces, R3 | 551 Sky blue light | Light Blue |
| blue | `#3E5FB0` | R2 / R3 blue block; plinth (pool); **HANUKKAH** | 504 Ultramarine | Blue |
| navy | `#2B2F6B` | R2 left faces (the darkest colour, **not black**) | 504 + 566 Prussian blue | Navy Blue |
| mint | `#A8DDB5` | R4, the "+" (half 2) | 660 Turquoise green light + white | Mint |
| teal | `#3E8F7C` | R4 right end, R3 half 2 | 661 Turquoise green | Emerald Green |
| green | `#4E9E5E` | R1; **Magen David** | 618 Permanent green light + touch of blue | Green |
| grey | `#A9B3B6` | R1 grey faces, stem (steel) | 710 Neutral grey + white | Light Grey |

That is 15 colours.

**12-pot version:**
- brick → coral;
- periwinkle → blue + white (mixed);
- grey → light_blue.

---

## 4. Colour program per ring

Sectors are in **fountain angles** (0 = centre of the user photo, counter-clockwise; half 1 = −90…90, half 2 = 90…270). Model angle = fountain + 207.

### R5 (top): same in both halves [H]

| Fountain ° | Right faces | Left faces |
|---|---|---|
| −90 … −50 | light_blue | lilac |
| −50 … −10 | white | lilac |
| −10 … 34 | white | yellow |
| 34 … 90 | white | orange |
| 90 … 130 | light_blue | lilac |
| 130 … 170 | white | lilac |
| 170 … 214 | white | yellow |
| 214 … 270 | white | orange |

### R4 [H half 1, M half 2]

| Fountain ° | Right faces | Left faces |
|---|---|---|
| −90 … −28 | coral | white |
| −28 … 14 | rose | white |
| 14 … 39 | white | mint |
| 39 … 90 | white | teal |
| 90 … 140 | coral | white |
| 140 … 190 | lilac | white |
| 190 … 230 | white | teal |
| 230 … 270 | white | mint |

### R3 (main) [H half 1 up to about +35° on the right faces; M elsewhere]

| Fountain ° | Right faces | Left faces | Motif |
|---|---|---|---|
| −90 … −21 | white | yellow | the disc sits at −34 … −21 (→ model 180°) |
| −21 … −11 | white | lilac | |
| −11 … 2 | lilac | rose | |
| 2 … 35 | periwinkle | rose | the "+" at about +24 (→ model 231°) |
| 35 … 54 | periwinkle | orange | |
| 54 … 90 | periwinkle | yellow | |
| 90 … 159 | white | yellow | (half 2 disc: dropped, under the word) |
| 159 … 180 | white | rose | |
| 180 … 200 | light_blue | coral | |
| 200 … 215 | teal | coral | |
| 215 … 234 | teal | orange | |
| 234 … 270 | blue | orange | |

### R2 [H half 1, M half 2]

| Fountain ° | Right faces | Left faces |
|---|---|---|
| −90 … −53 | orange | white |
| −53 … −8 | brick | white |
| −8 … 90 | white | navy |
| 90 … 135 | brick | white |
| 135 … 200 | white | navy |
| 200 … 270 | blue | blue (a solid blue block, as in 2012) |

The real R2 faces also carry small white rectangles at mid-height, a two-row pixel picture. They are left out: too fine for 7 mm stripes.

### R1 (bottom): same in both halves [M]

| Fountain ° | Right faces | Left faces |
|---|---|---|
| −90 … −30 | brick | white |
| −30 … 30 | white | green |
| 30 … 90 | grey | white |
| 90 … 150 | brick | white |
| 150 … 210 | white | green |
| 210 … 270 | grey | white |

### The rest

| Part | Paint | Why |
|---|---|---|
| Stem | grey (one colour, all 16 sectors) | the real stem is plain steel |
| Plinth | blue | the pool's blue mosaic |
| Ring tops | white | user rule; the real tops are bare steel |
| Dome | white | the real dome is clear |

### Emblems on R3 (model angles)

| Emblem | Angle | Paint | Stripes under it (from the script) |
|---|---|---|---|
| **HANUKKAH** (addition) | 0° ±44 | **blue** | white, yellow, rose, coral, light_blue |
| **Magen David** (addition) | 90° | **green** | orange (left faces), blue (right faces) |
| **Dreidel** (addition) | 270° | **orange**, ג **white** | yellow, periwinkle |
| Disc (fountain's own) | 180° | **orange**, no bar. The 1986 disc is yellow + marigold; orange is used because yellow would vanish on the yellow faces | white, yellow, lilac |
| "+" (fountain's own) | 225° | **mint** (side 2's colour; side 1's 2012 pink would vanish on the rose faces) | periwinkle, rose |

No outlines: paint each outline ridge in its emblem's own colour, or drop the ridge.

---

## 4b. Style direction: Dana Barlev concept sketch (not an Agam work)

[`user-reference-agam-menorah.png`](user-reference-agam-menorah.png) is a concept sketch by designer Dana Barlev (signed "דנה ברלב"). It is a hanukkiah in the fountain's style. **It is style direction only. The colours above stay anchored on the real fountain.**

What it shows about colour at this scale, ring by ring, with sampled hex values (sketch rendering only, for reference):

| Ring | Sketch | Lesson |
|---|---|---|
| Top drum (R5) + shamash collar | **plain white**, both faces | a calm white top frames the shamash and stops the stack looking busy |
| R4 | red / white (left end, right faces) → red / sky alternating → solid sky blue (right end, left faces). Red `#B13641`, sky `#4798C9` | a **two-colour picture swap**: right faces red, left faces blue, white in between. The same mechanism as the fountain's R4 (coral vs teal) |
| R3 (main) | yellow / white → **orange disc** on white → orange / white → white / blue with a **pink "+"** (two pink squares) → blue / white → solid cobalt with a ghost disc → solid red end. Yellow `#E0BB44`, orange `#CF5534`, pink `#CFA4B6`, cobalt `#224E95`, red `#C0352B` | **matches the real fountain's half 1 (2012 version) almost sector for sector.** One face set stays white, which is what makes the colours readable at a 7 mm pitch. Only one disc and one "+" on the visible side |
| R2 | a **continuous gradient, no white**: red → brown → green → turquoise → sky round the front, with a lighter lower band (orange / peach / mint) | gradient drums below make a calm base under the busy striped main ring |
| R1 | continuous gradient red → orange → olive green, no white | same idea, shorter walk |
| Stem + foot | white | white below and above frames the colour |
| Candles | blue `#2A5DA4` in white cups | the candles echo the cobalt |

Stripe density: the sketch shows about 22 pleats across the front of R3. The model has about 40 (81 teeth at a 7 mm pitch). That is finer, but the same reading: one face set white, the other coloured.

### Variant "sketch": fountain colours, sketch arrangement (optional)

This is `VARIANT = "sketch"` in [`fountain_colour_program.py`](fountain_colour_program.py), previewed in [`fountain_colour_program_sketch.svg`](fountain_colour_program_sketch.svg).

R3 and R4 stay exactly as in §4. Only these change:

| Part | Sketch variant |
|---|---|
| R5 | white on both faces |
| R2 | a gradient with no white, in each half (six 30° steps). Right faces: orange → coral → brick → navy → blue → light_blue. Left faces: one step ahead (coral → brick → navy → blue → light_blue → orange), so the two pictures differ and head-on the walk looks smooth |
| R1 | the same kind of gradient. Right faces: brick → coral → orange → yellow → green → teal. Left faces: one step ahead |
| Stem, plinth | white |

Emblems, tops and dome are the same as §4. Both variants use only the §3 palette.

## 5. Encoding in `model/config.py`

The existing `Stripes` already accepts one colour per face: `colours` = a tuple as long as the tooth count, `run=1`, `offset=0`. Steps:

1. Copy `PAINTS`, `SECTORS`, `ROTATION` and the functions `tooth_count`, `front_tooth`, `face_centre_concept`, `paint_at` and `faces` from [`fountain_colour_program.py`](fountain_colour_program.py) into a model module, e.g. `model/fountain_colours.py`. They mirror `paint_program.face_span` exactly.
   - For the §4b variant, also copy `SKETCH_OVERRIDES`, `sectors()` and `VARIANT`, and set `VARIANT = "sketch"`.
   - With that variant, `STEM_COLOURS = ("white",)` and `PLINTH_PAINT = "white"`.
   - The JSON holds both variants' per-face lists under `variants`.
2. In `config.py`:

```python
PAINTS = (  # numbers are the paint numbers on the maps
    Paint(1, "white", "#F4F1E4"),  Paint(2, "yellow", "#F2C94C"),   Paint(3, "orange", "#E8893F"),
    Paint(4, "coral", "#E8655C"),  Paint(5, "brick", "#A8322A"),    Paint(6, "rose", "#DC8A86"),
    Paint(7, "lilac", "#9A8CC0"),  Paint(8, "periwinkle", "#7484C4"), Paint(9, "light_blue", "#A3C1E0"),
    Paint(10, "blue", "#3E5FB0"),  Paint(11, "navy", "#2B2F6B"),    Paint(12, "mint", "#A8DDB5"),
    Paint(13, "teal", "#3E8F7C"),  Paint(14, "green", "#4E9E5E"),   Paint(15, "grey", "#A9B3B6"),
    Paint(0, "bare", "#DADBD6"),
)

def _ring(name: str) -> RingPaint:
    import fountain_colours as fc  # holds SECTORS / ROTATION / faces()
    teeth = fc.tooth_count(next(d for d in DRUMS if d.name == name).diameter_ratio * MAIN_DIAMETER)
    return RingPaint(left=Stripes(fc.faces(name, "left", teeth)), right=Stripes(fc.faces(name, "right", teeth)))

RING_PAINT = {d.name: _ring(d.name) for d in DRUMS}  # no top_ring_radii: tops stay white
DOME_PAINT, PLINTH_PAINT = "white", "blue"
STEM_COLOURS = ("grey",)
EMBLEM_PAINT = {
    "word": ("blue",), "star": ("green",), "dreidel": ("orange", "white"),
    "disc": ("orange", "orange"), "cross": ("mint",), "extra_disc": ("orange",),
}
EMBLEM_OUTLINE_PAINT = None  # = paint each ridge in its zone's colour (no outlines); needs a small code change
```

Notes:
- `COMPLEMENT`, `RAINBOW` and `BLACK_WHITE` are no longer used by the program.
- `faces()` follows whatever `DRUMS` says. R1/R5 at 0.36 (29 teeth) are fine here: explicit lists have no seam problem.
- Current tooth counts: R1 29, R2 55, R3 81, R4 50, R5 29.

---

## 6. Open points

- **Half 2 [M]** is reconstructed from 2012–14 photos, translated to 1986 shades. No 1980s photo of that side was found. A real 1980s photo of the far side would firm it up.
- **Exact sector edges** come from one oblique photo and are good to about ±5°. The right faces of half 1 beyond +35° are hidden in the 1986 photo; I used periwinkle, after the 2012 blue in the same place.
- **The 1986 slide may have shifted colour.** The 2012 shades (`refs/2014_front_vivid.jpg`) are the stronger alternative for each sector:

| 1986 | 2012 |
|---|---|
| coral | red |
| rose | pink |
| periwinkle | cobalt |
| mint | mint |
| teal | turquoise |
