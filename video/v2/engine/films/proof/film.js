/* Proof clip: one continuous take. Pleats rise -> the camera turns and the stripes change, a framed photo floats in -> the sheet
   closes into the big ring of the fountain -> the flame rises -> it climbs the shamash and splits onto the eight candles of our hanukkiah.
   update(t) sets everything from the time alone (no state carried between frames). */
import { THREE } from '../../src/core/stage.js';
import { createTimeline } from '../../src/core/timeline.js';
import { tween, spring, wobble, bump, softStart, lerp, prog, ease, rand, drift, bezier2, clamp } from '../../src/core/motion.js';
import { PAPER, WHITE, NIGHT, SPECTRUM, DOTS, FOUNTAIN as F } from '../../src/palette.js';
import { PleatedSurface } from '../../src/components/pleated.js';
import { PhotoFrame, loadPhoto } from '../../src/components/photoFrame.js';
import { discShadow } from '../../src/components/shadows.js';
import { createRingMotifs } from '../../src/components/motifs.js';
import { Fountain, Candle, ringSpec, RING_LEVELS, FOUNTAIN_TOP, FOUNTAIN_BOTTOM } from '../../src/components/fountain.js';
import { LineDotTitle } from '../../src/components/lineDotTitle.js';
import { Flame } from '../../src/components/flame.js';
import data from './timeline.js';

const DEG = Math.PI / 180;
const SKY = 0xDCE9F3;
const VIEW_ANGLE = 40;                                  // camera yaw at both ends of the polymorph turn
const SHEET = { pleats: 72, length: 1500, height: 1480, depthRatio: 0.65 };
// Agam at the fountain: a real press photograph (never a frame grabbed from a video), shown untouched in a frame.
const PHOTO = { url: 'assets/photos/agam_at_fountain_user.jpg', width: 800, y: 60 };
const COOL = [F.blue, F.periwinkle, F.light_blue, F.lilac, F.navy, F.teal];
const SHADOW_SHIFT = [16, 10];                         // every shadow falls a little to the right and forward
const DISC = { x: 150, y: 120, radius: 330 };
const POOL = { radius: 520, jets: 430 };
const R3 = ringSpec('R3');
const R3_LENGTH = 2 * Math.PI * R3.radius;
const SPIN = { R1: 26, R2: -18, R3: 12, R4: -24, R5: 34 };   // degrees per second
const TITLE = { words: ['אש', 'ומים'], cap: 165, y: 740 };
const MAIN_FLAME = { height: 240, width: 124 };
/* Our hanukkiah (model/): eight candles in white cups in a circle on the big ring, the shamash on the top drum,
   a white goblet foot under the lowest ring. */
const HANUKKIAH = {
  candles: 8, circle: 264, candle: 200, candleRadius: 19, shamash: 250, cup: { radius: 30, height: 24 },
  flame: 104, flameWidth: 54, flight: 0.45,
  foot: { neckRadius: 46, neckHeight: 84, baseRadius: 232, baseHeight: 54, side: 0xD9DDE8 },
};
const SHAMASH_TOP = FOUNTAIN_TOP + HANUKKIAH.cup.height + HANUKKIAH.shamash;
const CANDLE_BASE = RING_LEVELS.R3.top + HANUKKIAH.cup.height;
const SPARKS = 18;
const MOTIF_SHIFT = 0;                                  // turns the painted pictures around the ring (0..1)

const stripe = (i) => (i % 3 === 2 ? WHITE : SPECTRUM[Math.floor(i / 3) % SPECTRUM.length]);
const discStripe = (i) => (i % 3 === 2 ? F.yellow : F.coral);

const coolStripe = (i) => (i % 3 === 2 ? WHITE : COOL[Math.floor(i / 3) % COOL.length]);

function buildSheet() {
  const surface = new PleatedSurface({
    pleats: SHEET.pleats, colorA: stripe, colorB: coolStripe, colorDisc: discStripe,
    colorA2: (i) => R3.colorA(i, SHEET.pleats), colorB2: (i) => R3.colorB(i, SHEET.pleats),
  });
  surface.uniforms.discAspect.value = Math.cos(VIEW_ANGLE * DEG);
  surface.setMotifs(createRingMotifs({ pleats: SHEET.pleats, aspect: R3_LENGTH / R3.height }));
  const group = new THREE.Group();
  group.add(surface.mesh);
  return { surface, group };
}

