# Film v2: how to animate a beat

For whoever animates a beat of `films/v2` (people and agents). Read this, then your beats in
`../../../storyboard/storyboard.md` (Hebrew: §2 style bible, §3 beats, with timing and "קישור" = the link into the
next beat), the key frames `../../../storyboard/frames/bNN_K.png` (look at every frame of your beats), the spec in
`../../../storyboard/engine_needs.md`, and the Python reference of every shape in `../../../storyboard/tools/`
(`props.py`, `ai.py`, `frames_a.py`, `frames_b.py`, `geom.py`: same maths, port what you need).

## Rules that bind (from the user)

- One continuous take: no cuts. Every beat grows out of a shape already on screen ("turn" and "rise").
- Motion must look advanced and polished, never cheap: fast and exact, ease-in-out cubic/quart for big moves, a small
  overshoot (spring, 4-6%) on arrivals, moves overlap by 6-10 frames, anticipation before a big move, follow-through,
  secondary motion; nothing stands still for more than 1.5 s. NO rubbery stretch-in of big shapes and no decorative
  shape without a job (the user called both "cheap").
- Flat 2D look in real 3D: orthographic camera, no lights, flat colours, ONE step of shade (already in the components),
  soft flat shadows allowed (`shadows.js`). No gradients, no glow (glow only in beat 6), no black, no outlines.
- Photos and the two archive clips are shown UNTOUCHED (crop only) in a `StripeFrame`. Never filter, tint, cut up or
  fade a photo's colours. No video stills. Agam only as an older man (the photos in `assets/photos/` are all fine).
- No on-screen credits. No recycling symbol.
- The word "polymorph" (פולימורף) appears nowhere in the film (user, 26.11): it is "kinetic art" (אמנות קינטית).
- Frame 1080x1920. Safe zones (pixels from the top): 0-200 nothing important; titles 250-640; subject 560-1470;
  subtitles 1490-1700 (the engine draws them, keep that band calm: no small detail or text there); 1720-1920 only ground.
  72 px side margins for text.
- Titles: line-and-dot letters (`LineDotTitle`), ink `INK` by day and `PAPER` at night, in the upper third.
- Palette only from `src/palette.js` (`FOUNTAIN`, `SPECTRUM`, `DOTS` for dots only, `FLAME`, `GOLD`, `GROUND`, `CLAUDE`,
  `HOLO`, `PRINT_WHITE`). The ground colour of the whole film is set by `timeline.ground`: do not paint your own
  full-screen background unless your beat needs to cover the one before it.

## Files

- Yours: `films/v2/beats/bNN.js` (replace the placeholder) and new files under `films/v2/parts/` (prefix them with your
  beat, e.g. `parts/b06_claude.js`). Files of a beat stay under 400 lines: split into parts.
- Read-only for you: everything in `src/`, `films/v2/film.js`, `timeline.js`, `handoff.js`, `render.py`, other beats.
  If a shared file lacks something, build it in your own part and say so in your report. Do not edit them: other
  agents work on the other beats at the same time, in this same folder.
- Code style: ES modules, pure functions of time, named constants on top (no magic numbers inline), functions under
  50 lines, comments say why. Errors must throw with a clear message (no silent catch).

## The contract of a beat

```js
import { THREE } from '../../../src/core/stage.js';
export async function create(ctx) {           // ctx = { stage, timeline, beats, handoff, ground(t) }
  const beat = ctx.beats.b03;                 // { start, end, at(offset), local(t), progress(t) }
  const scene = new THREE.Scene();
  ...build everything once...
  function update(t) {                        // EVERYTHING from t alone: no state between calls, no Math.random,
    ctx.stage.setRig({ yaw, pitch, zoom, x, y, z, roll, shiftX, shiftY });   // no Date. First thing: the camera.
    ...
  }
  return { from: beat.start, to: beat.end, scene, update };   // or an array of such passes
}
```

- A pass is drawn only while `from <= t < to`. Passes are drawn in beat order, each over the one before, each with its
  own camera. So two beats may overlap in time: the later one is on top. Use this for links (the new beat's things
  slide / rise / grow in over the old beat while the old one moves out).
- A pass may also have `rect(t)` -> `[x, y, w, h]` (the whole picture drawn scaled into that rectangle), `clip(t)`
  (cut only) and `background(t)` (a colour that fills the rect first). A beat may return several passes (e.g. a
  split screen: two passes with two clips; a film inside a phone: an inner pass with a rect).
