/* "Fire and Water" v2. Every beat is a pass (or a few): its own scene and its own camera move, drawn in order,
   so neighbouring beats can overlap and one can grow out of the other without a cut.
   A beat module exports create(ctx) -> pass or [passes]:
     { from, to,            seconds the pass is drawn (to is exclusive)
       scene,               its THREE.Scene
       update(t),           sets the camera (stage.setRig) and the whole scene from the time alone
       rect(t), clip(t), background(t)   optional, see Stage.renderPasses }
   The ground colour comes from timeline.ground. update(t) of the film returns the passes of that instant.
   ?only=b03,b04 in the player URL (render.py --only) builds just those beats: faster while working on one. */
import { THREE } from '../../src/core/stage.js';
import { createTimeline } from '../../src/core/timeline.js';
import { ease } from '../../src/core/motion.js';
import data from './timeline.js';
import * as handoff from './handoff.js';

const BEAT_IDS = ['b01', 'b02', 'b03', 'b04', 'b05', 'b06', 'b07', 'b08', 'b09', 'b10'];

/** Ground colour at time t: smooth blends between the keys of the colour script. */
function groundAt(keys, t, out) {
  if (t <= keys[0][0]) return out.set(keys[0][1]);
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const k = ease.inOutCubic((t - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0]));
      return out.set(keys[i - 1][1]).lerp(new THREE.Color(keys[i][1]), k);
    }
  }
  return out.set(keys[keys.length - 1][1]);
}

/** Smooth, never-reversing curve through the anchors [real, planned] (monotone cubic), slope 1 after the last one:
    the picture's planned time for a real time. Smooth so the picture never changes speed with a jerk. */
function createWarp(anchors) {
  if (!anchors || anchors.length < 2) return (t) => t;
  const n = anchors.length;
  const x = anchors.map((a) => a[0]), y = anchors.map((a) => a[1]);
  const secant = x.slice(1).map((_, i) => (y[i + 1] - y[i]) / (x[i + 1] - x[i]));
  const slope = x.map((_, i) => {
    if (i === 0) return secant[0];
    if (i === n - 1) return 1;
    return (2 * secant[i - 1] * secant[i]) / (secant[i - 1] + secant[i]);   // harmonic mean keeps it monotone
  });
  return (t) => {
    if (t <= x[0]) return y[0] + (t - x[0]) * slope[0];
    if (t >= x[n - 1]) return y[n - 1] + (t - x[n - 1]);
    let i = 0;
    while (t > x[i + 1]) i++;
    const h = x[i + 1] - x[i], k = (t - x[i]) / h;
    const k2 = k * k, k3 = k2 * k;
    return (2 * k3 - 3 * k2 + 1) * y[i] + (k3 - 2 * k2 + k) * h * slope[i] + (-2 * k3 + 3 * k2) * y[i + 1] + (k3 - k2) * h * slope[i + 1];
  };
}

export async function createFilm(stage) {
  const timeline = createTimeline(data);
  const only = (new URLSearchParams(location.search).get('only') || '').split(',').filter(Boolean);
  const ids = BEAT_IDS.filter((id) => only.length === 0 || only.includes(id));
  const ctx = { stage, timeline, beats: timeline.beats, handoff, ground: (t) => groundAt(timeline.ground, t, new THREE.Color()) };
  const built = await Promise.all(ids.map(async (id) => {
    const module = await import(`./beats/${id}.js`);
    return module.create(ctx);
  }));
  const passes = built.flat();
  passes.forEach((pass, index) => {
    if (!pass.scene || typeof pass.update !== 'function' || !(pass.to > pass.from)) throw new Error(`film v2: pass ${index} is malformed`);
  });

  const warp = createWarp(timeline.warp);

  /** realTime = the film's clock (the narration's). The beats live in the script's planned time: warp gives it. */
  function update(realTime) {
    const t = warp(realTime);
    groundAt(timeline.ground, t, stage.background);
    return passes.filter((pass) => t >= pass.from && t < pass.to).map((pass) => ({
      scene: pass.scene,
      update: (time) => pass.update(warp(time)),
      rect: pass.rect ? pass.rect(t) : null,
      clip: pass.clip ? pass.clip(t) : null,
      background: pass.background ? pass.background(t) : null,
    }));
  }

  return { timeline, update };
}
