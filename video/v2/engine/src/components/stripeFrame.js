/* Stripe frame: the film's designed frame for anything real. A photograph, an archive clip or a placeholder is
   shown UNTOUCHED (crop only) inside a border of colour / white stripes in spectrum order, on a soft flat shadow.
   Options: a pleated accordion curtain that opens onto the picture, two tape strips (pasted in a notebook),
   a night look (the frame's white becomes night blue).
   User rules: no effects on photos, real photographs only (the two Kan 11 archive clips play as clips).
   The frame lies in the XY plane of its group, centred. Pin it with stage.place(frame.group, x, y) or billboard it. */
import { THREE } from '../core/stage.js';
import { PleatedSurface } from './pleated.js';
import { cardShadow } from './shadows.js';
import { SPECTRUM, FOUNTAIN as F, NIGHT_SLAT, INK, PAPER } from '../palette.js';
import { clamp } from '../core/motion.js';

const BAND = 26, STRIPE = 13, PIXEL_RATIO = 2;
const SHADOW_OFFSET = [14, -20];
const TAPE = { color: 0xF2E6B8, width: 150, height: 44 };
const CURTAIN = { pleats: 9, folded: 0.07, depth: 0.5 };
const css = (hex) => `#${hex.toString(16).padStart(6, '0')}`;

function canvasTexture(canvas) {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.NoColorSpace;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.anisotropy = 8;
  return texture;
}

/** Loads an image as a texture whose colours pass through untouched. */
export function loadPicture(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, (texture) => {
      texture.colorSpace = THREE.NoColorSpace;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.anisotropy = 8;
      resolve(texture);
    }, undefined, () => reject(new Error(`picture failed to load: ${url}`)));
  });
}

/** An archive clip as a frame atlas (made with ffmpeg tile). Returns { texture, aspect, duration, setTime(seconds) }:
    setTime shows the frame for that second of the clip and holds the first / last frame outside it. */
export async function loadClip(url, { columns, rows, frames, fps = 25, frameWidth, frameHeight }) {
  const texture = await loadPicture(url);
  texture.minFilter = THREE.LinearFilter;      // no mip maps: neighbours in the atlas must not bleed
  texture.generateMipmaps = false;
  texture.repeat.set(1 / columns, 1 / rows);
  const setTime = (seconds) => {
    const index = Math.floor(clamp(seconds * fps, 0, frames - 1));
    texture.offset.set((index % columns) / columns, 1 - (Math.floor(index / columns) + 1) / rows);
  };
  setTime(0);
  return { texture, aspect: frameWidth / frameHeight, duration: frames / fps, setTime, isClip: true };
}
export const CLIPS = Object.freeze({
  fountainDay: { url: 'assets/clips/kan_fountain_day_8x8.jpg', columns: 8, rows: 8, frames: 58, frameWidth: 640, frameHeight: 456 },
  fireOnWater: { url: 'assets/clips/kan_fire_on_water_9x8.jpg', columns: 9, rows: 8, frames: 69, frameWidth: 640, frameHeight: 518 },
});

/** Placeholder for a real photo of the girls that is still to come: grey hatched field, a line-and-dot camera,
    the label and "כאן תיכנס תמונה אמיתית". Swap it for loadPicture(...) when the photo arrives: same frame. */
