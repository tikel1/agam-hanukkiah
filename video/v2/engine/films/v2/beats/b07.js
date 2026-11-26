/* Beat 07 (76.0-97.0): the design, the heart of the film.
   76.0-92.6  ONE move (parts/b07_rig.js): inside beat 6's video player the painted hanukkiah turns slowly; at 77.9 the
              camera pushes into the phone's screen and the push simply goes on: the hanukkiah's own rings tell the
              tribute (all five whip round, alternate ways, like the fountain's rings) and then a bump runs up the stack, a
              dot for each (one to five); the orbit speeds up and arrives at the front of R3: mixed stripes,
              "מה מסתתר?"; it swings left: the Magen David comes out of the stripes by the angle alone, then the
              dreidel; it crosses the front to the right (a band of light sweeps the teeth): HANUKKAH from its "H",
              the word runs through, then the sufganiyah. Each symbol is held by slowing, never by stopping
   92.6-95.4  the kinetic sweep: our ring stays the picture; the fire / water example turns in a small stripe-framed card at
              the upper left, which hops to the upper right as its picture flips
   95.4-96.8  the card leaves, the camera pulls back to the T97 rest pose (whole hanukkiah)
   Passes: main (ring world, 76.0-97.0), card (the sheet, small), marks (eye track, card frame and connector). */
import { THREE } from '../../../src/core/stage.js';
import { Hanukkiah, HANUKKIAH_RINGS } from '../../../src/components/hanukkiah.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { FOUNTAIN } from '../../../src/palette.js';
import { B07_FROM, b07Pass, T97 } from '../handoff.js';
import { T, DEG, mainRig, rigOf, candleHeights } from '../parts/b07_rig.js';
import { ringMotion, answerTime, candleRattle } from '../parts/b07_rings.js';
import { EyeTrack, CountDots } from '../parts/b07_hud.js';
import { PolymorphSheet } from '../parts/b07_sheet.js';
import { CardMarks, CardShadow, cardRect, cardClip, cardVisible } from '../parts/b07_card.js';
import { LightSweep } from '../parts/b07_light.js';

const TITLE = { words: ['מה', 'מסתתר?'], cap: 112, x: 540, y: 345 };
const FRAME = { width: 1080, height: 1920 };
const SHEET_RIG = { pitch: 16, zoom: 0.55, y: 0, shiftY: 47 };     // the example's camera height; content centred
const ANSWERS = HANUKKIAH_RINGS.map((_, k) => answerTime(k));
const CARD_PASS = [T.bubbleIn, T.bubbleOut + 0.5];

const withRattle = (heights, rattle) => heights.map((h, i) => h * rattle[i]);

/** The rings' own motion (whip, bump up the stack) plus R3's spin from the camera path (degrees). */
function ringsAt(t, r3SpinDegrees) {
  const { offsetY, spin } = ringMotion(t);
  return { offsetY, spin: { ...spin, R3: spin.R3 + r3SpinDegrees * DEG } };
}

function buildMain(ctx) {
  const scene = new THREE.Scene();
  const hanukkiah = new Hanukkiah(ctx.stage);
  const title = new LineDotTitle({ words: TITLE.words, cap: TITLE.cap });
  const count = new CountDots();
  const cardShadowMark = new CardShadow();
  const sweep = new LightSweep(hanukkiah.rings.R3.surface.mesh);
  scene.add(hanukkiah.group, title.group, count.group, cardShadowMark.group);
  const probe = new THREE.Vector3();
  const ringY = (k) => {
    const spec = HANUKKIAH_RINGS[k];
    probe.set(0, spec.base + spec.height / 2, 0).project(ctx.stage.camera);
    return ((1 - probe.y) / 2) * FRAME.height;
  };

  function update(t) {
    const atRest = t >= T.rest;
    const sample = mainRig(t);
    ctx.stage.setRig(atRest ? T97.rig : rigOf(sample));
    hanukkiah.update(t, atRest ? T97.hanukkiah : {
      ...T97.hanukkiah, candles: withRattle(candleHeights(t), candleRattle(t)), ...ringsAt(t, sample.spin),
    });
    const titleVisible = t >= T.titleIn && t < T.titleOut + T.titleOutSpan;
    title.group.visible = titleVisible;
    if (titleVisible) {
      ctx.stage.place(title.group, TITLE.x, TITLE.y, { depth: 1500 });
      title.update(t - T.titleIn, { span: T.titleSpan, out: T.titleOut - T.titleIn, outSpan: T.titleOutSpan });
    }
    count.update(t, ctx.stage, ringY, ANSWERS);
    cardShadowMark.update(t, ctx.stage);
    sweep.update(t);
  }
  return {
    from: B07_FROM, to: T.to, scene, update,
    rect: (t) => b07Pass(t).rect, clip: (t) => b07Pass(t).clip, background: (t) => b07Pass(t).background,
  };
}

/** The kinetic-art example, drawn small into the card's window (rect + clip; CardMarks frames it). */
function buildCard(ctx) {
  const scene = new THREE.Scene();
  const sheet = new PolymorphSheet();
  scene.add(sheet.group);
  function update(t) {
    ctx.stage.setRig({ ...SHEET_RIG, yaw: mainRig(t).yaw });
    sheet.update({ fold: 1, floor: 1 });
  }
  return { from: CARD_PASS[0], to: CARD_PASS[1], scene, update, rect: cardRect, clip: cardClip, background: () => FOUNTAIN.white };
}

function buildMarks(ctx) {
  const scene = new THREE.Scene();
  const eye = new EyeTrack();
  const card = new CardMarks();
  scene.add(eye.group, card.group);
  function update(t) {
    ctx.stage.setRig({});
    eye.update(t, mainRig(t).yaw, ctx.stage);
    card.update(t, ctx.stage);
  }
  return { from: T.eyeIn, to: Math.max(T.eyeOut + 0.6, CARD_PASS[1]), scene, update };
}

export async function create(ctx) {
  if (ctx.beats.b07.end !== T.to) throw new Error(`b07: timeline says the beat ends at ${ctx.beats.b07.end}, the beat is built for ${T.to}`);
  if (cardVisible(CARD_PASS[1])) throw new Error('b07: the card pass ends before the card has gone');
  return [buildMain(ctx), buildCard(ctx), buildMarks(ctx)];
}
