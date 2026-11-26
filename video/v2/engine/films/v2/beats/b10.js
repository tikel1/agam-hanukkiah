/* Beat 10 (112.0-129.5): the tribute and the end card. Night falls, the candles light one by one from the shamash,
   "חנוכיית / אש ומים". The hanukkiah goes down, Agam's photo returns above it and the stripes of the opening wrap
   both like a gift ("מחווה / ליעקב אגם"). A flame flies from the photo to the shamash and the fire runs along the
   candles. The wrap and the photo rise away into the end card: "חג / שמח!", the burning hanukkiah, a dot rule, the
   girls' names and the school (Rubik) and our logo in line-and-dot letters. It holds to the end on flickering flames, twinkling stars and a slow drift.
   Starts from the rest pose T112 (handoff.js), shared with beat 9. Plan and layout: parts/b10_plan.js. */
import { THREE } from '../../../src/core/stage.js';
import { Hanukkiah, candleAngle } from '../../../src/components/hanukkiah.js';
import { StripeFrame, loadPicture } from '../../../src/components/stripeFrame.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { DOTS, PAPER } from '../../../src/palette.js';
import { clamp, drift, ease, lerp, prog, spring, track, bump } from '../../../src/core/motion.js';
import { T112 } from '../handoff.js';
import { CUE, RIG, YAW, DRIFT, LAYOUT, DEPTH, FLARE, arrive } from '../parts/b10_plan.js';
import { NightStars } from '../parts/b10_stars.js';
import { GiftWrap } from '../parts/b10_wrap.js';
import { FlameFlight } from '../parts/b10_flight.js';
import { DotRule, createCredits } from '../parts/b10_card.js';
import { FlameLight, EdgeLight } from '../parts/b10_light.js';

const PHOTO_URL = 'assets/photos/agam_tribute.jpg';
const CENTRE = [540, 960];
const DEG = Math.PI / 180;
const STAR_PARALLAX = { yaw: -3, y: 0.035 };     // pixels per degree of yaw / per pixel of camera rise
const LIFT = { flying: 1, resting: 0.35 };
const SEATS = 9;                                  // shamash + 8 candles
const yawAt = track(YAW.map(([time, yaw], i) => (i ? [time, yaw, 'inOutCubic'] : [time, yaw])));
const rotate = (colours, offset) => [...colours.slice(offset), ...colours.slice(0, offset)];

const TITLES = [
  { words: ['חנוכיית'], cue: CUE.titleA, out: CUE.titleAOut, at: LAYOUT.titleA, dots: 0 },
  { words: ['אש', 'ומים'], cue: CUE.titleB, out: CUE.titleBOut, at: LAYOUT.titleB, dots: 4 },
  { words: ['מחווה'], cue: CUE.titleC, out: CUE.titleCOut, at: LAYOUT.titleC, dots: 1 },
  { words: ['ליעקב', 'אגם'], cue: CUE.titleD, out: CUE.titleDOut, at: LAYOUT.titleD, dots: 6 },
  { words: ['חג'], cue: CUE.titleE, out: null, at: LAYOUT.titleE, dots: 2 },
  { words: ['שמח!'], cue: CUE.titleF, out: null, at: LAYOUT.titleF, dots: 5 },
  { words: ['חנוכיית', 'אש', 'ומים'], cue: CUE.logo, out: null, at: LAYOUT.logo, dots: 3 },     // our logo, small
];
const NIGHT_FALL = [112.0, 113.4];               // the global ground turns to night here (timeline.ground)
const EDGE_LIGHT_LIFT = 0.45;                    // the light sits this share of the flame's height above its base

/** Order in which the flames light (shamash first, then the candles from screen right to left at the hero yaw)
    and when each one leaps as the fire from the photo runs along them. Index 0 = shamash, 1..8 = candles 0..7. */
function flamePlan() {
  const yaw = YAW[0][1] * DEG;
  const ranked = Array.from({ length: SEATS - 1 }, (_, k) => k)
    .sort((a, b) => Math.sin(candleAngle(b) - yaw) - Math.sin(candleAngle(a) - yaw));
  const plan = Array.from({ length: SEATS }, () => ({ light: CUE.lightShamash, flare: CUE.flightLand }));
  ranked.forEach((k, rank) => {
    plan[k + 1] = { light: CUE.lightFirstCandle + rank * CUE.lightStep, flare: CUE.flareFirstCandle + rank * CUE.flareStep };
  });
  return plan;
}

