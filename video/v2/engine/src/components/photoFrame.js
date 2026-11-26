/* Framed photo: the photograph itself, untouched (no filter, no colour change, never cut up), on a white card with
   a strip of colour blocks under it and a soft shadow, so it floats over the drawn world.
   User rules: no effects on photos; real photographs only, never frames grabbed from a video.
   The card lies in the XY plane of its group, centred; face it to the camera with stage.billboard(group). */
import { THREE } from '../core/stage.js';
import { WHITE, SPECTRUM } from '../palette.js';
import { cardShadow } from './shadows.js';

const MAT = 26;                        // white border around the photo
const STRIP_HEIGHT = 34;               // colour blocks under the photo
const STRIP_GAP = 22;
const SHADOW_OFFSET = [22, -34];

/** Loads an image as a texture whose colours are passed through untouched. */
export function loadPhoto(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, (texture) => {
      texture.colorSpace = THREE.NoColorSpace;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.anisotropy = 8;
      resolve(texture);
    }, undefined, () => reject(new Error(`photo failed to load: ${url}`)));
  });
}

export class PhotoFrame {
  /** photo = texture from loadPhoto, width = width of the photo in world units (its height follows the image). */
  constructor({ photo, width, stripColors = SPECTRUM }) {
    if (!photo || !photo.image) throw new Error('PhotoFrame: photo texture is missing');
    const height = (width * photo.image.height) / photo.image.width;
    this.width = width + MAT * 2;
    this.height = height + MAT * 2 + STRIP_GAP + STRIP_HEIGHT;
    this.group = new THREE.Group();
    const flat = (w, h, material, x, y, z) => {
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material);
      mesh.position.set(x, y, z);
      this.group.add(mesh);
      return mesh;
    };
    const photoY = (STRIP_GAP + STRIP_HEIGHT) / 2;
    this.shadow = cardShadow(this.width, this.height);
    this.shadow.position.set(SHADOW_OFFSET[0], SHADOW_OFFSET[1], -2);
    this.group.add(this.shadow);
    flat(this.width, this.height, new THREE.MeshBasicMaterial({ color: WHITE }), 0, 0, 0);
    flat(width, height, new THREE.MeshBasicMaterial({ map: photo }), 0, photoY, 1);
    const block = width / stripColors.length;
    stripColors.forEach((color, index) => {
      flat(block, STRIP_HEIGHT, new THREE.MeshBasicMaterial({ color }), -width / 2 + block * (index + 0.5), -this.height / 2 + MAT + STRIP_HEIGHT / 2, 1);
    });
  }

  /** lift 0..1: how far the card floats off the surface behind it (moves and widens the shadow). */
  setLift(lift) {
    this.shadow.position.set(SHADOW_OFFSET[0] * lift, SHADOW_OFFSET[1] * lift, -2);
    this.shadow.material.uniforms.strength.value = 0.34 - 0.1 * lift;
  }
}
