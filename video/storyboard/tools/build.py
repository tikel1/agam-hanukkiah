"""Builds storyboard/frames/*.svg, renders PNGs with headless Edge, and makes the contact sheets.

Usage (from anywhere): python storyboard/tools/build.py [--no-render]
Needs: Pillow, Microsoft Edge (headless screenshot). No other dependency.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import scenes_a  # noqa: E402
import scenes_b  # noqa: E402
from style import FONT_FILE, H, NAVY, W, subtitle, svg_doc  # noqa: E402

STORY = HERE.parent
FRAMES = STORY / "frames"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SCENES = [getattr(scenes_a, f"scene{n:02d}", None) or getattr(scenes_b, f"scene{n:02d}") for n in range(1, 12)]
SAMPLE_SUBTITLE_NOTE = "Subtitle line is a sample of the safe band (y 900-1040), not final text."


def write_frames() -> list[Path]:
    FRAMES.mkdir(exist_ok=True)
    written = []
    for n, scene in enumerate(SCENES, start=1):
        data = scene()
        for key in ("a", "b", "c"):
            if key not in data:
                continue
            name = f"scene{n:02d}" + ("" if key == "a" else f"_{key}") + ".svg"
            path = FRAMES / name
            path.write_text(svg_doc(data[key] + subtitle(data["sub"])), encoding="utf-8")
            written.append(path)
    return written


def render(svg: Path) -> None:
    png = svg.with_suffix(".png")
    cmd = [str(EDGE), "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
           f"--screenshot={png}", f"--window-size={W},{H}", svg.as_uri()]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not png.exists():
        raise RuntimeError(f"render failed for {svg.name}: {result.stderr[-300:]}")


def contact_sheet(pattern: str, out: Path, cols: int = 4) -> None:
    """Grid of frames with big scene numbers. pattern: 'a' for key frames, 'b' for second frames."""
    tw, th, pad = 480, 270, 14
    files = []
    for n in range(1, 12):
        name = f"scene{n:02d}" + ("" if pattern == "a" else "_b") + ".png"
        files.append((n, FRAMES / name))
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), "#d9d6cc")
    font = ImageFont.truetype(str(STORY.parents[1] / "model" / "fonts" / "SecularOne-Regular.ttf"), 34)
    draw = ImageDraw.Draw(sheet)
    for idx, (n, path) in enumerate(files):
        x, y = pad + (idx % cols) * (tw + pad), pad + (idx // cols) * (th + pad)
        sheet.paste(Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        draw.rounded_rectangle((x + 8, y + 8, x + 62, y + 54), 8, fill=NAVY)
        draw.text((x + 35, y + 31), str(n), font=font, fill="white", anchor="mm")
    sheet.save(out)


def main() -> None:
    svgs = write_frames()
    if "--no-render" not in sys.argv:
        for svg in svgs:
            render(svg)
        contact_sheet("a", STORY / "contact_sheet.png")
        contact_sheet("b", STORY / "contact_sheet_motion.png")
    print(f"wrote {len(svgs)} frames")


if __name__ == "__main__":
    main()
