/* Timeline: named beats (may overlap), camera keyframe tracks, subtitles and audio in one data file per film.
   A beat gives scene code a local clock: beat.at(0.4) is an absolute time, beat.local(t) seconds since its start. */
import { track, prog } from './motion.js';

const REQUIRED = ['fps', 'duration', 'beats', 'size'];

export function createTimeline(data) {
  REQUIRED.forEach((key) => {
    if (data[key] === undefined) throw new Error(`timeline: missing "${key}"`);
  });
  const beats = {};
  data.beats.forEach((b) => {
    if (b.end <= b.start) throw new Error(`timeline: beat "${b.id}" ends before it starts`);
    if (beats[b.id]) throw new Error(`timeline: duplicate beat "${b.id}"`);
    beats[b.id] = Object.freeze({
      ...b,
      duration: b.end - b.start,
      at: (offset) => b.start + offset,
      local: (t) => t - b.start,
      progress: (t) => prog(t, b.start, b.end),
      active: (t) => t >= b.start && t < b.end,
    });
  });
  const camera = Object.fromEntries(Object.entries(data.camera || {}).map(([name, keys]) => [name, track(keys)]));
  return Object.freeze({
    fps: data.fps,
    width: data.size[0],
    height: data.size[1],
    duration: data.duration,
    frames: Math.round(data.duration * data.fps),
    beats,
    beat(id) {
      if (!beats[id]) throw new Error(`timeline: no beat "${id}"`);
      return beats[id];
    },
    /** All camera channels at time t: { yaw, pitch, zoom, x, y, ... }. */
    cameraAt: (t) => Object.fromEntries(Object.entries(camera).map(([name, fn]) => [name, fn(t)])),
    subtitles: data.subtitles || [],
    subtitleStyle: data.subtitleStyle || 'plain',
    ground: data.ground || null,
    warp: data.warp || null,
    audio: data.audio || null,
  });
}
