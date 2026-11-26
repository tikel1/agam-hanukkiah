/* The paint of our hanukkiah's rings, as textures that wrap once around a ring (one column per tooth).
   R3 carries the two hidden pictures, laid out like the colouring maps (model/out/maps/map_R3_*):
     A faces (seen from the left):  yellow ground, green Magen David, orange dreidel just after it, warm bands behind;
     B faces (seen from the right): white ground, HANUKKAH in blue block letters, orange sufganiyah with brick jam.
   The other rings: one spectral turn on the A faces, white on the B faces.
   Same maths as storyboard/tools/models.py. */
import { THREE } from '../core/stage.js';
import { FOUNTAIN as F, SPECTRUM } from '../palette.js';

const PIXELS_PER_TOOTH = 48;
const css = (hex) => `#${hex.toString(16).padStart(6, '0')}`;
export const R3_TEETH = 80;
const R3_DRAW_HEIGHT = 150;            // the pictures are drawn in ring units: y 0 (top) .. 150 (bottom)

const BLOCK = {                        // 3 x 5 block letters, one cell = one tooth wide
  H: ['X.X', 'X.X', 'XXX', 'X.X', 'X.X'], A: ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'],
  N: ['X.X', 'XXX', 'XXX', 'XXX', 'X.X'], U: ['X.X', 'X.X', 'X.X', 'X.X', 'XXX'],
  K: ['X.X', 'XX.', 'X..', 'XX.', 'X.X'],
};
const WORD = 'HANUKKAH';
const WORD_START = 24;                 // first tooth of the word: centred on tooth 40 (the front)
const LETTER_TOP = 22, LETTER_ROW = 21;

function ringCanvas(teeth, ground) {
  const canvas = document.createElement('canvas');
  canvas.width = teeth * PIXELS_PER_TOOTH;
  canvas.height = 256;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('ringPictures: no 2D canvas context');
  context.fillStyle = css(ground);
  context.fillRect(0, 0, canvas.width, canvas.height);
  // draw in "tooth columns" along x and ring units (0..150) along y
  const col = (c) => (c + 0.5) * PIXELS_PER_TOOTH;
  const y = (v) => (v / R3_DRAW_HEIGHT) * canvas.height;
  const band = (c0, c1, color) => { context.fillStyle = css(color); context.fillRect(col(c0), 0, col(c1) - col(c0), canvas.height); };
  return { canvas, context, col, y, band };
}

function toTexture(canvas) {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.NoColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.anisotropy = 8;
  return texture;
}

/** Units along the ring per ring unit of height, in canvas pixels: keeps shapes round on the real ring. */
function unitX(radius) {
  return (R3_TEETH * PIXELS_PER_TOOTH) / (2 * Math.PI * radius);
}

function pictureA(radius) {
  const { canvas, context, col, y, band } = ringCanvas(R3_TEETH, F.yellow);
  const ux = unitX(radius);
  band(56, 61, F.lilac);
  band(61, 80, F.rose);
  band(-0.5, 4, F.rose);
  band(4, 10, F.orange);
  // Magen David at the front
  context.fillStyle = css(F.green);
  const cx = col(39.5), cy = 78, r = 70;
  [90, 270].forEach((start) => {
    context.beginPath();
    for (let k = 0; k < 3; k++) {
      const a = ((start + k * 120) * Math.PI) / 180;
      context.lineTo(cx + r * Math.cos(a) * ux, y(cy - r * Math.sin(a)));
    }
    context.closePath();
    context.fill();
  });
  // dreidel: handle, body, point (straight lines only)
  const dx = col(49.5);
  context.fillStyle = css(F.orange);
  context.fillRect(dx - 14 * ux, y(14), 28 * ux, y(40) - y(14));
  context.beginPath();
  [[-66, 40], [66, 40], [66, 96], [0, 140], [-66, 96]].forEach(([px, py]) => context.lineTo(dx + px * ux, y(py)));
  context.closePath();
  context.fill();
  // the dreidel sits on yellow: give it a brick outline band so it reads against the orange-free ground
  return toTexture(canvas);
}

function pictureB(radius) {
  const { canvas, context, col, y, band } = ringCanvas(R3_TEETH, F.white);
  const ux = unitX(radius);
  band(-0.5, 8, F.periwinkle);
  band(8, 12, F.lilac);
  context.fillStyle = css(F.blue);
  [...WORD].forEach((ch, k) => BLOCK[ch].forEach((row, r) => [...row].forEach((cell, c) => {
    if (cell !== 'X') return;
    const x0 = col(WORD_START + k * 4 + c) - PIXELS_PER_TOOTH / 2;
    context.fillRect(x0, y(LETTER_TOP + r * LETTER_ROW), PIXELS_PER_TOOTH, y(LETTER_ROW) + 1);
  })));
  const sx = col(66);
  context.fillStyle = css(F.orange);
  context.beginPath();
  context.ellipse(sx, y(78), 120 * ux, y(40), 0, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = css(F.brick);
  context.fillRect(sx - 26 * ux, y(62), 52 * ux, y(26));
  return toTexture(canvas);
}

/** One spectral turn around a ring, starting at `offset`, one flat colour per tooth. */
function spectrumTexture(teeth, offset) {
  const canvas = document.createElement('canvas');
  canvas.width = teeth;
  canvas.height = 2;
  const context = canvas.getContext('2d');
  for (let i = 0; i < teeth; i++) {
    context.fillStyle = css(SPECTRUM[(offset + Math.floor((i * SPECTRUM.length) / teeth)) % SPECTRUM.length]);
    context.fillRect(i, 0, 1, 2);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.NoColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.minFilter = THREE.NearestFilter;
  texture.magFilter = THREE.NearestFilter;
  return texture;
}

function solidTexture(color) {
  const canvas = document.createElement('canvas');
  canvas.width = 2;
  canvas.height = 2;
  const context = canvas.getContext('2d');
  context.fillStyle = css(color);
  context.fillRect(0, 0, 2, 2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.NoColorSpace;
  return texture;
}

/** The two hidden pictures of R3: { left, right } for PleatedSurface.setMotifs. radius = the ring's radius. */
export function createR3Pictures(radius = 360) {
  return { left: pictureA(radius), right: pictureB(radius) };
}

/** Paint of a plain ring: { left: spectrum, right: white }. */
export function createStripePaint(teeth, offset) {
  return { left: spectrumTexture(teeth, offset), right: solidTexture(F.white) };
}

/** Teeth (0..80, fractions allowed) where the pictures sit on R3, and the motifShift that brings a tooth to the front.
    The sheet's middle (tooth 40) faces the viewer when the ring is not turned. */
export const R3_SPOTS = Object.freeze({ star: 39.5, dreidel: 49.5, word: 40, sufganiyah: 66 });
