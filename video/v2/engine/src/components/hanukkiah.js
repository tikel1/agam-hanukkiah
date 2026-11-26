/* Our hanukkiah, as printed: a round foot with the name plaque, a stem, five toothed rings (R1 bottom .. R5 top,
   70 degree folds = depth 0.71), eight blue candles in gold cups on the wide ring R3 and the shamash on R5.
   White (the raw print) or painted; the paint can rise as a wave, or go on column by column.
   y = 0 is the table. Proportions: storyboard/tools/models.py (HANUKKIAH_RINGS).
   Hero shots face it from yaw 30..40 degrees to one side (from the front the two pictures of R3 mix):
   from the LEFT (negative yaw) the Magen David and the dreidel, from the RIGHT (positive yaw) HANUKKAH. */
import { THREE } from '../core/stage.js';
import { ToothedRing } from './pleated.js';
import { Flame } from './flame.js';
import { LineDotTitle } from './lineDotTitle.js';
import { discShadow } from './shadows.js';
import { drum, flatMaterial } from './flatShade.js';
import { createR3Pictures, createStripePaint } from './ringPictures.js';
import { FOUNTAIN as F, GOLD, PRINT_WHITE } from '../palette.js';
import { clamp } from '../core/motion.js';

export const HANUKKIAH_DEPTH = 0.71;
/** id, teeth, radius, height, base (y of the bottom edge), spectrum offset of the paint. */
export const HANUKKIAH_RINGS = Object.freeze([
  { id: 'R1', teeth: 40, radius: 150, height: 62, base: 95, offset: 6 },
  { id: 'R2', teeth: 56, radius: 225, height: 78, base: 157, offset: 2 },
  { id: 'R3', teeth: 80, radius: 360, height: 150, base: 235, offset: 0 },
  { id: 'R4', teeth: 44, radius: 185, height: 64, base: 385, offset: 8 },
  { id: 'R5', teeth: 28, radius: 105, height: 56, base: 449, offset: 4 },
]);
export const HANUKKIAH = Object.freeze({
  top: 505,                                  // top of R5
  foot: { radius: 230, height: 34 }, stem: { radius: 58, top: 95 },
  candleCircle: 296, candles: 8, candleRadius: 15, candleHeight: 150, shamashHeight: 170,
  cup: { radius: 27, height: 24 }, flame: { height: 62, width: 30 },
  footSide: 0xE9E6DC, footTop: 0xF4F1E4, candle: F.blue, candleTop: 0x7E96CF,
  plaque: { words: ['חנוכיית', 'אש', 'ומים'], cap: 15, y: 17 },
});
const H = HANUKKIAH;
const TOTAL = H.top;
const SHADOW_STRENGTH = 0.26;
const CAST = [16, -9];                 // where a shadow falls on a level surface (x, z), away from the key light

/** Seat k (0..7) of the candle circle: angle in radians around y (0 = towards the viewer at yaw 0). */
export const candleAngle = (k) => ((-157.5 + k * 45) * Math.PI) / 180;

export class Hanukkiah {
  /** stage is needed to turn the flames to the camera. plaque = false leaves the name off the foot. */
  constructor(stage, { plaque = true } = {}) {
    this.stage = stage;
    this.group = new THREE.Group();
    this.buildFoot(plaque);
    this.buildRings();
    this.buildCandles();
    this.update(0, {});
  }

  buildFoot(plaque) {
    this.foot = new THREE.Group();
    const base = drum(H.foot.radius, H.foot.height, H.footSide, H.footTop);
    const stem = drum(H.stem.radius, H.stem.top - H.foot.height, H.footSide, H.footTop);
    stem.position.y = H.foot.height;
    this.foot.add(base, stem);
    if (plaque) {
      // the printed name on the front of the foot: blue line-and-dot letters
      this.plaque = new LineDotTitle({ ...H.plaque, ink: F.blue, ends: false });
      this.plaque.update(99, {});
      this.plaque.group.position.set(0, H.plaque.y, H.foot.radius + 1.5);
      this.foot.add(this.plaque.group);
    }
    // soft cast shadow on the table, falling away from the key light (to the right and back): depth without lighting
    this.tableShadow = discShadow(H.foot.radius * 1.5, { strength: 0.2, softness: 0.6 });
    this.tableShadow.scale.set(1.45, 1, 1);
    this.tableShadow.position.set(CAST[0] * 5, 0.6, CAST[1] * 5);
    this.foot.add(this.tableShadow);
    this.group.add(this.foot);
  }

