/* Scenes 7-11. Each: (t, d, tg) = local seconds, scene length, global seconds. */
"use strict";

/* ---------- 7  בינה מלאכותית ---------- */
SCENES[7] = (t) => {
  const out = [], rings = [], color = [];
  for (let i = 0; i < 5; i++) { rings.push(P(t, (4 - i) * 0.55, (4 - i) * 0.55 + 0.9)); color.push(E.io(P(t, 3.2 + (4 - i) * 0.5, 4.4 + (4 - i) * 0.5))); }
  const cmix = Math.max(...color);
  const sheetK = E.out(P(t, 2.6, 3.6));
  if (sheetK > 0) out.push(g(rect(250, 420, 330, 300, WHITE) + stripes(262, 432, 306, 276, SPECTRUM, 34, { white: WHITE }), `translate(${-80 * (1 - sheetK)},0)`, sheetK));
  out.push(hanukkiah(960, 250, 0.62, { rings, color, cands: P(t, 2.3, 3.3), candCol: mixHex(PALE[0], F.blue, cmix) }));
  out.push(title(["בינה"], 1180, 80, 130, t, 0.3, { span: 1.6, dotSpan: 0.6 }));
  out.push(g(label("מלאכותית בנתה:", 740, 170, 54), "", E.out(P(t, 0.2, 1.2))));
  out.push(g(label("דגמים  ·  צבעים  ·  לוגו", 960, 872, 46), "", E.out(P(t, 5.5, 6.5))));
  out.push(title(["אש", "ומים"], 1560, 480, 70, t, 6, { span: 2.6, dotSpan: 0.9 }));
  return out.join("");
};

/* ---------- 8  שתי תמונות ---------- */
SCENES[8] = (t, d, tg) => {
  const out = [], R3C = 491, w = 1300, h = w * 170 / 760;
  const z = E.io(P(t, 0, 1.4)), sc = lerp(0.62, w / 760, z), cy = lerp(250 + R3C * 0.62, 520, z), top = cy - R3C * sc;
  const side = 1 - E.io(P(t, 0, 0.9));
  if (side > 0) {   // plan sheet and logo of scene 7 leave
    out.push(g(rect(250, 420, 330, 300, WHITE) + stripes(262, 432, 306, 276, SPECTRUM, 34, { white: WHITE }) + title(["אש", "ומים"], 1560, 480, 70, 99, 0), "", side));
    out.push(g(label("דגמים  ·  צבעים  ·  לוגו", 960, 872, 46) + title(["בינה"], 1180, 80, 130, 99, 0) + label("מלאכותית בנתה:", 740, 170, 54), "", side));
  }
  const others = 1 - E.io(P(t, 0.3, 1.2));
  const hk = hanukkiah(960, top, sc, { cands: 1 });
  out.push(g(hk, "", others > 0.02 ? 1 : 0));
  const u = E.io(P(t, 1.2, 3.6)) + E.io(P(t, 4.2, 6.6));
  const art = u < 1 ? ringMix("A", "B", 1 - u, 960, cy - h / 2, w, h) : ringMix("B", "C", 2 - u, 960, cy - h / 2, w, h);
  out.push(g(ringCloseUp(960, cy - h / 2, w, h, art), "", E.io(P(t, 0.6, 1.4))));
  out.push(g(eye(lerp(480, 1440, u / 2)), "", E.out(P(t, 1, 1.8))));
  return out.join("");
};

