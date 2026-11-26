/* "Fire and Water", version 2: vertical 9:16, about 129.5 s, one continuous take.
   Source: v2/script.md (narration, beat times) and v2/storyboard/storyboard.md (pictures, colour script).
   Beats are the script's ten sections. The pictures of each beat live in beats/bNN.js; this file holds what they
   share: the clock, the ground colours and the subtitles.
   Beat times are the script's planned times. The real clock (narration) is in narration.js: see `warp` below. */
import { GROUND } from '../../src/palette.js';
import narration from './narration.js';

export default {
  fps: 30,
  size: [1080, 1920],
  duration: narration.duration,          // real length with the recorded narration
  plannedDuration: 129.5,                // length of the picture in the script's own (planned) time
  subtitleStyle: 'slats',
  beats: [
    { id: 'b01', start: 0, end: 6.5 },        // hello, meet Yaacov Agam
    { id: 'b02', start: 6.5, end: 23 },       // kinetic art: the works that change, pleats
    { id: 'b03', start: 23, end: 38 },        // the fountain "Fire and Water"
    { id: 'b04', start: 38, end: 55.5 },      // fire -> Hanukkah, New York, the tribute, the idea
    { id: 'b05', start: 55.5, end: 62.5 },    // learning
    { id: 'b06', start: 62.5, end: 78.5 },    // the AI (Claude)
    { id: 'b07', start: 78.5, end: 97 },      // the design: hidden symbols
    { id: 'b08', start: 97, end: 103 },       // printing
    { id: 'b09', start: 103, end: 112 },      // painting and stacking
    { id: 'b10', start: 112, end: 129.5 },    // the tribute, end card
  ],
  /* Colour script of the ground (storyboard §2.2): [time, colour]; the film blends between keys. */
  ground: [
    [0, GROUND.paper], [22.6, GROUND.paper], [24.2, GROUND.sky], [31.5, GROUND.sky], [34, GROUND.memory], [38, GROUND.memory],
    [39.5, GROUND.amber], [46.8, GROUND.amber], [48.2, GROUND.amberDim], [52, GROUND.amberDim], [53, GROUND.memory],
    [55.1, GROUND.memory], [55.9, GROUND.study], [61.95, GROUND.study], [62.6, GROUND.screen], [78.4, GROUND.screen],
    [79.2, GROUND.paper], [96.9, GROUND.paper], [97.9, GROUND.workshop], [111.9, GROUND.workshop], [113.4, GROUND.night],
    [129.5, GROUND.night],
  ],
  camera: {},
  /* The recorded narration decides the real clock: narration.js (made by sync_narration.py) holds the anchors
     [real time, planned time], the subtitle cues in real time, the real length and the audio file. The beats above
     keep the script's planned times; film.js plays the picture at the planned time that belongs to each real time. */
  warp: narration.anchors,
  subtitles: narration.subtitles,
  audio: narration.audio,
};