/** Flame sizes [shamash, c0..c7]: each one pops alight (small overshoot), then leaps once when the fire passes. */
function flameSizes(t, plan) {
  return plan.map(({ light, flare }) => {
    const on = spring(t - light, 3.0, 0.5);
    const leap = Math.pow(Math.sin(Math.PI * prog(t, flare, flare + CUE.flareSpan)), 2);
    return on * (1 + FLARE * leap);
  });
}

/** The camera: rest pose -> hero (title room above) -> tribute (lower half) -> end card, with a slow drift. */
function rigAt(t) {
  const { rest, hero, tribute, card } = RIG;
  const k1 = ease.inOutCubic(prog(t, ...CUE.heroMove));
  const k2 = arrive(t, ...CUE.tributeMove, 0.03);
  const k3 = arrive(t, ...CUE.cardMove, 0.03);
  const mix = (pick) => lerp(lerp(lerp(pick(rest), pick(hero), k1), pick(tribute), k2), pick(card), k3);
  // blend where the table sits on screen (not the camera target): mixing target and zoom apart would swing the
  // hanukkiah down through the subtitle band half way between two poses
  const zoom = mix((pose) => pose.zoom);
  const table = mix((pose) => CENTRE[1] + pose.y * pose.zoom);
  const push = 1 + RIG.holdPush * ease.inOutCubic(prog(t, CUE.cardMove[1] - 0.3, RIG.holdUntil));
  const ramp = ease.inOutCubic(prog(t, ...DRIFT.rampIn));        // no drift at the rest pose
  return {
    yaw: yawAt(t) + DRIFT.yaw * drift(t, 5, 0.06) * ramp,
    pitch: mix((pose) => pose.pitch), zoom: zoom * push, y: (table - CENTRE[1]) / zoom,
    shiftY: DRIFT.shiftY * drift(t, 9, 0.05) * ramp,
  };
}

/** Frame pixels of a point in the hanukkiah's own space (after the rig is set and the hanukkiah updated). */
function toScreen(stage, hanukkiah, local) {
  hanukkiah.group.updateMatrixWorld(true);
  const v = hanukkiah.group.localToWorld(local.clone()).project(stage.camera);
  return [(v.x + 1) * 0.5 * stage.width, (1 - v.y) * 0.5 * stage.height];
}

/** How far the wrap + photo have risen away (pixels, up) at the end; with a small dip first (anticipation). */
const exitRise = (t) => LAYOUT.exitRise * ease.inOutQuart(prog(t, ...CUE.exit)) - LAYOUT.exitDip * bump(t, ...CUE.exitDip);

export async function create(ctx) {
  const { stage } = ctx;
  const beat = ctx.beats.b10;
  if (Math.abs(beat.start - CUE.start) > 1e-6) throw new Error(`b10: beat starts at ${beat.start}, the plan at ${CUE.start}`);
  const scene = new THREE.Scene();
  const hanukkiah = new Hanukkiah(stage);
  const stars = new NightStars();
  const wrap = new GiftWrap(LAYOUT.wrap);
  const { photo: P } = LAYOUT;
  const photo = new StripeFrame({ picture: await loadPicture(PHOTO_URL), width: P.width, height: P.height, focus: P.focus, night: true, curtain: true });
  const titles = TITLES.map((spec) => ({
    ...spec, title: new LineDotTitle({ words: spec.words, cap: spec.at.cap, ink: PAPER, dotColors: rotate(DOTS, spec.dots), ends: spec.ends !== false }),
  }));
  const flight = new FlameFlight(LAYOUT.flight);
  const rule = new DotRule(LAYOUT.rule);
  const credits = await createCredits(LAYOUT);
  const light = new FlameLight(hanukkiah);
  const edge = new EdgeLight({ outer: [P.x - photo.width / 2, P.y - photo.height / 2, P.x + photo.width / 2, P.y + photo.height / 2], band: (photo.width - P.width) / 2 });
  scene.add(hanukkiah.group, stars.group, wrap.group, photo.group, edge.group, flight.group, rule.group, credits.names.group, credits.school.group);
  titles.forEach(({ title }) => scene.add(title.group));
  const plan = flamePlan();
  const parts = { stage, hanukkiah, stars, wrap, photo, titles, flight, rule, credits, light, edge, plan };
  return { from: beat.start, to: beat.end, scene, update: (t) => updateBeat(t, parts) };
}

