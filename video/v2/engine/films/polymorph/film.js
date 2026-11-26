/* Polymorph demo film (see timeline.js for the story). Everything is set from the time alone. */
import { THREE } from '../../src/core/stage.js';
import { createTimeline } from '../../src/core/timeline.js';
import { tween, spring, lerp, prog, ease } from '../../src/core/motion.js';
import { PAPER, NAVY, DOTS } from '../../src/palette.js';
import { PleatedSurface } from '../../src/components/pleated.js';
import { WallShadow } from '../../src/components/shadows.js';
import { createPictures } from './pictures.js';
import data from './timeline.js';

const DEG = Math.PI / 180;
const STRIPS = 16;                                    // strips per picture
const PICTURE = { width: 500, height: 700 };
const STRIP = PICTURE.width / STRIPS;
const FOLD_ANGLE = 50;                                // degrees each strip turns; 90 - 50 = the 40 degree viewing angle
const VIEW_ANGLE = 90 - FOLD_ANGLE;
const CARD_Y = 440;                                   // the two cards start above and below the centre
const SHADOW = 0xD8D2C0;                              // one flat shadow tone on the paper
const FLOOR = { color: 0xEFEBDF, radius: 620 };
const DROP = { rest: 9, lifted: 26 };                 // offset of a strip's hard shadow, lying and in flight
const LIGHT = [0.28, 0.5];                            // ground shadow per unit of height: to the right, towards the viewer
const HUD = { y: -650, span: 320, dots: 9, dotRadius: 10, eyeRadius: 28 };

function buildStrips(pictures) {
  const geometry = new THREE.PlaneGeometry(STRIP, PICTURE.height);
  const shadowMaterial = new THREE.MeshBasicMaterial({ color: SHADOW });
  return ['fire', 'water'].flatMap((name, set) => Array.from({ length: STRIPS }, (_, index) => {
    const map = pictures[name].clone();
    map.repeat.set(1 / STRIPS, 1);
    map.offset.set(index / STRIPS, 0);
    map.needsUpdate = true;
    const face = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ map }));
    const shadow = new THREE.Mesh(geometry, shadowMaterial);
    face.position.z = 2;
    const group = new THREE.Group();
    group.add(shadow, face);
    return { group, shadow, set, index };
  }));
}

/** The viewer marker under the picture: a row of dots and an "eye" that slides with the camera. */
function buildHud() {
  const group = new THREE.Group();
  const dot = new THREE.CircleGeometry(1, 32);
  Array.from({ length: HUD.dots }, (_, i) => {
    const mesh = new THREE.Mesh(dot, new THREE.MeshBasicMaterial({ color: DOTS[i % DOTS.length] }));
    const k = i / (HUD.dots - 1) - 0.5;
    mesh.position.set(k * 2 * HUD.span, -Math.cos(k * Math.PI) * 34, 0);
    mesh.scale.setScalar(HUD.dotRadius);
    group.add(mesh);
    return mesh;
  });
  const eye = new THREE.Group();
  const body = new THREE.Mesh(dot, new THREE.MeshBasicMaterial({ color: NAVY }));
  body.scale.setScalar(HUD.eyeRadius);
  const pointer = new THREE.Mesh(new THREE.CircleGeometry(HUD.eyeRadius * 0.9, 3), new THREE.MeshBasicMaterial({ color: NAVY }));
  pointer.rotation.z = Math.PI / 2;
  pointer.position.y = HUD.eyeRadius * 1.35;
  eye.add(body, pointer);
  eye.position.z = 1;
  group.add(eye);
  return { group, eye };
}

