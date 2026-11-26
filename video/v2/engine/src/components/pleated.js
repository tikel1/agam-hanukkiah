/* Pleated surface: the Agam polymorph. A sheet folded into V pleats; every pleat has an A face (seen from the left)
   and a B face (seen from the right), each with its own colour, so the picture changes as the camera turns.
   bend 0 = flat sheet, bend 1 = the sheet closed into a toothed ring (the drums of the fountain). The B faces can
   carry a photo (posterised to three flat inks), and a disc can cut the A stripes. Unlit: colours are exact. */
import { THREE } from '../core/stage.js';
import { hexToRgb, WHITE, PAPER, NAVY, INK, FOUNTAIN } from '../palette.js';

const VERTS_PER_PLEAT = 21;            // A face 6 + B face 6 + cap tip 3 + cap inner quad 6
const DEFAULT_DEPTH_RATIO = 0.65;      // ridge depth / pitch: beyond about 38 degrees only one face set shows
const CAP_INNER_RATIO = 0.82;          // how far the top cap reaches towards the centre of the ring
const KIND_A = 0, KIND_B = 1, KIND_CAP = 2;
// per vertex of a pleat: +1 valley, -1 ridge (A face, B face), 0 on the cap
const CREASE_PATTERN = [1, -1, -1, 1, -1, 1, -1, 1, 1, -1, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0];