export async function createPlaceholder(width, height, label, { dark = false } = {}) {
  await document.fonts.load('40px "Secular One"');
  const canvas = document.createElement('canvas');
  canvas.width = width * PIXEL_RATIO;
  canvas.height = height * PIXEL_RATIO;
  const c = canvas.getContext('2d');
  if (!c) throw new Error('stripeFrame: no 2D canvas context');
  c.scale(PIXEL_RATIO, PIXEL_RATIO);
  const field = dark ? '#2E3570' : '#E4E3DF', hatch = dark ? '#3A4285' : '#D3D2CD', ink = dark ? css(PAPER) : css(INK);
  c.fillStyle = field;
  c.fillRect(0, 0, width, height);
  c.strokeStyle = hatch;
  c.lineWidth = 3;
  for (let x = -height; x < width; x += 26) { c.beginPath(); c.moveTo(x, height); c.lineTo(x + height, 0); c.stroke(); }
  // line-and-dot camera
  const size = Math.min(width, height) * 0.2, cx = width / 2, cy = height / 2 - size * 0.55;
  c.strokeStyle = ink;
  c.lineWidth = Math.max(4, size * 0.07);
  c.lineJoin = 'miter';
  c.strokeRect(cx - size * 0.7, cy - size * 0.42, size * 1.4, size * 0.9);
  c.beginPath(); c.moveTo(cx - size * 0.3, cy - size * 0.42); c.lineTo(cx - size * 0.18, cy - size * 0.62); c.lineTo(cx + size * 0.18, cy - size * 0.62); c.lineTo(cx + size * 0.3, cy - size * 0.42); c.stroke();
  c.beginPath(); c.arc(cx, cy + size * 0.03, size * 0.27, 0, Math.PI * 2); c.stroke();
  c.fillStyle = css(0xE4432F);
  c.beginPath(); c.arc(cx + size * 0.5, cy - size * 0.22, size * 0.07, 0, Math.PI * 2); c.fill();
  c.fillStyle = ink;
  c.textAlign = 'center';
  c.direction = 'rtl';
  const big = clamp(width * 0.058, 22, 46);
  c.font = `${big}px "Secular One"`;
  c.fillText(label, cx, cy + size * 0.95 + big);
  c.globalAlpha = 0.6;
  c.font = `${big * 0.62}px "Secular One"`;
  c.fillText('כאן תיכנס תמונה אמיתית', cx, cy + size * 0.95 + big * 2.1);
  return canvasTexture(canvas);
}

/** The stripe border as one texture: stripes run across each side, colour / white alternating in spectrum order. */
function borderTexture(width, height, white, band) {
  const canvas = document.createElement('canvas');
  canvas.width = width * PIXEL_RATIO;
  canvas.height = height * PIXEL_RATIO;
  const c = canvas.getContext('2d');
  c.scale(PIXEL_RATIO, PIXEL_RATIO);
  c.fillStyle = css(white);
  c.fillRect(0, 0, width, height);
  let index = 0;
  const next = () => css(SPECTRUM[index++ % SPECTRUM.length]);
  for (let x = 0; x < width; x += STRIPE * 2) { c.fillStyle = next(); c.fillRect(x, 0, STRIPE, band); }                       // top
  for (let y = band; y < height - band; y += STRIPE * 2) { c.fillStyle = next(); c.fillRect(width - band, y, band, STRIPE); } // right
  for (let x = width - STRIPE; x > -STRIPE; x -= STRIPE * 2) { c.fillStyle = next(); c.fillRect(x, height - band, STRIPE, band); } // bottom
  for (let y = height - band - STRIPE; y > band - STRIPE; y -= STRIPE * 2) { c.fillStyle = next(); c.fillRect(0, y, band, STRIPE); } // left
  return canvasTexture(canvas);
}

