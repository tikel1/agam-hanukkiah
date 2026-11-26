/* Subtitles as a design element (storyboard v2 §2.6), readable by a child with the sound off:
   every line sits on its own slat (white, at night night-blue) with ends slanted like the museum letters, a flat
   shadow, a stamp of five thin stripes where the line starts (right side), and a logo-coloured dot that hops from
   word to word under the word being spoken.
   In: the slat unfolds right to left (8 frames), the text rises 6 px; the second line follows 3 frames later.
   Out: the slat folds back into its stamp.
   An HTML layer above the canvas, so the browser shapes the Hebrew. Everything is set from the time alone.
   Cue: { start, end, lines: ['...', '...'] (or text with \n), dark: true at night, words: [seconds, ...] optional
   start time of each word (from the TTS); without it the words share the cue's time by length. */
import { prog, ease, clamp, lerp } from './motion.js';
import { SPECTRUM, DOTS } from '../palette.js';

const BAND_TOP = 1490, BAND_HEIGHT = 210;
const FONT = 60, FONT_SMALL = 52, MAX_WIDTH = 820;
const LINE_HEIGHT = 84, LINE_GAP = 8;
const SLANT = 0.07;                    // 4 degrees
const IN_SECONDS = 8 / 30, OUT_SECONDS = 6 / 30, LINE_DELAY = 3 / 30, RISE = 6;
const STAMP = { stripes: 5, width: 7, gap: 5 };
const DOT = { size: 16, hop: 14, seconds: 0.16, lead: 0.15, tail: 0.3 };
const css = (hex) => `#${hex.toString(16).padStart(6, '0')}`;

const STYLE = `
.slats { position: absolute; left: 0; width: 100%; top: ${BAND_TOP}px; height: ${BAND_HEIGHT}px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: ${LINE_GAP}px; font-family: "Secular One", sans-serif; direction: rtl; }
.slat { position: relative; height: ${LINE_HEIGHT}px; line-height: ${LINE_HEIGHT - 4}px; white-space: nowrap; display: flex; align-items: center;
  padding: 0 30px 0 34px; color: #232C5E; --slat: #FFFFFF; --shade: rgba(35, 44, 94, 0.16); }
.slats.dark .slat { color: #F7F5EE; --slat: #2E3570; --shade: rgba(10, 14, 48, 0.55); }
.slat .back, .slat .shade { position: absolute; inset: 0; clip-path: polygon(${LINE_HEIGHT * SLANT}px 0, 100% 0, calc(100% - ${LINE_HEIGHT * SLANT}px) 100%, 0 100%); }
.slat .back { background: var(--slat); }
.slat .shade { background: var(--shade); transform: translate(6px, 6px); }
.slat .text { position: relative; }
.slat .stamp { position: relative; display: flex; gap: ${STAMP.gap}px; margin-inline-end: 22px; height: 100%; transform: skewX(${-Math.atan(SLANT) * 57.3}deg); }
.slat .stamp i { display: block; width: ${STAMP.width}px; height: 100%; }
.slat .dot { position: absolute; left: 0; bottom: 2px; width: ${DOT.size}px; height: ${DOT.size}px; border-radius: 50%; }
`;

function splitLines(item) {
  return item.lines ? item.lines : String(item.text || '').split('\n');
}

export class SlatSubtitles {
  constructor(layer, items = []) {
    if (!document.getElementById('slat-style')) {
      const style = document.createElement('style');
      style.id = 'slat-style';
      style.textContent = STYLE;
      document.head.appendChild(style);
    }
    this.root = document.createElement('div');
    this.root.className = 'slats';
    this.root.lang = 'he';
    layer.appendChild(this.root);
    this.items = items.map((item, index) => ({ ...item, index, lines: splitLines(item) }));
    this.current = null;
    this.measure = document.createElement('canvas').getContext('2d');
  }

