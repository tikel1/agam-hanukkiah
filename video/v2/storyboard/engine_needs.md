# What the engine needs for the v2 storyboard

For the animation session. Checked against `v2/engine/` on 26.11.2026 (README, `src/components/*`, `films/proof`).
N-numbers are the ones `storyboard.md` cites. "Have" = already in the engine; only the gap is listed.
Reference implementation for every item: `storyboard/tools/` (Python + SVG), same maths.

## Must have (the film does not work without them)

| # | Need | Have | Gap / spec | Used in |
|---|---|---|---|---|
| N1 | Glyphs: new **ק**, plus **?** and **!** | `glyphs.js` | Replace `'ק'` with `[56, ['M0,0 H56 L60,100', 'M8,36 L4,128'], [[0,0]]]` (user: the old one reads badly). Add `'?': [40, ['M0,14 L14,0 H40 V44 L20,56 V74'], [[20,100]]]`, `'!': [0, ['M0,0 V72'], [[0,100]]]`, a **ט** `[62, ['M0,0 V100 H62 V0 H34 L28,40'], [[0,0]]]` for the title "אמנות קינטית" (the film says kinetic art, not polymorph), an en dash for `1928–2026`, and Latin **A** `[70, ['M0,100 L35,0 L70,100', 'M15,60 H55'], [[35,0]]]` and **I** `[0, ['M0,0 V100'], [[0,0]]]` for the "AI" title (the script says AI, not בינה מלאכותית). Digits must lay out left to right inside RTL titles. | 4.2, 7.2, 10.5, 9.2 |
| N2 | **Two-value shading** on pleat faces | unlit only | One step: faces whose normal points away from a fixed key direction (−0.55, 0.45, 0.70) get `mix(colour, INK, 0.14)`. No gradients. A uniform `shadeStep` on `PleatedSurface`. | everywhere |
| N3 | **Per-pleat reveal / paint** | `motifAmount` (bottom-up wave) | `reveal(i, t)`: each A face drawn top-down on its own clock (1.1 stripes written right to left, two brushes leading). `paintedColumns(t)`: columns switch white→motif one by one (9.1–9.2, accelerating). | 1.1, 9.1, 9.2 |
| N4 | **Fold wave** | `bend`, fixed depth | `depthRatio` per pleat, so a fold can travel across a flat sheet (2.3); also the curtain (N5). | 2.3, 1.2 |
| N5 | **Stripe frame + curtain for photos** | `PhotoFrame` (white card, colour strip, shadow) | Add a `style: 'stripes'` frame: border 26 px of 13 px stripes, colour/white alternating in spectrum order (white = night colour at night). Add a **curtain**: two pleated sheets clipped to the photo, folded towards the sides, `open` 0..1 (0 = stripes cover the photo, 1 = gone). The photo itself never changes. Night variant. "Taped" variant (two tape strips, slight tilt) for 5.x. | 1.2, 2.1, 3.1, 4.2, 5.x, 10.x |
| N6 | **Per-ring offsets** on Fountain and Hanukkiah | rings fixed | `ringOffsetY[id]` for drops (3.2, 9.3: 9 frames fall + 6 frames settle with 5% overshoot) and the exploded view (8.1). | 3.2, 8.1, 9.3 |
| N14 | **Dreidel in the ring motifs** | `motifs.js` has star, HANUKKAH, sufganiyah | The script names the dreidel. Follow the paint maps (`model/out/maps/map_R3_A_left`): orange dreidel just after the star on the A side. Ring pleat depth 0.71 (70° folds) so each side reads alone beyond 35°. | 7.3 |
| — | **Our hanukkiah as a component** | built inside `films/proof/film.js` | Move it to `components/hanukkiah.js`: foot with the **name plaque** ("חנוכיית אש ומים" in blue line-and-dot letters on the front, as printed), stem, R1–R5, 8 blue candles in gold cups on R3, shamash on R5, `lit` count, `white` / `painted` states. Hero shots use yaw ±30–40°, never 0. | 6–10 |

## Should have (the look)

