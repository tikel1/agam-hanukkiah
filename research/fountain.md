# Yaacov Agam, "Fire and Water" (אש ומים), Dizengoff Square, Tel Aviv

Research brief for the 3D model and painting sessions.
Every statement is tagged:

- **[S]** sourced fact (source linked)
- **[P]** measured from photos (method given, roughly ±10–15%)
- **[G]** guess or interpretation

Local copies of the key photos are in [`refs/`](refs/). They come from Wikimedia Commons and israelpublicart.com and are kept here for personal reference only.

---

## 1. History in brief

| When | What | Tag |
|---|---|---|
| 1976–86 | Agam worked on the piece for about ten years | [S] en-wiki |
| 15 Jul 1986 | Dedicated in the centre of Dizengoff Square. The square was then a raised pedestrian deck above the traffic circle (built 1978). The fountain replaced a glass sculpture by Alan David | [S] he-wiki, en-wiki |
| 1986 | Built by **Ormat** (Yavne). About **6 t**. Kinetic: a mechanism **rotated the three central wheels**. Water jets ran at varying heights, a **gas flame** rose from the centre of the top wheel, and music played. Shows ran four times a day for about 15 minutes, later every hour | [S] he-wiki, israelpublicart |
| Aug 2011 – Sep 2012 | Restored for about ₪2 M. **Panels repainted in bright new colours.** The ring-rotation mechanism was **removed**, so the rings no longer turn | [S] he-wiki, ynetnews, Algemeiner 2012 |
| 18 Dec 2016 | Dismantled and stored at the Reading car park while the raised square was demolished. The square was then rebuilt at street level and reopened in 2018 | [S] he-wiki, en-wiki |
| Jul 2018 | Returned to the centre of the new street-level square in a new pool, **without the coloured panels**: bare grey steel drums only. Agam and the municipality disagreed, partly over the exact shades. Agam promised new panels for Eurovision 2019. They never came | [S] he-wiki, en-wiki, ynetnews |
| 2023–25 | The bare fountain became a makeshift memorial for the hostages. Banners were wrapped around the main drum | [S] en-wiki; photo 2026 |
| Jun 2026 | Agam died at 98. The panels are still not reinstalled. His son Ron hopes for a deal with the city | [S] ynetnews (Jun 2026) |
| **Today (Nov 2026)** | **Bare steel drums. Water still works (jets, top water-dome, curtain off the main ring). No colour, no rotation, no fire** | [S]/[P] |

**Which version to model:** the colourful **2012–2016 repaint**. It is the brightest and best photographed, and it is what people picture. The faded 1986 original palette is given in §4.4 as an alternative.

---

## 2. Geometry

### 2.1 Overall form [P]

Five stacked coaxial **drums (rings)** sit on a short stem in a large round shallow pool, with a small transparent dome on top.
- The stack is **symmetric about the big middle ring**: R1 matches R5 in diameter, and R2 matches R4.
- R3 is the biggest ring: widest and tallest. Seen from the side it looks like a spinning top or a stack of pancakes.
- Every ring has a **pleated, toothed outer skin**: vertical panels forming a zigzag in plan, like a gear with triangular teeth.
- Under the panels each ring is a **smooth steel cylinder**. The 2018 and 2022 photos of the bare drums show this clearly: [refs/2022_bare_core_no_panels.jpg](refs/2022_bare_core_no_panels.jpg).

The sources say **5 wheels** [S, he-wiki] and "five large concentric metal rings" [S, israelpublicart]. Photos agree: 5 rings.

### 2.2 Real dimensions

| Item | Value | Tag |
|---|---|---|
| Diameter of the largest (central) wheel | **6 m** | [S] he-wiki |
| Height | **9 m** | [S] he-wiki, **but see the note** |
| Weight | 6 t | [S] he-wiki |
| Visible sculpture height, water to dome top | **≈ 3.9 m** (0.65 × main diameter) | [P] |
| Pool diameter | ≈ 12–13 m (≈ 2 × main ring) | [P] |

