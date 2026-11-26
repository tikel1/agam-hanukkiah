"""High-resolution stills of the hanukkiah from the live viewer (headless Edge over CDP), for print documents.

Usage: python render_stills.py [shot ...]   (writes stills/<shot>.png; no names = every shot)
Needs `websocket-client`. Each shot sets the viewer's state through window.__viewer, then captures the canvas.
"""

from __future__ import annotations

import base64
import json
import math
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

HERE = Path(__file__).resolve().parent
PAGE = HERE / "live" / "index.html"
OUT = HERE / "stills"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
PORT = 9341
SIZE = (1400, 1400)
SCALE = 2  # device pixels per CSS pixel
TARGET = (0, 0.085, 0)

# name: (azimuth deg, elevation deg, distance m, settings JS run before the capture, settle seconds)
DAY = "v.setDark(false); v.setPainted(true); v.setExplode(false); v.setLit(true); v.setNight(8);"
SHOTS = {
    "hero_left": (-35, 20, 0.62, DAY, 4),
    "hero_right": (62, 20, 0.62, DAY, 4),
    "hero_right_wide": (80, 20, 0.62, DAY, 4),
    "night": (-20, 18, 0.66, "v.setDark(true); v.setPainted(true); v.setExplode(false); v.setLit(true); v.setNight(8);", 6),
    "white_print": (-25, 22, 0.66, "v.setDark(false); v.setPainted(false); v.setExplode(false); v.setLit(false);", 3),
    "paint_closeup": (-30, 8, 0.30, "v.setDark(false); v.setPainted(true); v.setExplode(false); v.setLit(false);", 3),
    "exploded": (-25, 16, 0.9, "v.setDark(false); v.setPainted(true); v.setLit(false); v.setExplode(true);", 5),
}

SHARP_SHADOWS = """window.__viewer.scene.traverse((o) => {
  if (o.isLight && o.castShadow) { o.shadow.mapSize.set(4096, 4096); o.shadow.radius = 4; if (o.shadow.map) { o.shadow.map.dispose(); o.shadow.map = null; } }
}); window.__viewer.renderer.shadowMap.needsUpdate = true;"""


class Edge:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [str(EDGE), "--headless=new", f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
             "--hide-scrollbars", f"--window-size={SIZE[0]},{SIZE[1]}", "--ignore-gpu-blocklist",
             "--enable-unsafe-swiftshader", f"--user-data-dir={tempfile.mkdtemp()}", "--no-first-run", PAGE.as_uri()],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ws = websocket.create_connection(self._socket(), max_size=None)
        self.next_id = 0

    def _socket(self) -> str:
        for _ in range(80):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                return next(t for t in tabs if t["type"] == "page")["webSocketDebuggerUrl"]
            except Exception:
                time.sleep(0.5)
        raise SystemExit("Edge did not start")

    def call(self, method: str, **params):
        self.next_id += 1
        self.ws.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == self.next_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]

    def eval(self, expression: str):
        result = self.call("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in result:
            raise RuntimeError(f"JS error in {expression[:80]}: {result['exceptionDetails']}")
        return result["result"].get("value")

    def close(self) -> None:
        self.proc.kill()


def camera_js(azimuth: float, elevation: float, distance: float) -> str:
    a, e = math.radians(azimuth), math.radians(elevation)
    x = TARGET[0] + distance * math.cos(e) * math.sin(a)
    y = TARGET[1] + distance * math.sin(e)
    z = TARGET[2] + distance * math.cos(e) * math.cos(a)
    return (f"v.controls.target.set({TARGET[0]}, {TARGET[1]}, {TARGET[2]}); v.camera.position.set({x:.4f}, {y:.4f}, {z:.4f});"
            " v.controls.update();")


def main() -> None:
    names = sys.argv[1:] or list(SHOTS)
    OUT.mkdir(exist_ok=True)
    edge = Edge()
    try:
        edge.call("Emulation.setDeviceMetricsOverride", width=SIZE[0], height=SIZE[1], deviceScaleFactor=SCALE, mobile=False)
        for _ in range(120):
            if edge.eval("!!window.__viewer && document.getElementById('loader').hidden"):
                break
            time.sleep(0.5)
        edge.eval("document.getElementById('chrome').style.display = 'none'; window.__viewer.setRotate(false);"
                  " window.__viewer.setBackground('white');")
        edge.eval(SHARP_SHADOWS)
        for name in names:
            azimuth, elevation, distance, settings, settle = SHOTS[name]
            edge.eval(f"(() => {{ const v = window.__viewer; {settings} {camera_js(azimuth, elevation, distance)} }})()")
            time.sleep(settle)
            shot = edge.call("Page.captureScreenshot", format="png")
            (OUT / f"{name}.png").write_bytes(base64.b64decode(shot["data"]))
            print("wrote", OUT / f"{name}.png")
    finally:
        edge.close()


if __name__ == "__main__":
    main()
