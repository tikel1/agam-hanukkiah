/* Scenes 1-6. Each: (t, d, tg) = local seconds, scene length, global seconds. */
"use strict";

/* ---------- 1  יעקב אגם ---------- */
SCENES[1] = (t) => {
  const out = [], sw = 54, period = sw * 2, y0 = 330, h = 520, skew = 60, n = 18;
  for (let i = 0; i < n; i++) {
    const k = E.out(P(t, 3 + i * 0.1, 3.9 + i * 0.1)), x = i * period - (1 - k) * (i * period + 200);
    if (k > 0) out.push(poly([[x, y0], [x + sw, y0], [x + sw + skew, y0 + h], [x + skew, y0 + h]], BAND[i % BAND.length]));
  }
  const r = 250 * E.io(P(t, 7, 9)), dc = [960, 590];
  if (r > 0) {
    const cols = [F.coral, F.brick, F.rose], inner = [];
    for (let i = -2; i < 12; i++) { const x = dc[0] - 400 + i * period; inner.push(poly([[x, y0], [x + sw, y0], [x + sw + skew, y0 + h], [x + skew, y0 + h]], cols[((i % 3) + 3) % 3])); }
    out.push(circle(dc[0], dc[1], r, WHITE), clipped(`<circle cx="${dc[0]}" cy="${dc[1]}" r="${r}"/>`, inner.join("")));
  }
  const hx = lerp(2400, 1450, E.out(P(t, 5.6, 7.2)));
  out.push(hand(hx, 560, -8, 0.95));
  out.push(title(["יעקב", "אגם"], 1000, 110, 150, t, 1.5, { span: 2.5, dotSpan: 0.8 }));
  out.push(g(`<text x="1000" y="312" text-anchor="middle" direction="ltr" font-family="SO" font-size="40" fill="${NAVY}" letter-spacing="4">1928–2026</text>`, "", E.out(P(t, 4.2, 5.2))));   // v3: quiet, appears with the line about his passing
  const z = 1 + 0.03 * P(t, 0, 10);
  return g(out.join(""), `translate(960,540) scale(${z}) translate(-960,-540)`);
};

/* ---------- 2  פולימורף ---------- */
const ARC_Y = x => 838 - 18 * (1 - Math.pow(((x - 430) / 1060 - 0.5) / 0.5, 2));
function polymorph(f, open, x0 = 260, y0 = 340, width = 1400, height = 470) {
  const per = 116, n = Math.ceil(width / per), out = [], reds = [F.coral, F.brick], blues = [F.blue, F.periwinkle];
  for (let k = 0; k < n; k++) {
    const op = E.io(clamp(open * 1.7 - (k / n) * 0.7)); if (op <= 0.01) continue;
    const slot = x0 + k * per, cxs = slot + per / 2, ws = per * op;
    let x = cxs - ws / 2; const tooth = [];
    for (const [wid, col] of [[ws * f, reds[k % 2]], [ws * (1 - f), blues[k % 2]]]) {
      if (wid > 0.5) tooth.push(poly([[x, y0], [x + wid, y0 + 8], [x + wid, y0 + height - 8], [x, y0 + height]], col));
      x += wid;
    }
    tooth.push(rect(slot + per - 3 - (per - ws) / 2, y0 + 4, 6 * op, height - 8, WHITE));
    out.push(...tooth);
  }
  return out.join("");
}
function eye(x) {
  const arc = Array.from({ length: 12 }, (_, i) => circle(430 + i * 96.4, ARC_Y(430 + i * 96.4), 6, DOTS[i % 10])).join("");
  const y = ARC_Y(x);
  return arc + poly([[x - 34, y + 28], [x + 34, y + 28], [x, y - 22]], NAVY_D) + circle(x, y - 42, 16, NAVY_D);
}
SCENES[2] = (t) => {
  const th = t < 2 ? -35 : t < 4.5 ? lerp(-35, 0, E.io(P(t, 2, 4.5))) : t < 5.5 ? 0 : lerp(0, 35, E.io(P(t, 5.5, 8)));
  const f = clamp(0.5 - th / 70), ex = lerp(430, 1490, (th + 35) / 70);
  const sub = g(label("הרבה צורות", 960, 308, 44), "", E.out(P(t, 8.2, 9.2)));
  return polymorph(f, P(t, 0, 2)) + g(eye(ex), "", P(t, 0.8, 1.6)) + title(["פולימורף"], 960, 90, 140, t, 7.4, { span: 1.5, dotSpan: 0.6 }) + sub;
};