> **Height conflict.** In every photo the visible stack is only about 0.6–0.65 × the main-ring diameter. With a 6 m ring that is about 3.9 m, not 9 m. The 9 m figure probably includes the water dome and flame, or the machinery below the pool (the old raised deck had a plant room underneath). **Use the photo proportions below. They are internally consistent across 6 photos from 4 different years.**

### 2.3 Rings, bottom to top [P]

Measured mainly from the 2014 telephoto front view ([refs/2014_front_vivid.jpg](refs/2014_front_vivid.jpg), shot from roughly the R2 level, so little distortion). Cross-checked against the 2010, 2013 and 2022 photos. Diameters include the panel teeth.

| Part | Diameter / main dia | Height / main dia | Notes |
|---|---|---|---|
| Stem / plinth | ≈ 0.25 | ≈ 0.03 | dark, recessed, partly under water; a round plinth disc sits in the pool |
| **R1** bottom ring | 0.36 | 0.09 | sits just above the water |
| **R2** | 0.68 | 0.11 | sits directly under R3 |
| **R3** main ring | **1.00** | **0.19** | overhangs R2 a lot; water curtain falls off its outer lower edge |
| **R4** | 0.67 | 0.10 | sits directly on R3 |
| **R5** top ring | 0.35 | 0.08 | sits on R4 |
| Dome | ≈ 0.20 | ≈ 0.05 | clear acrylic (or water-bell) cap; the flame came from here |

Ring spacing: **none**. The rings stack directly on one another with no visible gaps; each smaller ring is simply inset. R3's flat top is a wide visible step (annulus from r 0.34 to 0.5 × main dia). The same goes for R4's top. The water nozzles stand on these steps.

### 2.4 Toothed / gear-like edge [P/G]

- Each ring's outer surface is made of **flat vertical panels set as a zigzag (pleats)**. In plan it looks like a gear with **triangular teeth**, or a folded paper fan bent into a circle. [P] Panels look like fanned cards in [refs/2010_original_faded_profile.jpg](refs/2010_original_faded_profile.jpg), and the ragged top edge shows the zigzag.
- Panels run the **full height** of each ring, top to bottom. There are no horizontal breaks. [P]
- **Pitch** (tooth to tooth) ≈ **0.028 × main diameter** (about 17 cm real). It looks the **same on every ring**, so smaller rings have fewer teeth. [P] counted on the front half of each ring in the 2014 photo and doubled.
  - R3 ≈ 100–120 teeth (use **112**)
  - R2 / R4 ≈ 70–80 (use **75**)
  - R1 / R5 ≈ 36–44 (use **40**)
- **Tooth depth** ≈ 0.5 × pitch, faces at about ±45°, symmetric teeth. [G] Strong foreshortening of one face set when seen off-axis suggests near-symmetric V-pleats.
- The tops and bottoms of the rings are flat (steel). [P]
- Each tooth has **two faces, A and B**, that carry different colour images. This is the whole point of the piece (§4.1).

The pool has its own small teeth. Before 2016, the inner rim of the old pool had a **continuous row of small metal pyramid / zigzag teeth** plus grey spotlight cans on goosenecks (visible in pre-2016 photos). The 2018 pool has a plain rounded stone rim and small nozzles.

### 2.5 What moves, where the water and fire are

| Feature | Detail | Tag |
|---|---|---|
| Rotation | the **three central wheels (R2, R3, R4)** rotated; R1 and R5 were fixed. Removed in 2011–12 | [S] he-wiki |
| Fire | gas flame from the **centre of the top wheel** (under/through the dome) | [S] he-wiki |
| Water | jets at varying heights; music show | [S] |
| Water jets | a ring of thin vertical jets on the **top step of R3** near its outer edge, more on R4's step, arching outward; a **water dome / bell** over the top; a **curtain** falling from R3's rim; floor jets in the pool | [P] photos 2010–2022 |
| Pool floor | blue tile with radial stripes (pre-2016) | [P] |

**Hanukkiah tip** [G]: the top centre, where the flame used to be, is a natural spot for the **shamash**. The 8 candles could sit on the R3 top step: a ring of 8, or 4+4. The other session decides.

---