- `update(t)` is called several times per frame with slightly different t (motion blur). Motion blur and
  anti-aliasing are automatic.
- Camera: `stage.setRig` (degrees; zoom 1 = one world unit per pixel; x, y, z = the world point at the frame centre).
  Orthographic only. Pitch up to 10 for ring stacks (22 only when looking down on the candle circle). Yaw is the main tool.
- Screen-pinned things (titles, frames, HUD): `stage.place(group, px, py, { scale, depth, roll })` after `setRig`:
  px, py are frame pixels from the top left. `depth` orders them (bigger = nearer the camera; world things sit
  around 0; use 1500+ for overlays, less than -1500 for things behind the world).
- World things that must face the camera (flames): `stage.billboard(group)`.
- A hard hand-off between beats built by different people happens at a REST POSE from `handoff.js` (see below).

## Engine (read the files, they are short)

`src/core/motion.js`: `tween(t, start, dur, ease)`, `spring(x, freq, damping)`, `wobble`, `track(keys)`, `prog`, `lerp`,
`clamp`, `ease.*`, `bump`, `drift(t, seed, freq)`, `rand(seed)`, `bezier2`, `softStart`.

Components in `src/components/`:
- `pleated.js`: `PleatedSurface({ pleats, colorA, colorB, colorA2, colorB2, capColor })`: A faces show from the left
  (negative yaw), B faces from the right. `update({ length, height, bend 0..1, depth(i), top(i), bottom(i) })`:
  per-pleat top/bottom = stripes that draw themselves (N3), per-pleat depth = a fold wave (N4), bend 1 = closed ring.
  Uniforms: `colorMix` (blend to colorA2/B2), `motifAmount` (painted picture rising from below), `paintU` (painted
  only up to this fraction along the sheet), `motifShift`, `shadeStep` (set 0.14), `opacity` + `fadeTo`.
  `setMotifs({ left, right })` = pictures on the A / B faces. `ToothedRing`.
- `hanukkiah.js`: `new Hanukkiah(stage)`: OUR hanukkiah (foot with name plaque, 5 rings with the hidden pictures and
  the dreidel, 8 candles + shamash). `update(t, { painted, paintU, offsetY, show, spin, candles, lit, flameScale })`,
  `wick(k)`. Constants `HANUKKIAH`, `HANUKKIAH_RINGS`. Hero shots from yaw +-30..40 (never 0, the pictures mix);
  left (negative yaw) = Magen David + dreidel, right = HANUKKAH + sufganiyah. The pictures need about +-62 to sit centred.
- `fountain86.js`: `new Fountain86({ silhouette })`: the 1986 fountain (5 rings on a column, pool).
  `update(t, { spin, drop, show, pool, column })`. Constants `FOUNTAIN86`, `FOUNTAIN86_RINGS`, `fountain86Colors(k)`.
- `stripeFrame.js`: `StripeFrame({ picture, width, height, focus, style, night, curtain, tape })`, `setCurtain(0..1)`,
  `setClipTime(s)`, `loadPicture(url)`, `loadClip(CLIPS.fountainDay.url, CLIPS.fountainDay)` / `CLIPS.fireOnWater`,
  `createPlaceholder(w, h, label, { dark })` (for the three photos of the girls that are still to come).
- `lineDotTitle.js`: `new LineDotTitle({ words: ['אש', 'ומים'], cap, ink, rtl, ends })`, `update(tSinceStart, { span,
  out, outSpan })`, `.width`. Hebrew words rtl; digits and Latin ("408", "1928–2026", "AI", "1986"): `rtl: false`
  as a separate title. Glyphs exist for every title in the storyboard, incl. ק ? ! A I – 0 1 2 4 6 8 9.
- `flame.js`: `new Flame({ seed })`, `update(t, { height, width, lean, squash, energy })` (billboard it).
- `flatShade.js`: `flatMaterial(color, { shade, opacity })`, `box(w, h, d, color)`, `drum(radius, height, side, top)`:
  solid shapes in the film's look (printer, Claude, props).
- `shadows.js`: `discShadow`, `cardShadow` (soft), `WallShadow` (hard).
- `fountain.js`, `motifs.js`, `photoFrame.js`: v1 proof parts. Do not use them in v2.
- Small text (sub lines such as "הגדולה בעולם", the end card names): draw on a canvas with `"Secular One"`
  (`await document.fonts.load('48px "Secular One"')` first), make a `THREE.CanvasTexture` with
  `colorSpace = THREE.NoColorSpace`, put it on a plane and `stage.place` it. Numbers left to right.
