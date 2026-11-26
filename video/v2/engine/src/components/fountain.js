/* The "Fire and Water" fountain as five stacked toothed rings (R1 bottom .. R5 top), a pool with ripples and
   water jets. Proportions follow our hanukkiah model (model drums, mm x 4): they are ours, not a surveyed
   silhouette of the real fountain. The film moves the rings; this file only builds them. */
import { THREE } from '../core/stage.js';
import { ToothedRing } from './pleated.js';
import { FOUNTAIN as F, SPECTRUM, WHITE } from '../palette.js';
import { drift, clamp } from '../core/motion.js';

const cycle = (list, runs) => (i, n) => list[Math.floor((i / n) * list.length * runs) % list.length];

/** radius = valley radius, height, teeth; colorA / colorB = (toothIndex, teeth) -> hex. */
export const RING_SPECS = Object.freeze([
  { id: 'R1', radius: 120, height: 72, teeth: 24, colorA: cycle([F.brick, F.coral], 3), colorB: () => WHITE },
  { id: 'R2', radius: 224, height: 140, teeth: 44, colorA: cycle([F.orange, F.yellow, F.orange, F.coral], 2), colorB: cycle([F.blue, F.periwinkle, F.light_blue, F.periwinkle], 2) },
  { id: 'R3', radius: 362, height: 180, teeth: 72, colorA: cycle(SPECTRUM, 1), colorB: (i) => (i % 6 === 5 ? F.yellow : WHITE) },
  { id: 'R4', radius: 138, height: 88, teeth: 28, colorA: cycle([F.teal, F.green, F.mint], 3), colorB: (i) => (i % 2 ? WHITE : F.yellow) },
  { id: 'R5', radius: 74, height: 84, teeth: 16, colorA: cycle([F.coral, F.rose], 4), colorB: cycle([F.periwinkle, F.lilac], 4) },
]);

const TOTAL_HEIGHT = RING_SPECS.reduce((sum, spec) => sum + spec.height, 0);
/** Ring id -> { bottom, centre, top } in world y, the stack centred on y = 0. */
export const RING_LEVELS = Object.freeze(RING_SPECS.reduce((levels, spec) => {
  const bottom = levels.next;
  return { ...levels, next: bottom + spec.height, [spec.id]: { bottom, centre: bottom + spec.height / 2, top: bottom + spec.height } };
}, { next: -TOTAL_HEIGHT / 2 }));
export const FOUNTAIN_TOP = TOTAL_HEIGHT / 2;
export const FOUNTAIN_BOTTOM = -TOTAL_HEIGHT / 2;
export const ringSpec = (id) => {
  const spec = RING_SPECS.find((s) => s.id === id);
  if (!spec) throw new Error(`fountain: no ring "${id}"`);
  return spec;
};

const POOL_RADIUS = 600;
const RIPPLES = 3;
const RIPPLE_SECONDS = 3.2;
const JETS = 14;
const JET_RADIUS = 470;
const JET_WIDTH = 9;
const JET_DOT = 13;
const JET_COLORS = [F.blue, F.periwinkle, WHITE, F.light_blue];

export class Fountain {
  /** omit: ring ids the film builds itself (for example R3, which the polymorph sheet turns into). */
  constructor({ omit = [], poolRadius = POOL_RADIUS, jetRadius = JET_RADIUS } = {}) {
    this.poolRadius = poolRadius;
    this.jetRadius = jetRadius;
    this.group = new THREE.Group();
    this.rings = {};
    RING_SPECS.filter((spec) => !omit.includes(spec.id)).forEach((spec) => {
      const ring = new ToothedRing({ ...spec, colorA: (i) => spec.colorA(i, spec.teeth), colorB: (i) => spec.colorB(i, spec.teeth) });
      ring.group.position.y = RING_LEVELS[spec.id].centre;
      this.group.add(ring.group);
      this.rings[spec.id] = ring;
    });
    this.buildPool();
    this.buildJets();
  }

  buildPool() {
    this.pool = new THREE.Group();
    this.pool.position.y = FOUNTAIN_BOTTOM;
    this.pool.rotation.x = -Math.PI / 2;
    this.pool.add(new THREE.Mesh(new THREE.CircleGeometry(this.poolRadius, 96), new THREE.MeshBasicMaterial({ color: F.light_blue })));
    this.ripples = Array.from({ length: RIPPLES }, () => {
      const mesh = new THREE.Mesh(new THREE.RingGeometry(0.97, 1, 96), new THREE.MeshBasicMaterial({ color: WHITE, side: THREE.DoubleSide }));
      mesh.position.z = 1;
      this.pool.add(mesh);
      return mesh;
    });
    this.group.add(this.pool);
  }

  buildJets() {
    this.jets = Array.from({ length: JETS }, (_, i) => {
      const angle = ((i + 0.5) / JETS) * Math.PI * 2;
      const color = JET_COLORS[i % JET_COLORS.length];
      const column = new THREE.Mesh(new THREE.CylinderGeometry(JET_WIDTH / 2, JET_WIDTH / 2, 1, 12), new THREE.MeshBasicMaterial({ color }));
      const dot = new THREE.Mesh(new THREE.SphereGeometry(JET_DOT, 24, 16), new THREE.MeshBasicMaterial({ color }));
      const x = Math.sin(angle) * this.jetRadius, z = Math.cos(angle) * this.jetRadius;
      column.position.set(x, 0, z);
      dot.position.set(x, 0, z);
      this.group.add(column, dot);
      return { column, dot, seed: i * 7 + 3 };
    });
  }

  /** appear = 0..1+ scale of the pool (give it a spring). Ripples loop with t. */
  updatePool(t, appear) {
    this.pool.visible = appear > 0.001;
    this.pool.scale.setScalar(Math.max(appear, 0.001));
    this.ripples.forEach((ripple, i) => {
      const k = ((t / RIPPLE_SECONDS + i / RIPPLES) % 1 + 1) % 1;
      ripple.scale.setScalar(this.poolRadius * (0.55 + 0.42 * k));
      ripple.visible = k > 0.02 && k < 0.98;
    });
  }

  /** rise(i) = 0..1 how far jet i is up (drive it with springs); the jets then bob on their own. */
  updateJets(t, rise, maxHeight = 250) {
    this.jets.forEach((jet, i) => {
      const up = rise(i);
      const height = Math.max(0, up) * maxHeight * (0.62 + 0.38 * (0.5 + 0.5 * drift(t, jet.seed, 0.55)));
      const visible = height > 1;
      jet.column.visible = visible;
      jet.dot.visible = visible;
      jet.column.scale.y = Math.max(height, 0.001);
      jet.column.position.y = FOUNTAIN_BOTTOM + height / 2;
      jet.dot.position.y = FOUNTAIN_BOTTOM + height;
      jet.dot.scale.setScalar(clamp(up * 1.4));
    });
  }
}

/** A hanukkiah candle: a small pleated drum that grows from its base, with room for a flame on top. */
export class Candle {
  constructor({ radius = 15, teeth = 8, colorA, colorB = () => WHITE, capColor = WHITE }) {
    this.length = 2 * Math.PI * radius;
    this.ring = new ToothedRing({ radius, height: 1, teeth, colorA, colorB, capColor });
    this.group = this.ring.group;
  }

  /** height in world units; the base stays at the group's origin. squash 0..1 widens it a little. */
  update(height, squash = 0) {
    this.group.visible = height > 0.5;
    this.ring.surface.update({ length: this.length, height, bend: 1, top: () => height, bottom: () => 0 });
    this.group.scale.set(1 + 0.5 * squash, 1, 1 + 0.5 * squash);
  }
}