/* ---------- 3 + 4  the fountain (one shared drawing, so 3 -> 4 is a match cut) ---------- */
const FX = 960, FTOP = 250, FSC = 1.06;
const SIDE = [-1, 1, -1, 1, -1];
function phaseAt(T) {                       // integrated stripe speed (px) since the start of scene 3
  let s = 0; for (let u = 0; u < T; u += 0.05) s += (u < 11 ? 10 * P(u, 5, 6) : 10 + 16 * E.io(P(u, 11, 13))) * 0.05; return s;
}
function ringsDraw(o) {
  const out = [], sc = o.sc;
  for (let i = 4; i >= 0; i--) {
    const op = o.op ? o.op[i] : 1; if (op <= 0) continue;
    const dx = o.dx ? o.dx[i] : 0, ph = (o.phase || 0) * (i % 2 ? 1 : -1) * (i === 0 || i === 4 ? 0.5 : 1);
    let svg = stackRing(i, o.cx + dx, o.top, sc, { phase: ph });
    if (o.flash && o.flash[i] > 0) { const gm = stackRingGeom(i, o.top, sc); svg += poly(toothed(o.cx + dx, gm.y, gm.w, gm.h, Math.max(10, Math.floor(gm.w / 38))), WHITE, `opacity="${(o.flash[i] * 0.6).toFixed(2)}"`); }
    out.push(g(svg, "", op));
  }
  return out.join("");
}
SCENES[3] = (t, d, tg) => {
  const dx = [], op = [], flash = [];
  for (let i = 0; i < 5; i++) {
    const k = E.out(P(t, 0.3 + (4 - i) * 0.2, 1.3 + (4 - i) * 0.2)), w = RING_SPECS[i][0];
    dx.push(SIDE[i] * (1000 + w) * (1 - k)); op.push(1);
    flash.push(Math.sin(Math.PI * P(t, 7 + (4 - i) * 0.4, 7.6 + (4 - i) * 0.4)));
  }
  const bTop = FTOP + stackHeight(FSC) + 6;
  return basin(FX, bTop, 1100, P(t, 3.5, 5)) + ringsDraw({ cx: FX, top: FTOP, sc: FSC, dx, op, flash, phase: phaseAt(t) })
    + title(["אש", "ומים"], 960, 70, 130, t, 1, { span: 1.8, dotSpan: 0.8 });
};
const fireH = t => 150 * E.out(P(t, 4.5, 5.1)) + 40 * P(t, 5.1, 9);
SCENES[4] = (t, d, tg) => {
  const phase = phaseAt(t + 11), bTop = FTOP + stackHeight(FSC) + 6;
  const wet = waterJets(FX, bTop - 30, 700, 330, tg, E.io(P(t, 2.5, 4.5)));
  const fl = fireH(t), lean = 14 * Math.sin(2 * Math.PI * 0.8 * t) * P(t, 4.6, 5.4);
  return wet + basin(FX, bTop, 1100, 1) + ringsDraw({ cx: FX, top: FTOP, sc: FSC, phase }) + (fl > 1 ? flame(FX, FTOP + 6, fl, fl * 0.55, lean) : "")
    + title(["אש", "ומים"], 960, 70, 130, 99, 0, { op: 1 - E.io(P(t, 0, 0.7)) })
    + title(["1986"], 1640, 90, 100, t, 0.3, { span: 1.2, dotSpan: 0.6, rtl: false });
};

