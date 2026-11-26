# v2 animation engine

Three.js (orthographic camera, unlit flat colours) driven by a pure `update(t)` timeline, captured frame by frame
through headless Edge and encoded with ffmpeg. Proof: `proof.mp4` (18 s, vertical 1080x1920, 30 fps).

The frame size is the film's choice: `size: [1080, 1920]` in its `timeline.js` (v2 is 9:16 for phones; `[1920, 1080]`
works the same way). Phone layout used in the proof: subject centred and large, title in the upper third,
subtitles sitting above the bottom 16% of the frame and at most 84% wide, so platform buttons do not cover them.

## Why this and not HyperFrames

| Option | Result here | Verdict |
|---|---|---|
| **HyperFrames 0.9.98** (HeyGen, HTML to video) | Installs, but refuses to start: needs Node 22, this machine has Node 20.18. It is a capture + GSAP-seek layer; it adds no 3D and no motion blur of its own. | Not used. Would need a Node upgrade for no gain in look. |
| **Remotion** | Works on Node 20, but brings React + a bundler + its own Chrome download, and a licence to track. Same capture idea as ours. | Not used. |
| **Motion Canvas** | 2D canvas only; 3D pleats would have to be faked. | Not used. |
| **Three.js in the v1 capture pipeline** | Runs on the real GPU in headless Edge (ANGLE / D3D11), 0.17 s per frame with 12 sub-frames. Real 3D pleats, true motion blur, one continuous camera. | **Chosen.** |

The look comes from what is drawn, not from the framework: real pleated geometry seen by an orthographic camera
(so the polymorph effect is physical, not faked), flat unlit colours from the film palette, and an accumulation
pass that averages 12 sub-frames per frame (motion blur and clean edges together).

## Render

Use the v1 venv (imageio-ffmpeg, websocket-client, requests):

```
..\..\animation\.venv\Scripts\python render.py --film proof --video proof.mp4
..\..\animation\.venv\Scripts\python render.py --film proof --stills 2,5.5,9 --out stills
..\..\animation\.venv\Scripts\python render.py --film proof --video part.mp4 --range 6,9
..\..\animation\.venv\Scripts\python render.py --serve      # preview with a scrubber in the browser
..\..\animation\.venv\Scripts\python contact.py stills sheet.png 3
```

Measured at 1080x1920: 540 frames in about 80 s with 4 workers, plus about 22 s encode. A 2 minute film is about 11 minutes.
Options: `--workers`, `--samples` (sub-frames, default 12; 1 = no blur), `--shutter` (default 0.5), `--audio`.

- **Deterministic seeking:** the page exposes `seek(t)`; every value is a pure function of `t` (springs are
  analytic, noise is seeded). Frames render in any order, on several workers, and always come out the same.
- **Audio:** `--audio narration.wav`, or set `audio` in the film's timeline (path relative to this folder). AAC 192k, 48 kHz.
- **Subtitles:** `subtitles: [{ start, end, text, dark }]` in the timeline, or `parseSrt()` for an .srt file. They are an
  HTML layer over the canvas, so the browser does Hebrew shaping and right-to-left order; they are burned in by the
  screenshot. Secular One 54 px with a halo; `dark: true` for night scenes. `\n` gives a second line.
- ES modules need http, so `render.py` serves this folder on 127.0.0.1 for the length of the render.

## Structure

```
render.py, contact.py, player.html
src/core/        motion.js (easing, spring, wobble, track, drift)   stage.js (renderer, camera rig, motion blur)
                 timeline.js (beats, camera tracks)                 subtitles.js
src/components/  pleated.js (PleatedSurface, ToothedRing)   photoFrame.js (untouched photo in a frame)
                 shadows.js (soft flat shadows)
                 motifs.js (pictures painted on the big ring of our hanukkiah)
                 lineDotTitle.js + glyphs.js                 flame.js      fountain.js (Fountain, Candle)
src/palette.js   colours from the v1 style bible
films/proof/     timeline.js (beats, camera, subtitles, audio)   film.js (what happens in each beat)
films/polymorph/ demo of the polymorph principle: two pictures cut into strips, woven, folded; hard flat shadows
vendor/          three.js 0.187 (MIT)
```

## Making the full film

1. Copy `films/proof` to `films/v2`. Put all times in `timeline.js`: beats (they may overlap), camera keys
   `[time, value, ease]`, subtitles, audio.
2. In `film.js`, build components once in `createFilm`, then set everything in `update(t)` from the time alone.
   Never keep state between frames: motion blur calls `update` 12 times per frame at slightly different times.
3. Use `beat.at(seconds)` for times, `spring` / `wobble` for overshoot and follow-through, `tween(..., 'anticipate')`
   or `bump` for anticipation, and stagger starts by index for overlap.
4. Links between scenes are shape changes, not cuts: `PleatedSurface.update({ bend })` turns a sheet into a ring,
   `colorMix` and `motifAmount` change what the faces show, the camera rig carries the eye.

## Limits and open points

