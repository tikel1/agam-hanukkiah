/* Burned-in subtitles: an HTML layer above the canvas, so the browser does Hebrew shaping and right-to-left order.
   Style follows storyboard §1.4 (Secular One 54 px, navy, paper halo, band y 900..1040). Each line eases in and out. */
import { prog, ease } from './motion.js';

const FADE_SECONDS = 0.2;
const RISE_PIXELS = 14;

export class Subtitles {
  constructor(layer, items = []) {
    this.layer = layer;
    this.items = items.map((item) => ({ ...item }));
    this.line = document.createElement('div');
    this.line.className = 'subtitle';
    this.line.dir = 'rtl';
    this.line.lang = 'he';
    this.copies = ['halo', 'text'].map((name) => {
      const span = document.createElement('span');
      span.className = name;
      this.line.appendChild(span);
      return span;
    });
    layer.appendChild(this.line);
    this.currentText = null;
  }

  update(t) {
    const item = this.items.find((it) => t >= it.start && t < it.end);
    if (!item) {
      this.line.style.opacity = '0';
      return;
    }
    if (this.currentText !== item.text) {
      this.copies.forEach((span) => { span.textContent = item.text; });   // textContent: never parsed as HTML
      this.currentText = item.text;
      this.line.classList.toggle('on-dark', Boolean(item.dark));   // light text for night scenes
    }
    const inK = ease.outCubic(prog(t, item.start, item.start + FADE_SECONDS));
    const outK = 1 - ease.inCubic(prog(t, item.end - FADE_SECONDS, item.end));
    this.line.style.opacity = String(Math.min(inK, outK));
    this.line.style.transform = `translate(-50%, ${((1 - inK) * RISE_PIXELS).toFixed(2)}px)`;
  }
}

/** Parses SubRip text into [{ start, end, text }] (seconds). */
export function parseSrt(text) {
  const toSeconds = (stamp) => {
    const [h, m, s] = stamp.replace(',', '.').split(':').map(Number);
    return h * 3600 + m * 60 + s;
  };
  return text.replace(/\r/g, '').split(/\n\n+/).map((block) => {
    const lines = block.trim().split('\n');
    const timing = lines.find((line) => line.includes('-->'));
    if (!timing) return null;
    const [start, end] = timing.split('-->').map((part) => toSeconds(part.trim()));
    return { start, end, text: lines.slice(lines.indexOf(timing) + 1).join('\n') };
  }).filter(Boolean);
}
