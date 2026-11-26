"""Renders the v2 key frames (SVG -> PNG with headless Edge), the colour script and the contact sheet.

Usage: python build.py [frame-name-prefix ...] [--no-render] [--sheets-only]
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from style import BOARD, H, W, svg_doc, subtitle  # noqa: E402
import frames  # noqa: E402

FRAMES = BOARD / "frames"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def write(frame: dict) -> Path:
    body = frame["body"]
    if frame.get("sub"):
        body += subtitle(frame["sub"], dark=frame.get("dark", False))
    defs = "".join(frame.get("defs", []))
    path = FRAMES / f'{frame["name"]}.svg'
    path.write_text(svg_doc(body, frame.get("bg", "#F7F5EE"), defs), encoding="utf-8")
    return path


def render(svg: Path) -> Path:
    png = svg.with_suffix(".png")
    with tempfile.TemporaryDirectory() as profile:
        cmd = [str(EDGE), "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
               f"--user-data-dir={profile}", f"--screenshot={png}", f"--window-size={W},{H}", svg.as_uri()]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not png.exists():
        raise RuntimeError(f"render failed for {svg.name}: {result.stderr[-400:]}")
    return png


def main() -> None:
    FRAMES.mkdir(exist_ok=True)
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = [f for f in frames.ALL() if not wanted or any(f["name"].startswith(w) for w in wanted)]
    svgs = [write(f) for f in todo]
    if "--no-render" not in sys.argv:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for png in pool.map(render, svgs):
                print("rendered", png.name, flush=True)


if __name__ == "__main__":
    main()