- **Photos (user rules):** no effects on photos. They are shown untouched in a designed frame (`photoFrame.js`:
  white card, colour strip, soft shadow), never filtered, recoloured or cut into pleats. Real photographs only,
  never frames grabbed from a video. The proof uses `storyboard/photos/original/agam_at_fountain_user.jpg`
  (copied to `assets/photos`); rights are not checked.
- **Shadows (user note):** soft flat shadows give depth while the look stays two-dimensional (`shadows.js`:
  `discShadow` on ring tops, water and floor, `cardShadow` under cards; `shadeTop` on a ring darkens its top under a
  wider ring). There are no lights: a shadow is a shape the film places and scales.
  For a look with no gradients at all use the hard ones: `WallShadow` (a standing sheet's shadow on the floor) and
  plain offset copies in one flat tone, as in `films/polymorph`.
- Ring proportions are our hanukkiah model's, not a surveyed silhouette of the fountain.
- Letters beyond the logo set (and digits) are the v1 additions; a missing letter throws a clear error.
- Subtitles are not kept clear of the picture automatically: keep the important picture above the bottom 25% of the frame.
- The proof ends on our own hanukkiah (eight blue candles in a circle on the big ring, shamash on the top drum,
  white goblet foot), built from the numbers in `HANUKKIAH` in `films/proof/film.js`. The big ring is painted with
  our motifs (`motifs.js`: HANUKKAH on the right faces, Star of David on the left faces, sufganiyah), drawn after
  the model renders, not from the exact paint maps; the dreidel is not drawn.
- The subtitle lines in the proof are placeholders.


## Film v2 (`films/v2`): the full film

`films/v2` is the whole film (129.5 s, 1080x1920): `timeline.js` (beats, ground colours, subtitle cues), `film.js`
(joins the beats), `handoff.js` (the shared poses where one beat hands over to the next), `beats/b01.js` .. `b10.js`
(one file per section of the script) and `parts/` (what a beat is built from). `films/v2/BRIEF.md` is the manual for
animating a beat: the binding style rules, the beat contract, the components and the working loop.

```
python render.py --film v2 --video v2_draft.mp4                 # the whole film (about 3,900 frames)
python render.py --film v2 --only b06,b07 --stills 76,78.5,79 --out _stills/x   # only those beats: fast
python render.py --film v2 --range 84,97 --video part.mp4       # one stretch
```

What v2 added to the engine:

- **Passes** (`Stage.renderPasses`): a film's `update(t)` may return a list of passes, each its own scene with its own
  camera move, drawn in order. Beats overlap in time and grow out of each other without a cut. A pass can be drawn
  into a rectangle (`rect`: a film inside a phone) or cut (`clip`: a split screen). `stage.setRig({...})` sets the
  camera in one call, `stage.place(group, px, py)` pins things to screen pixels.
- **One step of shade** (`shadeStep` on `PleatedSurface`, `flatShade.js` for solid shapes): faces turned away from the
  key light get 14% ink. Still no lights and no gradients.
- **`hanukkiah.js`**: our hanukkiah as printed (foot with the name plaque, five rings with 70 degree folds, the hidden
  pictures of R3 incl. the dreidel from `ringPictures.js`, candles, flames). White or painted; the paint can rise as a
  wave (`painted`) or go on column by column (`paintU`); parts can be lifted (`offsetY`) for drops and exploded views.
- **`fountain86.js`**: the 1986 fountain (five rings on a column, pool), also as a one-colour silhouette.
- **`stripeFrame.js`**: the stripe frame for anything real: photos, the two archive clips (frame atlases in
  `assets/clips/`, picked by time so seeking stays exact), placeholders for the photos of the girls. Curtain, tape,
  night look. The picture inside is never changed.
- **`slatSubtitles.js`** (`subtitleStyle: 'slats'` in a timeline): each line on a slanted slat with a stripe stamp and
  a dot that hops from word to word. Give a cue `words: [seconds...]` (from the TTS) to time the dot exactly.
- Glyphs: new ק, ט, `?`, `!`, `A`, `I`, `2`, en dash.
- `render.py`: every browser gets its own free debug port (several renders can run at once), `--only` for v2, and a
  throw-away capture before each frame so the subtitles and the picture are from the same instant.

Open in v2: no narration yet (beat and cue times follow the script: move them in `timeline.js` when the TTS is
recorded); three placeholders wait for real photos of the girls (2.1 museum, 6.2 at the computer, 9.1 painting):
swap `createPlaceholder(...)` for `loadPicture('assets/photos/<file>')` in `parts/b02_feed.js`, `parts/b06_panels.js`
and `parts/b09_table.js`.

### Narration sync (v2)

`python sync_narration.py` reads `../narration/timings.json` (real start and end of every narration row) and writes
`films/v2/narration.js` and `films/v2/subtitles.srt`. The film then plays its picture at the script's planned time
that belongs to each real moment (a smooth time warp in `film.js`), so the beats keep their own timing and still sit
under their sentences. Run it again after every new recording, then render with `--audio`. With a narration in place,
`--stills` and `--range` take real (narration) seconds. The film is cut to the length of the sound.
