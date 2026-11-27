"""Colour grade for the family photos of the v2 film, so they sit in the film's look (one grade for every photo):
the dark room is lifted, shadows lean to the film's navy, lights to its paper white, the background is calmer
(greens and greys lose colour) and the painted colours stay vivid. Skin tones are left alone.
Usage: python grade_photo.py <source.jpg> <target.jpg>   (EXIF orientation is applied, the source is not changed)"""
import sys
import numpy as np
from PIL import Image, ImageOps

INK = np.array([0x23, 0x2C, 0x5E]) / 255        # palette.js INK
PAPER = np.array([0xF7, 0xF5, 0xEE]) / 255      # palette.js PAPER
MAX_SIDE = 2200
GRADE = dict(gamma=0.78, warm=0.025, navy=0.5, navy_falloff=2.4, paper=0.22, green_keep=0.4, grey_keep=0.7,
             wood_keep=0.86, vivid_gain=0.22, contrast=0.08)


def rgb_to_hsv(rgb):
    high, low = rgb.max(-1), rgb.min(-1)
    span = high - low
    safe = np.where(span == 0, 1, span)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.where(high == r, ((g - b) / safe) % 6, np.where(high == g, (b - r) / safe + 2, (r - g) / safe + 4)) / 6
    return np.stack([np.where(span == 0, 0, hue), np.where(high == 0, 0, span / np.where(high == 0, 1, high)), high], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0] * 6, hsv[..., 1], hsv[..., 2]
    channel = lambda n: v - v * s * np.clip(np.minimum((n + h) % 6, 4 - (n + h) % 6), 0, 1)
    return np.stack([channel(5), channel(3), channel(1)], -1)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def band(hue, lo, hi, soft=0.03):
    """1 inside the hue band lo..hi (0..1), soft edges."""
    return smoothstep(lo - soft, lo + soft, hue) * (1 - smoothstep(hi - soft, hi + soft, hue))


def grade(rgb, g=GRADE):
    rgb = rgb ** g['gamma']                                              # lift the room
    rgb = rgb * np.array([1 + g['warm'], 1, 1 - g['warm']])              # a little warmer
    rgb = np.clip(rgb, 0, 1)
    luma = (rgb @ np.array([0.299, 0.587, 0.114]))[..., None]
    rgb = rgb + g['contrast'] * (smoothstep(0, 1, rgb) - rgb)            # a touch of contrast back in the mids
    hsv = rgb_to_hsv(np.clip(rgb, 0, 1))
    hue, sat = hsv[..., 0], hsv[..., 1]
    keep = np.ones_like(sat)
    keep = keep * (1 - (1 - g['green_keep']) * band(hue, 0.17, 0.50))    # plants, green light
    keep = keep * (1 - (1 - g['grey_keep']) * (1 - smoothstep(0.12, 0.30, sat)))   # walls, sofa
    keep = keep * (1 - (1 - g['wood_keep']) * band(hue, 0.06, 0.13) * smoothstep(0.45, 0.6, sat))   # the table
    vivid = smoothstep(0.4, 0.7, sat) * (1 - band(hue, 0.03, 0.13))      # paint, markers, shirt: not skin, not wood
    hsv[..., 1] = np.clip(sat * keep * (1 + g['vivid_gain'] * vivid), 0, 1)
    rgb = hsv_to_rgb(hsv)
    shadow = g['navy'] * (1 - luma) ** g['navy_falloff']                 # shadows lean to navy (black becomes navy)
    rgb = rgb * (1 - shadow) + INK * shadow
    light = g['paper'] * luma ** 3                                       # lights lean to paper white
    rgb = rgb * (1 - light) + rgb * PAPER / PAPER.max() * light
    return np.clip(rgb, 0, 1)


def main(source, target):
    image = ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    image.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    out = grade(np.asarray(image, dtype=np.float64) / 255)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(target, quality=93)
    print(target, image.size)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
