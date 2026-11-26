/* Motion helpers. Everything is a pure function of time, so any frame can be rendered alone (seek) and
   sub-frame samples for motion blur are exact. Times are seconds. */
export const clamp = (x, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, x));
export const lerp = (a, b, k) => a + (b - a) * k;
/** Linear progress 0..1 of t between a and b. */
export const prog = (t, a, b) => clamp((t - a) / (b - a));

const BACK = 1.70158;
export const ease = {
  linear: (k) => k,
  inQuad: (k) => k * k,
  outQuad: (k) => 1 - (1 - k) * (1 - k),
  inCubic: (k) => k * k * k,
  outCubic: (k) => 1 - Math.pow(1 - k, 3),
  inOutCubic: (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  inQuart: (k) => k * k * k * k,
  outQuart: (k) => 1 - Math.pow(1 - k, 4),
  inOutQuart: (k) => (k < 0.5 ? 8 * k * k * k * k : 1 - Math.pow(-2 * k + 2, 4) / 2),
  outQuint: (k) => 1 - Math.pow(1 - k, 5),
  inOutQuint: (k) => (k < 0.5 ? 16 * Math.pow(k, 5) : 1 - Math.pow(-2 * k + 2, 5) / 2),
  inExpo: (k) => (k <= 0 ? 0 : Math.pow(2, 10 * k - 10)),
  outExpo: (k) => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k)),
  inOutExpo: (k) => (k <= 0 ? 0 : k >= 1 ? 1 : k < 0.5 ? Math.pow(2, 20 * k - 10) / 2 : (2 - Math.pow(2, -20 * k + 10)) / 2),
  inBack: (k) => (BACK + 1) * k * k * k - BACK * k * k,
  outBack: (k) => 1 + (BACK + 1) * Math.pow(k - 1, 3) + BACK * Math.pow(k - 1, 2),
  inOutBack: (k) => {
    const c = BACK * 1.525;
    return k < 0.5 ? (Math.pow(2 * k, 2) * ((c + 1) * 2 * k - c)) / 2 : (Math.pow(2 * k - 2, 2) * ((c + 1) * (k * 2 - 2) + c) + 2) / 2;
  },
  /** Pulls back first (anticipation), then shoots past and settles. */
  anticipate: (k) => (k < 0.25 ? -0.12 * Math.sin((k / 0.25) * Math.PI) : ease.outBack((k - 0.25) / 0.75)),
};
const resolveEase = (e) => (typeof e === 'function' ? e : ease[e || 'inOutCubic']);

/** Eased progress: tween(t, start, duration, 'outExpo'). */
export const tween = (t, start, duration, e = 'inOutCubic') => resolveEase(e)(prog(t, start, start + duration));

/** Damped spring from 0 to 1, starting at rest at x = 0 (x in seconds). freq in Hz, damping 0..1 (lower = more bounce). */
export function spring(x, freq = 3, damping = 0.45) {
  if (x <= 0) return 0;
  const w = 2 * Math.PI * freq, wd = w * Math.sqrt(1 - damping * damping);
  return 1 - Math.exp(-damping * w * x) * (Math.cos(wd * x) + ((damping * w) / wd) * Math.sin(wd * x));
}
/** Damped wobble around 0 after an impact at x = 0: for follow-through and reactions. */
export function wobble(x, freq = 4, damping = 0.3) {
  if (x <= 0) return 0;
  const w = 2 * Math.PI * freq;
  return Math.exp(-damping * w * x) * Math.sin(w * Math.sqrt(1 - damping * damping) * x);
}

/** Keyframe track: track([[0, 1], [2, 5, 'outExpo'], ...]). The ease of a key shapes the move arriving at it. */
export function track(keys) {
  return (t) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1, e] = keys[i];
      if (t <= t1) {
        const [t0, v0] = keys[i - 1];
        return lerp(v0, v1, resolveEase(e)((t - t0) / (t1 - t0)));
      }
    }
    return keys[keys.length - 1][1];
  };
}

/** Deterministic pseudo random 0..1 from an integer seed. */
export function rand(seed) {
  const s = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
}
/** Smooth organic drift around 0 in about -1..1 (sum of three sines, seeded). */
export function drift(t, seed = 0, freq = 1) {
  const a = rand(seed) * 6.283, b = rand(seed + 1) * 6.283, c = rand(seed + 2) * 6.283;
  return (Math.sin(t * freq * 6.283 + a) + 0.5 * Math.sin(t * freq * 2.17 * 6.283 + b) + 0.25 * Math.sin(t * freq * 4.31 * 6.283 + c)) / 1.75;
}
/** Quadratic bezier point. */
export const bezier2 = (a, c, b, k) => a.map((_, i) => (1 - k) * (1 - k) * a[i] + 2 * (1 - k) * k * c[i] + k * k * b[i]);
/** Seconds of travel at full speed after x seconds of a soft start (accelerates from rest, then constant speed). */
export const softStart = (x, rate = 2.5) => (x <= 0 ? 0 : x - (1 - Math.exp(-rate * x)) / rate);
/** One smooth bump 0 -> 1 -> 0 between a and b. */
export const bump = (t, a, b) => Math.sin(prog(t, a, b) * Math.PI);