## 3. Sketches

### 3.1 Elevation, normalised to total height H = 1.0 (stem bottom to dome top)

Full SVG with labels: [`fountain_sketch.svg`](fountain_sketch.svg)

```
                         )   flame (removed)
                       .-^-.         dome      h .077  d .31
                 +-----------+       R5        h .123  d .55
           +-----------------------+ R4        h .154  d 1.04
  +-----------------------------------------+
  |||||||||||||||||| R3 MAIN |||||||||||||||| h .292  d 1.54
  +-----------------------------------------+
           +-----------------------+ R2        h .169  d 1.04
                 +-----------+       R1        h .138  d .55
                   +-------+         stem      h .046  d .38
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  pool, d ≈ 3.1
```

### 3.2 Plan of one ring edge (zigzag pleats)

```
 outside
   /\  /\  /\  /\  /\  /\        A = left-hand face of each tooth
  /A \/A \/A \/A \/A \/A \         B = right-hand face
     B   B   B   B   B
 ------------------------------  smooth core drum
 inside
```

### 3.3 Top view

```
            .-""""""""""-.
         .'  .-""""""-.   '.        outer: R3 (d 1.54), toothed edge
        /  .'  .-""-.  '.   \       middle: R4 (d 1.04)
       |  |   |  ()  |   |   |      inner: R5 (d .55), dome + flame at centre
        \  '.  '-..-'  .'   /
         '.  '-......-'   .'
            '-..........-'
```

---

## 4. Colour

### 4.1 Pattern logic (Agam's polymorph principle)

- [S/G] Agam's signature is the **"polymorph"** (the same idea as his agamographs). A pleated surface carries **image A on one set of faces and image B on the other**. Walking around the work, you see A, then a mix, then B. The ring rotation did the same thing for a viewer standing still. The sources call it "coloured geometric shapes that look like different images from different angles" [S en-wiki, israelpublicart].
- [P] Each face set typically carries:
  1. **Spectrum stripes**: colours that progress gradually around the ring (white → yellow → orange → red → pink, or red → blue, or turquoise → mint).
  2. **Large flat geometric motifs** painted across many teeth, visible only from one viewpoint: a **big disc / circle** (dark red or teal) with a vertical bar through it, a **"+" cross** in mint, and solid sectors such as a full cobalt-blue or full orange block.
- [P] **Head-on**, you see thin interleaved stripes: one A colour, one B colour, alternating. That is the barcode look in photos.
- [P] **The sides differ.** No two quadrants look alike. Each ring runs a colour journey around its circumference, and the rings use different dominant hues so they contrast with their neighbours:
  - R3 is mostly white and spectrum with motifs.
  - R2 is darker: red, navy and blue.
  - R4 is lighter: crimson, white, turquoise and mint.

### 4.2 Colour map per ring: 2012–2016 repaint (recommended)

Sources: [refs/2014_front_vivid.jpg](refs/2014_front_vivid.jpg), [refs/2013_front_vivid_other_side.jpg](refs/2013_front_vivid_other_side.jpg), [refs/2012_after_repaint.jpg](refs/2012_after_repaint.jpg), [refs/2016_night.jpg](refs/2016_night.jpg). Sectors are named as clock positions **[G]**: it is not known which compass direction each faced.

