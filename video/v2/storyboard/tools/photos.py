"""Photos for the storyboard. Writes photos/treated/*.jpg from photos/original/.

User rule (26.11.2026): a real photo is shown as it is. Crop and resize only, no colour change, no duotone, no
cutting into pleats. The design happens around it: a stripe frame, a pleated curtain that opens onto it.
duotone() and palette_map() are kept only for our own drawings (never for photos) and are not called here.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from style import F, INK, PAPER, GOLD, NIGHT

BOARD = Path(__file__).resolve().parent.parent
SRC, OUT = BOARD / "photos" / "original", BOARD / "photos" / "treated"


def _hex(c: str) -> tuple[int, int, int]:
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _crop(img: Image.Image, box: tuple[float, float, float, float], size: tuple[int, int]) -> Image.Image:
    w, h = img.size
    l, t, r, b = box
    return img.crop((int(l * w), int(t * h), int(r * w), int(b * h))).resize(size, Image.LANCZOS)


def duotone(name: str, box, size, dark: str = INK, light: str = PAPER, lo: int = 40, hi: int = 200,
            steps: int = 0, mid: str | None = None, out: str | None = None) -> Path:
    img = _crop(Image.open(SRC / name).convert("L"), box, size)
    img = ImageOps.autocontrast(img, cutoff=1).filter(ImageFilter.GaussianBlur(0.8))
    lut = []
    for v in range(256):
        t = min(max((v - lo) / (hi - lo), 0.0), 1.0)
        if steps:
            t = min(int(t * steps), steps - 1) / (steps - 1)
        lut.append(t)
    d, l = _hex(dark), _hex(light)
    m = _hex(mid) if mid else None
    rgb = Image.new("RGB", img.size)
    px, src = rgb.load(), img.load()
    for y in range(img.height):
        for x in range(img.width):
            t = lut[src[x, y]]
            if m and t < 0.5:
                c = tuple(round(a + (b - a) * t * 2) for a, b in zip(d, m))
            elif m:
                c = tuple(round(a + (b - a) * (t - 0.5) * 2) for a, b in zip(m, l))
            else:
                c = tuple(round(a + (b - a) * t) for a, b in zip(d, l))
            px[x, y] = c
    path = OUT / (out or name.rsplit(".", 1)[0] + "_duo.png")
    rgb.save(path)
    return path


PALETTE = [F[k] for k in ("white", "yellow", "orange", "coral", "brick", "rose", "lilac", "periwinkle",
                          "light_blue", "blue", "navy", "mint", "teal", "green", "grey")] + [PAPER]


NEUTRALS = [INK, "#7D8299", "#DADDDC", PAPER]


def palette_map(name: str, box, size, colours=None, blur: float = 1.6, clean: int = 5,
                out: str | None = None, grey_cut: float = 0.22) -> Path:
    """Snaps every pixel to the palette. Greys go to a neutral ramp (ink, slate, light grey, paper) by
    luminance, coloured pixels to the nearest chromatic palette colour, so white walls stay white."""
    import colorsys
    colours = [c for c in (colours or PALETTE) if c not in NEUTRALS and c not in (F["white"], F["grey"], PAPER, F["navy"])]
    chroma = [_hex(c) for c in colours]
    neutral = [_hex(c) for c in NEUTRALS]
    img = _crop(Image.open(SRC / name).convert("RGB"), box, size).filter(ImageFilter.GaussianBlur(blur))
    out_img = Image.new("RGB", img.size)
    src, dst = img.load(), out_img.load()
    cache: dict = {}
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = src[x, y]
            key = (r >> 2, g >> 2, b >> 2)
            if key not in cache:
                h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                if sat * (1 - abs(2 * l - 1)) < grey_cut * 0.6 or sat < grey_cut:
                    cache[key] = neutral[min(int(l * len(neutral) * 1.05), len(neutral) - 1)]
                else:
                    cache[key] = min(chroma, key=lambda c: (c[0] - r) ** 2 * 0.3 + (c[1] - g) ** 2 * 0.59 + (c[2] - b) ** 2 * 0.11
                                     + 4000 * min(abs(colorsys.rgb_to_hls(*(v / 255 for v in c))[0] - h), 1 - abs(colorsys.rgb_to_hls(*(v / 255 for v in c))[0] - h)))
            dst[x, y] = cache[key]
    q = out_img.filter(ImageFilter.ModeFilter(clean)) if clean else out_img
    path = OUT / (out or name.rsplit(".", 1)[0] + "_pal.png")
    q.save(path)
    return path


def clean(name: str, box, size, out: str) -> Path:
    """Real photos are shown as they are (user rule 26.11): crop and resize only, no colour change."""
    img = _crop(Image.open(SRC / name).convert("RGB"), box, size)
    path = OUT / out
    img.save(path, quality=92)
    return path


def build() -> None:
    """Every real photo: crop only. The treatments above stay for our own drawings, never for photos."""
    OUT.mkdir(parents=True, exist_ok=True)
    clean("agam_portrait_kaprov.jpg", (0.0, 0.0, 1.0, 1.0), (720, 1086), "agam_portrait.jpg")
    # Agam only as an older man (user 26.11): the 1991 photo is not used; beat 5 tapes in a crop of the portrait.
    clean("agam_portrait_kaprov.jpg", (0.08, 0.50, 0.92, 0.97), (608, 534), "agam_portrait_face.jpg")
    clean("agam_at_fountain_user.jpg", (0.50, 0.0, 1.0, 1.0), (735, 1300), "agam_tribute.jpg")
    clean("menorah_nyc_2023_chabad.jpg", (0.27, 0.0, 0.67, 1.0), (620, 1170), "menorah_nyc.jpg")
    clean("work_sheba_circles.jpg", (0.08, 0.04, 0.94, 0.86), (720, 830), "work_circles.jpg")
    clean("work_museum_polymorph_4188.jpg", (0.22, 0.20, 0.66, 0.92), (620, 880), "work_polymorph.jpg")
    clean("work_museum_wall_4204.jpg", (0.50, 0.34, 1.0, 0.56), (900, 400), "work_wall.jpg")
    clean("fountain_2010_teicher.jpg", (0.18, 0.02, 0.82, 1.0), (720, 1100), "fountain_2010.jpg")


if __name__ == "__main__":
    build()
    print("photos written to", OUT)
