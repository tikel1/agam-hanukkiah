"""Build dist/index.html: index.html with the model GLB inlined as base64 (the artifact host does not serve .glb).

Usage: python build.py   (copies the newest ../model/out/hanukkiah_painted.glb into assets/ first)
"""
import base64
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_GLB = HERE.parent / "model" / "out" / "hanukkiah_painted.glb"
ASSET_GLB = HERE / "assets" / "hanukkiah_painted.glb"
MARKER = '<script type="importmap">'


def main() -> None:
    if not SOURCE_GLB.exists():
        raise SystemExit(f"Missing {SOURCE_GLB}: run the model build first")
    ASSET_GLB.parent.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE_GLB, ASSET_GLB)
    page = (HERE / "index.html").read_text(encoding="utf-8")
    if MARKER not in page:
        raise SystemExit("index.html has no import map to insert the model before")
    data = base64.b64encode(ASSET_GLB.read_bytes()).decode("ascii")
    blob = f'<script type="application/octet-stream" id="glb-data">{data}</script>\n'
    out = HERE / "dist" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page.replace(MARKER, blob + MARKER, 1), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