const blueCandle = () => new Candle({ radius: HANUKKIAH.candleRadius, teeth: 10, colorA: () => F.blue, colorB: () => F.periwinkle, capColor: F.light_blue });
const cupMesh = () => {
  const { radius, height } = HANUKKIAH.cup;
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, 32), new THREE.MeshBasicMaterial({ color: WHITE }));
  mesh.geometry.translate(0, height / 2, 0);
  return mesh;
};

/** Two-colour drum (white top, tinted side) for the goblet foot; its base sits at the group's origin. */
function drum(radius, height, side) {
  const group = new THREE.Group();
  const wall = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, 64, 1, true), new THREE.MeshBasicMaterial({ color: side }));
  wall.position.y = height / 2;
  const top = new THREE.Mesh(new THREE.CircleGeometry(radius, 64), new THREE.MeshBasicMaterial({ color: WHITE }));
  top.rotation.x = -Math.PI / 2;
  top.position.y = height;
  group.add(wall, top);
  return group;
}

function buildHanukkiah() {
  const group = new THREE.Group(), carousel = new THREE.Group();
  const { foot } = HANUKKIAH;
  const footGroup = new THREE.Group();
  const base = drum(foot.baseRadius, foot.baseHeight, foot.side), neck = drum(foot.neckRadius, foot.neckHeight, foot.side);
  neck.position.y = foot.baseHeight;
  footGroup.add(base, neck);
  footGroup.position.y = FOUNTAIN_BOTTOM - foot.baseHeight - foot.neckHeight;
  const shamash = { candle: blueCandle(), cup: cupMesh() };
  shamash.cup.position.y = FOUNTAIN_TOP;
  shamash.candle.group.position.y = FOUNTAIN_TOP + HANUKKIAH.cup.height;
  const candles = Array.from({ length: HANUKKIAH.candles }, (_, index) => {
    const angle = ((index + 0.5) / HANUKKIAH.candles) * Math.PI * 2;
    const x = Math.sin(angle) * HANUKKIAH.circle, z = Math.cos(angle) * HANUKKIAH.circle;
    const candle = blueCandle(), cup = cupMesh();
    cup.position.set(x, RING_LEVELS.R3.top, z);
    candle.group.position.set(x, CANDLE_BASE, z);
    const flame = new Flame({ seed: 20 + index * 5 });
    carousel.add(candle.group, cup);
    group.add(flame.group);
    return { candle, cup, flame, angle, order: index };
  });
  group.add(footGroup, carousel, shamash.cup, shamash.candle.group);
  return { group, carousel, foot: footGroup, shamash, candles };
}

/** Flat soft shadows that sit on the ring tops, the water and under the foot: depth without lighting. */
function buildShadows() {
  const group = new THREE.Group(), carousel = new THREE.Group();
  const lying = (radius, y, options) => {
    const mesh = discShadow(radius, options);
    mesh.position.set(SHADOW_SHIFT[0], y, SHADOW_SHIFT[1]);
    group.add(mesh);
    return mesh;
  };
  const candles = Array.from({ length: HANUKKIAH.candles }, (_, index) => {
    const angle = ((index + 0.5) / HANUKKIAH.candles) * Math.PI * 2;
    const mesh = discShadow(54, { strength: 0.3 });
    mesh.position.set(Math.sin(angle) * HANUKKIAH.circle + 10, RING_LEVELS.R3.top + 1, Math.cos(angle) * HANUKKIAH.circle + 6);
    carousel.add(mesh);
    return mesh;
  });
  group.add(carousel);
  return {
    group, carousel, candles,
    onR3: lying(ringSpec('R4').radius * 1.55, RING_LEVELS.R3.top + 0.8, { strength: 0.3 }),
    onR4: lying(ringSpec('R5').radius * 1.6, RING_LEVELS.R4.top + 0.8, { strength: 0.3 }),
    onR5: lying(52, FOUNTAIN_TOP + 0.8, { strength: 0.3 }),
    water: lying(ringSpec('R2').radius * 1.5, FOUNTAIN_BOTTOM + 2.5, { strength: 0.3 }),
    floor: lying(HANUKKIAH.foot.baseRadius * 1.55, FOUNTAIN_BOTTOM - HANUKKIAH.foot.baseHeight - HANUKKIAH.foot.neckHeight + 1, { strength: 0.6, tint: 0x10153A }),
  };
}

