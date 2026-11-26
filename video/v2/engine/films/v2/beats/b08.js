/* Beat 8 (97 - 103): printing.
   97.0      rest pose T97: the painted hanukkiah, exactly as beat 7 leaves it.
   97.0-98.9 "and now, from the computer to the real world": the paint drains off top-down (the raw white print),
             the candles sink, the parts come apart upwards along an axis of dots (exploded view).
   98.95-100.65 the parts drift up and away while the camera glides down to the printer below (easing back a
             little mid-glide): one calm move.
   100.4-102.3 "we printed all the parts on a 3D printer": the head glides in two slow passes over the front of the
             ring, the bed slides gently, R3 rises steadily in white with layer lines; the spool turns slowly.
   102.4-103.5 link: the bed brings the ring forward, it rises towards the camera and the camera rides with it to
             the painting table (beat 9 takes the ring over at the same place; this pass lasts until the printer
             has left the frame). */
import { THREE } from '../../../src/core/stage.js';
import { Hanukkiah } from '../../../src/components/hanukkiah.js';
import { PartShadows } from '../parts/b08_partShadows.js';
import { ease, prog, bump } from '../../../src/core/motion.js';
import { EXPLODE, buildAxis, updateAxis, hanukkiahState } from '../parts/b08_explode.js';
import { Printer } from '../parts/b08_printer.js';
import { PrintRing } from '../parts/b08_printRing.js';
import { PRINT, printState } from '../parts/b08_print.js';
import { PRINTER, PRINT_RIG, LINK, mixRig, linkRig, linkRingCentre, R3_HALF } from '../parts/b08_link.js';

const PASS_END = 103.5;                       // the printer has left the frame; beat 9 holds the ring from 103.0
const EXPLODE_RIG = { yaw: -14, pitch: 10, zoom: 0.8, x: 0, y: 520, z: 0 };
const CAMERA = {
  explode: [97.0, 99.2],                      // from rest: slow start, the view opens up as the parts separate
  drop: [98.95, 100.65],                      // down to the printer: one long, even glide (no quart whip)
  dropPullBack: 0.25,                         // the camera eases back mid-glide, so the frame moves slower
  push: [100.65, 102.4],                       // slow push-in while it prints
};
const DROP_RIG = { ...PRINT_RIG, yaw: -28, zoom: 0.76 };
const PRINTER_SHOWS = 99.2;

function rigAt(t, T97) {
  if (t <= T97.time) return { ...T97.rig };
  if (t >= LINK.camera[0]) return linkRig(t);
  const open = mixRig(T97.rig, EXPLODE_RIG, ease.inOutCubic(prog(t, ...CAMERA.explode)));
  const glide = (1 - Math.cos(Math.PI * prog(t, ...CAMERA.drop))) / 2;
  const drop = mixRig(open, DROP_RIG, glide);
  drop.zoom *= 1 - CAMERA.dropPullBack * bump(t, ...CAMERA.drop);
  return mixRig(drop, PRINT_RIG, ease.inOutCubic(prog(t, ...CAMERA.push)));
}

/** Where the printed ring is: on the bed while printing, then in flight to the table. */
function ringCentre(t, bedZ) {
  if (t >= LINK.lift[0]) return linkRingCentre(t);
  const [x, y, z] = PRINTER.origin;
  return [x, y + R3_HALF, z + bedZ];
}

export async function create(ctx) {
  const beat = ctx.beats.b08;
  const { T97 } = ctx.handoff;
  const { stage } = ctx;
  const scene = new THREE.Scene();
  const hanukkiah = new Hanukkiah(stage);
  const partShadows = new PartShadows(hanukkiah);
  const axis = buildAxis();
  const printer = new Printer();
  printer.group.position.set(...PRINTER.origin);
  const ring = new PrintRing();
  scene.add(hanukkiah.group, axis.group, printer.group, ring.group);

  function update(t) {
    stage.setRig(rigAt(t, T97));
    const atRest = t <= T97.time;
    hanukkiah.group.visible = t < EXPLODE.gone;
    if (atRest) {
      hanukkiah.update(t, { ...T97.hanukkiah });
      partShadows.reset();
    } else if (hanukkiah.group.visible) {
      const state = hanukkiahState(t);
      hanukkiah.update(t, state);
      partShadows.update(state);
    }
    updateAxis(axis, t, stage);

    printer.group.visible = t >= PRINTER_SHOWS;
    ring.group.visible = false;
    if (!printer.group.visible) return;
    const state = printState(t);
    const centre = ringCentre(t, state.bedZ);
    printer.update({ ...state, ringLift: Math.max(0, centre[1] - (PRINTER.origin[1] + R3_HALF)) });
    ring.update({
      centre: [centre[0], centre[1], centre[2]],
      height: state.height,
      lines: 1 - ease.inOutCubic(prog(t, ...LINK.layersOut)),
    });
    ring.group.visible = t >= PRINT.run[0] - 0.05;
  }

  return { from: beat.start, to: Math.max(beat.end, PASS_END), scene, update };
}