| # | Need | Spec | Used in |
|---|---|---|---|
| N7 | **Props**: paint marker (as in our photo: black barrel, white band, colour ring and cap, colour nib), pencil, notebook page with line-and-dot spiral | Straight lines, palette only; see `props.marker/pencil/notebook`. Marker tip follows the stroke end. | 1.1, 5.x, 9.2 |
| N8 | **Eye track** under a polymorph | Dotted arc of 15 grey dots, eye dot (navy ring) moving with the camera yaw, dashed sight line. | 2.2, 2.4–2.5, 7.3–7.4 |
| N9 | **Water as line-and-dot jets** | Quadratic stroke from the pool rim, arching in to 70% radius, ending in a dot; split behind/in front of the rings by depth; height pulses per jet. | 3.3, 3.4 |
| N10 | **Flame split** | One flame → 9: eight travel on dotted arcs to the candle seats on a ring (landings staggered 4 frames), one rises to the centre. Also the reverse journey in 10.4. | 4.3, 10.4 |
| N11 | **Light rings** | Concentric rings of logo dots expanding from a flame, staggered 20 frames. | 4.1, 4.2 |
| N12 | **Construction drawing** of a ring | Dashed top/bottom circles, 8 uprights, a dot on each joint; morphs into the solid white ring. | 6.2 |
| N13 | **Phone + timeline** | Navy body, slanted speaker slot, screen clip; timeline as a row of 24 logo dots with a playhead. The screen can show a render target of the film itself (6.4). | 6.1, 6.4 |
| N15 | **Split screen** | Two cameras in one frame (top fan / bottom ring), same yaw track, divider = dot rule. | 7.5 |
| N16 | **Our printer (Bambu Lab A1 style) + layers** | Real 3D in the film's flat look (boxes with the one shade step), not an exact model: grey base with a small screen, dark dotted bed that slides back (bed slinger: the gantry stays, the bed moves), dark arch frame, X gantry rail, light toolhead with a green status dot, a white spool on top with a white tube down to the toolhead. The ring grows in white (`height × progress`) with horizontal layer lines. Reference: `frames_b.a1_printer_3d`, `geom.box`, `geom.spool_3d`. | 8.2 |
| N17 | **Counter dots** | 2 × 20 dots filling in spectrum order as columns get painted. | 9.2 |
| N18 | **Night stars** | Small dots in logo colours mixed 45% into the night, seeded, slow twinkle. | 10.x |

| N19 | **Photo placeholders** for real photos of the girls | Stripe frame, grey hatched field, line-and-dot camera, label + "כאן תיכנס תמונה אמיתית" (`props.photo_placeholder`). Same size and place as the photo that replaces it: 2.1 museum (780x410), 6.2 at the computer (400x300, inside a holo screen), 9.1 painting (740x960). When the photos come, they go in `PhotoFrame` untouched. | 2.1, 6.2, 9.1 |
| N20 | **Claude, the character** | A small friendly block creature in Claude's coral `#D97757` (shade `#B95F42`): box body, two tall dark eyes, two arm nubs, four short legs, built from flat-shaded boxes like everything else (`ai.claude`). Poses: wave (right arm up), point (arm out), wink (one eye a short line), stand. Idle: a 2-frame hop every second, eyes blink. Enters 6.1 climbing out of the phone screen. | 6.x |
| N21 | **Hologram layer** (beat 6 only) | Glow (the one soft effect of the film: blur + add, cyan `#8FD3E8`), dotted hologram floor, glowing construction rings that solidify as the beam passes, a beam from Claude's hand (soft wedge + dotted core), a rising scan ring that leads the colour wave, holo screens with corner ticks, data rain (falling columns of logo dots). Reference: `ai.py`. | 6.x |

| N22 | **Archive clip in a frame** | Two short Kan 11 clips (`footage/kan_fountain_day.mp4` 2.35 s, `kan_fire_on_water.mp4` 2.8 s) play once inside the stripe frame (N5), untouched. For deterministic seeking, extract each to a PNG sequence (25 fps) and pick the frame from `t`; hold the last frame, then the curtain closes. The ▶ mark in the key frames is storyboard-only. | 3.1, 4.1 |

## Subtitles (user note: a design element, not plain captions)

`core/subtitles.js` renders plain text with a halo. Needed (spec in storyboard §2.6, code in `style.subtitle`):

- each line on its own **slat**: white (night `#2E3570`) parallelogram, ends slanted 4°, flat 6 px shadow;
- a **stripe stamp** of 5 thin stripes (colour/white) at the start of the line (right side);
- a **hopping dot** under the word being spoken (logo colours, needs per-word times from the TTS);
- Secular One 60, shrink to 52 for a long line, max width 820 px, two lines, band y 1490–1700;
- in: slat unfolds right to left like a pleat turning (8 frames), text rises 6 px; out: slat folds back into its stamp.

## Notes on the proof

- `PleatedSurface` still has a `photo` input (photo in three inks on the B faces): keep it for our own drawings only. Photos only in frames (N5).
- Video stills are not allowed (user rule); `photos/credits.md` lists only real photos.
- School film, not published (user 26.11): no on-screen photo credits, no rights limits on the photos.
- Agam only as an older man in photos (user): the Kaprov portrait and the photo at the fountain.
- The ending does not repeat his death (user): no years in beat 10, the tribute is "a small gift from us so his fire keeps burning".
- Proof camera keys show the engine can already do every camera move in the board (yaw sweeps, rises, zoom pushes).