/* ---------- 9  הדפסה ---------- */
function printer(cx, nozzleY, headX) {
  return rect(cx - 520, 190, 36, 600, F.periwinkle) + rect(cx + 484, 190, 36, 600, F.periwinkle)
    + rect(cx - 520, nozzleY - 90, 1040, 34, F.blue) + rect(headX - 30, nozzleY - 56, 60, 30, F.blue)
    + poly([[headX - 30, nozzleY - 26], [headX + 30, nozzleY - 26], [headX, nozzleY + 4]], F.orange) + rect(cx - 600, 790, 1200, 40, F.grey);
}
const bottle = (x, y, s) => g(rect(x - 14, y - 150, 28, 44, F.light_blue) + poly([[x - 14, y - 106], [x + 14, y - 106], [x + 44, y - 60], [x + 44, y + 80], [x - 44, y + 80], [x - 44, y - 60]], F.light_blue) + rect(x - 44, y - 10, 88, 40, F.mint), `translate(${x},${y + 80}) scale(${s}) translate(${-x},${-y - 80})`);
SCENES[9] = (t) => {
  const out = [], cols = [F.coral, F.yellow, F.teal, F.blue], p = E.io(P(t, 2.6, 7)), PX = 800, RING_W = 608, RING_H = 136;
  const head = PX + 260 * Math.sin(2 * Math.PI * 0.55 * t) * (p > 0 && p < 1 ? 1 : 0);
  const nozzleY = 790 - RING_H * p - 8, rec = P(t, 1, 2.4);
  const stackP = P(t, 7, 8.4);
  const printed = stackP > 0 ? 0 : 1;
  if (stackP <= 0) out.push(printer(PX, nozzleY, head));
  else out.push(rect(PX - 600, 790, 1200, 40, F.grey));
  if (printed) out.push(ring(PX, 790 - RING_H, RING_W, RING_H, cols, 30, { teeth: 18, layers: p }));
  else {      // the finished ring lifts into the stack of five and the rest join it
    const ease = E.io(stackP), s = 0.8, top0 = 370, gm = stackRingGeom(2, top0, s);
    const ringY = lerp(790 - RING_H, gm.y, ease);
    const later = i => E.out(P(t, 7.4 + (i === 3 ? 0 : i === 4 ? 0.3 : i === 1 ? 0.6 : 0.9), 8.6 + (i === 3 ? 0 : i === 4 ? 0.3 : i === 1 ? 0.6 : 0.9)));
    for (const i of [4, 3, 1, 0]) { const k = later(i); if (k > 0) out.push(g(stackRing(i, PX, top0, s, { layers: 1 }), `translate(${(i % 2 ? 1 : -1) * 500 * (1 - k)},${i < 2 ? -300 * (1 - k) : 0})`, k)); }
    out.push(ring(PX, ringY, RING_W, RING_H, cols, 30, { teeth: 18, layers: 1 }));
  }
  // the used bottle becomes the thread
  const bx = lerp(-150, 1500, E.out(P(t, 0.2, 1.4))), shrink = 1 - E.io(P(t, 2.2, 3.0));
  if (t < 3.1) out.push(bottle(bx, 500, 0.9 * Math.max(0.02, shrink)));
  if (t > 2.3 && t < 7.4) {     // the thread runs from the recycle mark along the gantry to the print head
    const k = P(t, 2.3, 3.2) * (1 - E.io(P(t, 6.8, 7.4))), ty = nozzleY - 73, col = cols[Math.floor(t * 6) % 4];
    const pts = [[1400, 572], [1400, ty], [head, ty]], len = [Math.abs(ty - 572), Math.abs(1400 - head)], tot = len[0] + len[1];
    const reach = tot * k, a = Math.min(reach, len[0]), b = Math.max(0, reach - len[0]);
    if (k > 0) out.push(line(1400, 572, 1400, lerp(572, ty, a / Math.max(1, len[0])), col, 9), line(1400, ty, lerp(1400, head, b / Math.max(1, len[1])), ty, col, 9));
  }
  out.push(recycle(1500, 500, 140, [F.green, F.teal, F.mint], rec));
  out.push(g(label("פלסטיק ממוחזר", 1500, 720, 46), "", E.out(P(t, 1.4, 2.4))));
  out.push(title(["הדפסה"], 960, 60, 120, t, 0.5, { span: 1.6, dotSpan: 0.6 }));
  return out.join("");
};