  buildRings() {
    this.rings = {};
    HANUKKIAH_RINGS.forEach((spec, index) => {
      const ring = new ToothedRing({
        radius: spec.radius, height: spec.height, teeth: spec.teeth, depthRatio: HANUKKIAH_DEPTH,
        colorA: () => PRINT_WHITE.a, colorB: () => PRINT_WHITE.b, capColor: PRINT_WHITE.cap,
      });
      ring.surface.setMotifs(spec.id === 'R3' ? createR3Pictures(spec.radius) : createStripePaint(spec.teeth, spec.offset));
      ring.surface.uniforms.shadeStep.value = 0.14;
      const above = HANUKKIAH_RINGS[index + 1];
      // soft flat shadow of the ring above on this ring's top (only where a narrower ring sits on a wider one)
      const shadow = above && above.radius < spec.radius ? discShadow(above.radius * 1.35, { strength: SHADOW_STRENGTH }) : null;
      if (shadow) { shadow.position.set(CAST[0], spec.height / 2 + 0.8, CAST[1]); ring.group.add(shadow); }
      this.group.add(ring.group);
      this.rings[spec.id] = { ...spec, ring, surface: ring.surface, group: ring.group, shadow };
    });
  }

  buildCandles() {
    const cup = () => drum(H.cup.radius, H.cup.height, GOLD, 0xE9C766, { segments: 28 });
    const stick = (height) => drum(H.candleRadius, height, H.candle, H.candleTop, { segments: 20 });
    const seat = (x, y, z, height, parent, seed) => {
      const group = new THREE.Group();
      group.position.set(x, y, z);
      const stickGroup = stick(height);
      stickGroup.position.y = H.cup.height;
      group.add(cup(), stickGroup);
      const flame = new Flame({ seed });
      // each candle throws a small soft shadow on the ring top it stands on
      const shadow = discShadow(H.cup.radius * 1.7, { strength: 0.24, softness: 0.55 });
      shadow.scale.set(1.5, 1, 1);
      shadow.position.set(CAST[0], 0.9, CAST[1]);
      group.add(shadow);
      parent.add(group);
      this.group.add(flame.group);
      return { group, stick: stickGroup, flame, height, x, z, parent };
    };
    const r3 = this.rings.R3, r5 = this.rings.R5;
    // candles ride on their ring's group (centre of the ring = group origin), so offsets and drops carry them along
    this.shamash = seat(0, r5.height / 2, 0, H.shamashHeight, r5.group, 3);
    this.candles = Array.from({ length: H.candles }, (_, k) => {
      const phi = candleAngle(k);
      return seat(H.candleCircle * Math.sin(phi), r3.height / 2, H.candleCircle * Math.cos(phi), H.candleHeight, r3.group, 20 + k * 5);
    });
  }

  /** World-local (in this.group) position of the wick of a candle: k = 0..7, or 'shamash'. For flames that fly in. */
  wick(k) {
    const item = k === 'shamash' ? this.shamash : this.candles[k];
    const ring = k === 'shamash' ? this.rings.R5 : this.rings.R3;
    return new THREE.Vector3(item.x, ring.group.position.y + ring.height / 2 + H.cup.height + item.height * item.stick.scale.y, item.z);
  }

