/* Player: loads films/<name>/film.js, exposes window.seek(t) for the renderer, and gives a scrubber for preview.
   URL: player.html?film=proof            preview (space = play / pause, ?t=12 starts at second 12)
        player.html?film=proof&render=1   used by render.py: no controls, frames only on seek()
        &samples=12&shutter=0.5           sub-frames per frame and shutter (motion blur) */
import { Stage } from './core/stage.js';
import { Subtitles } from './core/subtitles.js';
import { SlatSubtitles } from './core/slatSubtitles.js';
import { PAPER } from './palette.js';

const FILM_NAME = /^[a-z0-9_-]+$/i;
const DEFAULT_RENDER_SAMPLES = 12;
const PREVIEW_BLUR_SAMPLES = 8;

const params = new URLSearchParams(location.search);
const isRender = params.get('render') === '1';

function showError(error) {
  const box = document.getElementById('error');
  box.style.display = 'block';
  box.textContent = `Player error:\n${error && error.stack ? error.stack : error}`;
  window.__error = String(error);
  console.error(error);
}

function fitToWindow(frame, width, height) {
  const scale = Math.min(window.innerWidth / width, (window.innerHeight - 48) / height);
  frame.style.transform = `scale(${scale})`;
}

function setupPreview({ timeline, draw, getTime, setTime }) {
  const play = document.getElementById('play'), scrub = document.getElementById('scrub'), clock = document.getElementById('clock');
  scrub.max = String(timeline.duration);
  let playing = false, last = 0;
  const show = () => { scrub.value = String(getTime()); clock.textContent = getTime().toFixed(2); draw(); };
  const tick = (now) => {
    if (!playing) return;
    setTime((getTime() + (now - last) / 1000) % timeline.duration);
    last = now;
    show();
    requestAnimationFrame(tick);
  };
  const toggle = () => {
    playing = !playing;
    play.textContent = playing ? 'Pause' : 'Play';
    if (playing) { last = performance.now(); requestAnimationFrame(tick); }
  };
  play.addEventListener('click', toggle);
  document.addEventListener('keydown', (event) => { if (event.code === 'Space') { event.preventDefault(); toggle(); } });
  scrub.addEventListener('input', () => { setTime(Number(scrub.value)); show(); });
  document.getElementById('blur').addEventListener('change', show);
  show();
}

async function main() {
  const filmName = params.get('film') || 'proof';
  if (!FILM_NAME.test(filmName)) throw new Error(`bad film name "${filmName}"`);
  document.body.classList.toggle('render', isRender);
  // the frame size (16:9, 9:16, ...) is the film's choice: timeline.size
  const [width, height] = (await import(`../films/${filmName}/timeline.js`)).default.size;
  const frame = document.getElementById('frame'), canvas = document.getElementById('stage');
  [frame, canvas].forEach((element) => { element.style.width = `${width}px`; element.style.height = `${height}px`; });
  frame.style.setProperty('--frame-height', `${height}px`);
  if (!isRender) { fitToWindow(frame, width, height); window.addEventListener('resize', () => fitToWindow(frame, width, height)); }

  const stage = new Stage({ canvas, width, height, background: PAPER });
  const { createFilm } = await import(`../films/${filmName}/film.js`);
  const film = await createFilm(stage);
  await document.fonts.load('54px "Secular One"');
  await document.fonts.ready;
  const SubtitleClass = film.timeline.subtitleStyle === 'slats' ? SlatSubtitles : Subtitles;
  const subtitles = new SubtitleClass(document.getElementById('subtitles'), film.timeline.subtitles);

  const renderSamples = Number(params.get('samples')) || DEFAULT_RENDER_SAMPLES;
  const shutter = Number(params.get('shutter')) || 0.5;
  const renderAt = (t, samples) => {
    stage.render(film.update, t, { fps: film.timeline.fps, samples, shutter });
    subtitles.update(t);
  };

  /** Renders the frame for time t (seconds). Deterministic: the same t always gives the same picture. */
  window.seek = (t) => { renderAt(t, renderSamples); return true; };
  window.__film = { name: filmName, width, height, duration: film.timeline.duration, fps: film.timeline.fps, frames: film.timeline.frames, audio: film.timeline.audio };

  if (isRender) {
    window.seek(0);
  } else {
    let time = Math.min(Number(params.get('t')) || 0, film.timeline.duration);
    setupPreview({
      timeline: film.timeline, getTime: () => time, setTime: (value) => { time = value; },
      draw: () => renderAt(time, document.getElementById('blur').checked ? PREVIEW_BLUR_SAMPLES : 1),
    });
  }
  window.__ready = true;
}

main().catch(showError);
