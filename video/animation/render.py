"""Renders index.html frames through headless Edge (DevTools protocol) and encodes draft_v1.mp4 with ffmpeg.

  stills:  python render.py --stills 5,15.5,60 --out stills/            (PNG per time in seconds)
  video:   python render.py --video draft_v1.mp4 [--workers 4]
  Needs the venv in .venv (imageio-ffmpeg, websocket-client, requests). Edge is driven over a debugging port, no driver."""
import argparse, base64, json, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import requests, websocket

HERE = Path(__file__).resolve().parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FPS = 30
TMP = Path.home() / "AppData/Local/Temp/agam_anim"


class Page:
    def __init__(self, port, page="index.html"):
        self.port, self.n = port, 0
        TMP.mkdir(parents=True, exist_ok=True)
        url = (HERE / page).as_uri() + "?render=1"
        self.proc = subprocess.Popen([EDGE, "--headless", "--disable-gpu", f"--remote-debugging-port={port}", "--allow-file-access-from-files",
                                      "--hide-scrollbars", "--window-size=1920,1080", f"--user-data-dir={TMP / ('prof' + str(port))}", url],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                tab = [t for t in requests.get(f"http://127.0.0.1:{port}/json", timeout=2).json() if t["type"] == "page"][0]
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise RuntimeError("Edge did not start")
        self.ws = websocket.create_connection(tab["webSocketDebuggerUrl"], max_size=None)
        self.call("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=1, mobile=False)
        for _ in range(100):
            if self.eval("window.__ready === true"):
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("page never became ready: " + str(self.eval("document.title")))

    def call(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.n:
                if "error" in r:
                    raise RuntimeError(f"{method}: {r['error']}")
                return r.get("result", {})

    def eval(self, js):
        r = self.call("Runtime.evaluate", expression=js, returnByValue=True)
        if "exceptionDetails" in r:
            raise RuntimeError(json.dumps(r["exceptionDetails"], ensure_ascii=False)[:600])
        return r["result"].get("value")

    def frame(self, t):
        self.eval(f"seek({t})")
        return base64.b64decode(self.call("Page.captureScreenshot", format="png")["data"])

    def close(self):
        self.ws.close()
        self.proc.terminate()


def worker(args):
    port, frames, outdir = args
    page = Page(port)
    try:
        for i in frames:
            (outdir / f"f{i:05d}.png").write_bytes(page.frame(i / FPS))
    finally:
        page.close()
    return len(frames)


def stills(times, outdir, pg="index.html"):
    outdir.mkdir(parents=True, exist_ok=True)
    page = Page(9400, pg)
    try:
        for t in times:
            (outdir / f"t{t:07.3f}.png").write_bytes(page.frame(t))
            print("still", t)
    finally:
        page.close()


def video(out, workers, audio=None):
    import imageio_ffmpeg
    total = int(round(json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))["duration"] * FPS))
    frames_dir = TMP / "frames"
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True)
    chunks = [list(range(w, total, workers)) for w in range(workers)]
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        done = sum(ex.map(worker, [(9410 + w, chunks[w], frames_dir) for w in range(workers)]))
    print(f"rendered {done} frames in {time.time() - t0:.0f}s")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-framerate", str(FPS), "-i", str(frames_dir / "f%05d.png")]
    if audio:
        cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", help="comma separated seconds")
    ap.add_argument("--out", default="stills")
    ap.add_argument("--video")
    ap.add_argument("--audio", help="wav/mp3 muxed into the video (AAC 192k)")
    ap.add_argument("--page", default="index.html")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.stills:
        stills([float(x) for x in a.stills.split(",")], Path(a.out), a.page)
    if a.video:
        video(Path(a.video), a.workers, Path(a.audio) if a.audio else None)