export async function createFilm(stage) {
  const timeline = createTimeline(data);
  const beats = timeline.beats;
  const pictures = createPictures(PICTURE.width, PICTURE.height);
  const strips = buildStrips(pictures);
  const sheet = new PleatedSurface({ pleats: STRIPS, colorA: () => NAVY, colorB: () => NAVY });
  sheet.setMotifs({ left: pictures.fire, right: pictures.water });
  sheet.uniforms.motifAmount.value = 1;
  const floor = new THREE.Mesh(new THREE.CircleGeometry(FLOOR.radius, 96), new THREE.MeshBasicMaterial({ color: FLOOR.color }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -PICTURE.height / 2 - 1;
  const groundShadow = new WallShadow({ segments: STRIPS * 2, color: SHADOW });
  const hud = buildHud();
  stage.scene.add(stage.camera, floor, groundShadow.mesh, sheet.mesh, ...strips.map((s) => s.group));
  stage.camera.add(hud.group);
  stage.background.set(PAPER);

  function updateCamera(t) {
    const cam = timeline.cameraAt(t);
    Object.assign(stage.rig, { yaw: cam.yaw, pitch: cam.pitch, zoom: cam.zoom });
    stage.rig.target.set(0, cam.y, 0);
    stage.applyRig();
  }

  /** A strip: slides in as part of its card, is cut loose, then flies to its slot in the woven row. */
  function updateStrip(t, strip) {
    const { cards, cut, weave, fold } = beats;
    const side = strip.set === 0 ? -1 : 1;
    const arrive = ease.outExpo(prog(t, cards.at(0.1 + strip.set * 0.15), cards.at(0.8 + strip.set * 0.15)));
    const loose = tween(t, cut.at(0.05 + strip.index * 0.02), 0.35, 'outCubic');
    const fly = tween(t, weave.at(0.1 + strip.index * 0.06), 0.9, 'inOutCubic');
    const homeX = (-PICTURE.width / 2 + (strip.index + 0.5) * STRIP) * (1 + 0.2 * loose);
    const homeY = -side * CARD_Y + (strip.index % 2 ? 1 : -1) * 12 * loose;
    const slotX = -PICTURE.width + (2 * strip.index + strip.set + 0.5) * STRIP;
    const lift = Math.sin(fly * Math.PI);
    strip.group.visible = t < fold.start;
    strip.group.position.set(lerp(homeX, slotX, fly) + side * (1 - arrive) * 1100, lerp(homeY, 0, fly), strip.set + lift * 40);
    strip.group.scale.setScalar(1 + 0.05 * lift);
    const settle = 1 - tween(t, weave.at(1.75), 0.25);
    const offset = (DROP.rest + (DROP.lifted - DROP.rest) * lift) * settle;
    strip.shadow.position.set(offset, -offset, 0);
  }

  function updateSheet(t) {
    const { fold } = beats;
    const foldK = tween(t, fold.at(0), 1.3, 'inOutCubic');
    const angle = FOLD_ANGLE * DEG * foldK;
    const length = STRIPS * 2 * STRIP * Math.cos(angle), depth = STRIP * Math.sin(angle);
    sheet.mesh.visible = t >= fold.start;
    sheet.update({ length, height: PICTURE.height, bend: 0, depth: () => depth });
    floor.visible = sheet.mesh.visible;
    floor.scale.setScalar(Math.max(0.001, ease.outCubic(prog(t, fold.at(0.1), fold.at(1.0)))));
    // hard shadow of the standing pleats on the floor
    const pitch = length / STRIPS;
    const points = Array.from({ length: STRIPS * 2 + 1 }, (_, i) => [-length / 2 + (i * pitch) / 2, i % 2 ? depth : 0]);
    groundShadow.mesh.visible = sheet.mesh.visible && foldK > 0.02;
    groundShadow.update(points, -PICTURE.height / 2 - 0.5, [LIGHT[0] * PICTURE.height * foldK, LIGHT[1] * PICTURE.height * foldK]);
  }

  function updateHud(t) {
    const appear = spring(t - beats.fold.at(1.0), 3, 0.5);
    const zoom = stage.rig.zoom;
    hud.group.visible = appear > 0.01;
    hud.group.position.set(0, HUD.y / zoom, -100);
    hud.group.scale.setScalar(Math.max(0.001, appear) / zoom);
    hud.eye.position.x = (stage.rig.yaw / VIEW_ANGLE) * HUD.span;
    hud.eye.position.y = -Math.cos((stage.rig.yaw / VIEW_ANGLE) * 0.5 * Math.PI) * 34 - 4;
  }

  function update(t) {
    updateCamera(t);
    strips.forEach((strip) => updateStrip(t, strip));
    updateSheet(t);
    updateHud(t);
  }

  return { timeline, update };
}
