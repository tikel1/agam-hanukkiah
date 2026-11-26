/* The "Fire and Water" fountain as it stood in 1986, for v2: five toothed rings on a central column, with air
   between them, in a round pool. The middle three rings turned. y = 0 is the water line.
   Proportions: storyboard/tools/models.py (FOUNTAIN_RINGS), a drawing of the idea and not a survey.
   Water jets and the flame are the film's (they change per beat); this file builds rings, column and pool. */
import { THREE } from '../core/stage.js';
import { ToothedRing } from './pleated.js';
import { drum, flatMaterial } from './flatShade.js';
import { discShadow } from './shadows.js';
import { FOUNTAIN as F, SPECTRUM, PAPER } from '../palette.js';
import { clamp } from '../core/motion.js';

export const FOUNTAIN86_DEPTH = 0.6;
/** teeth, radius, height, base, spectrum offset, turns (only the middle three turned). */
export const FOUNTAIN86_RINGS = Object.freeze([
  { teeth: 40, radius: 210, height: 92, base: 70, offset: 9, turns: false },
  { teeth: 52, radius: 290, height: 104, base: 196, offset: 3, turns: true },
  { teeth: 72, radius: 410, height: 138, base: 336, offset: 0, turns: true },
  { teeth: 52, radius: 310, height: 100, base: 510, offset: 5, turns: true },
  { teeth: 36, radius: 200, height: 86, base: 646, offset: 7, turns: false },
]);
export const FOUNTAIN86 = Object.freeze({ top: 732, poolRadius: 640, columnRadius: 40, flameBase: 744 });
const COLUMN = { side: 0xC9CED0, top: 0xDADDDC };
const RIPPLE_RADII = [560, 470, 380, 300];
const RIPPLE_SECONDS = 3.2;

const spectrumFrom = (offset, teeth) => (i) => SPECTRUM[(offset + Math.floor((i * SPECTRUM.length) / teeth)) % SPECTRUM.length];
/** Face colours of ring k, as functions of the tooth index: exported so a sheet can turn into a ring (beat 2 -> 3). */
export const fountain86Colors = (k) => {
  const spec = FOUNTAIN86_RINGS[k];
  return { colorA: spectrumFrom(spec.offset, spec.teeth), colorB: k % 2 === 0 ? () => F.white : spectrumFrom(spec.offset + 6, spec.teeth) };
};

export class Fountain86 {
  /** silhouette = one flat colour for the whole fountain (the ghost behind the hanukkiah in beat 7), or null. */
  constructor({ silhouette = null } = {}) {
    this.group = new THREE.Group();
    this.rings = FOUNTAIN86_RINGS.map((spec, k) => {
      const colors = silhouette === null ? fountain86Colors(k) : { colorA: () => silhouette, colorB: () => silhouette };
      const ring = new ToothedRing({ ...spec, ...colors, capColor: silhouette === null ? F.white : silhouette, depthRatio: FOUNTAIN86_DEPTH });
      ring.surface.uniforms.shadeStep.value = silhouette === null ? 0.14 : 0;
      // a ring that carries a narrower ring above it gets that ring's soft shadow on its top
      const above = FOUNTAIN86_RINGS[k + 1];
      if (silhouette === null && above && above.radius < spec.radius) {
        const cast = discShadow(above.radius * 1.12, { strength: 0.2, softness: 0.4 });
        cast.position.set(18, spec.height / 2 + 0.8, -10);
        ring.group.add(cast);
      }
      this.group.add(ring.group);
      return { ...spec, ring, surface: ring.surface, group: ring.group };
    });
    // column pieces: pool -> ring 0, then between the rings, then a short tip
    const tops = [0, ...FOUNTAIN86_RINGS.map((spec) => spec.base + spec.height)];
    const bottoms = [...FOUNTAIN86_RINGS.map((spec) => spec.base), FOUNTAIN86.top + 12];
    this.columns = tops.map((y0, index) => {
      const piece = silhouette === null
        ? drum(index === 5 ? 30 : FOUNTAIN86.columnRadius, bottoms[index] - y0, COLUMN.side, COLUMN.top, { segments: 24 })
        : new THREE.Mesh(new THREE.CylinderGeometry(40, 40, bottoms[index] - y0, 24).translate(0, (bottoms[index] - y0) / 2, 0), flatMaterial(silhouette, { shade: 0 }));
      piece.position.y = y0;
      this.group.add(piece);
      return piece;
    });
    this.pool = new THREE.Group();
    this.pool.rotation.x = -Math.PI / 2;
    if (silhouette === null) {
      const water = new THREE.Color(F.light_blue).lerp(new THREE.Color(PAPER), 0.15);
      this.pool.add(new THREE.Mesh(new THREE.CircleGeometry(FOUNTAIN86.poolRadius, 96), new THREE.MeshBasicMaterial({ color: water })));
      this.ripples = RIPPLE_RADII.map((radius, i) => {
        const mesh = new THREE.Mesh(new THREE.RingGeometry(0.985, 1, 96), new THREE.MeshBasicMaterial({ color: i % 2 ? F.light_blue : F.white, side: THREE.DoubleSide }));
        mesh.position.z = 1;
        this.pool.add(mesh);
        return { mesh, radius };
      });
      this.shadow = discShadow(330, { strength: 0.22 });
      this.shadow.position.set(14, 2.5, 8);
      this.group.add(this.shadow);
    } else this.ripples = [];
    this.group.add(this.pool);
    this.update(0, {});
  }

  /** spin     radians: the middle three rings turn, neighbours in opposite directions
      drop     { 0..4: dy } lifts a ring (a ring that is still falling); its column piece hides until it lands
      show     { 0..4: 0..1 } scale of a ring (0 = not there yet)
      pool     0..1+ scale of the pool (give it a spring)
      column   0..1 how much of the column shows (default 1) */
  update(t, { spin = 0, drop = {}, show = {}, pool = 1, column = 1 } = {}) {
    this.rings.forEach((item, k) => {
      const scale = show[k] === undefined ? 1 : show[k];
      item.group.visible = scale > 0.002;
      item.group.scale.setScalar(Math.max(0.001, scale));
      item.group.position.y = item.base + item.height / 2 + (drop[k] || 0);
      item.group.rotation.y = item.turns ? spin * (k % 2 ? 1 : -1) : 0;
    });
    const there = (k) => k < 0 || k > 4 || ((show[k] === undefined ? 1 : show[k]) > 0.5 && Math.abs(drop[k] || 0) < 1);
    this.columns.forEach((piece, index) => {
      // piece index sits under ring `index` (piece 5 = the tip above ring 4)
      piece.visible = column > 0.01 && (index === 5 ? there(4) : there(index) && (index === 0 || there(index - 1)));
      piece.scale.set(1, Math.max(0.001, column), 1);
    });
    this.pool.visible = pool > 0.002;
    this.pool.scale.setScalar(Math.max(0.001, pool));
    this.ripples.forEach(({ mesh, radius }, i) => {
      const k = ((t / RIPPLE_SECONDS + i / RIPPLE_RADII.length) % 1 + 1) % 1;
      mesh.scale.setScalar(radius * (0.94 + 0.08 * k));
    });
    if (this.shadow) { this.shadow.visible = this.pool.visible && there(0); this.shadow.scale.setScalar(clamp(pool)); }
  }
}
