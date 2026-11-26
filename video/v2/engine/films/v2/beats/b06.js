/* Beat 06 (62.5-78.5, passes to 79.3): the AI, inside the computer, with Claude.
   61.95-62.85  beat 5's picture shrinks into a phone (navy body, glowing rim lit from the top); the ground goes navy.
   62.6-64.0    title "AI"; Claude grabs the top edge from inside, peeks, pulls himself up onto it and waves.
   64.0-65.1    the hologram world rises over the page inside the screen, the screen grows to the full frame (the camera
                dives in) and Claude jumps in with it, landing on the hologram table.
   64.95-68.6   the model's construction drawing draws itself (upper rings floating above); Claude's beam passes over it
                from the foot up and every part grows solid, white. Holo screen: placeholder "the girls at the computer".
   69.0-75.0    the camera rises; the map screen arrives and Claude hops onto it; a glowing scan ring climbs the model and
                the paint follows right under it; Claude points at it; the candles grow; a cheer.
   75.0-79.3    the wink: the world shrinks into the phone of handoff.js, which is a VIDEO PLAYER playing this film:
                play button, progress dots with a playhead at the film's real position, timecode on its bezel, and an
                editor timeline of the whole film (thumbnails of every scene) sliding under it. Claude jumps out beside
                it, taps play at 76.0 (beat 7 starts playing in the screen), points at the playhead, winks at us at 77
                and waves as the camera pushes into the screen (77.9-79.3): rain, player, timeline and Claude slide out
                past the frame edges as layers at their own depths (handoff.PUSH_PARALLAX), the push goes on in beat 7.
   Passes: outer 61.95-79.3 (phone, rain, title), inner 64.0-76.6 (hologram world, rect = phone screen), Claude
   62.9-79.3 (on top of both). */
import { THREE } from '../../../src/core/stage.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { PAPER, INK } from '../../../src/palette.js';
import { prog, ease } from '../../../src/core/motion.js';
import { phoneRect, PHONE, PUSH_PARALLAX } from '../handoff.js';
import { OPEN, SWITCH_TO_CLOSING, screenRect, pushMap, openRect, isFullFrame } from '../parts/b06_rig.js';
import { DataRain } from '../parts/b06_holo.js';
import { PhoneBody } from '../parts/b06_phone.js';
import { PlayerBar, PLAYER_BOTTOM } from '../parts/b06_player.js';
import { EditorStrip } from '../parts/b06_strip.js';
import { buildInnerWorld } from '../parts/b06_inner.js';
import { buildClaudePass } from '../parts/b06_claude_pass.js';

const OUTER = { from: OPEN.shrink[0], to: PHONE.grow[1] };
const INNER = { from: OPEN.wipe[0], to: 76.6, grown: OPEN.grow[1], shrinks: 75.0 };
const TITLE = { at: 62.6, span: 0.7, out: 64.0, outSpan: 0.35, cap: 170, y: 430 };
const OFF = 1e6;                         // 'never' for the player before the closing phone
const RAIN_IN = [62.35, 62.9];
const RIM_TRACE = [62.2, 62.85];
/** The wink: the phone becomes a video player playing this film (controls on its bezel, an editor timeline below). */
export const PLAYER = Object.freeze({ strip: 75.78, controls: 75.7, tap: 76.0 });

/** Places a group laid out in frame pixels around the phone at rest so that it follows the phone (outerMap). */
function followPhone(group, map, z) {
  group.position.set(map.ox - 540 + 540 * map.s, 960 - map.oy - 960 * map.s, z);
  group.scale.setScalar(map.s);
}

async function buildOuter(ctx) {
  const scene = new THREE.Scene();
  const player = await PlayerBar.create();
  const strip = new EditorStrip();
  const rain = new DataRain({ seed: 5 });
  rain.group.position.z = -500;
  const phone = new PhoneBody();
  const title = new LineDotTitle({ words: ['AI'], rtl: false, ink: PAPER, cap: TITLE.cap });
  title.group.position.set(0, 960 - TITLE.y, 10);
  scene.add(rain.group, phone.group, title.group, player.group, strip.group);

  function update(t) {
    ctx.stage.setRig({});
    const screen = screenRect(t);
    followPhone(rain.group, pushMap(t, PUSH_PARALLAX.rain), -500);
    followPhone(player.group, pushMap(t, PUSH_PARALLAX.player), 20);
    followPhone(strip.group, pushMap(t, PUSH_PARALLAX.strip), 15);
    rain.update(t, { amount: ease.inOutCubic(prog(t, ...RAIN_IN)), hole: isFullFrame(screen) ? [0, 0, 1080, 1920] : screen });
    const closing = t >= SWITCH_TO_CLOSING;
    phone.update(screen, { trace: closing ? 1 : ease.inOutCubic(prog(t, ...RIM_TRACE)), bottom: closing ? PLAYER_BOTTOM : undefined, shadow: closing });
    player.update(t, { appear: closing ? PLAYER.controls : OFF, tap: PLAYER.tap });
    strip.update(t, closing ? PLAYER.strip : OFF);
    title.group.visible = t >= TITLE.at && t < TITLE.out + TITLE.outSpan;
    title.update(t - TITLE.at, { span: TITLE.span, out: TITLE.out - TITLE.at, outSpan: TITLE.outSpan });
  }
  return { from: OUTER.from, to: OUTER.to, scene, update };
}

/** Where the inner world is drawn: the opening phone's screen, the full frame, then the closing phone's screen. */
function innerRect(t) {
  if (t < INNER.grown) return openRect(t);
  if (t < INNER.shrinks) return null;
  return phoneRect(t);
}
/** While it first appears, the hologram world rises over the page inside the screen (a wipe from below). */
function innerClip(t) {
  if (t >= OPEN.wipe[1]) return null;
  const rect = openRect(t);
  const k = ease.inOutCubic(prog(t, ...OPEN.wipe));
  return [rect[0], rect[1] + rect[3] * (1 - k), rect[2], Math.max(1, rect[3] * k)];
}

export async function create(ctx) {
  const beat = ctx.beats.b06;
  if (Math.abs(beat.start - 62.5) > 1e-6) throw new Error(`b06: expected the beat to start at 62.5, got ${beat.start}`);
  const outer = await buildOuter(ctx);
  const world = await buildInnerWorld(ctx.stage);
  const inner = {
    from: INNER.from, to: INNER.to, scene: world.scene, update: world.update,
    rect: innerRect, clip: innerClip, background: () => INK,
  };
  const claude = buildClaudePass(ctx.stage);
  return [outer, inner, claude];
}
