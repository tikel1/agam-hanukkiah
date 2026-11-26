# Agam's colour schemes, and a palette and colour program for the hanukkiah

> **Superseded (user scope change).** The colours now copy the real fountain: see [`fountain-colour-program.md`](fountain-colour-program.md). This file is background only. Do not encode §5.

User constraints:
- **No black anywhere and no outlines.**
- White PETG, painted by kids with about 10-12 acrylic colours.
- Ring tops stay white.

Companion files:
- [`agam_program_preview.py`](agam_program_preview.py) prints and draws the program below using the model's own face-numbering and tooth-count rules.
- [`agam_program_preview.svg`](agam_program_preview.svg) is the unrolled preview it draws.
- [`fountain.md`](fountain.md) covers the fountain itself.

Tags used throughout:
- **[S]** sourced
- **[P]** observed in photos
- **[G]** my interpretation

Photo hex values are approximate. Daylight, shade and JPEG all shift colour, so §5 gives *normalised* paint targets.

---

## 1. Works surveyed

| Work | What it shows about colour | References |
|---|---|---|
| **Fire and Water, Dizengoff, 1986 original** | Earthy, mid-saturation set: cream, ochre, olive, teal, brick, navy. Each ring has its own dominant hue. Colour runs are gradual sweeps around the ring [P] | [`refs/pre2011_front_original.jpg`](refs/pre2011_front_original.jpg), [PikiWiki 8440](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_8440_water-fire_by_yaacov_agam.jpg) |
| **Fire and Water, 2012 repaint** | Full-chroma set: yellow, orange, red, pink, crimson, sky, cobalt, turquoise, mint, lilac. **One face of each pleat coloured, the other white.** Big flat motifs (disc, disc + bar, "+") laid over the stripes. Adjacent rings contrast (light R3 between darker R2 and R4) [P] | [`refs/2014_front_vivid.jpg`](refs/2014_front_vivid.jpg), [`refs/2013_front_vivid_other_side.jpg`](refs/2013_front_vivid_other_side.jpg), [Commons](https://commons.wikimedia.org/wiki/File:Fire_and_Water_Fountain.jpg) |
| **Fontaine Agam, La Défense, Paris (1975-77)** | "86 shades" of Venetian enamel glass mosaic [S]. The basin wall is vertical stripe modules, **each colour stripe paired with a white stripe** [P]. The hue walks the whole spectrum along the wall: blue-violet → teal → green → yellow-green → yellow → orange → red → magenta → purple [P]. A second, offset row runs a shifted version of the same gradient [P] | [Fontainemonumentale (Commons)](https://commons.wikimedia.org/wiki/File:Fontainemonumentale-YaacovAgam.jpg), [La Défense dsc07200](https://commons.wikimedia.org/wiki/File:La_Defense_dsc07200.jpg), [Paris La Défense page](https://parisladefense.com/en/discover/artwork/fontaine-monumentale) |
| **Dan Tel Aviv Hotel façade (1986, "Rainbow Hotel")** | Façade in "the colours of the rainbow" [S]. Vertical piers step red → orange → yellow, repeated in short runs, and the gradient travels to blue at the far end [P]. Pure hue sits next to pure hue here, with **no white**: the white is the building's window frames [P] | [DanHotelAgam001 (Commons)](https://commons.wikimedia.org/wiki/File:DanHotelAgam001.jpg), [JNS on the museum and hotel](https://www.jns.org/unique-colorful-kinetic-yaacov-agam-museum-in-rishon-letzion/) |
| **Agam Museum, Rishon LeZion (2017)** | White curved halls; "color fades in and out of the white background" [S]. A long wall band of thin stripes, each colour separated by white, walks through the spectrum [P]. Pillars use triangle and checker patterns, many with black [P]. The entrance columns are stacked blocks: yellow, green, navy, yellow, orange [P] | [142293](https://commons.wikimedia.org/wiki/File:142293_rishon_lezion_agam_museum_PikiWiki_Israel.jpg), [142315](https://commons.wikimedia.org/wiki/File:142315_rishon_lezion_agam_museum_PikiWiki_Israel.jpg), [84404](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_84404_agam_museum.jpg), [4168](https://commons.wikimedia.org/wiki/File:Yaacov_Agam_museum4168.jpg), [142275](https://commons.wikimedia.org/wiki/File:142275_rishon_lezion_agam_museum_PikiWiki_Israel.jpg) |
| **Pleated polymorph relief (museum)** | Close-up of a pleated relief. **One face white, the other face a saturated hue** (navy, red, red-orange, teal), with a different hue on every pleat [P]. This is the same scheme as the Dizengoff 2012 repaint | [147021](https://commons.wikimedia.org/wiki/File:147021_yaakov_agam_museum_PikiWiki_Israel.jpg) |
| **Free-standing polymorphs (museum)** | Folded panels: one side carries white discs on stripes, the other side a red / yellow / green / blue / white checker. Two different images, one per face set [P] | [4188](https://commons.wikimedia.org/wiki/File:Yaacov_Agam_museum4188.jpg) |
| **Polymorph wall pieces and prints** | Op-art grids, "rainbow" series (Rainbow Rhythm, Rainbow Visual Prayer). Often a full-spectrum gradient over a dark (navy or black) ground [P] | [4198](https://commons.wikimedia.org/wiki/File:Yaacov_Agam_museum4198.jpg), [Agam discont (Commons)](https://commons.wikimedia.org/wiki/File:Agam_discont.jpg), [Rainbow Rhythm](https://masterworksfineart.com/artists/yaacov-agam/screen-print/yaacov-agam-rainbow-rhythm-c-1994-1996-polymorphic-screenprint/id/w-6037) |
| **Double Metamorphosis II (1964, MoMA)** | Oil on corrugated aluminium, 11 sections [S]. Pompidou's sister piece (Double métamorphose III) is described as "a constellation of colours dotted with black" seen from the front [S] | [MoMA](https://www.moma.org/collection/works/78793), [Pompidou](https://www.centrepompidou.fr/en/ressources/oeuvre/cqGjbEg) |
| **Star of the Knesset (Jerusalem)** | Magen David work: **a single blue field with steel stars**, no rainbow. Left, front and right views exist [P] | [left](https://commons.wikimedia.org/wiki/File:The_Star_of_The_Knesset_(Left_side_view)_by_Yaacov_Agam_(2574457685).jpg), [front](https://commons.wikimedia.org/wiki/File:The_Star_of_The_Knesset_(front_view)_by_Yaacov_Agam_(2575281246).jpg), [right](https://commons.wikimedia.org/wiki/File:The_Star_of_The_Knesset_by_Yaacov_Agam_(right_side_view)_(2574458997).jpg) |
| **Menorahs** | World's Largest Menorah (NYC): gold-coloured steel [S]. "Roots-Menorah" (Tel Aviv) and the 1966 kinetic chanukiah: bare metal [S/P]. **Agam's menorahs carry no rainbow**. The colour comes from his kinetic paintings, not his Judaica | [Worlds Largest Menorah](https://commons.wikimedia.org/wiki/File:Worlds_Largest_Menorah.jpg), [Roots-Menorah](https://commons.wikimedia.org/wiki/File:PikiWiki_Israel_19307_quot;Roots-Menorahquot;_by_Yaacov_AgamTel_Aviv.JPG), [1stdibs 1966 chanukiah](https://www.1stdibs.com/art/sculptures/yaacov-agam-levels-chanukiah-kinetic-menorah-c-1966-silver-plated-brass-yaacov-agam/id-a_13964772) |
| **Communication X9, Peace monuments** | Communication X9 changes colour "as viewers walk around the tower, similar to a lenticular painting" [S]. No colour list found. No usable photo found of a "Peace Monument" | [Pikes Peak Bulletin](https://pikespeakbulletin.org/news/green-box-festival-lifts-the-lid-on-installations/) |

What Agam said about colour:
- He studied with Johannes Itten, the Bauhaus colour-wheel teacher [S, [en-wiki](https://en.wikipedia.org/wiki/Yaacov_Agam); dealer pages].
- Asked why he uses the rainbow, he tells the story of Noah. He calls the rainbow "the unity of difference" [S, [Taipei Times 2010](https://www.taipeitimes.com/News/feat/archives/2010/05/27/2003473960)].

---

## 2. Recurring palettes

| Palette | Hues | Saturation / value | White | Where |
|---|---|---|---|---|
| **A. Full spectrum (signature)** | 9-12 steps round the wheel: yellow, yellow-orange, orange, red, magenta / pink, violet, ultramarine, sky / cyan, turquoise, green, yellow-green | High chroma (S 0.8-1.0); values follow the hue's natural lightness: yellow light, violet and ultramarine darkest | Usually a **white separator** stripe or face between colours | La Défense, 2012 Dizengoff, museum band, pleated reliefs |
| **B. Earth-modern (1970s-80s)** | cream, ochre, olive, teal, brick red, navy, orange | Medium chroma (S 0.4-0.7) | Cream instead of white | Dizengoff 1986 original |
| **C. Op-art graphic** | black + white with spectrum accents | Maximum value contrast | White as ground | Prints, museum pillars, Double métamorphose. **Excluded here (black)** |
| **D. Monochrome Judaica** | one blue (or gold / steel) | n/a | n/a | Star of the Knesset, menorahs |

Approximate normalised hex for palette A, from the 2012 Dizengoff and La Défense photos [P]:

| Colour | Hex |
|---|---|
| yellow | `#FFD200` |
| yellow-orange | `#FFA000` |
| orange | `#FF6A13` |
| red | `#E1251B` |
| magenta-pink | `#E6338A` |
| violet | `#6E3FA3` |
| ultramarine / cobalt | `#1F4FB4` |
| sky | `#2FA3E6` |
| turquoise | `#00A79D` |
| green | `#22A04B` |
| yellow-green | `#9BCB3C` |
| white | `#F7F5EE` |

**White as separator vs pure next to pure:**
- In **pleats and polymorphs, Agam separates with white**: one face coloured, the other white. Examples are Dizengoff 2012, the museum relief and La Défense's paired stripes. [P]
- Pure hue next to pure hue happens on **flat façades** (the Dan Hotel) and in prints over a dark ground. [P]

---

## 3. Sequencing rules [P → G]

1. **Wheel order, never random.** Hues follow the colour wheel (Itten order). A run moves one step at a time. A sequence closes on itself, so violet or lime returns to yellow, and every sequence on a ring has no seam.
2. **Gradient length.** A run uses 9-12 hues. On a closed ring there is **one full sweep per ring** (Dizengoff R3, La Défense wall). On long façades Agam uses short repeated runs of 3-4 hues (the Dan Hotel's red-orange-yellow).
3. **Stripe width.**
   - Within one work the stripe module is fixed: one pleat face, one enamel strip.
   - A colour "band" is widened by repeating a hue over several modules. Bands of about 30-40° each on the Dizengoff rings.
   - Bands are narrower on smaller elements, so every ring still shows the whole spectrum.
4. **Left vs right faces (polymorph).** Three relations recur:
   - (a) **colour / white**: Dizengoff 2012, museum relief;
   - (b) **two different images**: stripes vs checker, discs vs stripes;
   - (c) **complementary or reversed gradient**: La Défense's second row is a shifted gradient. Head-on, the interleaving makes hues vibrate. That is the op-art effect.
5. **Complementary pairs.** Itten's pairs: yellow–violet, yellow-orange–blue-violet, orange–blue, red–green, magenta–yellow-green, turquoise–red-orange. Agam puts them side by side for vibration.
6. **Stacked elements.**
   - Each element gets its own dominant hue or its own phase of the sweep, so neighbours contrast. Dizengoff has a light R3 between darker R2 and R4. The entrance columns stack contrasting blocks.
   - The fountain is symmetric (R1 = R5, R2 = R4), and its colour treatment echoes that.
7. **Motifs over stripes.** A big flat disc, a disc with a bar, or a "+" is painted straight across many pleats in one solid hue. It contrasts in *value* with the stripes underneath. Agam does not outline these.

---

## 4. What fits a white PETG piece painted by kids

- **Use:**
  - palette A (spectrum, high chroma);
  - the **colour / white** face relation. Half of some rings need no paint, and white primer is the separator;
  - one sweep per ring with band width ∝ ring size;
  - complementary left / right on the two middle rings for the op-art vibration;
  - ring-to-ring phase shift;
  - motifs in one solid hue chosen for value contrast. That replaces outlines.
- **Drop:**
  - black-and-white op-art runs and black grounds (user rule). Cobalt and violet are the darkest hues.
  - navy: it reads as near-black on a small piece.
  - 86-shade gradients: 11 hues + white is enough.
  - pure-on-pure without white on every ring: too much painting and too busy at 7 mm stripes.
- **Seam rule for the model:** a ring's sequence closes only if `run x len(colours)` divides the tooth count.
  - R2 55, R3 81 and R4 50 work: 55 = 11×5, 81 = 9×9, 50 = 10×5.
  - R1 and R5 have 29 teeth (ratio 0.36). That is prime, so every sweep jumps **at the front**.
  - **Recommend ratio 0.372 → 30 teeth** (= 10×3). That is +2 mm on the diameter, within the fountain tolerance in fountain.md §2.3.

---

## 5. Recommendation

### 5.1 Final palette: 11 hues + white (no black, no navy)

Nearest paint names come from the makers' standard ranges. **Check against a real swatch before buying.** Posca PC-5M names, Amsterdam Standard Series acrylic numbers.

| # | Name (config) | Hex | Posca (nearest) | Amsterdam Standard (nearest) |
|---|---|---|---|---|
| 1 | yellow | `#FFD200` | Yellow | 275 Primary yellow |
| 2 | marigold | `#FFA000` | Sunshine Yellow | 270 Azo yellow deep |
| 3 | orange | `#FF6A13` | Orange | 276 Azo orange |
| 4 | red | `#E1251B` | Red | 315 Pyrrole red |
| 5 | pink | `#E6338A` | Pink (or Fuchsia, deeper) | 369 Primary magenta |
| 6 | violet | `#6E3FA3` | Violet | 568 Permanent blue violet |
| 7 | cobalt | `#1F4FB4` | Blue | 504 Ultramarine (or 512 Cobalt blue ultramarine) |
| 8 | sky | `#2FA3E6` | Light Blue | 572 Primary cyan (+ white) |
| 9 | turquoise | `#00A79D` | Emerald Green / turquoise | 661 Turquoise green |
| 10 | green | `#22A04B` | Green | 618 Permanent green light |
| 11 | lime | `#9BCB3C` | Light Green | 617 Yellowish green |
| 12 | white | `#F7F5EE` | White | 105 Titanium white (or leave white primer) |

Wheel order is the list order 1 → 11, then back to 1.

Complements, for the "complement" programs:

| Colour | Complement |
|---|---|
| yellow | violet |
| violet | yellow |
| marigold | cobalt |
| cobalt | marigold |
| orange | sky |
| sky | orange |
| red | green |
| green | red |
| pink | lime |
| lime | pink |
| turquoise | red |

### 5.2 Colour program per part

Face k = 0 sits at the front (concept 0°). k counts counter-clockwise, which is left to right for someone facing the ring.

| Part | Teeth | LEFT faces | RIGHT faces | Front colours (L / R) | Polymorph idea |
|---|---|---|---|---|---|
| **R5** (top) | 30* | 10-hue wheel (no marigold), run 3, one sweep | white | orange / white | colour from the left |
| **R4** | 50 | complements of the right | 10-hue wheel, run 5, one sweep | green / red | complementary vibration |
| **R3** (main) | 81 | white | 9-hue wheel (yellow, marigold, orange, red, pink, violet, cobalt, turquoise, lime), run 9, one sweep, **yellow centred on the front** | white / yellow | colour from the right, as on Dizengoff 2012 |
| **R2** | 55 | complements of the right | 11-hue wheel, run 5, one sweep, **cobalt centred on the front** | marigold / cobalt | complementary vibration |
| **R1** (bottom) | 30* | 10-hue wheel, run 3, one sweep | white | turquoise / white | colour from the left (mirrors R5) |
| **Stem** | 16 sectors | n/a | n/a | n/a | spectrum with white separators (La Défense): red, white, orange, white, yellow, white, green, white, turquoise, white, sky, white, cobalt, white, violet, white |
| **Ring tops** (all steps) | n/a | n/a | n/a | n/a | white: no bands, no circles. Washer seats stay bare |
| **Dome** | n/a | n/a | n/a | n/a | white (crown bare) |
| **Plinth disc** | n/a | n/a | n/a | n/a | cobalt (the pool) |

\* 30 teeth needs ratio 0.372. At 0.36 (29 teeth) R1/R5 still work, but their sweep jumps at the front.

Walking round the piece:
- **From the right:** R3 and the two middle rings blaze; R1 and R5 go white.
- **From the left:** R3 goes white with only its emblems showing; R1 and R5 light up.
- **Head-on:** you see every ring as interleaved stripes.

The stack alternates colour and white as Agam's polymorphs do. The light R3 front sits between a dark cobalt R2 and a red R4. That is the "light main ring between darker neighbours" of the 2012 fountain.

### 5.3 Emblems on R3: no outlines, no black

The emblems stand out by value contrast against the stripes underneath. The simulation in `agam_program_preview.py` lists the colours under each one.

| Emblem | Angle | Under it: left faces / right faces | Colour |
|---|---|---|---|
| **HANUKKAH** letters | 0° (±44°) | white / lime, yellow, marigold | **cobalt**: strong on both faces |
| Magen David | 90° | white / orange, red | **cobalt**: Agam's Knesset star is blue |
| Disc + bar | 180° | white / pink, violet | disc **orange**, bar **cobalt** |
| "+" | 225° | white / cobalt, violet | **pink** |
| Dreidel + ג | 270° | white / turquoise | body **orange**, ג **white** (leave unpainted) |

**Outline ridges:** paint each raised outline ridge **in its own zone's fill colour**, so it disappears. Better still, set the ridge height equal to the fill height. Then the ridge is still a paint dam but no longer a visible line.

### 5.4 Config-ready block for `model/config.py`

This uses the existing `Paint`, `Stripes` and `RingPaint` dataclasses unchanged. Two small model changes go with it:
1. R1/R5 ratio 0.372.
2. Outline paint = the zone's fill (`EMBLEM_OUTLINE_PAINT = None` meaning "same as the fill", or drop the outline zones).

```python
PAINTS = (
    Paint(1, "yellow", "#FFD200"),   Paint(2, "marigold", "#FFA000"), Paint(3, "orange", "#FF6A13"),
    Paint(4, "red", "#E1251B"),      Paint(5, "pink", "#E6338A"),     Paint(6, "violet", "#6E3FA3"),
    Paint(7, "cobalt", "#1F4FB4"),   Paint(8, "sky", "#2FA3E6"),      Paint(9, "turquoise", "#00A79D"),
    Paint(10, "green", "#22A04B"),   Paint(11, "lime", "#9BCB3C"),    Paint(12, "white", "#F7F5EE"),
    Paint(0, "bare", "#DADBD6"),
)
WHEEL_11 = ("yellow", "marigold", "orange", "red", "pink", "violet", "cobalt", "sky", "turquoise", "green", "lime")
WHEEL_10 = ("yellow", "orange", "red", "pink", "violet", "cobalt", "sky", "turquoise", "green", "lime")
WHEEL_9_R3 = ("yellow", "marigold", "orange", "red", "pink", "violet", "cobalt", "turquoise", "lime")
WHITE = ("white",)
COMPLEMENT = {
    "yellow": "violet", "violet": "yellow", "marigold": "cobalt", "cobalt": "marigold",
    "orange": "sky", "sky": "orange", "red": "green", "green": "red",
    "pink": "lime", "lime": "pink", "turquoise": "red", "white": "white",
}
# DRUMS: Drum("drum1_R1", 0.372, 0.138) and Drum("drum5_R5_dome", 0.372, 0.123) -> 30 teeth each
RING_PAINT = {
    "drum1_R1": RingPaint(left=Stripes(WHEEL_10, run=3, offset=22), right=Stripes(WHITE)),
    "drum2_R2": RingPaint(left=Stripes(WHEEL_11, run=5, offset=32, complement=True),
                          right=Stripes(WHEEL_11, run=5, offset=32)),
    "drum3_R3": RingPaint(left=Stripes(WHITE), right=Stripes(WHEEL_9_R3, run=9, offset=4)),
    "drum4_R4": RingPaint(left=Stripes(WHEEL_10, run=5, offset=12, complement=True),
                          right=Stripes(WHEEL_10, run=5, offset=12)),
    "drum5_R5_dome": RingPaint(left=Stripes(WHEEL_10, run=3, offset=4), right=Stripes(WHITE)),
}  # top_ring_radii=() everywhere: ring tops stay white
DOME_PAINT = "white"
PLINTH_PAINT = "cobalt"
STEM_SECTORS = 16
STEM_COLOURS = ("red", "white", "orange", "white", "yellow", "white", "green", "white",
                "turquoise", "white", "sky", "white", "cobalt", "white", "violet", "white")
EMBLEM_PAINT = {
    "word": ("cobalt",), "star": ("cobalt",), "disc": ("orange", "cobalt"),
    "cross": ("pink",), "dreidel": ("orange", "white"), "extra_disc": ("orange",),
}
EMBLEM_OUTLINE_PAINT = None  # NEW meaning: paint each outline ridge in its zone's fill colour (no outlines)
```

Notes:
- **Offsets:** the offsets centre a colour band on the front: R3 yellow, R2 cobalt, R4 red, R1 turquoise, R5 orange. Every ring closes without a seam. Checked with `python agam_program_preview.py`.
- **Paint load (counted by the script):**
  - 492 pleat faces in all; 141 stay white (29%).
  - Every other colour covers 24-35 faces, except red at 45 (it is also the complement of green and turquoise).
  - That is even enough for 12 small pots or Posca pens.

---

## Sources

- Fountain research and photos: [`fountain.md`](fountain.md) and [`refs/`](refs/)
- Paris La Défense: [Monumental fountain](https://parisladefense.com/en/discover/artwork/fontaine-monumentale); [La Défense art guide PDF](https://en.suresnes-tourisme.com:443/Local/suresnes/files/883/defacto_ang_guide_oeuvresart_bd.pdf)
- Agam Museum: [JNS](https://www.jns.org/unique-colorful-kinetic-yaacov-agam-museum-in-rishon-letzion/); [Hadassah Magazine](https://hadassahmagazine.org/?p=18601)
- MoMA: [Double Metamorphosis II](https://www.moma.org/collection/works/78793); Centre Pompidou: [Double métamorphose III](https://www.centrepompidou.fr/en/ressources/oeuvre/cqGjbEg)
- Agam on the rainbow: [Taipei Times 2010](https://www.taipeitimes.com/News/feat/archives/2010/05/27/2003473960); [Yaacov Agam, Wikipedia](https://en.wikipedia.org/wiki/Yaacov_Agam)
- Menorahs: [Time Out NYC](https://www.timeout.com/newyork/things-to-do/worlds-largest-menorah-lighting); [1stdibs 1966 kinetic chanukiah](https://www.1stdibs.com/art/sculptures/yaacov-agam-levels-chanukiah-kinetic-menorah-c-1966-silver-plated-brass-yaacov-agam/id-a_13964772)
- Communication X9: [Pikes Peak Bulletin](https://pikespeakbulletin.org/news/green-box-festival-lifts-the-lid-on-installations/)
- Wikimedia Commons photos linked in §1 (CC licences; personal reference use)
