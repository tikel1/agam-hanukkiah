/* Polymorph demo: how one object holds two pictures. Two cards (fire, water) are cut into strips, the strips are
   woven together, the woven sheet folds into pleats, and the camera walks around it: fire from the left, both in
   front, water from the right. Depth comes from hard flat shadows only (no gradients, no shading). */
export default {
  fps: 30,
  size: [1080, 1920],
  duration: 12.5,
  beats: [
    { id: 'cards', start: 0, end: 1.1 },      // the two pictures arrive
    { id: 'cut', start: 1.0, end: 1.7 },      // each is cut into strips
    { id: 'weave', start: 1.6, end: 3.6 },    // the strips zip together: fire, water, fire, water
    { id: 'fold', start: 3.6, end: 5.1 },     // the sheet folds into pleats and stands up
    { id: 'fire', start: 5.1, end: 6.1 },     // from the left: only fire
    { id: 'turn', start: 6.1, end: 8.5 },     // walking round: fire dissolves into water
    { id: 'water', start: 8.5, end: 9.5 },    // from the right: only water
    { id: 'back', start: 9.5, end: 11.5 },    // and back again
    { id: 'hold', start: 11.5, end: 12.5 },
  ],
  camera: {
    yaw: [[0, 0], [3.6, 0], [5.0, -40], [6.1, -40], [8.5, 40], [9.5, 40], [11.5, -40]],
    pitch: [[0, 0], [3.6, 0], [5.0, 16]],
    zoom: [[0, 1], [3.6, 1], [5.0, 1.5]],
    y: [[0, 0], [3.6, 0], [5.0, -90]],
  },
  subtitles: [],
  audio: null,
};
