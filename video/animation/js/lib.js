/* Core helpers: easing, palette, SVG string builders and flat Agam-style shapes. Global scope on purpose (no build step). */
"use strict";
const W = 1920, H = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const P = (t, a, b) => clamp((t - a) / (b - a));           // progress of t between a and b
const lerp = (a, b, k) => a + (b - a) * k;
const E = {
  io: x => x * x * x * (x * (6 * x - 15) + 10),            // smootherstep
  out: x => 1 - Math.pow(1 - x, 3),
  in: x => x * x * x,
  back: x => { const c = 2.2; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
  sine: x => 0.5 - 0.5 * Math.cos(Math.PI * x),
};

const PAPER = "#F7F5EE", WHITE = "#FFFFFF", NAVY = "#232C5E", NAVY_D = "#2B2F6B";
const F = { white: "#F4F1E4", yellow: "#F2C94C", orange: "#E8893F", coral: "#E8655C", brick: "#A8322A", rose: "#DC8A86",
  lilac: "#9A8CC0", periwinkle: "#7484C4", light_blue: "#A3C1E0", blue: "#3E5FB0", navy: "#2B2F6B", mint: "#A8DDB5",
  teal: "#3E8F7C", green: "#4E9E5E", grey: "#A9B3B6" };
const SPECTRUM = ["yellow", "orange", "coral", "brick", "rose", "lilac", "periwinkle", "blue", "light_blue", "mint", "teal", "green"].map(k => F[k]);
const BAND = [F.blue, F.yellow, F.coral, F.teal, F.lilac, F.orange, F.light_blue, F.green];
const DOTS = ["#E4432F", "#F6D21C", "#1FA3A8", "#6A5EA8", "#6BB7E6", "#1B7F3E", "#A81F2A", "#4F63B0", "#CFA3D1", "#F39A1E"];
const FLAME_OUT = "#F39A1E", FLAME_IN = "#F6D21C";

const n1 = v => (Math.round(v * 10) / 10);
const poly = (pts, fill, ex = "") => `<polygon points="${pts.map(p => n1(p[0]) + "," + n1(p[1])).join(" ")}" fill="${fill}" ${ex}/>`;
const rect = (x, y, w, h, fill, ex = "") => (w <= 0 || h <= 0) ? "" : `<rect x="${n1(x)}" y="${n1(y)}" width="${n1(w)}" height="${n1(h)}" fill="${fill}" ${ex}/>`;
const circle = (cx, cy, r, fill, ex = "") => r <= 0 ? "" : `<circle cx="${n1(cx)}" cy="${n1(cy)}" r="${n1(r)}" fill="${fill}" ${ex}/>`;
const line = (x1, y1, x2, y2, col, w, ex = "") => `<line x1="${n1(x1)}" y1="${n1(y1)}" x2="${n1(x2)}" y2="${n1(y2)}" stroke="${col}" stroke-width="${n1(w)}" ${ex}/>`;
const g = (inner, tf = "", op = 1) => (op <= 0 || inner === "") ? "" : `<g${tf ? ` transform="${tf}"` : ""}${op < 1 ? ` opacity="${op.toFixed(3)}"` : ""}>${inner}</g>`;
let clipN = 0;
const clipped = (shape, inner) => { const id = "c" + (++clipN); return `<clipPath id="${id}">${shape}</clipPath><g clip-path="url(#${id})">${inner}</g>`; };
const label = (text, x, y, size = 44, anchor = "middle", fill = NAVY, ex = "") =>
  `<text x="${x}" y="${y}" text-anchor="${anchor}" direction="rtl" font-family="SO" font-size="${size}" fill="${fill}" ${ex}>${text}</text>`;
const mixHex = (a, b, k) => { const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16); let o = 0;
  for (const s of [16, 8, 0]) o = (o << 8) | Math.round(lerp((pa >> s) & 255, (pb >> s) & 255, k)); return "#" + (o >>> 0).toString(16).padStart(6, "0"); };

