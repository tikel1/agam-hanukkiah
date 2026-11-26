/* Beat 4 (38-55.5, pass to 56.0): from the fire to Hanukkah, a tribute to Agam, the idea.
   38-41.5   the camera climbs into the drawn flame, which grows to fill the frame on amber; the real clip of the fire
             dancing on the water (1986) rises in a stripe frame, its curtain opens, it plays once; light rings
             expand; title "חנוכה". The clip's curtain closes and the frame folds away (turns edge-on).
   41.5-47   the camera rises up into the light (the flame's body stays below); the user's photo of the New York
             hanukkiah (landscape) rises in a stripe frame; "ניו יורק" + "הגדולה בעולם".
   47-47.5   quiet: the photo scrolls up, the light dims.
   47.5-52   slow and quiet: Agam's photo rises in the upper half, "1928–2026" under it, a small quiet flame below.
   52-55.5   the photo leaves up, the fountain rises back under the flame, a spark: the flame splits into eight
             on the wide ring plus one on top. 55-56: the flames shrink into colour dots, the fountain sinks a little
             (beat 5's notebook page rises over all this). */
import { THREE } from '../../../src/core/stage.js';
import { track, ease, prog, lerp } from '../../../src/core/motion.js';
import { StripeFrame, loadClip, loadPicture, CLIPS } from '../../../src/components/stripeFrame.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { FountainWorld, rigAt } from '../parts/b03_world.js';
import { createTextLine, placeTextLine } from '../parts/b03_text.js';
import { LightRings, RING_PERIOD } from '../parts/b04_lights.js';
import { frameLift, FrameGlint } from '../parts/b03_light.js';
import { FlameSplit, SPARK } from '../parts/b04_split.js';

const DEG = Math.PI / 180;
const PASS_END = 56.0;
const FIRE = {
  width: 780, height: 632, y: 916, clipStart: 38.7,
  rise: track([[38.1, 2380], [38.65, 900, 'outCubic'], [38.85, 916, 'inOutCubic']]),
  curtain: track([[38.55, 0], [38.95, 1, 'inOutCubic'], [41.45, 1], [41.75, 0, 'inOutCubic']]),
  fold: track([[41.7, 0], [42.0, 90, 'inCubic']]), span: [38.1, 42.0],
};
const NYC = {
  // the user's photo: landscape 743x496, shown at 1.21x (no more, it is small) and uncropped; the flame's body and
  // the light rings carry the lower part of the frame
  url: 'assets/photos/user_menorah_nyc.jpg', width: 900, height: 601, focus: [0, 0], span: [41.75, 47.7],
  y: track([[41.75, 2300], [42.35, 886, 'outCubic'], [42.55, 900, 'inOutCubic'], [47.0, 884, 'inOutCubic'], [47.7, -480, 'inCubic']]),
};
const TRIBUTE = {
  url: 'assets/photos/agam_tribute.jpg', width: 620, height: 800, focus: [0, 0.35], span: [47.35, 52.8],
  y: track([[47.35, 2420], [48.95, 660, 'inOutCubic'], [52.0, 640, 'inOutCubic'], [52.8, -720, 'inCubic']]),
};
const TITLES = [
  { words: ['חנוכה'], cap: 160, y: 320, at: 38.45, span: 0.9, out: 41.3 },
  { words: ['ניו', 'יורק'], cap: 150, y: 320, at: 42.1, span: 1.0, out: 46.55 },
  { words: ['1928–2026'], cap: 62, y: 1142, at: 49.05, span: 1.2, out: 51.75, rtl: false },
];
const SUB = { text: 'הגדולה בעולם', size: 50, y: 488, inAt: 42.95, outAt: 46.6 };
const LIGHT = {
  start: 38.3, stop: 54.6,
  cy: track([[38, 950], [41.6, 950], [42.4, 900], [47.0, 900], [48.8, 1320], [52.2, 1320]]),
  scale: track([[38, 1], [41.6, 1], [42.4, 1.15], [47.0, 1.15], [48.6, 0.62], [52.2, 0.62], [53.2, 0.4]]),
  strength: track([[38, 0], [38.3, 1], [47.0, 1], [48.0, 0.38], [52.2, 0.38], [53.2, 0.55], [54.8, 0.55], [55.6, 0]]),
};

