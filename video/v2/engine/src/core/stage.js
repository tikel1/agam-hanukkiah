/* Stage: WebGL renderer, orthographic camera rig, and an accumulation pass that renders several sub-frames per
   frame (spread over the shutter time, each with a sub-pixel jitter) and averages them. That gives real motion
   blur and clean edges at once. Colours pass through untouched (no lighting, no tone mapping). */
import * as THREE from '../../vendor/three.module.js';

THREE.ColorManagement.enabled = false;

const CAMERA_DISTANCE = 4000;
const DEG = Math.PI / 180;
const HALTON = (index, base) => {
  let f = 1, r = 0, i = index;
  while (i > 0) { f /= base; r += f * (i % base); i = Math.floor(i / base); }
  return r;
};

const COPY_VERTEX = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';
const COPY_FRAGMENT = 'uniform sampler2D map; uniform float weight; varying vec2 vUv; void main(){ gl_FragColor = vec4(texture2D(map, vUv).rgb * weight, 1.0); }';

export class Stage {
  constructor({ canvas, width = 1920, height = 1080, background = 0xffffff }) {
    this.width = width;
    this.height = height;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, alpha: false });
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(width, height, false);
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
    this.renderer.autoClear = false;
    this.scene = new THREE.Scene();
    this.emptyScene = new THREE.Scene();
    this.background = new THREE.Color(background);
    this.camera = new THREE.OrthographicCamera(-width / 2, width / 2, height / 2, -height / 2, 1, CAMERA_DISTANCE * 2);
    /** yaw/pitch/roll in degrees, zoom 1 = one world unit per pixel, target = world point at the frame centre,
        shiftX/shiftY = pan in screen pixels after aiming. */
    this.rig = { yaw: 0, pitch: 0, roll: 0, zoom: 1, target: new THREE.Vector3(), shiftX: 0, shiftY: 0 };

    const targetOptions = { depthBuffer: true, samples: 4, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter };
    this.frameTarget = new THREE.WebGLRenderTarget(width, height, targetOptions);
    this.sumTarget = new THREE.WebGLRenderTarget(width, height, { depthBuffer: false, type: THREE.HalfFloatType });
    this.copyMaterial = new THREE.ShaderMaterial({
      uniforms: { map: { value: null }, weight: { value: 1 } },
      vertexShader: COPY_VERTEX, fragmentShader: COPY_FRAGMENT,
      depthTest: false, depthWrite: false, transparent: true, blending: THREE.AdditiveBlending,
    });
    this.copyScene = new THREE.Scene();
    this.copyScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.copyMaterial));
    this.copyCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  /** Aims the camera from the rig. Call after changing rig values and before orienting billboards. */
  applyRig() {
    const { yaw, pitch, roll, zoom, target, shiftX, shiftY } = this.rig;
    const cosPitch = Math.cos(pitch * DEG);
    const direction = new THREE.Vector3(Math.sin(yaw * DEG) * cosPitch, Math.sin(pitch * DEG), Math.cos(yaw * DEG) * cosPitch);
    this.camera.position.copy(target).addScaledVector(direction, CAMERA_DISTANCE);
    this.camera.up.set(0, 1, 0);
    this.camera.lookAt(target);
    this.camera.rotateZ(roll * DEG);
    this.camera.translateX(-shiftX / zoom);
    this.camera.translateY(-shiftY / zoom);
    this.camera.zoom = zoom;
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld(true);
  }

  /** Sets the whole rig in one go (anything left out returns to its neutral value) and aims the camera. */
  setRig({ yaw = 0, pitch = 0, roll = 0, zoom = 1, x = 0, y = 0, z = 0, shiftX = 0, shiftY = 0 } = {}) {
    Object.assign(this.rig, { yaw, pitch, roll, zoom, shiftX, shiftY });
    this.rig.target.set(x, y, z);
    this.applyRig();
  }

  /** Pins an object to the screen: px, py = frame pixels from the top left corner, whatever the camera does.
      scale 1 = one object unit per pixel. depth = how far in front of the camera target it sits (draw order).
      Call after applyRig / setRig. The object faces the camera. */
  place(object, px, py, { scale = 1, depth = 1500, roll = 0 } = {}) {
    const zoom = this.rig.zoom;
    object.position.set((px - this.width / 2) / zoom, (this.height / 2 - py) / zoom, -(CAMERA_DISTANCE - depth));
    this.camera.localToWorld(object.position);
    object.quaternion.copy(this.camera.quaternion);
    if (roll) object.rotateZ(roll * DEG);
    object.scale.setScalar(Math.max(1e-4, scale) / zoom);
  }

  /** Makes an object face the camera (titles, flames, dots). */
  billboard(object) {
    object.quaternion.copy(this.camera.quaternion);
  }

  /** Layered frame: each pass is its own scene with its own camera move, drawn in order over the one before.
      pass = { scene, update(time) (sets the rig and the scene), rect: [x, y, w, h] in frame pixels from the top
      left (optional: the whole picture is drawn scaled into that rectangle, e.g. a film inside a phone),
      clip: [x, y, w, h] (optional: only cuts, no scaling), background (optional colour that fills the rect/clip first) }. */
  renderPasses(passes, time) {
    const { renderer, width, height, frameTarget } = this;
    const full = () => { frameTarget.viewport.set(0, 0, width, height); frameTarget.scissor.set(0, 0, width, height); frameTarget.scissorTest = false; };
    full();
    renderer.setRenderTarget(frameTarget);
    renderer.setClearColor(this.background, 1);
    renderer.clear();
    passes.forEach((pass) => {
      pass.update(time);
      this.camera.updateProjectionMatrix();
      const rect = pass.rect || null, clip = pass.clip || rect;
      if (rect) frameTarget.viewport.set(rect[0], height - rect[1] - rect[3], rect[2], rect[3]);
      if (clip) { frameTarget.scissor.set(clip[0], height - clip[1] - clip[3], clip[2], clip[3]); frameTarget.scissorTest = true; }
      renderer.setRenderTarget(frameTarget);
      if (pass.background !== undefined && pass.background !== null) {
        renderer.setClearColor(pass.background, 1);
        renderer.clear(true, true, false);
      } else renderer.clearDepth();
      renderer.render(pass.scene, this.camera);
      if (rect || clip) { full(); renderer.setRenderTarget(frameTarget); }
    });
    // The anti-aliased target is only copied out after a render call, and only inside the clip of that call. So an
    // instant with no pass, or one whose last pass was clipped, needs one more (empty) full-frame render.
    if (passes.length === 0 || passes.some((pass) => pass.rect || pass.clip)) renderer.render(this.emptyScene, this.camera);
  }

  /** Renders the frame at time t. update may return a list of passes (see renderPasses) instead of using stage.scene. update(time) must set the whole scene from the time alone.
      samples = sub-frames, shutter = fraction of the frame interval the shutter stays open (0.5 = 180 degrees). */
  render(update, t, { fps = 30, samples = 1, shutter = 0.5 } = {}) {
    const { renderer, width, height } = this;
    renderer.setRenderTarget(this.sumTarget);
    renderer.setClearColor(0x000000, 1);
    renderer.clear();
    for (let i = 0; i < samples; i++) {
      const offset = samples === 1 ? 0 : ((i + 0.5) / samples - 0.5) * (shutter / fps);
      if (samples > 1) this.camera.setViewOffset(width, height, HALTON(i + 1, 2) - 0.5, HALTON(i + 1, 3) - 0.5, width, height);
      else this.camera.clearViewOffset();
      const passes = update(t + offset);
      if (Array.isArray(passes)) this.renderPasses(passes, t + offset);
      else {
        this.camera.updateProjectionMatrix();
        renderer.setRenderTarget(this.frameTarget);
        renderer.setClearColor(this.background, 1);
        renderer.clear();
        renderer.render(this.scene, this.camera);
      }
      this.copyMaterial.uniforms.map.value = this.frameTarget.texture;
      this.copyMaterial.uniforms.weight.value = 1 / samples;
      renderer.setRenderTarget(this.sumTarget);
      renderer.render(this.copyScene, this.copyCamera);
    }
    this.camera.clearViewOffset();
    this.copyMaterial.uniforms.map.value = this.sumTarget.texture;
    this.copyMaterial.uniforms.weight.value = 1;
    renderer.setRenderTarget(null);
    renderer.setClearColor(0x000000, 1);
    renderer.clear();
    renderer.render(this.copyScene, this.copyCamera);
  }
}

export { THREE };
