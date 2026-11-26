/* Hand-offs between beats that are built apart. Two kinds:
   - a REST POSE: at one instant the old beat stops being drawn and the new one starts, with exactly the same
     picture (same object state, same camera), so nothing jumps. Both beats read the pose from here.
   - the PHONE: beat 7 first plays inside the phone of beat 6, then the camera pushes into the phone's screen in
     one eased push that beat 7's camera continues (the screen becomes the frame, the push does not stop).
   Change a number here and both sides follow. */
import { ease, prog, lerp } from '../../src/core/motion.js';
import { GROUND } from '../../src/palette.js';
import { FOUNTAIN86_RINGS, FOUNTAIN86_DEPTH, fountain86Colors } from '../../src/components/fountain86.js';

const FRAME = [0, 0, 1080, 1920];

/** 24.6 s: the fan of beat 2 has closed into the BOTTOM ring of the fountain (ring 0), at its own level, where the pool will be.
    User note: the fan stays a flat picture until the narration starts "ויש לו יצירה גדולה" (23.0); only then it
    bends (23.0 - 24.45, beat 2's pass). Beat 3 may show its title and frame from 23.0 on top, but draws its
    Fountain86 only from this instant: only ring `ringIndex`, with `drop`, nothing else yet. */
const RING_INDEX = 0;   // user note: the ring the fan turns into is the BOTTOM ring; the other four land on it
const RING = FOUNTAIN86_RINGS[RING_INDEX];
export const T23 = Object.freeze({
  time: 24.6,
  bendFrom: 23.0,
  rig: { yaw: 0, pitch: 10, zoom: 0.7, y: 673 },
  ringIndex: RING_INDEX,
  drop: 0,
  /** What beat 2's pleated sheet must be at 23.0 to equal that ring (PleatedSurface, bend 1, mesh.position.y = centreY). */
  sheet: {
    pleats: RING.teeth, length: 2 * Math.PI * RING.radius, height: RING.height, depth: ((2 * Math.PI * RING.radius) / RING.teeth) * FOUNTAIN86_DEPTH,
    centreY: RING.base + RING.height / 2, shadeStep: 0.14, ...fountain86Colors(RING_INDEX),
  },
});

/** 97.0 s: the painted hanukkiah (Hanukkiah at the origin, y = 0 its table), seen from the left. */
export const T97 = Object.freeze({
  time: 97.0,
  rig: { yaw: -34, pitch: 8, zoom: 0.9, y: 330 },
  hanukkiah: { painted: 1, lit: 0, candles: 1 },
});

/** 112.0 s: the stacked, painted hanukkiah, seen from the right (HANUKKAH), unlit; the night falls after this. */
export const T112 = Object.freeze({
  time: 112.0,
  rig: { yaw: 34, pitch: 8, zoom: 0.9, y: 330 },
  hanukkiah: { painted: 1, lit: 0, candles: 1 },
});

/** The phone of 6.4. Screen rectangle in frame pixels [x, y, w, h] (9:16, so a full frame fits exactly). */
export const PHONE = Object.freeze({
  rest: [392, 520, 432, 768],
  shrink: [75.0, 75.8],        // the full frame shrinks into the phone (beat 6's world)
  wipe: [76.0, 76.5],          // inside the phone, beat 7 scrolls in from below over beat 6's world
  grow: [77.9, 79.3],          // the camera pushes into the screen until it is the frame (eased out at the edge;
                               // beat 7's own camera keeps the push going, see films/v2/parts/b07_rig.js)
});
/** Parallax of the layers around the phone while the camera pushes in: nearer layers grow faster (k > 1). */
export const PUSH_PARALLAX = Object.freeze({ claude: 1.7, strip: 1.4, player: 1.25, rain: 0.75 });
const mixRect = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));

/** Screen rectangle of the phone at time t (full frame before the shrink and after the grow). */
export function phoneRect(t) {
  if (t < PHONE.grow[0]) return mixRect(FRAME, PHONE.rest, ease.inOutCubic(prog(t, ...PHONE.shrink)));
  return mixRect(PHONE.rest, FRAME, ease.inOutCubic(prog(t, ...PHONE.grow)));
}

/** Beat 7's pass while it plays inside the phone: where it is drawn, what part shows, and its own ground. */
export function b07Pass(t) {
  if (t >= PHONE.grow[1]) return { rect: null, clip: null, background: null };
  const rect = phoneRect(t);
  const k = ease.inOutCubic(prog(t, ...PHONE.wipe));
  const clip = [rect[0], rect[1] + rect[3] * (1 - k), rect[2], rect[3] * k];
  return { rect, clip, background: GROUND.paper };
}
export const B07_FROM = PHONE.wipe[0];