  /** Builds the DOM of one cue (only when the cue changes). */
  build(item) {
    this.root.textContent = '';
    this.root.classList.toggle('dark', Boolean(item.dark));
    this.measure.font = `${FONT}px "Secular One"`;
    const widest = Math.max(...item.lines.map((line) => this.measure.measureText(line).width));
    const fontSize = widest > MAX_WIDTH ? FONT_SMALL : FONT;
    let wordIndex = 0;
    this.lines = item.lines.map((line, lineIndex) => {
      const slat = document.createElement('div');
      slat.className = 'slat';
      slat.style.fontSize = `${fontSize}px`;
      const shade = document.createElement('div'); shade.className = 'shade';
      const back = document.createElement('div'); back.className = 'back';
      const stamp = document.createElement('span'); stamp.className = 'stamp';
      for (let i = 0; i < STAMP.stripes; i += 2) {
        const bar = document.createElement('i');
        bar.style.background = css(SPECTRUM[(item.index * 3 + lineIndex * 5 + i) % SPECTRUM.length]);
        stamp.appendChild(bar);
      }
      const text = document.createElement('span'); text.className = 'text';
      const words = line.split(' ').filter(Boolean).map((word, i, all) => {
        const span = document.createElement('span');
        span.textContent = word + (i < all.length - 1 ? ' ' : '');   // textContent: never parsed as HTML
        text.appendChild(span);
        return { span, index: wordIndex++, length: word.length };
      });
      const dot = document.createElement('div'); dot.className = 'dot';
      dot.style.background = css(DOTS[item.index % DOTS.length]);
      slat.append(shade, back, stamp, text, dot);
      this.root.appendChild(slat);
      return { slat, text, dot, words, stamp };
    });
    // word clocks: from the TTS if given, else shared by length
    const all = this.lines.flatMap((line) => line.words);
    const from = item.start + DOT.lead, to = item.end - DOT.tail;
    const total = all.reduce((sum, word) => sum + word.length + 1, 0);
    let passed = 0;
    all.forEach((word, i) => {
      word.at = item.words && item.words[i] !== undefined ? item.words[i] : lerp(from, to, passed / total);
      passed += word.length + 1;
    });
    this.words = all;
    // positions after layout
    this.lines.forEach((line) => {
      const box = line.slat.getBoundingClientRect(), scale = box.width / line.slat.offsetWidth || 1;
      line.words.forEach((word) => {
        const rect = word.span.getBoundingClientRect();
        word.x = (rect.left + rect.width / 2 - box.left) / scale;
        word.line = line;
      });
      line.stampWidth = line.stamp.offsetWidth + 52;
      line.width = line.slat.offsetWidth;
    });
  }

  update(t) {
    const item = this.items.find((it) => t >= it.start && t < it.end);
    if (!item) {
      this.root.style.visibility = 'hidden';
      this.current = null;
      return;
    }
    if (this.current !== item) { this.build(item); this.current = item; }
    this.root.style.visibility = 'visible';
    this.lines.forEach((line, lineIndex) => {
      const delay = lineIndex * LINE_DELAY;
      const inK = ease.outCubic(prog(t, item.start + delay, item.start + delay + IN_SECONDS));
      const outK = ease.inCubic(prog(t, item.end - OUT_SECONDS, item.end));
      // unfold right to left; fold back to the stamp at the right end
      const shown = inK * (1 - outK * (1 - line.stampWidth / line.width));
      const hide = (1 - shown) * 100;
      line.slat.style.clipPath = `inset(-10px -10px -12px ${hide.toFixed(2)}%)`;
      line.slat.style.opacity = String(clamp(inK * 4) * (1 - ease.inCubic(prog(t, item.end - 0.06, item.end))));
      line.text.style.transform = `translateY(${((1 - inK) * RISE).toFixed(2)}px)`;
      line.text.style.opacity = String(clamp(inK * 1.6 - 0.3) * (1 - clamp(outK * 2)));
    });
    // the hopping dot: sits under the spoken word, hops to the next one
    const now = this.words.filter((word) => t >= word.at);
    const word = now[now.length - 1] || this.words[0];
    const previous = now.length > 1 ? now[now.length - 2] : null;
    const hop = previous && previous.line === word.line ? prog(t, word.at, word.at + DOT.seconds) : 1;
    const outK = prog(t, item.end - OUT_SECONDS, item.end);
    this.lines.forEach((line) => {
      const here = line === word.line;
      const x = here && hop < 1 ? lerp(previous.x, word.x, ease.inOutCubic(hop)) : word.x;
      const lift = here && hop < 1 ? Math.sin(hop * Math.PI) * DOT.hop : 0;
      const pop = here ? clamp((t - (previous && previous.line === line ? item.start : word.at)) / 0.1) * (1 - clamp(outK * 3)) : 0;
      const visible = here && t >= item.start + IN_SECONDS * 0.7;
      line.dot.style.transform = `translate(${(x - DOT.size / 2).toFixed(2)}px, ${(DOT.size * 0.45 - lift).toFixed(2)}px) scale(${visible ? pop.toFixed(3) : 0})`;
    });
  }
}
