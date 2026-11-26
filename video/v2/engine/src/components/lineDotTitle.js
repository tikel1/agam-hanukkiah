/* Line-and-dot title that builds itself: strokes are drawn letter by letter (Hebrew: right to left), each letter
   settles with a small spring, then the coloured dots drop onto the stroke ends and pop. Drawn as flat meshes in
   the 3D scene (so it gets motion blur and can sit in space); face it to the camera with stage.billboard(group). */
import { THREE } from '../core/stage.js';
import { INK, DOTS } from '../palette.js';
import { LOGO, layoutTitle } from './glyphs.js';
import { prog, ease, spring, clamp } from '../core/motion.js';

const MAX_QUADS = 400;
const MITER_LIMIT = 3;
const DOT_SEGMENTS = 48;
const LETTER_DRAW_SECONDS = 0.55;
const DOT_STAGGER_SECONDS = 0.07;
const DOT_DROP_SECONDS = 0.28;
const DOT_DROP_HEIGHT = 0.55;          // in cap heights
const LETTER_SETTLE = 0.06;            // how far a letter over-scales while it is being drawn

/** Cuts a polyline to the first `fraction` of its length. Returns points (open), or the full closed loop. */
function cutPolyline(points, closed, fraction) {
  const path = closed ? [...points, points[0]] : points;
  if (fraction >= 1) return { points: closed ? points : path, closed };
  const lengths = path.slice(1).map((p, i) => Math.hypot(p[0] - path[i][0], p[1] - path[i][1]));
  let remaining = lengths.reduce((a, b) => a + b, 0) * fraction;
  const out = [path[0]];
  for (let i = 0; i < lengths.length && remaining > 0; i++) {
    const k = Math.min(1, remaining / lengths[i]);
    out.push([path[i][0] + (path[i + 1][0] - path[i][0]) * k, path[i][1] + (path[i + 1][1] - path[i][1]) * k]);
    remaining -= lengths[i];
  }
  return { points: out, closed: false };
}

/** Appends a stroked polyline (miter joins, butt ends) as triangles. write(x, y) receives the vertices. */
function strokePolyline(points, closed, width, write) {
  const n = points.length;
  if (n < 2) return 0;
  const half = width / 2;
  const normalOf = (a, b) => {
    const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
    return [-dy / len, dx / len];
  };
  const sides = points.map((p, i) => {
    const hasPrev = closed || i > 0, hasNext = closed || i < n - 1;
    const prev = points[(i - 1 + n) % n], next = points[(i + 1) % n];
    const n0 = hasPrev ? normalOf(prev, p) : normalOf(p, next);
    const n1 = hasNext ? normalOf(p, next) : n0;
    let mx = n0[0] + n1[0], my = n0[1] + n1[1];
    const len = Math.hypot(mx, my) || 1;
    mx /= len; my /= len;
    const scale = Math.min(MITER_LIMIT, 1 / Math.max(1e-3, mx * n0[0] + my * n0[1])) * half;
    return [[p[0] + mx * scale, p[1] + my * scale], [p[0] - mx * scale, p[1] - my * scale]];
  });
  const segments = closed ? n : n - 1;
  for (let i = 0; i < segments; i++) {
    const a = sides[i], b = sides[(i + 1) % n];
    write(a[0]); write(a[1]); write(b[0]); write(a[1]); write(b[1]); write(b[0]);
  }
  return segments;
}