function updateBeat(t, parts) {
  const { stage, hanukkiah, plan } = parts;
  // the rest pose, exactly as beat 9 leaves it
  if (t <= CUE.start) {
    stage.setRig(T112.rig);
    hanukkiah.update(t, T112.hanukkiah);
  } else {
    const rig = rigAt(t);
    stage.setRig(rig);
    hanukkiah.update(t, { ...T112.hanukkiah, lit: flameSizes(t, plan) });
  }
  // flame light and the night shadow: all zero / day at the rest pose, so 112.0 stays exactly T112
  parts.light.update(t, t <= CUE.start ? new Array(9).fill(0) : flameSizes(t, plan), ease.inOutCubic(prog(t, ...NIGHT_FALL)));
  updateStars(t, parts);
  updateTitles(t, parts);
  updateTribute(t, parts);
  updateFlight(t, parts);
  updateCard(t, parts);
}

function updateStars(t, { stage, stars }) {
  const rig = stage.rig;
  stars.update(t, {
    appear: CUE.starsIn,
    shiftX: (rig.yaw - T112.rig.yaw) * STAR_PARALLAX.yaw,
    shiftY: (rig.target.y - T112.rig.y) * rig.zoom * STAR_PARALLAX.y,
  });
  stage.place(stars.group, ...CENTRE, { depth: DEPTH.stars });
}

function updateTitles(t, { stage, titles }) {
  titles.forEach(({ title, cue, out, at }) => {
    const local = t - cue[0];
    title.update(local, { span: cue[1], out: out === null ? null : out - cue[0], outSpan: CUE.titleOutSpan });
    title.group.visible = local > 0 && (out === null || t < out + CUE.titleOutSpan + 0.05);
    stage.place(title.group, CENTRE[0], at.y, { depth: DEPTH.titles });
  });
}

/** Agam's photo and the gift wrap: come in at 115, hold, rise away together at 122.5. */
function updateTribute(t, { stage, wrap, photo }) {
  const { photo: P } = LAYOUT;
  const rise = exitRise(t);
  const head = wrap.total * ease.inOutCubic(prog(t, ...CUE.wrapIn));
  const tail = wrap.total * (1 - ease.inOutCubic(prog(t, ...CUE.unwrap)));
  wrap.update(head, tail);
  stage.place(wrap.group, CENTRE[0], CENTRE[1] - rise, { depth: DEPTH.wrap });

  const arrived = arrive(t, ...CUE.photoIn, 0.04);
  const settle = ease.outCubic(prog(t, CUE.photoIn[0], CUE.photoIn[1] + 0.3));
  const leaving = prog(t, ...CUE.exit);
  photo.group.visible = t >= CUE.photoIn[0] && leaving < 1;
  photo.setCurtain(ease.inOutCubic(prog(t, ...CUE.curtain)));
  photo.setLift(lerp(LIFT.flying, LIFT.resting, settle) + (LIFT.flying - LIFT.resting) * clamp(leaving * 3));
  const y = lerp(P.enterFrom, P.y, arrived) - rise;
  stage.place(photo.group, P.x, y, { depth: DEPTH.photo, roll: P.swing * (1 - settle) });
}

function updateFlight(t, { stage, hanukkiah, flight, photo, edge }) {
  const { photo: P, flight: F } = LAYOUT;
  const active = t >= CUE.flightIgnite && t < CUE.flightLand + 1.2;
  flight.group.visible = active;
  stage.place(edge.group, ...CENTRE, { depth: DEPTH.photo + 10 });
  if (!active) { edge.update([0, 0], 0); return; }
  const wick = toScreen(stage, hanukkiah, hanukkiah.wick('shamash'));
  const frameTop = P.y - photo.height / 2 + F.lift;      // the flame is born standing on the frame's top band
  const lamp = flight.update(t, {
    cue: { ignite: CUE.flightIgnite, go: CUE.flightGo, land: CUE.flightLand },
    from: [P.x, frameTop], to: wick,
  });
  // the travelling flame warms the frame's stripes as it passes (only the band: the photo stays untouched)
  edge.update([lamp.x, lamp.y - lamp.height * EDGE_LIGHT_LIFT], lamp.amount);
  stage.place(flight.group, ...CENTRE, { depth: DEPTH.flight });
}

function updateCard(t, { stage, rule, credits }) {
  rule.update(t, CUE.rule);
  stage.place(rule.group, CENTRE[0], LAYOUT.rule.y, { depth: DEPTH.card });
  const rise = credits.update(t, CUE);
  stage.place(credits.names.group, CENTRE[0], LAYOUT.names.y + rise.names, { depth: DEPTH.card });
  stage.place(credits.school.group, CENTRE[0], LAYOUT.school.y + rise.school, { depth: DEPTH.card });
}
