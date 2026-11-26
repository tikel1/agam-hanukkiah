/* Soft shadows: flat, blurred patches of one dark tint. They give depth (a ring resting on a ring, a card floating
   over the stripes) while everything stays unlit and two-dimensional in look. No lights are involved: a shadow is
   just a shape the film places and scales. */
import { THREE } from '../core/stage.js';
import { NAVY } from '../palette.js';

const VERTEX = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }';
const FRAGMENT = `
uniform vec3 tint; uniform float strength; uniform float softness; uniform vec2 size; uniform float round;
varying vec2 vUv;
void main(){
  vec2 p = (vUv - 0.5) * size;
  float edge;
  if (round > 0.5) {
    edge = 1.0 - smoothstep(1.0 - softness, 1.0, length(p) / (size.x * 0.5));
  } else {
    vec2 d = abs(p) - (size * 0.5 - softness);
    float distance = length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
    edge = 1.0 - smoothstep(0.0, softness, distance);
  }
  gl_FragColor = vec4(tint, strength * edge);
}`;

function shadowMesh({ width, height, isRound, strength, softness, tint }) {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      tint: { value: new THREE.Color(tint) }, strength: { value: strength }, softness: { value: softness },
      size: { value: new THREE.Vector2(width, height) }, round: { value: isRound ? 1 : 0 },
    },
    vertexShader: VERTEX, fragmentShader: FRAGMENT, transparent: true, depthWrite: false, side: THREE.DoubleSide,
  });
  return new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
}

/** Round shadow lying flat (on a ring's top, on the water). softness 0..1 = blurred share of the radius. */
export function discShadow(radius, { strength = 0.3, softness = 0.45, tint = NAVY } = {}) {
  const mesh = shadowMesh({ width: radius * 2, height: radius * 2, isRound: true, strength, softness, tint });
  mesh.rotation.x = -Math.PI / 2;
  return mesh;
}

/** Rectangular shadow for a card facing the camera. softness = blur width in world units. */
export function cardShadow(width, height, { strength = 0.28, softness = 60, tint = NAVY } = {}) {
  return shadowMesh({ width: width + softness, height: height + softness, isRound: false, strength, softness, tint });
}

/** Hard flat shadow that a standing wall (a pleated sheet) throws on the floor: one flat colour, crisp edge.
    update(points, y, offset): points = the wall's footprint [[x, z], ...], offset = [dx, dz] the shadow reaches. */
export class WallShadow {
  constructor({ segments, color }) {
    this.segments = segments;
    this.positions = new Float32Array(segments * 6 * 3);
    const geometry = new THREE.BufferGeometry();
    this.attribute = new THREE.BufferAttribute(this.positions, 3).setUsage(THREE.DynamicDrawUsage);
    geometry.setAttribute('position', this.attribute);
    this.mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide }));
    this.mesh.frustumCulled = false;
  }

  update(points, y, offset) {
    if (points.length !== this.segments + 1) throw new Error(`WallShadow: expected ${this.segments + 1} points, got ${points.length}`);
    const pos = this.positions;
    let k = 0;
    const put = (x, z) => { pos[k++] = x; pos[k++] = y; pos[k++] = z; };
    for (let i = 0; i < this.segments; i++) {
      const [ax, az] = points[i], [bx, bz] = points[i + 1];
      put(ax, az); put(bx, bz); put(bx + offset[0], bz + offset[1]);
      put(ax, az); put(bx + offset[0], bz + offset[1]); put(ax + offset[0], az + offset[1]);
    }
    this.attribute.needsUpdate = true;
  }
}
