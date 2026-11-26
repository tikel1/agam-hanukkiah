/* Engine: seek(t) draws any frame deterministically. Scene functions live in scenes_a.js / scenes_b.js and take
   (t, d) = seconds since the scene start and the scene length. Transitions, subtitles and narration are driven by timeline.json. */
"use strict";
const TL = window.TIMELINE;
const SCENES = {};          // id -> function(t, d) returning SVG markup

function curtain(type, k, reveal) {
  // k in 0..1: how far the curtain has moved. cover: hides the picture; reveal: lets it show again.
  if (k <= 0) return "";
  const out = [], n = type === "bands" ? 12 : 24, size = (type === "bands" ? H : W) / n;
  for (let i = 0; i < n; i++) {
    const kk = E.io(clamp(k * 1.7 - (i / n) * 0.7)); if (kk <= 0) continue;
    const col = type === "flip" ? [F.coral, F.brick][i % 2] : SPECTRUM[i % 12];
    if (type === "bands") {
      const w = W * kk; out.push(rect(reveal ? W - w : 0, i * size, w + 1, size + 1, col));
    } else if (type === "flip") {                  // every stripe turns about its own vertical axis
      const w = (size + 1) * kk; out.push(rect(i * size + (size - w) / 2, 0, w, H, col));
    } else {
      const h = H * kk; out.push(rect(i * size, reveal ? H - h : 0, size + 1, h + 1, col));
    }
  }
  if (type === "flip" && reveal) return out.join("");
  return out.join("");
}

function sceneIndex(t) { for (let i = TL.scenes.length - 1; i >= 0; i--) if (t >= TL.scenes[i].start) return i; return 0; }

function overlay(t, i) {
  const sc = TL.scenes[i], tr = sc.transition || { type: "none" }, prev = TL.scenes[i - 1], out = [];
  // cover at the end of this scene
  if (tr.type !== "none" && tr.cover > 0 && t > sc.end - tr.cover) {
    const k = (t - (sc.end - tr.cover)) / tr.cover;
    if (tr.type === "fade-navy") out.push(rect(0, 0, W, H, NAVY, `opacity="${E.sine(clamp(k)).toFixed(3)}"`));
    else if (tr.type === "fade-white") out.push(rect(0, 0, W, H, PAPER, `opacity="${E.sine(clamp(k)).toFixed(3)}"`));
    else out.push(curtain(tr.type, clamp(k), false));
  }
  // reveal at the start of this scene
  const pt = prev && prev.transition;
  if (pt && pt.reveal > 0 && t < sc.start + pt.reveal && !/^fade/.test(pt.type)) out.push(curtain(pt.type, 1 - (t - sc.start) / pt.reveal, true));
  return out.join("");
}

let measureCtx = null;
function textWidth(s, size) {
  if (!measureCtx) measureCtx = document.createElement("canvas").getContext("2d");
  measureCtx.font = `${size}px SO`;
  return measureCtx.measureText(s).width;
}

/* Subtitles: navy text with a paper halo. A paper-coloured plate sits behind the lines: invisible on the light
   scenes, it keeps the text readable on the dark panel of the closing scene. */
function subtitles(t) {
  const z = TL.subtitleZone, cue = (TL.subtitles || []).find(c => t >= c.start && t < c.end);
  if (!cue) return "";
  const lines = String(cue.text).split(/\n/), lh = z.fontSize * 1.15, y0 = z.baseline - (lines.length - 1) * lh;
  const cx = cue.x || W / 2, w = Math.min(z.maxWidth, Math.max(...lines.map(s => textWidth(s, z.fontSize)))) + 72;
  const top = y0 - z.fontSize * 0.88 - 14, h = (lines.length - 1) * lh + z.fontSize * 1.2 + 28;
  const plate = `<rect x="${cx - w / 2}" y="${top}" width="${w}" height="${h}" rx="26" fill="${PAPER}" opacity="0.94"/>`;
  return (cue.plate ? plate : "") + lines.map((s, i) => `<text x="${cx}" y="${y0 + i * lh}" text-anchor="middle" direction="rtl" font-family="SO" font-size="${z.fontSize}" fill="${z.color}" paint-order="stroke" stroke="${z.halo}" stroke-width="14" stroke-linejoin="round">${s}</text>`).join("");
}

function frameMarkup(t) {
  t = clamp(t, 0, TL.duration - 1e-3);
  const i = sceneIndex(t), sc = TL.scenes[i];
  const body = SCENES[sc.id] ? SCENES[sc.id](t - sc.start, sc.end - sc.start, t) : label("scene " + sc.id, W / 2, H / 2, 80);
  return `<rect width="${W}" height="${H}" fill="${PAPER}"/>${body}${overlay(t, i)}<g id="subtitle-layer">${subtitles(t)}</g>`;
}

let stage = null;
function seek(t) { if (!stage) stage = document.getElementById("stage"); clipN = 0; stage.innerHTML = frameMarkup(t); window.__t = t; return t; }