export class StripeFrame {
  /** picture = texture from loadPicture / createPlaceholder, or a clip from loadClip.
      width, height = size of the picture window in world units; the picture is cropped (never stretched) to fill it,
      focus = [-1..1, -1..1] which part survives the crop (0, 0 = centre).
      style 'stripes' (default) or 'plain' (thin white border, for photos pasted in a notebook).
      night: the frame's white is night blue. curtain: adds the accordion curtain (see setCurtain). tape: two tape strips. */
  constructor({ picture, width, height, focus = [0, 0], style = 'stripes', night = false, curtain = false, tape = false, shadow = true }) {
    const texture = picture && picture.isClip ? picture.texture : picture;
    if (!texture || !texture.image) throw new Error('StripeFrame: picture is missing');
    const band = style === 'stripes' ? BAND : 10;
    this.pictureWidth = width;
    this.pictureHeight = height;
    this.width = width + band * 2;
    this.height = height + band * 2;
    this.group = new THREE.Group();
    this.clip = picture.isClip ? picture : null;
    const white = night ? NIGHT_SLAT : F.white;

    if (shadow) {
      this.shadow = cardShadow(this.width, this.height, { strength: night ? 0.45 : 0.24, softness: 44, tint: night ? 0x10153A : INK });
      this.shadow.position.set(SHADOW_OFFSET[0], SHADOW_OFFSET[1], -2);
      this.group.add(this.shadow);
    }
    const borderMaterial = style === 'stripes'
      ? new THREE.MeshBasicMaterial({ map: borderTexture(this.width, this.height, white, band) })
      : new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
    this.group.add(new THREE.Mesh(new THREE.PlaneGeometry(this.width, this.height), borderMaterial));

    // the picture: crop to fill (uv only), colours untouched
    const imageAspect = picture.isClip ? picture.aspect : texture.image.width / texture.image.height;
    const windowAspect = width / height;
    const keepU = Math.min(1, windowAspect / imageAspect), keepV = Math.min(1, imageAspect / windowAspect);
    const u0 = (1 - keepU) * (0.5 + focus[0] * 0.5), v0 = (1 - keepV) * (0.5 + focus[1] * 0.5);
    const geometry = new THREE.PlaneGeometry(width, height);
    const uv = geometry.attributes.uv;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, u0 + uv.getX(i) * keepU, v0 + uv.getY(i) * keepV);
    this.picture = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ map: texture }));
    this.picture.position.z = 1;
    this.group.add(this.picture);

    if (curtain) this.buildCurtain();
    if (tape) this.buildTape();
  }

  buildCurtain() {
    const stripe = (side) => (i) => SPECTRUM[(side * 5 + i) % SPECTRUM.length];
    this.curtain = [-1, 1].map((side) => {
      const surface = new PleatedSurface({ pleats: CURTAIN.pleats, colorA: stripe(side < 0 ? 0 : 1), colorB: () => F.white, capColor: F.white });
      surface.uniforms.shadeStep.value = 0.14;
      surface.mesh.position.z = 3;
      this.group.add(surface.mesh);
      return { surface, side };
    });
    this.setCurtain(0);
  }

  buildTape() {
    [[-1, 7], [1, -6]].forEach(([side, angle]) => {
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(TAPE.width, TAPE.height), new THREE.MeshBasicMaterial({ color: TAPE.color, transparent: true, opacity: 0.88 }));
      mesh.position.set(side * (this.width / 2 - 40), this.height / 2 - 6, 4);
      mesh.rotation.z = ((side * 38 + angle) * Math.PI) / 180;
      this.group.add(mesh);
    });
  }

  /** open 0 = the stripes cover the picture, 1 = folded like an accordion at both sides (a narrow rest stays). */
  setCurtain(open) {
    if (!this.curtain) return;
    const k = clamp(open);
    const half = this.pictureWidth / 2;
    const length = half * (1 - k * (1 - CURTAIN.folded * 2));
    this.curtain.forEach(({ surface, side }) => {
      const pitch = length / CURTAIN.pleats;
      const depth = (half / CURTAIN.pleats) * CURTAIN.depth * Math.sin(k * Math.PI * 0.5) + 0.01;
      surface.update({ length, height: this.pictureHeight, bend: 0, depth: () => depth });
      surface.mesh.position.x = side * (half - length / 2);
      surface.mesh.visible = pitch > 0.05;
    });
  }

  /** For clips: shows the frame of the clip at `seconds` (holds the last frame after its end). */
  setClipTime(seconds) {
    if (this.clip) this.clip.setTime(seconds);
  }

  /** lift 0..1: how far the frame floats (moves the shadow away). */
  setLift(lift) {
    if (this.shadow) this.shadow.position.set(SHADOW_OFFSET[0] * (0.4 + lift), SHADOW_OFFSET[1] * (0.4 + lift), -2);
  }
}