/* ---- stripes: colour then white; "grow" in 0..1 reveals stripes top to bottom (per-stripe stagger by `stag`) ---- */
function stripes(x, y, w, h, cols, sw, o = {}) {
  const white = o.white || PAPER, wr = o.wr === undefined ? 1 : o.wr, phase = o.phase || 0, skew = o.skew || 0;
  const out = []; let cx = x - phase, i = 0, k = 0;
  while (cx < x + w) {
    const isCol = i % 2 === 0, step = isCol ? sw : sw * wr;
    let hh = h, dy = 0, grow = 1;
    if (o.grow !== undefined && isCol) { const n = o.n || 10; grow = clamp(o.grow * (1 + (o.stag || 0.5) * 1) - (k / n) * (o.stag || 0.5)); grow = E.io(clamp(grow)); hh = h * grow; k++; }
    else if (o.grow !== undefined) hh = h * (k > 0 ? grow : 1) * 0 + 0;
    const col = isCol ? cols[(i >> 1) % cols.length] : white;
    if (hh > 0.5) out.push(skew ? poly([[cx, y], [cx + step, y], [cx + step + skew * hh / h, y + hh], [cx + skew * hh / h, y + hh]], col) : rect(cx, y, step + 0.6, hh, col));
    cx += step; i++;
  }
  return out.join("");
}

/* ---- toothed rings ---- */
function toothed(cx, top, w, h, teeth, amp = 12) {
  const x0 = cx - w / 2, st = w / teeth, up = [], lo = [];
  for (let i = 0; i <= teeth; i++) { up.push([x0 + i * st, top + (i % 2 ? amp : 0)]); lo.push([x0 + w - i * st, top + h - (i % 2 ? amp : 0)]); }
  return up.concat(lo);
}
function ring(cx, top, w, h, cols, sw, o = {}) {
  const outline = poly(toothed(cx, top, w, h, o.teeth || 20), WHITE);
  if (o.layers === undefined) return clipped(outline, stripes(cx - w / 2, top - 2, w, h + 4, cols, sw, { phase: o.phase || 0, wr: 0.3 }));
  const rows = []; let y = top + h + 2, i = 0;
  while (y > top + h * (1 - o.layers)) { rows.push(rect(cx - w / 2, y - 11, w, 11, cols[i % cols.length])); y -= 11; i++; }
  return clipped(outline, rows.join(""));
}
const RING_SPECS = [[230, 92, 0], [390, 112, 3], [760, 170, 6], [390, 112, 9], [230, 92, 1]];
const ringCols = off => [0, 1, 2, 3].map(k => SPECTRUM[(off + k) % 12]);
/* one ring of the stack i (0 = top) at stack origin (cx, top0); returns {svg, y, h} */
function stackRingGeom(i, top0, sc) { let y = top0; for (let k = 0; k < i; k++) y += (RING_SPECS[k][1] - 14) * sc; return { y, w: RING_SPECS[i][0] * sc, h: RING_SPECS[i][1] * sc }; }
function stackRing(i, cx, top0, sc, o = {}) {
  const { y, w, h } = stackRingGeom(i, top0, sc), off = RING_SPECS[i][2];
  return ring(cx, y, w, h, o.cols || ringCols(off), Math.max(8, w / 22), { phase: o.phase || 0, teeth: Math.max(10, Math.floor(w / 38)), layers: o.layers });
}
const stackHeight = sc => RING_SPECS.reduce((s, r) => s + r[1], 0) * sc - 14 * sc * 4;

