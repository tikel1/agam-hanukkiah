/* Beat 9 (103 - 112): painting and stacking.
   103.0-103.5 the printed ring (from beat 8, same place, same rig) rises to the painting table and settles.
   103.2-104.6 "and the most fun part?": the photo of the girls painting rises in over the ring, the acrylic markers
             roll in one by one into a row under it.
   104.55-105.6 "painting!": the photo lifts away, the camera dives to the ring, the yellow marker flies to it.
   105.6-108.2 "we painted 408 stripes by hand": R3 turns, the marker paints it column by column, faster and faster;
             "408 / פסים" + "צבועים ביד", the counter dots fill in spectrum order.
   108.3-111.7 "and finally we stacked it all, ring on ring": R3 lifts, the painted rings gather in a column and land
             one by one bottom to top, R5 last, the candles rise; the camera pulls back and turns to the right.
   111.7-112.0 rest pose T112 exactly. */
import { THREE } from '../../../src/core/stage.js';
import { Hanukkiah } from '../../../src/components/hanukkiah.js';
import { ease, prog } from '../../../src/core/motion.js';
import { LINK, TABLE_RIG, mixRig, linkRig, linkRingCentre, R3_HALF } from '../parts/b08_link.js';
import { buildTable, updateTable, TABLE } from '../parts/b09_table.js';
import { buildCollage, updateCollage, hideCollage } from '../parts/b09_collage.js';
import { PAINT, PRESPIN, LEFTOVER, paintState } from '../parts/b09_paint.js';
import { buildTitles, updateTitles } from '../parts/b09_titles.js';
import { STACK, stackState, ringSideX } from '../parts/b09_stack.js';
import { PartShadows } from '../parts/b08_partShadows.js';
import { ArrivalShadow } from '../parts/b09_arrival.js';

const DEG = Math.PI / 180;
const LANDED = LINK.lift[1];
const PAINT_AIM = 0;                            // the camera centres on this ring angle while painting
const PAINT_RIG = {
  yaw: -40, pitch: 4, zoom: 2.1, shiftY: -150,   // from 40 degrees left only the A faces (the star) show
  x: 360 * Math.sin(PAINT_AIM), y: PAINT.centreY, z: 360 * Math.cos(PAINT_AIM),
};
const PAINT_END = { ...PAINT_RIG, yaw: -36, zoom: 2.2 };
const WIDE_RIG = { yaw: 0, pitch: 8, zoom: 0.85, x: 0, y: 430, z: 0 };
const CAMERA = {
  tablePush: [103.55, 104.6], tableZoom: 0.03,
  dive: [104.6, 105.55],
  paint: [105.55, 108.25],
  pull: [108.25, 109.5],
  turn: [108.5, STACK.rest],
  settle: [109.6, STACK.rest],
};
const SHIFT_TRADE = 108.25;                     // the picture shift is traded for whole teeth (after the last column)
const HIDDEN_RINGS = { R1: 0, R2: 0, R4: 0, R5: 0 };

function rigAt(t, T112) {
  if (t >= STACK.rest) return { ...T112.rig };
  const table = linkRig(t);
  table.zoom *= 1 + CAMERA.tableZoom * ease.inOutCubic(prog(t, ...CAMERA.tablePush));
  const dive = mixRig(table, PAINT_RIG, ease.inOutQuart(prog(t, ...CAMERA.dive)));
  const paint = mixRig(dive, PAINT_END, ease.inOutCubic(prog(t, ...CAMERA.paint)));
  const pull = mixRig(paint, WIDE_RIG, ease.inOutCubic(prog(t, ...CAMERA.pull)));
  const settle = mixRig(pull, T112.rig, ease.inOutCubic(prog(t, ...CAMERA.settle)));
  const yaw = PAINT_END.yaw + (T112.rig.yaw - PAINT_END.yaw) * ease.inOutCubic(prog(t, ...CAMERA.turn));
  return t < CAMERA.pull[0] ? paint : { ...settle, yaw };
}

/** The hanukkiah before the stacking: only R3 (white, then painted column by column), the foot hidden inside it. */
function tableState(t, hanukkiah) {
  const centre = linkRingCentre(t);
  hanukkiah.group.position.set(centre[0], centre[1] - R3_HALF, centre[2]);
  const paint = paintState(t);
  const isPainting = t >= PAINT.run[0];
  const prespin = PRESPIN.angle * ease.inOutCubic(prog(t, ...PRESPIN.window));
  hanukkiah.rings.R3.surface.uniforms.motifShift.value = paint.shift;
  return {
    painted: { R1: 0, R2: 0, R3: isPainting ? 1 : 0, R4: 0, R5: 0 }, paintU: { R3: paint.paintU },
    offsetY: { R3: STACK.table }, show: { foot: t >= LANDED ? 1 : 0, R3: 1, ...HIDDEN_RINGS },
    spin: { R3: isPainting ? paint.spin : prespin }, candles: 0, lit: 0,
  };
}

function updateHanukkiah(hanukkiah, shadows, t, T112) {
  const rings = hanukkiah.rings;
  if (t >= STACK.rest) {
    hanukkiah.group.position.set(0, 0, 0);
    rings.R3.surface.uniforms.motifShift.value = 0;
    hanukkiah.update(t, { ...T112.hanukkiah });
    Object.values(rings).forEach((ring) => { ring.group.position.x = 0; });
    shadows.reset();
    return;
  }
  if (t < SHIFT_TRADE) {
    const state = tableState(t, hanukkiah);
    hanukkiah.update(t, state);
    shadows.update(state);
    return;
  }
  hanukkiah.group.position.set(0, 0, 0);
  rings.R3.surface.uniforms.motifShift.value = 0;
  const state = stackState(t, LEFTOVER);
  hanukkiah.update(t, state);
  const sideX = { R1: ringSideX('R1', t), R2: ringSideX('R2', t) };
  ['R1', 'R2'].forEach((id) => { rings[id].group.position.x = sideX[id]; });
  shadows.update({ ...state, sideX });
}

/** Screen pixels of a world point (after the camera is set). */
function project(stage, point) {
  const v = new THREE.Vector3(...point).project(stage.camera);
  return [(v.x + 1) / 2 * stage.width, (1 - v.y) / 2 * stage.height];
}

export async function create(ctx) {
  const beat = ctx.beats.b09;
  const { T112 } = ctx.handoff;
  const { stage } = ctx;
  const scene = new THREE.Scene();
  const hanukkiah = new Hanukkiah(stage);
  const shadows = new PartShadows(hanukkiah);
  const arrival = new ArrivalShadow();
  scene.add(hanukkiah.group, arrival.mesh);
  const table = await buildTable(scene);
  const collage = await buildCollage(scene);
  const titles = await buildTitles(scene);
  if (TABLE_RIG.zoom <= 0) throw new Error('b09: table rig zoom must be positive');

  function update(t) {
    stage.setRig(rigAt(t, T112));
    updateHanukkiah(hanukkiah, shadows, t, T112);
    arrival.update(linkRingCentre(t), t < LANDED);
    const atRest = t >= STACK.rest;
    hideCollage(collage);
    table.markers.forEach((marker) => { marker.group.visible = false; });
    titles.number.group.visible = false;
    titles.word.group.visible = false;
    titles.line.visible = false;
    titles.counter.group.visible = false;
    if (atRest) return;
    updateCollage(collage, t, stage);
    updateTable(table, t, stage, project(stage, paintState(t).tip));
    updateTitles(titles, t, stage);
  }

  return { from: beat.start, to: beat.end, scene, update };
}