export class LineDotTitle {
  /** words: e.g. ['אש', 'ומים']. cap = letter height in world units. rtl = false for digits.
      ends = dots before and after the title, as in the logo. */
  constructor({ words, cap = 120, ink = INK, rtl = true, dotColors = DOTS, ends = true }) {
    this.cap = cap;
    this.layout = layoutTitle(words, rtl);
    this.scale = cap / LOGO.CAP;
    this.width = this.layout.total * this.scale;
    this.group = new THREE.Group();

    this.positions = new Float32Array(MAX_QUADS * 6 * 3);
    this.geometry = new THREE.BufferGeometry();
    this.positionAttribute = new THREE.BufferAttribute(this.positions, 3).setUsage(THREE.DynamicDrawUsage);
    this.geometry.setAttribute('position', this.positionAttribute);
    const strokes = new THREE.Mesh(this.geometry, new THREE.MeshBasicMaterial({ color: ink, side: THREE.DoubleSide }));
    strokes.frustumCulled = false;
    this.group.add(strokes);

    const dotGeometry = new THREE.CircleGeometry(1, DOT_SEGMENTS);
    const dotSpots = [];
    this.layout.items.forEach((item, letter) => item.dots.forEach(([x, y]) => dotSpots.push({ x: item.x + x, y, letter })));
    this.layout.separators.forEach((x) => dotSpots.push({ x, y: LOGO.CAP / 2, letter: -1 }));
    if (ends && rtl) [-LOGO.WORD_GAP / 2, this.layout.total + LOGO.WORD_GAP / 2].forEach((x) => dotSpots.push({ x, y: LOGO.CAP / 2, letter: -1 }));
    // order of arrival follows the reading direction
    const ordered = [...dotSpots].sort((a, b) => (rtl ? b.x - a.x : a.x - b.x));
    this.dots = ordered.map((spot, index) => {
      const mesh = new THREE.Mesh(dotGeometry, new THREE.MeshBasicMaterial({ color: dotColors[index % dotColors.length] }));
      mesh.position.z = 2;
      this.group.add(mesh);
      return { ...spot, mesh };
    });
  }

  /** t = seconds since the title starts. span = time for all strokes, out = time at which it un-draws (optional). */
  update(t, { span = 1.5, dotsAfter = -0.25, out = null, outSpan = 0.5 } = {}) {
    const { items, total } = this.layout;
    const s = this.scale, count = items.length;
    const stagger = count > 1 ? Math.max(0, span - LETTER_DRAW_SECONDS) / (count - 1) : 0;
    const leaving = out === null ? 0 : ease.inCubic(prog(t, out, out + outSpan));
    let k = 0, quads = 0;
    const toWorld = (x, y) => [(x - total / 2) * s, (LOGO.CAP / 2 - y) * s];

    items.forEach((item, i) => {
      const local = t - i * stagger;
      const drawn = ease.inOutCubic(prog(local, 0, LETTER_DRAW_SECONDS)) * (1 - leaving);
      if (drawn <= 0) return;
      const settle = 1 + LETTER_SETTLE * (1 - spring(local - LETTER_DRAW_SECONDS * 0.6, 3.2, 0.5));
      const cx = item.x + item.width / 2, cy = LOGO.CAP;
      const write = (p) => {
        const gx = cx + (p[0] - cx) * settle, gy = cy + (p[1] - cy) * settle;
        const [wx, wy] = toWorld(gx, gy);
        this.positions[k++] = wx; this.positions[k++] = wy; this.positions[k++] = 0;
      };
      item.lines.forEach((line) => {
        if (quads + line.points.length + 1 > MAX_QUADS) throw new Error('LineDotTitle: title too long for the stroke buffer');
        const cut = cutPolyline(line.points.map(([x, y]) => [item.x + x, y]), line.closed, drawn);
        quads += strokePolyline(cut.points, cut.closed, LOGO.STROKE, write);
      });
    });
    this.geometry.setDrawRange(0, quads * 6);
    this.positionAttribute.needsUpdate = true;

    const dotsStart = span + dotsAfter;
    this.dots.forEach((dot, index) => {
      const local = t - dotsStart - index * DOT_STAGGER_SECONDS;
      const fall = ease.inQuad(prog(local, 0, DOT_DROP_SECONDS));
      const landed = local - DOT_DROP_SECONDS;
      const pop = local <= 0 ? 0 : (0.65 + 0.35 * spring(landed, 4.5, 0.35)) * clamp(local / 0.08) * (1 - leaving);
      const squash = 1 - 0.3 * Math.max(0, Math.sin(clamp(landed / 0.12) * Math.PI)) * (landed > 0 ? 1 : 0);
      const [wx, wy] = toWorld(dot.x, dot.y);
      const radius = LOGO.DOT_R * s * pop;
      dot.mesh.visible = radius > 0.01;
      dot.mesh.position.set(wx, wy + (1 - fall) * DOT_DROP_HEIGHT * this.cap - (1 - squash) * radius, 2);
      dot.mesh.scale.set(radius * (2 - squash), radius * squash, 1);
    });
  }
}