  /** Everything from the options (nothing is remembered between calls):
      painted   0..1 wave of paint rising from the foot (1 = all painted), or { R1: 0..1, ... } per ring
      paintU    { R3: 0..1 } how far round a ring the paint has got, column by column (default 1)
      offsetY   { foot, R1..R5 }: lifts / drops per part (drops, exploded view)
      show      { foot, R1..R5 }: 0..1 scale of a part (0 hides it)
      spin      { R1..R5 } radians: turns a ring about its axis
      candles   0..1 height of all candles (0 = no candles, no cups), or an array of 9: [shamash, c0..c7]
      lit       number of burning flames 0..9, shamash first, then candles 0..7; the fraction grows the next one.
                Or an array of 9 sizes (0..1+) [shamash, c0..c7].
      flameScale  size of the flames (1 = as in the model)
      shade     0..1 strength of the one shade step (default 1) */
  update(t, { painted = 1, paintU = {}, offsetY = {}, show = {}, spin = {}, candles = 1, lit = 0, flameScale = 1, shade = 1 } = {}) {
    const footShow = show.foot === undefined ? 1 : show.foot;
    this.foot.visible = footShow > 0.002;
    this.foot.scale.setScalar(Math.max(0.001, footShow));
    this.foot.position.y = offsetY.foot || 0;
    Object.values(this.rings).forEach((item) => {
      const amount = typeof painted === 'number' ? clamp((painted * TOTAL * 1.02 - item.base) / item.height) : (painted[item.id] === undefined ? 1 : painted[item.id]);
      const scale = show[item.id] === undefined ? 1 : show[item.id];
      item.surface.uniforms.motifAmount.value = amount;
      item.surface.uniforms.paintU.value = paintU[item.id] === undefined ? 1 : paintU[item.id];
      item.surface.uniforms.shadeStep.value = 0.14 * shade;
      item.group.visible = scale > 0.002;
      item.group.scale.setScalar(Math.max(0.001, scale));
      item.group.position.y = item.base + item.height / 2 + (offsetY[item.id] || 0);
      item.group.rotation.y = spin[item.id] || 0;
      if (item.shadow) {
        const aboveId = `R${Number(item.id[1]) + 1}`;
        const gap = Math.abs((offsetY[aboveId] || 0) - (offsetY[item.id] || 0));
        const aboveShow = show[aboveId] === undefined ? 1 : show[aboveId];
        item.shadow.material.uniforms.strength.value = SHADOW_STRENGTH * clamp(1 - gap / 160) * clamp(aboveShow);
      }
    });
    const seats = [this.shamash, ...this.candles];
    seats.forEach((item, index) => {
      const grow = Array.isArray(candles) ? candles[index] : candles;
      const size = Array.isArray(lit) ? lit[index] : clamp(lit - index);
      item.group.visible = grow > 0.01;
      item.group.scale.setScalar(Math.max(0.001, clamp(grow * 3)));
      item.stick.scale.y = Math.max(0.001, grow);
      const wick = this.wick(index === 0 ? 'shamash' : index - 1);
      item.flame.group.position.copy(wick);
      item.flame.group.position.y -= 3;
      item.flame.update(t, { height: H.flame.height * size * flameScale, width: H.flame.width * Math.min(1, size * 1.3) * flameScale, energy: 0.9 });
      item.flame.group.visible = item.flame.group.visible && item.group.visible;
      // face the camera: undo the parents' rotation (the hanukkiah group may be turned by the film)
      this.stage.billboard(item.flame.group);
      if (this.group.parent) {
        const parentQuaternion = new THREE.Quaternion();
        this.group.getWorldQuaternion(parentQuaternion);
        item.flame.group.quaternion.premultiply(parentQuaternion.invert());
      }
    });
  }
}

/** A flat silhouette of the hanukkiah's ring stack in one colour (for ghosts). Not used by the hanukkiah itself. */
export function ringSilhouette(specs, color, opacity = 1) {
  const group = new THREE.Group();
  specs.forEach((spec) => {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(spec.radius * 1.03, spec.radius * 1.03, spec.height, 64), flatMaterial(color, { shade: 0, opacity }));
    mesh.position.y = spec.base + spec.height / 2;
    group.add(mesh);
  });
  return group;
}
