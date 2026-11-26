/* The two pictures of the polymorph demo, drawn on canvases: fire (flame on navy) and water (drop on light blue).
   Flat colours only. */
import { THREE } from '../../src/core/stage.js';
import { FOUNTAIN as F, FLAME, WHITE } from '../../src/palette.js';

const css = (hex) => `#${hex.toString(16).padStart(6, '0')}`;
const PIXELS_PER_UNIT = 2;

function canvasOf(width, height) {
  const canvas = document.createElement('canvas');
  canvas.width = width * PIXELS_PER_UNIT;
  canvas.height = height * PIXELS_PER_UNIT;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('pictures: no 2D canvas context');
  context.scale(canvas.width, canvas.height);     // draw in 0..1 x 0..1, y down
  return { canvas, context };
}

function toTexture(canvas) {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.NoColorSpace;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.anisotropy = 8;
  return texture;
}

/** Teardrop with its point up: centre x, base y, width and height in 0..1 units; lean shifts the tip sideways. */
function teardrop(context, cx, baseY, width, height, color, lean = 0) {
  const r = width / 2, tipX = cx + lean * width, tipY = baseY - height;
  context.fillStyle = color;
  context.beginPath();
  context.moveTo(tipX, tipY);
  context.bezierCurveTo(cx + r * 0.35, baseY - height * 0.55, cx + r, baseY - r * 1.5, cx + r, baseY - r);
  context.arc(cx, baseY - r, r, 0, Math.PI);
  context.bezierCurveTo(cx - r, baseY - r * 1.5, cx - r * 0.35, baseY - height * 0.55, tipX, tipY);
  context.fill();
}

function drawFire(width, height) {
  const { canvas, context } = canvasOf(width, height);
  context.fillStyle = css(F.navy);
  context.fillRect(0, 0, 1, 1);
  teardrop(context, 0.5, 0.86, 0.56, 0.72, css(FLAME.outer), 0.1);
  teardrop(context, 0.5, 0.86, 0.34, 0.46, css(FLAME.inner), 0.06);
  teardrop(context, 0.5, 0.86, 0.16, 0.22, css(FLAME.core), 0.03);
  return toTexture(canvas);
}

function drawWater(width, height) {
  const { canvas, context } = canvasOf(width, height);
  context.fillStyle = css(F.light_blue);
  context.fillRect(0, 0, 1, 1);
  teardrop(context, 0.5, 0.8, 0.52, 0.64, css(F.blue));
  context.fillStyle = css(WHITE);               // highlight: a flat white crescent
  context.beginPath();
  context.ellipse(0.4, 0.6, 0.045, 0.1, 0.35, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = css(F.blue);               // the pool under the drop
  context.fillRect(0, 0.9, 1, 0.1);
  return toTexture(canvas);
}

/** Returns { fire, water } textures for pictures of the given size in world units. */
export function createPictures(width, height) {
  return { fire: drawFire(width, height), water: drawWater(width, height) };
}
