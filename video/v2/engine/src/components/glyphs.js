/* Line-and-dot lettering data. Base glyphs come from submission/logo.py; the others were designed for v1 in the same
   spirit (video/animation/js/glyphs.js): straight lines only, slight slants, a coloured dot on a stroke's top end.
   Glyph box: height 100, y grows downwards. Entry: [width, [svg paths], [[dotX, dotY], ...]]. */
export const LOGO = Object.freeze({ CAP: 100, STROKE: 7.5, DOT_R: 10.5, LETTER_GAP: 26, WORD_GAP: 62 });

export const GLYPHS = Object.freeze({
  // from submission/logo.py
  'ח': [58, ['M0,100 L12,0 H58 V100'], [[58, 0]]],
  'נ': [44, ['M8,0 H44 V93 L0,100'], [[8, 0]]],
  'ו': [0, ['M0,0 V100'], [[0, 0]]],
  'כ': [56, ['M0,0 H38 L56,50 L38,95 L0,100'], [[0, 0]]],
  'י': [0, ['M0,0 V40'], [[0, 0]]],
  'ת': [64, ['M0,0 H64 V100', 'M14,0 V100 H0'], [[0, 0]]],
  'א': [70, ['M0,0 L70,100', 'M64,0 L44,62', 'M28,40 L4,100'], [[0, 0], [64, 0]]],
  'ש': [70, ['M0,0 L12,100 H70 V0', 'M36,0 L40,100'], [[0, 0], [36, 0], [70, 0]]],
  'מ': [90, ['M0,0 L32,48', 'M14,82 L56,0 L90,94 L40,99'], [[0, 0], [56, 0]]],
  'ם': [60, ['M0,0 H60 V100 H0 Z'], [[0, 0], [60, 0]]],
  // the museum logo gimel
  'ג': [60, ['M26,0 L60,98', 'M43,50 L0,100'], [[26, 0]]],
  // designed for v1, same rules (ours, not Agam's)
  'ע': [58, ['M58,0 L52,48 L8,100', 'M0,0 L52,48'], [[0, 0], [58, 0]]],
  'ק': [56, ['M0,0 H56 L60,100', 'M8,36 L4,128'], [[0, 0]]],          // redrawn for v2 (user: the old one read badly)
  'ט': [62, ['M0,0 V100 H62 V0 H34 L28,40'], [[0, 0]]],                 // for "אמנות קינטית" (v2)
  'ן': [20, ['M0,0 H20 V128'], [[0, 0]]],                              // final nun: for the names on the end card
  'צ': [58, ['M4,0 L52,100 H0', 'M58,0 L38,52'], [[4, 0], [58, 0]]],
  "'": [6, ['M6,0 L0,26'], []],
  ',': [6, ['M6,86 L0,112'], []],
  '?': [40, ['M0,14 L14,0 H40 V44 L20,56 V74'], [[20, 100]]],
  '!': [0, ['M0,0 V72'], [[0, 100]]],
  'ב': [52, ['M0,0 H52 V98', 'M-4,98 L68,102'], [[0, 0]]],
  'פ': [50, ['M0,0 H50 V96 L0,100', 'M0,0 L4,42 H26'], [[0, 0]]],
  'ף': [50, ['M0,0 H50 V118', 'M0,0 L4,42 H28'], [[0, 0]]],
  'ל': [46, ['M8,-34 V30 L46,42 V100 H0'], [[8, -34]]],
  'ר': [46, ['M0,0 H46 L50,100'], [[0, 0]]],
  'ד': [54, ['M0,0 H54 V100'], [[0, 0], [54, 0]]],
  'ה': [56, ['M0,0 H56 V100', 'M4,32 L0,100'], [[0, 0]]],
  'ס': [58, ['M14,0 H52 L58,60 L44,100 H6 L0,40 Z'], [[14, 0]]],
});

/** Digits read left to right. */
export const DIGITS = Object.freeze({
  '1': [26, ['M0,22 L26,0 V100'], [[26, 0]]],
  '9': [44, ['M0,0 H44 V100 M0,0 V52 H44'], [[0, 0]]],
  '8': [44, ['M0,0 H44 V100 H0 Z M0,50 H44'], [[0, 0]]],
  '6': [44, ['M44,0 H0 V100 H44 V52 H0'], [[44, 0]]],
  '4': [48, ['M0,0 V56 H48', 'M34,0 V100'], [[0, 0], [34, 0]]],
  '0': [44, ['M6,0 H44 L38,100 H0 Z'], [[6, 0]]],
  '2': [44, ['M0,0 H44 V50 H0 V100 H44'], [[0, 0]]],
  '–': [34, ['M0,52 H34'], []],
  // Latin capitals for "AI"
  'A': [70, ['M0,100 L35,0 L70,100', 'M15,60 H55'], [[35, 0]]],
  'I': [0, ['M0,0 V100'], [[0, 0]]],
});

/** Parses a path made of M / L / H / V / Z into polylines: [{ points: [[x, y], ...], closed }]. */
export function parsePath(d) {
  const tokens = d.match(/[MLHVZ]|-?\d+(?:\.\d+)?/g);
  if (!tokens) throw new Error(`glyph path has no commands: "${d}"`);
  const lines = [];
  let current = null, command = null, x = 0, y = 0, i = 0;
  while (i < tokens.length) {
    if (/[MLHVZ]/.test(tokens[i])) { command = tokens[i++]; if (command !== 'Z') continue; }
    if (command === 'Z') { if (current) current.closed = true; command = null; continue; }
    if (command === 'M') { x = +tokens[i++]; y = +tokens[i++]; current = { points: [[x, y]], closed: false }; lines.push(current); command = 'L'; continue; }
    if (command === 'L') { x = +tokens[i++]; y = +tokens[i++]; }
    else if (command === 'H') { x = +tokens[i++]; }
    else if (command === 'V') { y = +tokens[i++]; }
    else throw new Error(`glyph path: unexpected token "${tokens[i]}" in "${d}"`);
    current.points.push([x, y]);
  }
  return lines;
}

/** Lays words out in glyph units. Hebrew runs right to left (rtl = true); digits left to right.
    Returns { items: [{ ch, x, width, lines, dots }], separators: [x], total }. */
export function layoutTitle(words, rtl = true) {
  const table = rtl ? GLYPHS : DIGITS;
  const items = [], separators = [];
  let x = 0;
  words.forEach((word, wordIndex) => {
    if (wordIndex) { separators.push(x + LOGO.WORD_GAP / 2); x += LOGO.WORD_GAP; }
    [...word].forEach((ch, charIndex) => {
      if (charIndex) x += LOGO.LETTER_GAP;
      const glyph = table[ch] || GLYPHS[ch] || DIGITS[ch];   // a digit inside a Hebrew word (ב'1) and the reverse
      if (!glyph) throw new Error(`no line-and-dot glyph for "${ch}"`);
      items.push({ ch, x, width: glyph[0], lines: glyph[1].flatMap(parsePath), dots: glyph[2] });
      x += glyph[0];
    });
  });
  const total = x;
  if (!rtl) return { items, separators, total };
  return {
    items: items.map((item) => ({ ...item, x: total - item.x - item.width })),
    separators: separators.map((s) => total - s),
    total,
  };
}