function buildSparks() {
  const geometry = new THREE.SphereGeometry(1, 20, 12);
  return Array.from({ length: SPARKS }, (_, i) => {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color: DOTS[i % DOTS.length] }));
    const side = i % 2 ? 1 : -1;
    return {
      mesh, seed: i * 13 + 5, radius: 7 + rand(i + 40) * 7, delay: rand(i + 80) * 1.5,
      x: side * (130 + rand(i) * 300), y: -150 + rand(i + 20) * 950, z: (rand(i + 60) - 0.5) * 500,
    };
  });
}

export async function createFilm(stage) {
  const timeline = createTimeline(data);
  const sheet = buildSheet();
  const card = new PhotoFrame({ photo: await loadPhoto(PHOTO.url), width: PHOTO.width });
  const shadows = buildShadows();
  const fountain = new Fountain({ omit: ['R3'], poolRadius: POOL.radius, jetRadius: POOL.jets });
  const title = new LineDotTitle(TITLE);
  const mainFlame = new Flame({ seed: 1 });
  const hanukkiah = buildHanukkiah();
  const sparks = buildSparks();
  stage.scene.add(card.group, shadows.group, sheet.group, fountain.group, title.group, mainFlame.group, hanukkiah.group, ...sparks.map((s) => s.mesh));

  const beats = timeline.beats;
  const landings = { R4: beats.wrap.at(2.3), R5: beats.wrap.at(2.55) };
  const paper = new THREE.Color(PAPER), sky = new THREE.Color(SKY), night = new THREE.Color(NIGHT);

  function updateCamera(t) {
    const cam = timeline.cameraAt(t);
    Object.assign(stage.rig, { yaw: cam.yaw + drift(t, 3, 0.07) * 1.2, pitch: cam.pitch, zoom: cam.zoom });
    stage.rig.target.set(0, cam.y, 0);
    stage.applyRig();
    stage.background.copy(paper).lerp(sky, tween(t, beats.wrap.at(0.6), 1.6)).lerp(night, tween(t, beats.flame.at(0.5), 1.6));
  }

  function updateSheet(t) {
    const { unfold, wrap } = beats;
    const centre = (SHEET.pleats - 1) / 2;
    const wrapK = tween(t, wrap.at(0.2), 2.0, 'inOutCubic');
    const length = lerp(SHEET.length, R3_LENGTH, wrapK), height = lerp(SHEET.height, R3.height, wrapK);
    const delay = (i) => unfold.at(0.3) + (Math.abs(i - centre) / centre) * 0.9;
    const rise = (i) => spring(t - delay(i), 2.4, 0.55);
    const fullDepth = (length / SHEET.pleats) * SHEET.depthRatio;
    sheet.surface.update({
      length, height, bend: wrapK,
      depth: (i) => fullDepth * tween(t, delay(i) + 0.15, 0.7, 'outBack'),
      top: (i) => (height / 2) * rise(i), bottom: (i) => (-height / 2) * rise(i),
    });
    const u = sheet.surface.uniforms;
    u.colorMix.value = tween(t, wrap.at(0.9), 1.1);
    u.motifAmount.value = tween(t, beats.split.at(0.5), 1.1);   // our hanukkiah's pictures are painted onto the big ring
    u.motifShift.value = MOTIF_SHIFT;
    const discRadius = DISC.radius * spring(t - unfold.at(1.65), 2.4, 0.42) * (1 - tween(t, wrap.at(-0.4), 0.4));
    u.discCentreRadius.value.set(DISC.x, DISC.y, discRadius);
    const dips = Object.values(landings).reduce((sum, at) => sum + wobble(t - at, 5, 0.35), 0);
    sheet.group.position.y = lerp(0, RING_LEVELS.R3.centre, wrapK) - 7 * dips;
    sheet.group.rotation.y = SPIN.R3 * DEG * softStart(t - wrap.at(2.2));
  }

  /** Places a ring: scale = uniform size, squash = vertical squash (0..1), anchored at its bottom edge. */
  function placeRing(id, { scale = 1, squash = 0, lift = 0 }, t, spinFrom) {
    const ring = fountain.rings[id], level = RING_LEVELS[id], spec = ringSpec(id);
    const sy = scale * (1 - squash);
    ring.group.visible = scale > 0.002;
    ring.group.scale.set(scale * (1 + squash * 0.5), sy, scale * (1 + squash * 0.5));
    ring.group.position.y = level.bottom + (spec.height / 2) * sy + lift;
    ring.group.rotation.y = SPIN[id] * DEG * softStart(t - spinFrom);
  }

  function updateFountain(t) {
    const { wrap, fountain: fb, flame } = beats;
    fountain.updatePool(t, spring(t - wrap.at(1.2), 1.8, 0.6) * (1 - tween(t, beats.split.at(0.15), 0.45, 'inBack')));
    placeRing('R1', { scale: spring(t - wrap.at(1.55), 2.6, 0.5) }, t, wrap.at(1.6));
    placeRing('R2', { scale: spring(t - wrap.at(1.75), 2.4, 0.5) }, t, wrap.at(1.8));
    ['R4', 'R5'].forEach((id) => {
      const land = landings[id];
      const fall = ease.inQuad(prog(t, land - 0.5, land));
      let squash = 0.2 * wobble(t - land, 4.5, 0.32);
      if (id === 'R5') squash += 0.22 * bump(t, flame.at(0), flame.at(0.3)) - 0.12 * wobble(t - flame.at(0.28), 4, 0.3);
      placeRing(id, { scale: t > land - 0.5 ? 1 : 0, squash, lift: (1 - fall) * 1300 }, t, land);
    });
    const sink = 1 - tween(t, flame.at(0.9), 0.8, 'inCubic');
    fountain.updateJets(t, (i) => spring(t - fb.at(0.05 + i * 0.06), 2.2, 0.5) * sink);
  }

  function updateTitle(t) {
    const { fountain: fb, flame } = beats;
    const start = fb.at(0.3);
    title.update(t - start, { span: 1.4, out: flame.at(0.5) - start, outSpan: 0.45 });
    const yaw = 14 * DEG;
    title.group.position.set(Math.sin(yaw) * 900, TITLE.y, Math.cos(yaw) * 900);   // centred, in front of the fountain
    title.group.visible = t > start && t < flame.at(1.0);
    stage.billboard(title.group);
  }

  function updateFire(t) {
    const { flame, split } = beats;
    const grow = spring(t - flame.at(0.28), 2.4, 0.42);
    const riseK = spring(t - split.at(0.3), 2.2, 0.55);
    const flameBase = lerp(FOUNTAIN_TOP, SHAMASH_TOP, riseK);
    const shrink = tween(t, split.at(0.45), 0.7);
    const squash = 0.5 * bump(t, split.at(0), split.at(0.3)) - 0.35 * bump(t, split.at(0.3), split.at(0.62));
    mainFlame.update(t, {
      height: lerp(MAIN_FLAME.height, HANUKKIAH.flame * 1.2, shrink) * grow,
      width: lerp(MAIN_FLAME.width, HANUKKIAH.flameWidth * 1.2, shrink) * grow, squash, energy: 1.1,
    });
    mainFlame.group.position.set(0, flameBase, 0);
    stage.billboard(mainFlame.group);
    // the shamash carries the flame up from the top drum
    hanukkiah.shamash.cup.scale.setScalar(Math.max(0.001, spring(t - split.at(0.15), 3, 0.5)));
    hanukkiah.shamash.candle.update(Math.max(0, flameBase - FOUNTAIN_TOP - HANUKKIAH.cup.height));
    // the pool gives way to the goblet foot
    hanukkiah.foot.scale.setScalar(Math.max(0.001, spring(t - split.at(0.45), 2.4, 0.5)));
    hanukkiah.foot.visible = t > split.at(0.45);
    const spin = sheet.group.rotation.y;
    hanukkiah.carousel.rotation.y = spin;
    hanukkiah.candles.forEach((item) => updateCandle(t, item, flameBase, spin));
  }

  function updateCandle(t, item, flameBase, spin) {
    const { split } = beats;
    const cupAt = split.at(0.5 + 0.05 * item.order), popAt = split.at(0.62 + 0.06 * item.order);
    const departAt = split.at(0.9 + 0.07 * item.order), landAt = departAt + HANUKKIAH.flight;
    const hit = wobble(t - landAt, 5, 0.4);
    const height = HANUKKIAH.candle * spring(t - popAt, 3, 0.45) * (1 - 0.1 * hit);
    item.cup.scale.setScalar(Math.max(0.001, spring(t - cupAt, 3.4, 0.45)));
    item.candle.update(height, 0.25 * Math.max(0, hit));
    const angle = item.angle + spin, side = Math.sin(angle);
    const target = [Math.sin(angle) * HANUKKIAH.circle, CANDLE_BASE + height, Math.cos(angle) * HANUKKIAH.circle];
    const k = ease.inOutCubic(prog(t, departAt, landAt));
    const [x, y, z] = bezier2([0, flameBase + 30, 0], [target[0] * 0.5, SHAMASH_TOP + 210, target[2] * 0.5], target, k);
    const size = t < departAt ? 0 : lerp(0.45, 0.7, k) + 0.3 * spring(t - landAt, 4, 0.35);
    item.flame.update(t, {
      height: HANUKKIAH.flame * size, width: HANUKKIAH.flameWidth * size,
      lean: -side * 0.9 * Math.sin(k * Math.PI), squash: 0.4 * Math.max(0, hit), energy: 1,
    });
    item.flame.group.position.set(x, y, z);
    stage.billboard(item.flame.group);
  }

  /** The framed photo floats in over the stripes once the camera has turned, then lifts away as the sheet wraps. */
  function updateCard(t) {
    const { polymorph, wrap } = beats;
    const inAt = polymorph.at(1.9), out = tween(t, wrap.at(0.1), 0.45, 'inBack');
    const pop = spring(t - inAt, 2.2, 0.5), rise = ease.outExpo(prog(t, inAt, inAt + 0.7));
    card.group.visible = t > inAt && out < 1;
    const yaw = stage.rig.yaw * DEG;
    card.group.position.set(Math.sin(yaw) * 1000, PHOTO.y - (1 - rise) * 700 + out * 420 + drift(t, 9, 0.2) * 8, Math.cos(yaw) * 1000);
    card.group.scale.setScalar(Math.max(0.001, lerp(0.7, 1, pop) * (1 - out)));
    stage.billboard(card.group);
    card.group.rotateZ((-2.5 + 6 * (1 - pop) + drift(t, 11, 0.15)) * DEG);
    card.setLift(pop);
  }

  const size = (mesh, k) => { mesh.visible = k > 0.01; mesh.scale.setScalar(Math.max(0.001, k)); };

  function updateShadows(t) {
    const { wrap, split } = beats;
    const poolLeft = 1 - tween(t, split.at(0.15), 0.45, 'inBack');
    size(shadows.onR3, ease.inQuad(prog(t, landings.R4 - 0.5, landings.R4)));
    size(shadows.onR4, ease.inQuad(prog(t, landings.R5 - 0.5, landings.R5)));
    size(shadows.water, spring(t - wrap.at(1.75), 2.4, 0.5) * poolLeft);
    size(shadows.onR5, spring(t - split.at(0.15), 3, 0.5));
    size(shadows.floor, spring(t - split.at(0.45), 2.4, 0.5));
    shadows.carousel.rotation.y = sheet.group.rotation.y;
    shadows.candles.forEach((mesh, index) => size(mesh, spring(t - split.at(0.5 + 0.05 * index), 3.4, 0.45)));
    // the wide ring above darkens the top of the rings under it
    fountain.rings.R2.surface.uniforms.shadeTop.value = 0.38 * tween(t, wrap.at(1.9), 0.6);
    fountain.rings.R1.surface.uniforms.shadeTop.value = 0.3 * tween(t, wrap.at(1.9), 0.6);
  }

  function updateSparks(t) {
    const start = beats.split.at(1.3);
    sparks.forEach((spark) => {
      const local = t - start - spark.delay;
      const pop = spring(local, 3.5, 0.4);
      spark.mesh.visible = pop > 0.01;
      spark.mesh.scale.setScalar(Math.max(0.001, spark.radius * pop));
      spark.mesh.position.set(spark.x + drift(t, spark.seed, 0.12) * 18, spark.y + clamp(local, 0, 99) * 14, spark.z);
    });
  }

  function update(t) {
    updateCamera(t);
    updateSheet(t);
    updateFountain(t);
    updateTitle(t);
    updateFire(t);
    updateSparks(t);
    updateCard(t);
    updateShadows(t);
  }

  return { timeline, update };
}