/* ---- flame, water, people ---- */
function flame(cx, base, h, w, lean = 0) {
  const o = [[cx + lean, base - h], [cx + w * 0.5, base - h * 0.38], [cx + w * 0.34, base], [cx - w * 0.34, base], [cx - w * 0.5, base - h * 0.38]];
  const i = [[cx + lean * 0.7, base - h * 0.62], [cx + w * 0.26, base - h * 0.24], [cx + w * 0.18, base], [cx - w * 0.18, base], [cx - w * 0.26, base - h * 0.24]];
  return poly(o, FLAME_OUT) + poly(i, FLAME_IN);
}
function waterJets(cx, base, spread, height, t, rise = 1, n = 7) {
  const cols = [F.blue, F.light_blue, F.teal, F.periwinkle], out = [];
  for (let i = 0; i < n; i++) for (const side of [-1, 1]) {
    const x = cx + side * (spread * 0.55 + i * spread * 0.11);
    const wave = 0.78 + 0.22 * Math.sin(t * 2.4 + i * 0.9 + (side > 0 ? 1.7 : 0));
    const hh = height * (1 - 0.13 * i) * wave * rise, topY = base - hh, sh = side * 34 * (hh / height);
    if (hh < 4) continue;
    out.push(poly([[x - 9, base], [x + 9, base], [x + 9 + sh, topY], [x - 9 + sh, topY]], cols[(i + (side > 0 ? 1 : 0)) % 4]));
    out.push(circle(x + sh, topY - 10, 13 * clamp(rise * 2), cols[(i + 1) % 4]));
  }
  return out.join("");
}
function basin(cx, y, w, p = 1) {
  const cols = [F.blue, F.light_blue, F.teal], n = Math.floor(w / 26) + 1, out = [];
  for (let i = 0; i < n; i++) {   // poured in from left to right
    const k = E.out(clamp(p * 1.6 - (i / n) * 0.6)); if (k <= 0) continue;
    const off = i % 2 ? 10 : 0, hh = (44 - off) * k;
    out.push(rect(cx - w / 2 + i * 26, y + off + (44 - off) - hh, 16, hh, cols[i % 3]));
  }
  return out.join("");
}
const person = (x, base, h, c) => circle(x, base - h + h * 0.11, h * 0.11, c) +
  poly([[x - h * 0.13, base - h * 0.74], [x + h * 0.13, base - h * 0.74], [x + h * 0.2, base], [x - h * 0.2, base]], c);

function hand(x, y, angle = -8, scale = 1, colour = NAVY_D, flip = false) {
  const s = [poly([[300, 108], [640, 80], [640, 310], [300, 280]], colour), poly([[120, 112], [310, 96], [320, 282], [140, 262]], NAVY),
    poly([[-170, 128], [130, 120], [130, 170], [-170, 158]], colour), poly([[20, 178], [135, 172], [140, 214], [24, 212]], colour),
    poly([[34, 220], [140, 218], [142, 254], [40, 250]], colour), poly([[52, 260], [144, 258], [144, 290], [60, 284]], colour)];
  return `<g transform="translate(${x},${y}) rotate(${angle}) scale(${flip ? -scale : scale},${scale})">${s.join("")}</g>`;
}
const brush = (x, y, angle = 35, colour = F.coral) => `<g transform="translate(${x},${y}) rotate(${angle})">${rect(0, -8, 260, 16, F.yellow)}${poly([[-46, -14], [0, -10], [0, 10], [-46, 14], [-70, 0]], colour)}</g>`;

