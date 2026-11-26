/* The pictures painted on the big ring of our hanukkiah, as two textures that wrap once around the ring:
   A faces (seen from the left): periwinkle and yellow fields with a green Star of David,
   B faces (seen from the right): HANUKKAH in blue on white, then a sufganiyah on rose and lilac stripes.
   Give them to PleatedSurface.setMotifs(); motifAmount then paints them in from the bottom up.
   The layout follows the model renders (submission/shots); it is a drawing of the idea, not the exact paint map. */
import { THREE } from '../core/stage.js';
import { FOUNTAIN as F, WHITE } from '../palette.js';

const PIXELS_PER_PLEAT = 48;
const css = (hex) => `#${hex.toString(16).padStart(6, '0')}`;

function makeCanvas(pleats, aspect) {
  const canvas = document.createElement('canvas');
  canvas.width = pleats * PIXELS_PER_PLEAT;
  canvas.height = Math.round(canvas.width / aspect);
  const context = canvas.getContext('2d');
  if (!context) throw new Error('motifs: no 2D canvas context');
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

function star(context, cx, cy, radius, color) {
  context.fillStyle = color;
  [0, Math.PI].forEach((turn) => {
    context.beginPath();
    for (let corner = 0; corner < 3; corner++) {
      const angle = turn - Math.PI / 2 + (corner * Math.PI * 2) / 3;
      context.lineTo(cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius);
    }
    context.closePath();
    context.fill();
  });
}

function sufganiyah(context, cx, cy, radius) {
  const dot = (x, y, r, color) => { context.fillStyle = color; context.beginPath(); context.arc(x, y, r, 0, Math.PI * 2); context.fill(); };
  dot(cx, cy, radius, css(F.orange));
  dot(cx, cy - radius * 0.12, radius * 0.72, css(F.yellow));
  dot(cx, cy - radius * 0.18, radius * 0.3, css(F.brick));
}

function word(context, text, x, width, height, color) {
  const size = height * 0.7;
  context.font = `900 ${size}px "Arial Black", Arial, sans-serif`;
  context.textBaseline = 'middle';
  context.textAlign = 'center';
  context.fillStyle = color;
  const squeeze = Math.min(1.6, (width * 0.9) / context.measureText(text).width);
  context.save();
  context.translate(x + width / 2, height * 0.53);
  context.scale(squeeze, 1);
  context.fillText(text, 0, 0);
  context.restore();
}

/** Left-face picture: `repeats` times around the ring [periwinkle | yellow with a green star]. */
function drawLeft(pleats, aspect, repeats) {
  const { canvas, context } = makeCanvas(pleats, aspect);
  const sector = canvas.width / repeats, h = canvas.height;
  for (let i = 0; i < repeats; i++) {
    context.fillStyle = css(F.periwinkle);
    context.fillRect(i * sector, 0, sector / 2, h);
    context.fillStyle = css(F.yellow);
    context.fillRect((i + 0.5) * sector, 0, sector / 2, h);
    star(context, (i + 0.75) * sector, h / 2, h * 0.4, css(F.green));
  }
  return toTexture(canvas);
}

/** Right-face picture: `repeats` times around the ring [HANUKKAH on white | sufganiyah on rose and lilac]. */
function drawRight(pleats, aspect, repeats, wordShare) {
  const { canvas, context } = makeCanvas(pleats, aspect);
  const sector = canvas.width / repeats, h = canvas.height;
  for (let i = 0; i < repeats; i++) {
    const x = i * sector, wordWidth = sector * wordShare;
    context.fillStyle = css(WHITE);
    context.fillRect(x, 0, wordWidth, h);
    word(context, 'HANUKKAH', x, wordWidth, h, css(F.blue));
    for (let px = x + wordWidth, stripe = 0; px < x + sector; px += PIXELS_PER_PLEAT, stripe++) {
      context.fillStyle = css(stripe % 2 ? F.lilac : F.rose);
      context.fillRect(px, 0, PIXELS_PER_PLEAT, h);
    }
    sufganiyah(context, x + wordWidth + (sector - wordWidth) / 2, h / 2, h * 0.36);
  }
  return toTexture(canvas);
}

/** pleats = teeth of the ring, aspect = circumference / height. Returns { left, right } textures. */
export function createRingMotifs({ pleats, aspect, leftRepeats = 4, rightRepeats = 2, wordShare = 0.68 }) {
  return { left: drawLeft(pleats, aspect, leftRepeats), right: drawRight(pleats, aspect, rightRepeats, wordShare) };
}
