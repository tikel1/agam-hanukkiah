/* Solid shapes in the film's flat look: one colour per face plus ONE step of shade (faces turned away from the key
   light get 14% ink). No lights, no gradients. Use for boxes, drums, candles, the printer, Claude. */
import { THREE } from '../core/stage.js';
import { INK } from '../palette.js';

export const KEY_LIGHT = new THREE.Vector3(-0.55, 0.45, 0.70).normalize();
export const SHADE_STEP = 0.18;

const VERTEX = 'varying vec3 vWorld; void main(){ vWorld = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vWorld, 1.0); }';
const FRAGMENT = `
uniform vec3 color; uniform vec3 shadeInk; uniform vec3 keyLight; uniform float shadeStep; uniform float opacity; uniform vec3 tint; uniform float tintAmount;
varying vec3 vWorld;
void main(){
  vec3 n = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
  vec3 toViewer = vec3(viewMatrix[0][2], viewMatrix[1][2], viewMatrix[2][2]);
  if (dot(n, toViewer) < 0.0) n = -n;
  float facing = dot(n, keyLight);
  vec3 c = mix(color, shadeInk, shadeStep * (1.0 - smoothstep(-0.18, 0.18, facing)));   // soft edge between light and shade
  c = mix(c, vec3(1.0), 0.07 * max(facing, 0.0) * step(0.001, shadeStep));               // lit faces catch a little light
  gl_FragColor = vec4(mix(c, tint, tintAmount), opacity);
}`;

/** Material with the one-step shade. uniforms.color / opacity / tint + tintAmount can be animated. */
export function flatMaterial(color, { shade = SHADE_STEP, opacity = 1, side = THREE.DoubleSide } = {}) {
  return new THREE.ShaderMaterial({
    uniforms: {
      color: { value: new THREE.Color(color) }, shadeInk: { value: new THREE.Color(INK) }, keyLight: { value: KEY_LIGHT.clone() },
      shadeStep: { value: shade }, opacity: { value: opacity }, tint: { value: new THREE.Color(INK) }, tintAmount: { value: 0 },
    },
    vertexShader: VERTEX, fragmentShader: FRAGMENT, side, transparent: opacity < 1, depthWrite: opacity >= 1,
  });
}

/** Box with its base centre at the origin of the mesh (so scale.y grows it upwards). */
export function box(width, height, depth, color, options) {
  const geometry = new THREE.BoxGeometry(width, height, depth);
  geometry.translate(0, height / 2, 0);
  return new THREE.Mesh(geometry, flatMaterial(color, options));
}

/** Upright drum: shaded side wall and a flat top of its own colour. Base at the group's origin. */
export function drum(radius, height, side, top = side, { segments = 64, shade = SHADE_STEP } = {}) {
  const group = new THREE.Group();
  const wall = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, segments, 1, true), flatMaterial(side, { shade }));
  wall.position.y = height / 2;
  const lid = new THREE.Mesh(new THREE.CircleGeometry(radius, segments), new THREE.MeshBasicMaterial({ color: top }));
  lid.rotation.x = -Math.PI / 2;
  lid.position.y = height;
  group.add(wall, lid);
  group.userData = { wall, lid };
  return group;
}
