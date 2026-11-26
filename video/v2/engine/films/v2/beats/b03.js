/* Beat 3 (23-38): the fountain "Fire and Water".
   23-24.6 over beat 2's fan (which bends into a ring and travels down): title "אש ומים" + "1986", the clip frame rises.
   24.6  the rest pose T23: our fountain world appears as only ring 0, the bottom ring (beat 2's ring); then the pool
         springs in and the column grows up to it.
   23-28 sky ground; the real archive clip of the fountain by day plays once in its stripe frame (curtain opens,
         holds the last frame, curtain closes, the frame leaves up by 27.95).
   28-31.5 the other four rings land on it one by one, bottom to top; the camera rises and pulls back with the stack.
   31.5-36 the middle rings turn, line-and-dot jets rise, the flame rises on top; the ground warms to memory.
   36-38 water at its peak, flame 1.5x, the camera starts to climb with the flame (it goes on in beat 4). */
import { THREE } from '../../../src/core/stage.js';
import { track } from '../../../src/core/motion.js';
import { StripeFrame, loadClip, CLIPS } from '../../../src/components/stripeFrame.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { FountainWorld, rigAt } from '../parts/b03_world.js';
import { createTextLine, placeTextLine } from '../parts/b03_text.js';
import { frameLift } from '../parts/b03_light.js';

const CLIP_FRAME = { width: 820, height: 585, x: 540, y: 880, depth: 1500 };
/* frame: rises in from below with a small overshoot, curtain opens, clip plays once, curtain closes, frame leaves up */
const FRAME_Y = track([[24.2, 2350], [24.8, 866, 'outCubic'], [25.0, CLIP_FRAME.y, 'inOutCubic'], [27.4, CLIP_FRAME.y], [27.95, -520, 'inCubic']]);
const CURTAIN = track([[24.75, 0], [25.2, 1, 'inOutCubic'], [27.1, 1], [27.42, 0, 'inOutCubic']]);
const CLIP_START = 24.9;                 // plays once (2.32 s) and holds its last frame until the curtain closes
const FRAME_SPAN = [24.2, 27.95];
const TITLE = { words: ['אש', 'ומים'], cap: 150, y: 330, at: 23.6, span: 1.1, out: 27.3, outSpan: 0.45 };
const YEAR = { text: '1986', size: 52, y: 488, inAt: 24.45, outAt: 27.25 };

export async function create(ctx) {
  const { stage } = ctx;
  const beat = ctx.beats.b03;
  const scene = new THREE.Scene();
  const world = new FountainWorld();
  const clip = await loadClip(CLIPS.fountainDay.url, CLIPS.fountainDay);
  const frame = new StripeFrame({ picture: clip, width: CLIP_FRAME.width, height: CLIP_FRAME.height, curtain: true });
  const title = new LineDotTitle({ words: TITLE.words, cap: TITLE.cap });
  const year = await createTextLine(YEAR.text, { size: YEAR.size, rtl: false });
  scene.add(world.group, frame.group, title.group, year.group);

  function updateFrame(t) {
    frame.group.visible = t >= FRAME_SPAN[0] && t < FRAME_SPAN[1];
    if (!frame.group.visible) return;
    frame.setCurtain(CURTAIN(t));
    frame.setClipTime(t - CLIP_START);
    frameLift(frame, FRAME_Y, t);             // its shadow spreads while it flies, tightens as it lands
    stage.place(frame.group, CLIP_FRAME.x, FRAME_Y(t), { depth: CLIP_FRAME.depth });
  }

  function updateTitles(t) {
    const local = t - TITLE.at;
    title.group.visible = local > 0 && t < TITLE.out + TITLE.outSpan + 0.05;
    title.update(local, { span: TITLE.span, out: TITLE.out - TITLE.at, outSpan: TITLE.outSpan });
    stage.place(title.group, 540, TITLE.y, { depth: 1600 });
    placeTextLine(stage, year, t, { px: 540, py: YEAR.y, inAt: YEAR.inAt, outAt: YEAR.outAt });
  }

  function update(t) {
    stage.setRig(rigAt(t));
    world.update(t, stage);
    updateFrame(t);
    updateTitles(t);
  }

  return { from: beat.start, to: beat.end, scene, update };
}