/* gold menorah; g = growth 0..1 (stem first, then arms from the middle outwards) */
function nyMenorah(cx, base, h, gr = 1) {
  const gold = F.yellow, goldD = F.orange, out = [];
  const foot = E.out(P(gr, 0, 0.2)), stem = E.out(P(gr, 0.05, 0.4));
  out.push(poly([[cx - h * 0.22 * foot, base], [cx + h * 0.22 * foot, base], [cx + h * 0.12 * foot, base - h * 0.08], [cx - h * 0.12 * foot, base - h * 0.08]], goldD));
  out.push(rect(cx - h * 0.025, base - h * stem * 0.93 - h * 0.07 * stem, h * 0.05, h * 0.93 * stem, gold));
  for (let k = 0; k < 4; k++) {
    const a = E.io(P(gr, 0.3 + k * 0.15, 0.55 + k * 0.15)); if (a <= 0) continue;
    for (const side of [-1, 1]) {
      const tx = cx + side * h * (0.12 + 0.11 * k), ty = base - h * (0.62 + 0.09 * k);
      const bx = cx + side * h * 0.03, by = base - h * 0.2;
      const ex = lerp(bx, tx, a), ey = lerp(by, ty, a);
      out.push(poly([[bx - side * h * 0.01, by], [bx + side * h * 0.02, by], [ex + side * h * 0.02, ey], [ex - side * h * 0.02, ey]], k % 2 ? gold : goldD));
      out.push(rect(ex - h * 0.03, ey - h * 0.035 * a, h * 0.06, h * 0.035 * a, gold));
    }
  }
  return out.join("");
}

function recycle(cx, cy, r, cols, p = 1) {     // p: how much of the three arrows is drawn (each arrow in turn)
  const pts = [[cx, cy - r], [cx + r * 0.87, cy + r * 0.5], [cx - r * 0.87, cy + r * 0.5]], out = [];
  for (let i = 0; i < 3; i++) {
    const k = E.io(clamp(p * 3 - i)); if (k <= 0) continue;
    const a = pts[i], b = pts[(i + 1) % 3], len = 0.75 * k;
    const mx = a[0] + (b[0] - a[0]) * len, my = a[1] + (b[1] - a[1]) * len;
    out.push(line(a[0], a[1], mx, my, cols[i], r * 0.16));
    if (k > 0.95) {
      const nx = (b[1] - a[1]) / 3.2, ny = -(b[0] - a[0]) / 3.2, tip = [a[0] + (b[0] - a[0]) * 0.97, a[1] + (b[1] - a[1]) * 0.97];
      out.push(poly([[mx + nx, my + ny], [mx - nx, my - ny], tip], cols[i]));
    }
  }
  return out.join("");
}

/* ---- the hanukkiah redrawn flat ----
   o: {rings:[p0..p4] build 0..1 (index 0 = top ring), color:[c0..c4] painted 0..1 left-to-right sweep, cands: 0..1,
       lit: 0..1 (flame size), flick: -1..1, phase, mono} */
const PALE = ["#CFCBBE", "#E6E3D8"];
const CAND_XS = [-330, -255, -180, -100, 100, 180, 255, 330];
function hanukkiah(cx, top, sc, o = {}) {
  const rings = o.rings || [1, 1, 1, 1, 1], color = o.color || [1, 1, 1, 1, 1], parts = [];
  const y3 = 230 + 78 + 98;
  for (let i = 4; i >= 0; i--) {            // bottom ring is built first
    const bp = rings[i]; if (bp <= 0) continue;
    const ease = E.out(bp), geom = stackRingGeom(i, 230, 1), ry = -(1 - ease) * 60;
    const monoSvg = stackRing(i, 0, 230, 1, { cols: PALE });
    const col = color[i];
    let inner = g(monoSvg);
    if (col > 0) {
      const w = RING_SPECS[i][0], cut = -w / 2 + w * col;
      inner += clipped(`<rect x="${-w / 2 - 4}" y="${geom.y - 4}" width="${w * col + 4}" height="${geom.h + 8}"/>`, stackRing(i, 0, 230, 1, { phase: o.phase ? o.phase[i] : 0 }));
    }
    parts.push(g(inner, `translate(0,${ry})`, clamp(bp * 3)));
  }
  const cands = [], ca = o.cands === undefined ? 1 : o.cands, flick = o.flick || 0, lit = o.lit || 0;
  if (ca > 0) {
    CAND_XS.forEach((x, i) => {
      const h0 = i % 2 ? 190 : 170, k = E.out(clamp(ca * 1.5 - i * 0.07)), h = h0 * k;
      cands.push(rect(x - 17, y3 + 8 - h, 34, h, o.candCol || F.blue), rect(x - 26, y3 - 6, 52, 14, F.yellow));
      if (lit > 0) { const l = E.back(clamp(lit * 1.6 - Math.abs(i - 3.5) * 0.1)); const s = i % 2 ? 1 : -1;
        cands.push(flame(x, y3 + 8 - h - 4, 74 * l * (1 + 0.15 * flick * s), 36, 7 * flick * s)); }
    });
    const hs = 252 * E.out(ca);
    cands.push(rect(-19, 252 - hs, 38, hs, o.candCol || F.blue), rect(-28, 232, 56, 14, F.yellow));
    if (lit > 0) cands.push(flame(0, -4, 92 * E.back(clamp(lit * 1.6)) * (1 + 0.12 * flick), 44, -6 * flick));
  }
  const fp = E.out(P(rings[4], 0, 1));
  const foot = g(poly([[-30, 752], [30, 752], [40, 800], [-40, 800]], F.white) + poly([[-230, 800], [230, 800], [250, 842], [-250, 842]], F.grey), "", fp);
  return `<g transform="translate(${cx},${top}) scale(${sc})">${foot}${parts.join("")}${cands.join("")}</g>`;
}

