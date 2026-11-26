/* Flat flame: three nested teardrops (orange, yellow, cream), no outline, no glow. It sways from a seeded drift,
   licks travel up its body, and it can lean (drag while it flies), squash (anticipation) and grow.
   Lives in the XY plane of its group, base at the origin; face it to the camera with stage.billboard(group). */
import { THREE } from '../core/stage.js';
import { FLAME } from '../palette.js';
import { drift } from '../core/motion.js';

const ROWS = 28;
const BELLY_AT = 0.3;                  // height (0..1) of the widest point
const LAYERS = [
  { color: FLAME.outer, width: 1, height: 1, z: 0 },
  { color: FLAME.inner, width: 0.58, height: 0.62, z: 1 },
  { color: FLAME.core, width: 0.26, height: 0.3, z: 2 },
];
const SWAY_HZ = 0.9;
const LICK_HZ = 2.2;

/** Half width (0..1) of a teardrop at height v (0 base .. 1 tip). */
function teardrop(v) {
  if (v < BELLY_AT) return Math.sqrt(Math.max(0, 1 - Math.pow((BELLY_AT - v) / BELLY_AT, 2)));
  return 1 - Math.pow((v - BELLY_AT) / (1 - BELLY_AT), 1.55);
}

export class Flame {
  constructor({ seed = 0 } = {}) {
    this.seed = seed;
    this.group = new THREE.Group();
    this.layers = LAYERS.map((layer) => {
      const positions = new Float32Array(ROWS * 6 * 3);
      const geometry = new THREE.BufferGeometry();
      const attribute = new THREE.BufferAttribute(positions, 3).setUsage(THREE.DynamicDrawUsage);
      geometry.setAttribute('position', attribute);
      const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color: layer.color, side: THREE.DoubleSide }));
      mesh.frustumCulled = false;
      mesh.position.z = layer.z;
      this.group.add(mesh);
      return { ...layer, positions, attribute };
    });
  }

  /** t = absolute time (drives sway). height / width in world units. lean = sideways pull of the tip in widths
      (negative = left). squash > 0 = shorter and wider. energy = how lively the sway is (0..2). */
  update(t, { height, width, lean = 0, squash = 0, energy = 1 }) {
    this.group.visible = height > 0.5 && width > 0.5;
    if (!this.group.visible) return;
    const h = height * (1 - 0.45 * squash), w = width * (1 + 0.6 * squash);
    const sway = drift(t, this.seed, SWAY_HZ) * 0.22 * energy + lean;
    this.layers.forEach((layer, layerIndex) => {
      const lh = h * layer.height, lw = (w / 2) * layer.width;
      const centre = (v) => {
        const lick = Math.sin(v * 5.5 - t * LICK_HZ * 6.283 + this.seed + layerIndex * 0.7) * 0.07 * energy * v;
        return (sway * v * v + lick) * w;
      };
      const pos = layer.positions;
      let k = 0;
      const put = (x, y) => { pos[k++] = x; pos[k++] = y; pos[k++] = 0; };
      for (let row = 0; row < ROWS; row++) {
        const v0 = row / ROWS, v1 = (row + 1) / ROWS;
        const c0 = centre(v0), c1 = centre(v1), r0 = teardrop(v0) * lw, r1 = teardrop(v1) * lw;
        put(c0 - r0, v0 * lh); put(c0 + r0, v0 * lh); put(c1 + r1, v1 * lh);
        put(c0 - r0, v0 * lh); put(c1 + r1, v1 * lh); put(c1 - r1, v1 * lh);
      }
      layer.attribute.needsUpdate = true;
    });
  }
}
