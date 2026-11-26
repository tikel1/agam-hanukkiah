/* Proof clip timeline: the one place for beat times, camera moves, subtitles and audio.
   Beats overlap on purpose (the next action starts before the last one ends). Scene code asks for
   timeline.beat('wrap').at(0.2) and never hard-codes absolute seconds.
   Camera keys: [time, value, ease] - the ease shapes the move arriving at that key (default inOutCubic).
   yaw / pitch in degrees, zoom 1 = 1 world unit per pixel, y = world height the camera aims at.
   Phone layout: subject centred and large, title in the upper third, subtitles above the bottom 15%. */
export default {
  fps: 30,
  size: [1080, 1920],                            // vertical 9:16 for phones
  duration: 18,
  beats: [
    { id: 'unfold', start: 0, end: 2.8 },        // pleats rise and fold, the disc cuts the stripes
    { id: 'polymorph', start: 2.6, end: 6.4 },   // the camera turns: warm stripes become cool ones, the framed photo floats in
    { id: 'wrap', start: 6.4, end: 9.2 },        // the sheet closes into the big ring, the other rings arrive
    { id: 'fountain', start: 9.0, end: 12.4 },   // rings turn, water rises, the title builds itself
    { id: 'flame', start: 11.6, end: 13.9 },     // the flame rises, day turns to night
    { id: 'split', start: 13.7, end: 15.9 },     // the flame climbs the shamash and splits onto eight candles; pool -> foot
    { id: 'hold', start: 15.9, end: 18 },
  ],
  camera: {
    yaw: [[0, -40], [2.6, -40], [5.0, 40], [6.5, 40], [9.0, 14], [11.8, 14], [13.6, 0], [15.4, 0], [18, -12, 'inOutQuart']],
    pitch: [[0, 0], [6.5, 0], [9.0, 18], [13.7, 18], [15.6, 15]],
    zoom: [[0, 1.04], [2.6, 1], [6.5, 1], [9.0, 0.96], [11.7, 0.96], [13.4, 1.3], [13.8, 1.3], [15.6, 1.12], [18, 1.18, 'outCubic']],
    y: [[0, 0], [6.5, 0], [9.0, 110], [11.7, 110], [13.4, 400], [13.8, 400], [15.6, 190]],
  },
  // Demo lines only (to prove right-to-left subtitles); the real text comes from the v2 script.
  subtitles: [
    { start: 9.5, end: 12.1, text: 'בכיכר דיזנגוף: מזרקת "אש ומים"' },
    { start: 14.9, end: 17.7, text: 'והאש הפכה לנרות של חנוכה.', dark: true },
  ],
  audio: null,
};