/* ---------- 5  חנוכה ---------- */
const CX = 1190, CBASE = 800, SRC = { x: 380, top: 560, sc: 0.62 };
const LIGHT_ORDER = [8, 7, 6, 5, 3, 2, 1, 0, 4];   // eight nights from the right, the shamash last
const candleX = i => CX + (i - 4) * 120;
SCENES[5] = (t, d, tg) => {
  const out = [], glide = E.io(P(t, 0, 1.0));
  const cx = lerp(FX, SRC.x, glide), top = lerp(FTOP, SRC.top, glide), sc = lerp(FSC, SRC.sc, glide);
  const fade = 1 - E.io(P(t, 0, 0.7)), bTop = FTOP + stackHeight(FSC) + 6;
  const srcOp = 1 - E.io(P(t, 5, 6.2));
  const camK = 1 + 0.22 * E.io(P(t, 5, 6.5)) - 0.22 * E.io(P(t, 9, 10.5));
  const left = [];
  if (fade > 0) left.push(g(waterJets(FX, bTop - 30, 700, 330, tg, 1) + basin(FX, bTop, 1100, 1), "", fade));
  left.push(ringsDraw({ cx, top, sc, op: [1, 1, fade, fade, fade], phase: phaseAt(t + 20) * fade }));
  const nlit = LIGHT_ORDER.map((_, k) => 1.5 + 0.35 * k);            // departure times
  const left_k = LIGHT_ORDER.filter((_, k) => t < nlit[k]).length / 9;
  const fh = lerp(190, 230, glide) * (0.15 + 0.85 * left_k) * (t < 1.5 ? 1 : 1);
  const ftop = stackRingGeom(0, top, sc).y + 6 * sc;
  if (fh > 2) left.push(flame(cx, ftop, fh * (0.7 + 0.3 * glide), fh * 0.55 * (0.7 + 0.3 * glide), 10 * Math.sin(t * 5)));
  out.push(g(left.join(""), "", srcOp));
  // candles
  const cs = [], dots = [];
  for (let i = 0; i < 9; i++) {
    const sham = i === 4, x = candleX(i), hh = (sham ? 250 : 160) * E.out(clamp(P(t, 1.2 + i * 0.06, 2.0 + i * 0.06)));
    const gold = E.io(P(t, 9 + Math.abs(i - 4) * 0.12, 10 + Math.abs(i - 4) * 0.12));
    const col = gold > 0.5 ? (i % 2 ? F.yellow : F.orange) : (sham ? F.periwinkle : F.blue);
    cs.push(rect(x - 20, CBASE - hh, 40, hh, col), rect(x - 30, CBASE - 18, 60, 18 * clamp(hh / 40), F.yellow));
    const k = LIGHT_ORDER.indexOf(i), dep = nlit[k], u = P(t, dep, dep + 0.9), tipY = CBASE - (sham ? 250 : 160) - 6;
    if (u > 0 && u < 1) { const e = E.io(u); dots.push(circle(lerp(SRC.x, x, e), lerp(ftop - 100, tipY, e) - 170 * Math.sin(Math.PI * e), 14 + (k % 3) * 3, DOTS[k % 10])); }
    if (u >= 1) { const l = E.back(P(t, dep + 0.9, dep + 1.3)) * (1 - E.io(P(t, 9, 10)));
      const lean = (i % 2 ? 5 : -5) * Math.sin(t * 5 + i), br = 1 + 0.08 * Math.sin(t * 4 + i * 1.3);
      cs.push(flame(x, tipY, (sham ? 78 : 66) * l * br, 38 * l, lean)); }
  }
  const rowSq = 1 - 0.85 * E.io(P(t, 9.3, 10.6)), rowOp = 1 - E.io(P(t, 10.2, 11.2));
  out.push(g(g(cs.join(""), `translate(0,${CBASE}) scale(1,${rowSq}) translate(0,${-CBASE})`, rowOp) + dots.join(""), `translate(${CX},${CBASE}) scale(${camK}) translate(${-CX},${-CBASE})`));
  // the big menorah
  const gr = P(t, 10, 13.6);
  if (gr > 0) {
    const ppl = person(700, 840, 90, F.periwinkle) + person(760, 840, 70, F.coral) + person(1180, 840, 85, F.teal);
    const pk = E.out(P(t, 13, 14.6));
    out.push(nyMenorah(960, 840, 520, gr) + g(ppl, `translate(${-300 * (1 - pk)},0)`, pk));
    out.push(g(label("החנוכייה הגדולה בעולם, ניו יורק", 960, 290, 54), "", E.out(P(t, 12, 13.2))));
  }
  out.push(title(["חנוכה"], 960, 80, 140, t, 0.7, { span: 1.6, dotSpan: 0.8 }));
  return out.join("");
};