| Ring | Sector / face | Colours seen [P] |
|---|---|---|
| **R5** top | side 1 | sky blue, pale blue, white |
| | side 2 | orange, peach, white |
| **R4** | sector 1 | crimson + white stripes |
| | sector 2 | crimson / sky blue / lilac interleaved |
| | sector 3 | turquoise → mint gradient, white, lots of white faces |
| **R3** main | sector 1 (≈ 9 o'clock) | white faces + **lemon / golden / orange** stripes, with a big **dark-red disc** spanning about 8 teeth |
| | sector 2 (≈ 10–11) | white + **pink / crimson** stripes, with a **teal disc with a vertical bar** |
| | sector 3 (≈ 12) | interleaved **orange / turquoise / red** with a **mint "+" cross** |
| | sector 4 (≈ 1–2) | **red / sky-blue** alternating; faint circle ghosts |
| | sector 5 (≈ 3) | ends in solid **cobalt blue** on one side; solid **orange** at the opposite end |
| **R2** | sector 1 | **crimson / white / navy** stripes |
| | sector 2 | navy, white |
| | sector 3 | solid **cobalt blue** block |
| | other side | **orange / yellow** dominant with blue stripes (2016 night, 2012 photos) |
| **R1** bottom | all round | **red, white, green**, light grey stripes; one side yellow + red |
| Stem, ring tops and bottoms, dome frame | | stainless / grey steel (paint mid grey or silver) |
| Dome | | clear (leave unpainted, or very pale blue) |
| Pool | | deep blue water; blue tiles; rim light stone |

### 4.3 Palette, 2012 repaint (approximate hex)

Picked by eye and k-means from sunlit photo areas, then normalised to clean paint colours. **Photos shift colour, so treat these as ±.**

| # | Paint-friendly name | Hex | Where |
|---|---|---|---|
| 1 | Bright white | `#F5F3EA` | the dominant face colour on R3 and R4 |
| 2 | Lemon yellow | `#F5CF1D` | R3 sector 1, R2 other side |
| 3 | Marigold / golden yellow | `#F0A431` | R3 sector 1 |
| 4 | Orange | `#F36A1E` | R3 end, R5, R2 |
| 5 | Red-orange (vermilion) | `#E8432B` | R3 sector 3–4 |
| 6 | Crimson | `#C2283F` | R4, R3, R2, R1 |
| 7 | Pink | `#F07C95` | R3 sector 2, R4 |
| 8 | Light pink | `#F5BCC8` | R3 sector 2 |
| 9 | Lilac / violet | `#8E6BB0` | R4 middle |
| 10 | Navy | `#1D2554` | R2 |
| 11 | Cobalt / royal blue | `#1F64B4` | R3 end, R2 block |
| 12 | Sky blue | `#4AAEE0` | R3, R4, R5 |
| 13 | Pale blue | `#B8DCF0` | R5 |
| 14 | Turquoise / teal | `#22A9A8` | R3 disc, R4 |
| 15 | Mint | `#9FDCCB` | R4, R3 cross |
| 16 | Grass green | `#47A84A` | R1 |
| 17 | Peach | `#F1C39B` | R5 |
| 18 | Steel grey | `#9A9C9E` | tops, bottoms, stem |

### 4.4 Original 1986 palette (faded by 2010), alternative [P]

> **Correction:** a fresh 1980s photo ([`user-reference-top.png`](user-reference-top.png)) shows the original was bright: soft yellow, coral, rose, lilac, periwinkle, mint, teal, navy. The earthy colours below are fading, and the 2012 repaint kept the original layout. The per-ring program is in [`fountain-colour-program.md`](fountain-colour-program.md).

Sources: [refs/pre2011_front_original.jpg](refs/pre2011_front_original.jpg) and [refs/2010_original_faded_profile.jpg](refs/2010_original_faded_profile.jpg).

Earthier colours: cream `#E9DDB4`, ochre `#CFA444`, olive green `#6F8F4A`, teal `#2F7E7F`, brick red `#A8452F`, navy `#26304F`, plus orange.

| Ring | Colours |
|---|---|
| R5 | yellow / teal / orange |
| R4 | brick red / navy / teal |
| R3 | cream → yellow → green → teal gradient, with an orange disc motif |
| R2 | ochre-yellow dominant, with navy / green / red |
| R1 | red / green / yellow |

---

## 5. Reference images

| Image | Shows |
|---|---|
| [Fire and Water Fountain.jpg (2014)](https://commons.wikimedia.org/wiki/File:Fire_and_Water_Fountain.jpg), local [refs/2014_front_vivid.jpg](refs/2014_front_vivid.jpg) | **Best side view.** Telephoto, near level, all 5 rings, 2012 colours, disc motif, water jets. Used for the proportions |
| [Fire and Water Fountain 2011.jpg (shot Feb 2013)](https://commons.wikimedia.org/wiki/File:Fire_and_Water_Fountain_2011.jpg), local [refs/2013_front_vivid_other_side.jpg](refs/2013_front_vivid_other_side.jpg) | other side: pink sector, teal disc, mint cross, cobalt-blue end; close detail of the stripes |
| [PikiWiki 21520](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_21520_Agam_Fountain.JPG) / [21521](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_21521_Agam_Fountain.JPG) (Aug 2012), local [refs/2012_after_repaint.jpg](refs/2012_after_repaint.jpg) | fresh repaint: red split-disc, yellow/orange sector, people for scale |
| [2016.07.06 Tel Aviv … 06715 (night)](https://commons.wikimedia.org/wiki/File:2016.07.06_Tel_Aviv_People_and_Places_06715.jpg), local [refs/2016_night.jpg](refs/2016_night.jpg) | lit at night: R2 yellow/orange, R1 yellow/red, purple disc on R3 |
| [PikiWiki 8440 (2010)](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_8440_water-fire_by_yaacov_agam.jpg), local [refs/2010_original_faded_profile.jpg](refs/2010_original_faded_profile.jpg) | original colours, **ragged zigzag panel edge, top dome**, pool with radial tiles and toothed rim |
| [israelpublicart.com p=957](https://israelpublicart.com/?p=957) ([img 1](https://israelpublicart.com/wp-content/uploads/sites/8/2022/04/fire_and_water_fountain.jpg)), local [refs/pre2011_front_original.jpg](refs/pre2011_front_original.jpg) | original colours, **close front view of the teeth**, pool rim teeth |
| [Fire and Water without panels.jpg (2018)](https://commons.wikimedia.org/wiki/File:Fire_and_Water_without_panels.jpg) | bare drums right after reinstall, empty pool, stem |
| [Dizengoff Square Fountain, 2022.jpg](https://commons.wikimedia.org/wiki/File:Dizengoff_Square_Fountain,_2022.jpg), local [refs/2022_bare_core_no_panels.jpg](refs/2022_bare_core_no_panels.jpg) | **bare core cylinders**: the cleanest view of the 5-drum silhouette, water curtain and dome |
| [Tel Aviv 120326 Dizengoff 03.jpg (Mar 2026)](https://commons.wikimedia.org/wiki/File:Tel_Aviv_120326_Dizengoff_03.jpg), local [refs/2026_current_bare.jpg](refs/2026_current_bare.jpg) | current state, from slightly above: R3/R4/R5 tops, dome |
| [Dizengoff Square Fountain.jpg (2019)](https://commons.wikimedia.org/wiki/File:Dizengoff_Square_Fountain.jpg) | bare, new square |
| [Agam sizi.jpg](https://commons.wikimedia.org/wiki/File:Agam_sizi.jpg) | pre-2011, original colours with water show |

**No true top-down view was found.** Ring tops are flat steel annuli. The top view in §3.3 is constructed from the side views [G].

---

## 6. For the modeller

All values are **normalised to sculpture height H = 1.0** (stem bottom to dome top, pool excluded). They are photo estimates [P], except that the main ring is sourced as 6 m. Z is measured from the stem bottom. All parts are coaxial.

| # | Part | Z bottom | Height | Outer dia (tooth tips) | Core dia (no teeth) | Teeth |
|---|---|---|---|---|---|---|
| 1 | Stem / plinth | 0.000 | 0.046 | 0.38 | 0.38 | none |
| 2 | R1 bottom ring | 0.046 | 0.138 | 0.55 | 0.50 | 40 |
| 3 | R2 | 0.184 | 0.169 | 1.04 | 0.99 | 75 |
| 4 | R3 main ring | 0.353 | 0.292 | **1.54** | 1.49 | 112 |
| 5 | R4 | 0.645 | 0.154 | 1.04 | 0.99 | 75 |
| 6 | R5 top ring | 0.799 | 0.123 | 0.55 | 0.50 | 40 |
| 7 | Dome (half-ellipsoid) | 0.922 | 0.078 | 0.31 | n/a | none |
| 8 | (optional) Pool: shallow disc + rim | below 0 | rim ≈ 0.12 above water | ≈ 3.1 | n/a | old rim had small zigzag teeth |

Notes:
- **Tooth profile:** symmetric V / triangle, pitch ≈ 0.043 H (0.028 × the main diameter, the same on all rings), depth ≈ 0.025 H. Teeth are vertical prisms running the full ring height. Ring tops and bottoms are flat.
- **Scale:** a 20 cm-wide print makes H ≈ 13 cm, pitch ≈ 5.6 mm and depth ≈ 3 mm. Printable, and good for brush painting stripe by stripe.
- **Real scale:** H ≈ 3.9 m and main dia 6 m.
- **Overhang:** R3 overhangs R2 by about 0.25 H all round. Flat underside, so it needs support or a split print: print R3 and R4–R5 upside down, or as separate stackable rings. Stackable rings would also let the kids paint each ring separately.
- **Tolerance:** the proportions are within about ±10%. The symmetry (R1 = R5, R2 = R4) is a strong visual feature, so keep it.

---

## 7. For the painter

Base: white print, so **white faces can stay unpainted**. Paint **face A and face B** of each tooth separately: alternate teeth faces, as in §2.4. For young kids, a simplified version per ring is given below, with the full version in §4.2. Hex values are in §4.3.

| Part | Simple kid version (pick one A colour per tooth, B = white) | Faithful version |
|---|---|---|
| Stem, ring tops and bottoms | silver / grey | steel grey `#9A9C9E` |
| R1 bottom | red, green, white repeating | red / green / grey / white stripes; one side yellow + red |
| R2 | rainbow sweep around the ring: red → orange → yellow, then navy → blue | crimson / navy / white stripes → solid cobalt sector; other side orange / yellow + blue |
| R3 main | white ring with a rainbow sweep all the way round: yellow → orange → red → pink → turquoise → blue → (back to) yellow. **Add one big circle** (dark red) across about 8 teeth and **one "+"** in mint | five sectors as in §4.2: yellow / orange + red disc; pink / crimson + teal disc with bar; orange / turquoise / red + mint cross; red / sky-blue; solid cobalt and solid orange ends |
| R4 | crimson → lilac → turquoise → mint around the ring, alternating with white | same, with sky-blue accents |
| R5 top | sky blue half, orange half, alternating with white | sky / pale blue / white on one side; orange / peach / white on the other |
| Dome | leave clear or white; a little orange flame on top | n/a |

**Rule of thumb:** neighbouring rings use contrasting dominant hues. R3 is light and spectrum, R2 dark red / blue, R4 light red / turquoise. The colour changes gradually around each ring, never randomly. That is what makes it read as Agam.

---

## Sources

- Hebrew Wikipedia, [מזרקת אש ומים](https://he.wikipedia.org/wiki/מזרקת_אש_ומים): 5 wheels, 900 / 600 dimensions, 6 t, Ormat, 3 rotating wheels, gas flame, renovation dates
- English Wikipedia, [Fire and Water Fountain](https://en.wikipedia.org/wiki/Fire_and_Water_Fountain) and [Dizengoff Square](https://en.wikipedia.org/wiki/Dizengoff_Square)
- [Israel Public Art, Fire and Water Fountain](https://israelpublicart.com/?p=957): sheet metal; five concentric rings
- [ynetnews, Jun 2026: "Two Israeli giants are gone…"](https://www.ynetnews.com/real-estate/article/byer11ttgfe): current state, dispute over shades, 2011 changes
- [ynetnews: "From Dizengoff Square to Paris…"](https://www.ynetnews.com/real-estate/article/s19jcdszfx)
- [Algemeiner, Jul 2012: relaunch](https://www.algemeiner.com/2012/07/23/the-relaunch-agam%E2%80%99s-fire-and-water-fountain/)
- [Times of Israel: fountain to be moved](https://www.timesofisrael.com/iconic-agam-fountain-to-be-moved-from-dizengoff-square/)
- [Eldad Spivak engineering](https://www.spivak.co.il/en/projects/the-dizengoff-square-fountain/): water, gas and sound systems
- Wikimedia Commons photos listed in §5