/* ring close-up with three pictures: A star (left), B HANUKKAH (right), C doughnut (back) */
function viewArt(v, cx, top, w, h) {
  const u = h / 300, sw = 46 * (w / 1000);
  if (v === "A") {
    const star = poly([[cx, top + h * 0.1], [cx + 90 * u, top + h * 0.7], [cx - 90 * u, top + h * 0.7]], F.green) + poly([[cx, top + h * 0.9], [cx + 90 * u, top + h * 0.3], [cx - 90 * u, top + h * 0.3]], F.green);
    const dx = cx + w * 0.3, dreidel = poly([[dx - 38 * u, top + h * 0.3], [dx + 38 * u, top + h * 0.3], [dx + 38 * u, top + h * 0.6], [dx, top + h * 0.82], [dx - 38 * u, top + h * 0.6]], F.orange) + rect(dx - 5 * u, top + h * 0.12, 10 * u, h * 0.2, F.orange);
    return stripes(cx - w / 2, top, w, h, [F.periwinkle, F.yellow, F.blue, F.yellow], sw, { wr: 0.3 }) + star + dreidel;
  }
  if (v === "B") return stripes(cx - w / 2, top, w, h, [F.coral, F.rose, F.brick, F.coral], sw, { wr: 0.3 }) + rect(cx - w * 0.33, top + h * 0.25, w * 0.66, h * 0.5, WHITE) +
    `<text x="${cx}" y="${top + h * 0.64}" text-anchor="middle" font-family="SO" font-size="${h * 0.36}" fill="${F.blue}" letter-spacing="6">HANUKKAH</text>`;
  return stripes(cx - w / 2, top, w, h, [F.rose, F.lilac, F.periwinkle], sw, { wr: 0.3 }) + circle(cx, top + h / 2, h * 0.39, F.orange) + circle(cx, top + h / 2, h * 0.11, F.brick);
}
/* mix of two pictures: f = share of picture p visible (period 116 like the polymorph sheet) */
function ringMix(p, q, f, cx, top, w, h) {
  let s = viewArt(p, cx, top, w, h);
  if (f >= 0.999) return s;
  const per = 58, cuts = [];
  for (let x = cx - w / 2; x < cx + w / 2; x += per) cuts.push(`<rect x="${n1(x + per * f)}" y="${top - 2}" width="${n1(per * (1 - f) + 0.6)}" height="${h + 4}"/>`);
  return s + clipped(cuts.join(""), viewArt(q, cx, top, w, h));
}
function ringCloseUp(cx, top, w, h, inner) { return clipped(poly(toothed(cx, top, w, h, 28, 16), WHITE), inner); }
