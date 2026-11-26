/* Line-and-dot lettering. Base glyphs are copied from submission/logo.py; the rest are designed in the same spirit:
   straight lines only, slight slants, a coloured dot on a stroke's top end. Box: height 100, strokes y 0..100. */
"use strict";
const LOGO = { CAP: 100, STROKE: 7.5, DOT_R: 10.5, LETTER_GAP: 26, WORD_GAP: 62 };
const GLYPHS = {
  // --- from submission/logo.py ---
  "ח": [58, ["M0,100 L12,0 H58 V100"], [[58, 0]]],
  "נ": [44, ["M8,0 H44 V93 L0,100"], [[8, 0]]],
  "ו": [0, ["M0,0 V100"], [[0, 0]]],
  "כ": [56, ["M0,0 H38 L56,50 L38,95 L0,100"], [[0, 0]]],
  "י": [0, ["M0,0 V40"], [[0, 0]]],
  "ת": [64, ["M0,0 H64 V100", "M14,0 V100 H0"], [[0, 0]]],
  "א": [70, ["M0,0 L70,100", "M64,0 L44,62", "M28,40 L4,100"], [[0, 0], [64, 0]]],
  "ש": [70, ["M0,0 L12,100 H70 V0", "M36,0 L40,100"], [[0, 0], [36, 0], [70, 0]]],
  "מ": [90, ["M0,0 L32,48", "M14,82 L56,0 L90,94 L40,99"], [[0, 0], [56, 0]]],
  "ם": [60, ["M0,0 H60 V100 H0 Z"], [[0, 0], [60, 0]]],
  // --- the museum's ג: a stroke from the top-left dot to the bottom right, a short leg from its middle to the bottom left ---
  "ג": [60, ["M26,0 L60,98", "M43,50 L0,100"], [[26, 0]]],
  // --- new, same rules ---
  "ע": [58, ["M58,0 L52,48 L8,100", "M0,0 L52,48"], [[0, 0], [58, 0]]],
  "ק": [54, ["M0,0 H54 L50,50 H6", "M28,50 L24,116"], [[0, 0]]],
  "ב": [52, ["M0,0 H52 V98", "M-4,98 L68,102"], [[0, 0]]],
  "פ": [50, ["M0,0 H50 V96 L0,100", "M0,0 L4,42 H26"], [[0, 0]]],
  "ף": [50, ["M0,0 H50 V118", "M0,0 L4,42 H28"], [[0, 0]]],
  "ל": [46, ["M8,-34 V30 L46,42 V100 H0"], [[8, -34]]],
  "ר": [46, ["M0,0 H46 L50,100"], [[0, 0]]],
  "ד": [54, ["M0,0 H54 V100"], [[0, 0], [54, 0]]],
  "ה": [56, ["M0,0 H56 V100", "M4,32 L0,100"], [[0, 0]]],
  "ס": [58, ["M14,0 H52 L58,60 L44,100 H6 L0,40 Z"], [[14, 0]]],
};
const DIGITS = {  // read left to right
  "1": [26, ["M0,22 L26,0 V100"], [[26, 0]]], "9": [44, ["M0,0 H44 V100 M0,0 V52 H44"], [[0, 0]]],
  "8": [44, ["M0,0 H44 V100 H0 Z M0,50 H44"], [[0, 0]]], "6": [44, ["M44,0 H0 V100 H44 V52 H0"], [[44, 0]]],
  "4": [48, ["M0,0 V56 H48", "M34,0 V100"], [[0, 0], [34, 0]]], "0": [44, ["M6,0 H44 L38,100 H0 Z"], [[6, 0]]],
};

/* Layout in glyph units: Hebrew words right to left; digits left to right (rtl=false). Returns items with x and the dot list. */
function layoutTitle(words, rtl = true) {
  const items = [], seps = []; let x = 0;
  words.forEach((word, wi) => {
    if (wi) { seps.push(x + LOGO.WORD_GAP / 2); x += LOGO.WORD_GAP; }
    [...word].forEach((ch, ci) => {
      if (ci) x += LOGO.LETTER_GAP;
      const gl = (rtl ? GLYPHS : DIGITS)[ch]; if (!gl) throw new Error("no glyph for " + ch);
      items.push({ ch, x, w: gl[0], paths: gl[1], dots: gl[2] }); x += gl[0];
    });
  });
  const total = x;
  if (rtl) { items.forEach(it => { it.x = total - it.x - it.w; }); return { items, seps: seps.map(s => total - s), total }; }
  return { items, seps, total };
}
const titleWidth = (words, cap, rtl = true) => layoutTitle(words, rtl).total * cap / LOGO.CAP;

/* Animated title. a = start time, o.span = time the lines take to be drawn (staggered letter by letter, first letter = rightmost),
   o.dotAt = delay after the last line starts before dots begin to jump in. Draws fully when t is past the end. */
function title(words, cx, top, cap, t, a, o = {}) {
  const rtl = o.rtl !== false, span = o.span === undefined ? 1.6 : o.span, dotSpan = o.dotSpan || 0.9, op = o.op === undefined ? 1 : o.op;
  const L = layoutTitle(words, rtl), sc = cap / LOGO.CAP, ox = cx - L.total * sc / 2;
  const n = L.items.length, each = Math.min(1.0, span / Math.max(1, n) * 2.2), stag = n > 1 ? (span - each) / (n - 1) : 0;
  const lines = [], dots = []; let ci = 0;
  const colour = () => DOTS[(ci++) % DOTS.length];
  const dotAt0 = a + span;                 // dots start once the lines are (nearly) done
  let di = 0;
  const addDot = (px, py) => {
    const k = P(t, dotAt0 + di * (dotSpan / 6), dotAt0 + di * (dotSpan / 6) + 0.45); di++;
    const c = colour(); if (k <= 0) return;
    const bounce = E.back(k), rr = LOGO.DOT_R * sc * bounce, hop = (1 - E.out(k)) * -cap * 0.35;
    dots.push(circle(px, py + hop, rr, c));
  };
  L.items.forEach((it, i) => {
    const p = E.io(P(t, a + i * stag, a + i * stag + each));
    if (p > 0) it.paths.forEach(d => lines.push(`<path d="${d}" transform="translate(${n1(ox + it.x * sc)},${n1(top)}) scale(${sc.toFixed(4)})" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - p).toFixed(4)}"/>`));
    it.dots.forEach(([px, py]) => addDot(ox + (it.x + px) * sc, top + py * sc));
  });
  L.seps.forEach(s => addDot(ox + s * sc, top + cap / 2));
  if (rtl && o.ends !== false) [-LOGO.WORD_GAP / 2, L.total + LOGO.WORD_GAP / 2].forEach(e => addDot(ox + e * sc, top + cap / 2));
  const sw = LOGO.STROKE * sc / sc;      // stroke width is in glyph units (the path is scaled)
  const body = `<g fill="none" stroke="${NAVY}" stroke-width="${sw}" stroke-linejoin="miter" stroke-linecap="butt">${lines.join("")}</g>${dots.join("")}`;
  return op < 1 ? g(body, "", op) : body;
}