/* ---------- 6  ללמוד ---------- */
const PAL = Object.values(F);
const palPos = i => [1560 + (i % 3) * 64, 330 + Math.floor(i / 3) * 70];
SCENES[6] = (t) => {
  const out = [], shift = E.io(P(t, 6.8, 8.2)) * -160, nbOp = 1 - E.io(P(t, 6.8, 8.2));
  const nb = [rect(520, 250, 880, 630, F.periwinkle), rect(560, 272, 800, 586, WHITE)];
  for (let i = 0; i < 14; i++) nb.push(circle(548, 300 + i * 40, 11, F.light_blue));
  const st = [], used = new Set();
  for (let k = 0; k < 10; k++) {
    const a = 2 + k * 0.5, grow = E.io(P(t, a + 0.3, a + 0.85)), col = SPECTRUM[k], pi = PAL.indexOf(col);
    if (grow > 0) st.push(rect(600 + k * 80, 272, 40, 586 * grow, col));
    if (t > a - 0.2) used.add(pi);
  }
  nb.push(clipped(`<rect x="560" y="272" width="800" height="586"/>`, st.join("")));
  const coverK = 1 - E.io(P(t, 0, 1.6));
  nb.push(g(rect(520, 250, 880, 630, F.periwinkle) + Array.from({ length: 14 }, (_, i) => circle(548, 300 + i * 40, 11, F.light_blue)).join(""), `translate(520,0) scale(${coverK.toFixed(3)},1) translate(-520,0)`, coverK > 0.01 ? 1 : 0));
  out.push(g(nb.join(""), `translate(${shift},0)`, nbOp));
  // palette dots (the ones used fly into their stripe)
  PAL.forEach((c, i) => {
    const [px, py] = palPos(i);
    const k = SPECTRUM.indexOf(c);
    if (k >= 0 && k < 10) {
      const a = 2 + k * 0.5 - 0.2, u = E.io(P(t, a, a + 0.5));
      if (u < 1) out.push(circle(lerp(px, 620 + k * 80 + shift * 0, u), lerp(py, 272, u) - 120 * Math.sin(Math.PI * u), 22 * (1 - 0.5 * u), c));
      return;
    }
    const tgt = [590, 290 + (i % 5) * 120 + 48]; const u = E.io(P(t, 7.6 + (i % 5) * 0.2, 8.9 + (i % 5) * 0.2));
    out.push(circle(lerp(px, tgt[0], u), lerp(py, tgt[1], u), lerp(22, 14, u), c));
  });
  for (let i = 0; i < 5; i++) {
    const k = E.out(P(t, 7 + i * 0.25, 8.4 + i * 0.25)), x = lerp(1960, 650, k);
    out.push(rect(x, 290 + i * 120, 640, 96, WHITE) + stripes(x + 8, 298 + i * 120, 624, 80, [0, 1, 2].map(q => SPECTRUM[(i * 3 + q) % 12]), 40, { white: WHITE }));
  }
  out.push(title(["ללמוד"], 700, 80, 130, t, 0.5, { span: 1.6, dotSpan: 0.6 }));
  out.push(g(label("ככה התחלנו:", 1250, 170, 56), "", E.out(P(t, 0.3, 1.2))));
  return out.join("");
};