const VERTEX = `
attribute vec3 colorB;
attribute vec3 colorDisc;
attribute vec2 plane;
attribute float kind;
attribute float crease;
varying float vCrease;
varying vec3 vColor; varying vec3 vColorB; varying vec3 vColorDisc; varying vec2 vPlane; varying float vKind;
varying vec3 vWorld;
void main(){
  vColor = color; vColorB = colorB; vColorDisc = colorDisc; vPlane = plane; vKind = kind;
  vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
  vCrease = crease;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;
const FRAGMENT = `
uniform float colorMix; uniform float photoAmount; uniform sampler2D photo;
uniform vec2 uvScale; uniform vec2 uvOffset; uniform vec2 planeSize;
uniform vec3 discCentreRadius; uniform vec3 inkDark; uniform vec3 inkMid; uniform vec3 inkLight;
uniform vec2 levels; uniform float opacity; uniform vec3 fadeTo; uniform float discAspect; uniform float photoSoftness;
uniform int photoMode; uniform vec3 photoGrade;
uniform float shadeTop; uniform float shadeBand;
uniform sampler2D motifA; uniform sampler2D motifB; uniform float motifAmount; uniform float motifShift;
uniform float paintU; uniform float shadeStep; uniform vec3 shadeInk; uniform vec3 keyLight; uniform float lightPlay;
varying vec3 vWorld; varying float vCrease;
varying vec3 vColor; varying vec3 vColorB; varying vec3 vColorDisc; varying vec2 vPlane; varying float vKind;
void main(){
  vec3 c = mix(vColor, vColorB, colorMix);
  if (vKind < 0.5 && discCentreRadius.z > 0.0) {           // A faces: the disc swaps in its own colours
    float d = length((vPlane * planeSize - discCentreRadius.xy) * vec2(discAspect, 1.0));
    c = mix(c, vColorDisc, (1.0 - colorMix) * (1.0 - smoothstep(discCentreRadius.z - 1.0, discCentreRadius.z + 1.0, d)));
  }
  if (vKind > 0.5 && vKind < 1.5 && photoAmount > 0.0) {   // B faces: photo in three flat inks
    vec2 uv = vPlane * uvScale + uvOffset + 0.5;
    vec3 p;
    if (photoMode == 0) {                                  // natural: the photo itself, lightly graded
      p = texture2D(photo, uv).rgb;
      float grey = dot(p, vec3(0.299, 0.587, 0.114));
      p = mix(vec3(grey), p, photoGrade.x);                // saturation
      p = (p - 0.5) * photoGrade.y + 0.5 + photoGrade.z;   // contrast, lift
      p = clamp(p, 0.0, 1.0);
    } else {
      float l = dot(texture2D(photo, uv, photoMode == 2 ? photoSoftness : 0.0).rgb, vec3(0.299, 0.587, 0.114));
      l = smoothstep(levels.x, levels.y, l);
      if (photoMode == 1) p = l < 0.5 ? mix(inkDark, inkMid, l * 2.0) : mix(inkMid, inkLight, l * 2.0 - 1.0);   // smooth duotone
      else p = l < 0.34 ? inkDark : (l < 0.66 ? inkMid : inkLight);                                          // three flat inks
    }
    c = mix(c, p, photoAmount);
  }
  if (motifAmount > 0.0 && vKind < 1.5) {                  // painted picture, rising from the bottom edge
    vec2 muv = vec2(fract(vPlane.x + 0.5 + motifShift), vPlane.y + 0.5);
    vec4 m = vKind < 0.5 ? texture2D(motifA, muv) : texture2D(motifB, muv);
    c = mix(c, m.rgb, m.a * step(muv.y, motifAmount * 1.02) * step(vPlane.x + 0.5, paintU));
  }
  if (shadeStep > 0.0) {
    // Light and shadow that stay flat: faces turned from the key light take a soft step of ink (it shifts as the
    // sheet or the camera turns), the valleys of the folds are a little darker (the planes shade each other), the
    // ridges catch a thin rim of light. All of it scales with how deep the fold really is: a flat sheet stays flat.
    vec3 n = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
    vec3 toViewer = vec3(viewMatrix[0][2], viewMatrix[1][2], viewMatrix[2][2]);
    if (dot(n, toViewer) < 0.0) n = -n;
    float facing = dot(n, keyLight);
    c = mix(c, shadeInk, shadeStep * (1.0 - smoothstep(-0.12, 0.12, facing)));
    if (vKind < 1.5) {
      float valley = max(vCrease, 0.0), ridge = max(-vCrease, 0.0);
      c = mix(c, shadeInk, lightPlay * 0.24 * valley * valley);
      c = mix(c, vec3(1.0), lightPlay * 0.26 * smoothstep(0.72, 1.0, ridge));
      c = mix(c, vec3(1.0), lightPlay * 0.08 * max(facing, 0.0) * step(0.02, abs(vCrease)));
    }
  }
  gl_FragColor = vec4(mix(fadeTo, c, opacity), 1.0);
}`;

export class PleatedSurface {
  /** colorA(i), colorB(i): face colours per pleat (hex). colorA2 / colorB2: second set, blended in with the
      colorMix uniform. colorDisc(i): A-face colours inside the disc. photo: optional THREE.Texture for the B faces. */
  constructor({ pleats, colorA, colorB, colorA2 = colorA, colorB2 = colorB, colorDisc = colorA, capColor = WHITE, photo = null }) {
    this.pleats = pleats;
    const count = pleats * VERTS_PER_PLEAT;
    this.positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3), colorsB = new Float32Array(count * 3), colorsDisc = new Float32Array(count * 3);
    const plane = new Float32Array(count * 2), kind = new Float32Array(count);
    const capRgb = hexToRgb(capColor);
    for (let i = 0; i < pleats; i++) {
      const u0 = i / pleats - 0.5, um = (i + 0.5) / pleats - 0.5, u1 = (i + 1) / pleats - 0.5;
      const base = i * VERTS_PER_PLEAT;
      const disc = hexToRgb(colorDisc(i));
      const put = (n, rgb1, rgb2, u, v, k) => {
        colors.set(rgb1, (base + n) * 3); colorsB.set(rgb2, (base + n) * 3); colorsDisc.set(disc, (base + n) * 3);
        plane.set([u, v], (base + n) * 2); kind[base + n] = k;
      };
      const a1 = hexToRgb(colorA(i)), a2 = hexToRgb(colorA2(i)), b1 = hexToRgb(colorB(i)), b2 = hexToRgb(colorB2(i));
      // plane = where the point appears in the picture: each face set alone spans the whole pitch when seen from its side
      [[u0, -0.5], [u1, -0.5], [u1, 0.5], [u0, -0.5], [u1, 0.5], [u0, 0.5]].forEach(([u, v], n) => put(n, a1, a2, u, v, KIND_A));
      [[u0, -0.5], [u1, -0.5], [u1, 0.5], [u0, -0.5], [u1, 0.5], [u0, 0.5]].forEach(([u, v], n) => put(6 + n, b1, b2, u, v, KIND_B));
      for (let n = 12; n < VERTS_PER_PLEAT; n++) put(n, capRgb, capRgb, um, 0.5, KIND_CAP);
    }
    const geometry = new THREE.BufferGeometry();
    this.positionAttribute = new THREE.BufferAttribute(this.positions, 3).setUsage(THREE.DynamicDrawUsage);
    geometry.setAttribute('position', this.positionAttribute);
    this.crease = new Float32Array(count);
    this.creaseAttribute = new THREE.BufferAttribute(this.crease, 1).setUsage(THREE.DynamicDrawUsage);
    geometry.setAttribute('crease', this.creaseAttribute);
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('colorB', new THREE.BufferAttribute(colorsB, 3));
    geometry.setAttribute('colorDisc', new THREE.BufferAttribute(colorsDisc, 3));
    geometry.setAttribute('plane', new THREE.BufferAttribute(plane, 2));
    geometry.setAttribute('kind', new THREE.BufferAttribute(kind, 1));
    this.uniforms = {
      colorMix: { value: 0 }, photoAmount: { value: 0 }, photo: { value: photo },
      uvScale: { value: new THREE.Vector2(1, 1) }, uvOffset: { value: new THREE.Vector2(0, 0) },
      planeSize: { value: new THREE.Vector2(1, 1) }, discCentreRadius: { value: new THREE.Vector3(0, 0, 0) },
      inkDark: { value: new THREE.Color(NAVY) }, inkMid: { value: new THREE.Color(FOUNTAIN.periwinkle) },
      inkLight: { value: new THREE.Color(PAPER) }, levels: { value: new THREE.Vector2(0.12, 0.9) },
      opacity: { value: 1 }, fadeTo: { value: new THREE.Color(PAPER) },
      photoMode: { value: 0 },         // 0 natural, 1 smooth duotone, 2 three flat inks
      photoGrade: { value: new THREE.Vector3(1.05, 1.06, 0.0) },   // saturation, contrast, lift
      shadeTop: { value: 0 }, shadeBand: { value: 0.55 },   // darkens the top of the faces: the ring above casts a shadow
      motifA: { value: null }, motifB: { value: null }, motifAmount: { value: 0 }, motifShift: { value: 0 },
      paintU: { value: 1 },            // the painted picture only reaches this far along the sheet (0..1): column by column
      lightPlay: { value: 1 },         // 0..1 strength of the fold shading (valleys, ridge rim); only with shadeStep > 0
      shadeStep: { value: 0 },         // 0.14 = the film's one step of shade on faces turned away from keyLight
      shadeInk: { value: new THREE.Color(INK) }, keyLight: { value: new THREE.Vector3(-0.55, 0.45, 0.70).normalize() },
      photoSoftness: { value: 2.2 },   // mip bias: higher = calmer, simpler photo shapes
      discAspect: { value: 1 },   // below 1 widens the disc along the sheet: cos(view angle) keeps it round on screen
    };
    const material = new THREE.ShaderMaterial({
      uniforms: this.uniforms, vertexShader: VERTEX, fragmentShader: FRAGMENT, vertexColors: true, side: THREE.DoubleSide,
    });
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.frustumCulled = false;
  }

  /** Photo crop: fills a view of the given aspect (width / height as seen on screen), shifted by focus (-0.5..0.5).
      keep = the part of the photo that may show, as fractions [left, bottom, right, top] (to drop a caption, say). */
  fitPhoto(viewAspect, focusX = 0, focusY = 0, keep = [0, 0, 1, 1]) {
    const image = this.uniforms.photo.value && this.uniforms.photo.value.image;
    if (!image) throw new Error('PleatedSurface.fitPhoto: no photo texture loaded');
    const keepWidth = keep[2] - keep[0], keepHeight = keep[3] - keep[1];
    const photoAspect = (image.width * keepWidth) / (image.height * keepHeight);
    const fit = viewAspect > photoAspect ? [1, photoAspect / viewAspect] : [viewAspect / photoAspect, 1];
    this.uniforms.uvScale.value.set(fit[0] * keepWidth, fit[1] * keepHeight);
    this.uniforms.uvOffset.value.set(
      keep[0] + keepWidth / 2 - 0.5 + focusX * (1 - fit[0]) * keepWidth,
      keep[1] + keepHeight / 2 - 0.5 + focusY * (1 - fit[1]) * keepHeight,
    );
  }

  /** Pictures painted on the faces: left = texture for the A faces, right = for the B faces (see motifs.js). */
  setMotifs({ left, right }) {
    this.uniforms.motifA.value = left;
    this.uniforms.motifB.value = right;
  }

  /** Rebuilds the shape. length = sheet length (ring circumference at bend 1), height, bend 0..1,
      depth(i) = ridge depth of pleat i (default: pitch * 0.65), top(i) / bottom(i) = y of the edges of pleat i. */
  update({ length, height, bend = 0, depth = null, top = null, bottom = null }) {
    const pleats = this.pleats, pitch = length / pleats, pos = this.positions;
    const defaultDepth = pitch * DEFAULT_DEPTH_RATIO;
    const isBent = bend > 1e-4;
    const radius = isBent ? length / (2 * Math.PI * bend) : 0;
    const closedRadius = length / (2 * Math.PI);
    const capInner = bend * closedRadius * CAP_INNER_RATIO;
    let k = 0;
    const put = (u, n, y) => {
      if (isBent) {
        const phi = u / radius;
        pos[k] = (radius + n) * Math.sin(phi);
        pos[k + 2] = (radius + n) * Math.cos(phi) - radius + closedRadius * bend;
      } else {
        pos[k] = u;
        pos[k + 2] = n;
      }
      pos[k + 1] = y;
      k += 3;
    };
    const crease = this.crease;
    for (let i = 0; i < pleats; i++) {
      const u0 = -length / 2 + i * pitch, um = u0 + pitch / 2, u1 = u0 + pitch;
      const d = depth ? depth(i) : defaultDepth;
      // + at the valley, - at the ridge, 0 on a flat sheet: the shader shades valleys and rims ridges with it
      const fold = Math.min(1, Math.abs(d) / (pitch * 0.3)), base = i * VERTS_PER_PLEAT;
      CREASE_PATTERN.forEach((sign, n) => { crease[base + n] = sign * fold; });
      const yt = top ? top(i) : height / 2, yb = bottom ? bottom(i) : -height / 2;
      put(u0, 0, yb); put(um, d, yb); put(um, d, yt); put(u0, 0, yb); put(um, d, yt); put(u0, 0, yt);   // A face
      put(um, d, yb); put(u1, 0, yb); put(u1, 0, yt); put(um, d, yb); put(u1, 0, yt); put(um, d, yt);   // B face
      put(u0, 0, yt); put(um, d, yt); put(u1, 0, yt);                                                   // cap: tooth tip
      put(u0, 0, yt); put(u1, 0, yt); put(u1, -capInner, yt);                                           // cap: inner
      put(u0, 0, yt); put(u1, -capInner, yt); put(u0, -capInner, yt);
    }
    this.creaseAttribute.needsUpdate = true;
    this.positionAttribute.needsUpdate = true;
    this.uniforms.planeSize.value.set(length, height);
  }
}

/** A toothed ring of the fountain: a pleated surface closed into a drum. radius = valley radius. */
export class ToothedRing {
  /** depthRatio = tooth depth / pitch (0.65 default; 0.71 = the 70 degree folds of our hanukkiah). */
  constructor({ radius, height, teeth, colorA, colorB, colorA2, colorB2, capColor, depthRatio = DEFAULT_DEPTH_RATIO }) {
    this.radius = radius;
    this.height = height;
    this.surface = new PleatedSurface({ pleats: teeth, colorA, colorB, colorA2, colorB2, capColor });
    this.group = new THREE.Group();
    this.group.add(this.surface.mesh);
    const length = 2 * Math.PI * radius, depth = (length / teeth) * depthRatio;
    this.surface.update({ length, height, bend: 1, depth: () => depth });
  }
}
