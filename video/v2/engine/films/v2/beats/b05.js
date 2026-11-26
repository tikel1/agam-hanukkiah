/* Beat 05 (55.5-62.5): learning. A standing notebook page rises over beat 4 (55.0-55.8) on its own study-coloured
   ground; nine colour dots land in a row on it (the nine flames of beat 4, now notes), Agam's portrait is pasted in the
   corner beside lines of "reading" that write themselves; then three real photos of his works are pasted one under
   the other while the camera scrolls slowly down the page. Link to beat 6: the whole picture shrinks into a phone
   screen (b06_rig.openRect) while the camera pushes in until the page fills that screen.
   Pass: 55.0-64.4 (it stays visible inside the phone until beat 6's hologram world has risen over it). */
import { THREE } from '../../../src/core/stage.js';
import { DOTS, GROUND } from '../../../src/palette.js';
import { track, spring } from '../../../src/core/motion.js';
import { buildPage, WrittenLine, FallingDots } from '../parts/b05_page.js';
import { buildPasted, updatePasted } from '../parts/b05_pasted.js';
import { openRect, OPEN } from '../parts/b06_rig.js';

const PASS_FROM = 55.0;
const PASS_TO = 64.4;
const RISE = { at: 55.0, from: -2150, freq: 1.2, damping: 0.78 };   // the page rises from below and settles
const DOTS_AT = 55.45;
/** Reading lines beside the portrait (right to left, the pen dot stays at each line's start). */
const READING = { at: 56.35, stagger: 0.17, duration: 0.42, right: 840, first: 470, step: 58, lengths: [200, 150, 110, 200, 160] };
/** Notes written under the last photo. */
const NOTES = [{ at: 60.35, y: 1724, length: 300 }, { at: 60.62, y: 1782, length: 190 }];
const NOTE_DURATION = 0.5;

/** Camera: still while the page arrives, a slow scroll down the page while photos are pasted, then a push-in until the
    page fills the frame width exactly (as the picture shrinks into the phone it becomes the phone's screen). */
const cameraZoom = track([[57.3, 1], [61.95, 1.06, 'inOutCubic'], [62.85, 1080 / 860, 'inOutCubic']]);
const cameraY = track([[57.3, 0], [61.95, -300, 'inOutCubic'], [62.85, -190, 'inOutCubic']]);

export async function create(ctx) {
  const beat = ctx.beats.b05;
  if (Math.abs(beat.start - 55.5) > 1e-6) throw new Error(`b05: expected the beat to start at 55.5, got ${beat.start}`);
  const scene = new THREE.Scene();
  const page = buildPage();
  scene.add(page);

  const dots = new FallingDots({});
  page.add(dots.group);
  const reading = READING.lengths.map((length, k) => new WrittenLine({
    x1: READING.right, y: READING.first + k * READING.step, length, color: DOTS[(k * 3) % DOTS.length],
  }));
  const notes = NOTES.map((note, k) => new WrittenLine({ x1: READING.right, y: note.y, length: note.length, color: DOTS[(k * 4 + 2) % DOTS.length] }));
  [...reading, ...notes].forEach((line) => page.add(line.group));
  const pasted = await buildPasted();
  pasted.forEach((item) => page.add(item.frame.group));

  function update(t) {
    ctx.stage.setRig({ zoom: cameraZoom(t), y: cameraY(t) });
    page.position.y = RISE.from * (1 - spring(t - RISE.at, RISE.freq, RISE.damping));
    dots.update(t - DOTS_AT);
    reading.forEach((line, k) => line.update(t - READING.at - k * READING.stagger, READING.duration));
    notes.forEach((line, k) => line.update(t - NOTES[k].at, NOTE_DURATION));
    pasted.forEach((item) => updatePasted(item, t));
  }

  const inPhone = (t) => t >= OPEN.shrink[0];
  return {
    from: PASS_FROM, to: PASS_TO, scene, update,
    rect: (t) => (inPhone(t) ? openRect(t) : null),
    background: (t) => (inPhone(t) ? GROUND.study : null),
  };
}