/* ---------- 10  408 ---------- */
SCENES[10] = (t) => {
  const out = [], cardFade = 1 - E.io(P(t, 7, 8));
  const cardX = 560, cardY = 330, cw = 800, ch = 520, sw = 42;
  const st = []; let bx = cardX + 40, by = cardY, nk = 0;
  for (let k = 0; k < 10; k++) {
    const a = 0.3 + k * 0.5, gk = E.io(P(t, a, a + 0.5)), x = cardX + k * 2 * sw * 1.0;
    if (gk > 0) st.push(rect(x, cardY, sw, ch * gk, SPECTRUM[k % 12]));
    if (gk > 0 && gk < 1) { bx = x + sw / 2; by = cardY + ch * gk; nk = k; }
    else if (gk >= 1 && k === 9) { bx = x + sw / 2; by = cardY + ch; }
  }
  const card = rect(cardX, cardY, cw, ch, WHITE) + clipped(`<rect x="${cardX}" y="${cardY}" width="${cw}" height="${ch}"/>`, st.join(""));
  const tip = [bx + 6, by + 4], handleEnd = [tip[0] + 257, tip[1] + 36];
  const wob = 5 * Math.sin(t * 9);
  out.push(g(card + brush(tip[0] + 70, tip[1] + wob, 8) + hand(handleEnd[0] + 150, handleEnd[1] - 143, 0, 1.0) + hand(430, 800, 6, 0.8, NAVY_D, true), "", cardFade));
  out.push(title(["408"], 960, 70, 130, t, 5, { span: 1.1, dotSpan: 0.7, rtl: false }));
  out.push(g(label("פאות צבועות ביד", 960, 270, 56), "", E.out(P(t, 5.6, 6.6))));
  const rings = [0, 1, 2, 3, 4].map(i => P(t, 7.2 + (4 - i) * 0.4, 8.0 + (4 - i) * 0.4));
  out.push(hanukkiah(960, 300, 0.66, { rings, cands: P(t, 8.9, 9.8) }));
  return out.join("");
};

/* ---------- 11  חנוכיית אש ומים ---------- */
SCENES[11] = (t) => {
  const out = [], z = E.io(P(t, 0.2, 1.8)), ph = E.out(P(t, 0.3, 1.6));
  out.push(rect(0, 0, W, H, NAVY));
  DOTS.forEach((c, i) => { const k = E.out(P(t, 0.2 + i * 0.1, 1.3 + i * 0.1)), fx = i % 2 ? 2100 : -200, x = 120 + i * 100;
    out.push(circle(lerp(fx, x, k), 70 + (i % 3) * 36 + 6 * Math.sin(t * 1.6 + i), 14, c)); });
  out.push(hanukkiah(lerp(960, 520, z), lerp(300, 110, z), lerp(0.66, 0.68, z), { lit: P(t, 1.0, 3.0), flick: Math.sin(2 * Math.PI * 0.8 * t) }));
  out.push(g(rect(1040, 0, 880, H, PAPER) + stripes(1040, 0, 64, H, BAND, 32), `translate(${880 * (1 - ph)},0)`));
  out.push(title(["חנוכיית"], 1500, 140, 100, t, 2, { span: 1.4, dotSpan: 0.6 }));
  out.push(title(["אש", "ומים"], 1500, 330, 100, t, 3, { span: 1.6, dotSpan: 0.7 }));
  out.push(g(label("מחווה לאמן יעקב אגם", 1500, 520, 44), "", E.out(P(t, 3.6, 4.6))));   // v3: tribute line, as in the logo
  const nm = E.out(P(t, 4, 5));
  out.push(g(label("נעמי קפלן ב'1", 1500, 625, 54) + label("ליבי קפלן ד'1", 1500, 695, 54) + label("בית ספר כצנלסון, גבעתיים", 1500, 757, 42), "", nm));
  out.push(recycle(1500, 840, 30, [F.green, F.teal, F.mint], P(t, 4.5, 7)));
  const ins = E.io(P(t, 5, 7));
  out.push(g(rect(52, 552, 224, 260, WHITE) + `<svg x="60" y="560" width="208" height="244" viewBox="250 10 900 1040"><image href="assets/night_front.png" width="1400" height="1400" style="filter:brightness(2.6) saturate(1.2)"/></svg>`, "", ins));
  return out.join("");
};
