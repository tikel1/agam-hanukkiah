/* Beat 2 (6.5-23, drawn to 24.6): kinetic art. Planned script seconds (the film maps them onto the narration).
   6.5-11.6   the feed: a large hero card of the Agam museum gallery rises while beat 1's page leaves, then two works
              side by side (standing polymorph, colour grid), a page step to the place for "the girls at the Agam
              museum"; a scroll bar of dots on the right; at 11 the feed scrolls out
   11.35-14.2 "אמנות / קינטית" writes itself; under it two pictures arrive (fire from the left, water from the
              right), are cut into 16 strips each and the strips weave into one row (films/polymorph)
   14.55-16.2 on "folds" the row folds into pleats and stands on a floor with its hard flat shadow; first look
              from the side; the eye marker appears under it
   16.2-20.95 the walk round: fire alone from the left (hold), both mixed in front, water alone from the right (hold)
   20.95-22.9 "every step, a new picture!": three quick steps, fire / water / fire
   23.0-24.45 the folds open flat, the sheet becomes the ring sheet (unseen swap), floor, shadow and eye
              go, it closes into the fountain's bottom ring and lands low; at rest on T23 from 24.45; the pass ends at 24.6. */
import { THREE } from '../../../src/core/stage.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { T, rigAt, yawAt } from '../parts/b02_rig.js';
import { createDemo } from '../parts/b02_demo.js';
import { createRingSheet, closingAt } from '../parts/b02_sheet.js';
import { createFeed } from '../parts/b02_feed.js';
import { createEyeTrack } from '../parts/b02_eye.js';
import { FRAME } from '../parts/b01_common.js';

const TITLE = [
  { words: ['אמנות'], cap: 130, py: 300, start: T.title[0], span: 0.75 },
  { words: ['קינטית'], cap: 130, py: 478, start: T.title[1], span: 0.8 },
];
const EYE = { py: 1440, depth: 1600 };
const TITLE_DEPTH = 1600;

export async function create(ctx) {
  const { stage } = ctx;
  const beat = ctx.beats.b02;
  const scene = new THREE.Scene();
  const demo = createDemo();
  const ring = createRingSheet(demo.pictures);
  const feed = await createFeed();
  const eye = createEyeTrack();
  const titles = TITLE.map((spec) => ({ spec, title: new LineDotTitle({ words: spec.words, cap: spec.cap }) }));
  scene.add(demo.group, ring.mesh, eye.group, ...feed.objects, ...titles.map((x) => x.title.group));

  function updateTitles(t) {
    titles.forEach(({ spec, title }) => {
      const local = t - spec.start;
      title.group.visible = local > 0 && t < T.titleOut + T.titleOutSpan + 0.05;
      title.update(local, { span: spec.span, out: T.titleOut - spec.start, outSpan: T.titleOutSpan });
      stage.place(title.group, FRAME.centreX, spec.py, { depth: TITLE_DEPTH });
    });
  }

  function update(t) {
    stage.setRig(rigAt(t));
    const closing = closingAt(t);
    demo.update(t, closing);
    ring.update(t, closing);
    feed.update(t, stage);
    updateTitles(t);
    eye.group.visible = t > T.eyeIn && t < T.eyeOut + 0.6;
    eye.update(t, { appearAt: T.eyeIn, leaveAt: T.eyeOut, yaw: yawAt(t) });
    stage.place(eye.group, FRAME.centreX, EYE.py, { depth: EYE.depth });
  }

  return { from: beat.start, to: T.passEnd, scene, update };
}