- Subtitles are drawn by the engine from `timeline.js` (slats with a hopping dot). Not your job; just keep the band calm.
- Photos: `assets/photos/` (`agam_portrait.jpg` 720x1086, `agam_portrait_face.jpg`, `agam_tribute.jpg` 735x1300,
  `fountain_2010.jpg`, `menorah_nyc.jpg` 620x1170, `work_circles.jpg`, `work_polymorph.jpg`, `work_wall.jpg`,
  `map_R3_A_band.png`, `map_R3_B_band.png` = our real colouring maps).

## Hand-offs (`handoff.js`)

- 23.0 `T23`: beat 2 ends with its sheet closed into fountain ring 2, resting low; beat 3 starts with `Fountain86`
  showing only that ring (`drop: { 2: T23.drop }`, `show` 0 for the others, `pool: 0`, `column: 0`) and the same rig.
  Both at rest at 23.0 (no speed), so the switch cannot be seen.
- 55.0-56.0: beat 5's notebook page rises over beat 4 (plain overlap, beat 5 on top; beat 4's pass must last to 56.0).
- 75.0-79.2 `PHONE`, `phoneRect(t)`, `b07Pass(t)`: beat 6 draws the phone around `phoneRect(t)` and its own world
  inside it (an inner pass with `rect: phoneRect`); beat 7's pass starts at `B07_FROM` and uses `b07Pass(t)` for
  rect / clip / background, so it first plays inside the phone and then IS the frame. Beat 6 lasts to 79.2.
- 97.0 `T97`: beat 7 ends and beat 8 starts with the painted hanukkiah in that pose and rig, at rest.
- 112.0 `T112`: beat 9 ends and beat 10 starts with the stacked painted hanukkiah in that pose and rig, at rest.

## Working loop

Python: `../../animation/.venv/Scripts/python.exe` (call it `PY`), run from the `engine/` folder.

```
PY render.py --film v2 --only b03,b04 --stills 23.5,25,27 --out _stills/b03 --samples 4
PY contact.py _stills/b03 _stills/b03.png 6
```

Then LOOK at the picture (Read tool) and compare with the key frame. `--only` builds just your beats (fast). Write
your stills only under `_stills/<your beat>/`. Render stills densely where things move (every 0.2-0.3 s through a
transition) to judge the motion: you cannot watch video, so check arcs, overlaps and that nothing pops. A player
error shows as a failed render: read the message. Check the first and last instant of every pass and both sides of
every hand-off. When done, report: what each beat shows second by second, what differs from the storyboard and why,
which shared-file gaps you worked around, and the stills you checked.

## Light and shadow (user note, second review)

The user wants more play of light and shadow in EVERY beat, while the look stays minimalist and flat: a sense of depth,
not realism. The engine now does part of it by itself wherever `shadeStep` is set: a soft step of shade on faces turned
from the key light (it shifts as things or the camera turn), darker valleys and a thin rim of light on the ridges of
every fold (`lightPlay` uniform, 0..1), a soft terminator on `flatShade` solids, cast shadows under the hanukkiah, its
candles and the fountain's rings. The key light comes from the upper left front: (-0.55, 0.45, 0.70). So shadows on a
level surface fall to the RIGHT and BACK; on a wall behind an object they fall to the right and down.
What each beat still has to add itself, with `shadows.js` (`cardShadow`, `discShadow` soft; `WallShadow` hard) or its
own flat shapes in one ink at 10-25%:
- cast shadows of its objects on the ground / page / table they stand on, long and soft, falling the same way
  everywhere; a shadow grows and moves away as its object lifts and tightens as it lands;
- shadows that MOVE: when a sheet, card or ring turns or the camera walks round it, its shadow changes shape with it;
- contact shade where planes meet (a card on a page, a ring on a ring, a foot on a table);
- a light sweep across a surface as it folds or turns (a band of lighter tint travelling over the pleats) where a
  big fold or turn happens;
- nothing glossy, no blur glow (glow stays in beat 6), no gradients on photos (photos stay untouched; their FRAME
  may cast a shadow). Night beats: shadows are a darker night, light is warm near flames.
Compare a still before and after for each of your beats and say what changed.
