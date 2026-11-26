/* Beat 1 (0-6.5, drawn to 7.3): hello, meet Yaacov Agam.
   0.1-0.7   white paper; the place for the girls' photo drops onto it
   0.3-3.25  18 stripes, colour / paper, paint themselves right to left over the whole page, alternately down and
             up, each at its own speed with a small settle; each stands up as a lit fold while it arrives and lies
             down as it lands; they run behind the girls' card, which lifts off and leaves (3.42-3.92)
   2.78-4.25 a ripple of folds runs right to left across the row and stays: the camera turns a little with it
   3.85-5.3  the folded pleats squeeze to the sides like an accordion curtain (one gesture with the ripple), opening onto Agam's
             portrait in its stripe frame; the curtain stacks drop into the frame
   4.45-5.9  "יעקב / אגם" writes itself in the upper third
   6.25-7.25 the page scrolls up (a small pull down first): photo, curtain and title leave through the top while
             beat 2's cards rise from below (beat 2 draws over this pass).
   Beat 1 films at zoom 1, so world units are frame pixels: x = px - 540, y = 960 - py. */
import { THREE } from '../../../src/core/stage.js';
import { prog, ease, tween, bump } from '../../../src/core/motion.js';
import { StripeFrame, loadPicture } from '../../../src/components/stripeFrame.js';
import { LineDotTitle } from '../../../src/components/lineDotTitle.js';
import { createCurtain, WINDOW } from '../parts/b01_curtain.js';
import { createGirlsCard } from '../parts/b01_girls.js';
import { FRAME } from '../parts/b01_common.js';

const PASS_END = 7.3;
const PORTRAIT = { url: 'assets/photos/agam_portrait.jpg', focus: [0, -0.55], appear: 3.97, shadowIn: [4.0, 4.6] };
const TITLE = [
  { words: ['יעקב'], cap: 130, py: 335, start: 4.45, span: 0.75 },
  { words: ['אגם'], cap: 130, py: 515, start: 4.8, span: 0.6 },
];
const SCROLL = { pull: 12, pullAt: [6.2, 6.46], from: 6.36, to: 7.22, distance: 1560, creep: 8, creepAt: [5.2, 6.3] };
/** A small turn from the ripple through the curtain: the folds show their depth (the film's verb "turn"). */
const SWAY = { yaw: -9, at: [2.8, 6.1] };
const SHADOW_STRENGTH = 0.24;

const worldX = (px) => px - FRAME.centreX;
const worldY = (py) => FRAME.centreY - py;

/** Pixels the page has moved up at time t (the link into beat 2). */
export function pageScroll(t) {
  const creep = SCROLL.creep * tween(t, SCROLL.creepAt[0], SCROLL.creepAt[1] - SCROLL.creepAt[0]);
  return creep - SCROLL.pull * bump(t, ...SCROLL.pullAt) + SCROLL.distance * ease.inOutCubic(prog(t, SCROLL.from, SCROLL.to));
}

async function buildPortrait() {
  const width = WINDOW.right - WINDOW.left, height = WINDOW.bottom - WINDOW.top;
  const frame = new StripeFrame({ picture: await loadPicture(PORTRAIT.url), width, height, focus: PORTRAIT.focus });
  frame.group.position.set(worldX((WINDOW.left + WINDOW.right) / 2), worldY((WINDOW.top + WINDOW.bottom) / 2), -8);
  return frame;
}

export async function create(ctx) {
  const { stage } = ctx;
  const beat = ctx.beats.b01;
  const scene = new THREE.Scene();
  const portrait = await buildPortrait();
  const curtain = createCurtain(portrait);
  const girls = await createGirlsCard();
  const titles = TITLE.map((spec) => ({ spec, title: new LineDotTitle({ words: spec.words, cap: spec.cap }) }));
  scene.add(portrait.group, curtain.group, girls.group, ...titles.map((x) => x.title.group));

  function updateTitles(t) {
    titles.forEach(({ spec, title }) => {
      title.group.visible = t > spec.start;
      title.update(t - spec.start, { span: spec.span });
      title.group.position.set(0, worldY(spec.py), 60);
      stage.billboard(title.group);
    });
  }

  function update(t) {
    stage.setRig({ yaw: SWAY.yaw * bump(t, ...SWAY.at) ** 2, shiftY: pageScroll(t) });
    curtain.update(t);
    girls.update(t);
    portrait.group.visible = t > PORTRAIT.appear;
    portrait.shadow.material.uniforms.strength.value = SHADOW_STRENGTH * tween(t, PORTRAIT.shadowIn[0], PORTRAIT.shadowIn[1] - PORTRAIT.shadowIn[0]);
    updateTitles(t);
  }

  return { from: beat.start, to: PASS_END, scene, update };
}