async function buildFrames() {
  const clip = await loadClip(CLIPS.fireOnWater.url, CLIPS.fireOnWater);
  const [nyc, tribute] = await Promise.all([loadPicture(NYC.url), loadPicture(TRIBUTE.url)]);
  return {
    fire: new StripeFrame({ picture: clip, width: FIRE.width, height: FIRE.height, curtain: true }),
    nyc: new StripeFrame({ picture: nyc, width: NYC.width, height: NYC.height, focus: NYC.focus }),
    tribute: new StripeFrame({ picture: tribute, width: TRIBUTE.width, height: TRIBUTE.height, focus: TRIBUTE.focus }),
  };
}

/** Frame pixel of a world point (for screen-pinned things that follow the world). */
function screenOf(stage, x, y, z) {
  const v = new THREE.Vector3(x, y, z).project(stage.camera);
  return [((v.x + 1) / 2) * stage.width, ((1 - v.y) / 2) * stage.height];
}

export async function create(ctx) {
  const { stage } = ctx;
  const beat = ctx.beats.b04;
  const scene = new THREE.Scene();
  const world = new FountainWorld();
  const split = new FlameSplit();
  const lights = new LightRings();
  const frames = await buildFrames();
  const titles = TITLES.map((spec) => ({ spec, title: new LineDotTitle({ words: spec.words, cap: spec.cap, rtl: spec.rtl !== false }) }));
  const sub = await createTextLine(SUB.text, { size: SUB.size });
  scene.add(lights.group, world.group, split.group, frames.fire.group, frames.nyc.group, frames.tribute.group, sub.group);
  titles.forEach(({ title }) => scene.add(title.group));

  const glints = [frames.fire, frames.nyc, frames.tribute].map((frame) => new FrameGlint(frame));

  function placeFrame(frame, t, span, yOf, depth) {
    frame.group.visible = t >= span[0] && t < span[1];
    if (!frame.group.visible) return false;
    frameLift(frame, yOf, t);
    stage.place(frame.group, 540, yOf(t), { depth });
    return true;
  }

  function updateFrames(t) {
    if (placeFrame(frames.fire, t, FIRE.span, FIRE.rise, 1500)) {
      frames.fire.setCurtain(FIRE.curtain(t));
      frames.fire.setClipTime(t - FIRE.clipStart);
      frames.fire.group.rotateY(FIRE.fold(t) * DEG);        // folds away edge-on, curtain closed over the clip
    }
    placeFrame(frames.nyc, t, NYC.span, NYC.y, 1520);
    placeFrame(frames.tribute, t, TRIBUTE.span, TRIBUTE.y, 1540);
    // the light rings brighten the frames' stripe borders as they pass (never the photos)
    const phase = (((t - LIGHT.start) / RING_PERIOD) % 1 + 1) % 1;
    glints.forEach((glint) => glint.update(phase, t > LIGHT.start ? LIGHT.strength(t) : 0));
  }

  function updateTitles(t) {
    titles.forEach(({ spec, title }) => {
      const local = t - spec.at;
      title.group.visible = local > 0 && t < spec.out + 0.5;
      title.update(local, { span: spec.span, out: spec.out - spec.at, outSpan: 0.4 });
      stage.place(title.group, 540, spec.y, { depth: 1600 });
    });
    placeTextLine(stage, sub, t, { px: 540, py: SUB.y, inAt: SUB.inAt, outAt: SUB.outAt });
  }

  function updateLights(t) {
    const spark = screenOf(stage, 0, SPARK.y - SPARK.radius, 0);
    const follow = ease.inOutCubic(prog(t, 52.2, 53.0));
    lights.update(stage, t, {
      start: LIGHT.start, stop: LIGHT.stop, cx: 540, cy: lerp(LIGHT.cy(t), spark[1], follow),
      scale: LIGHT.scale(t), strength: LIGHT.strength(t),
    });
  }

  function update(t) {
    stage.setRig(rigAt(t));
    const state = world.update(t, stage);
    split.update(t, stage, { offset: state.offset, main: state.flame });
    updateLights(t);
    updateFrames(t);
    updateTitles(t);
  }

  return { from: beat.start, to: PASS_END, scene, update };
}

