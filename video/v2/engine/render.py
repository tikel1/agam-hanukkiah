"""Renders a film from player.html through headless Edge (DevTools protocol) and encodes it with ffmpeg.

  stills:  python render.py --film proof --stills 2,5.5,9 --out stills
  video:   python render.py --film proof --video proof.mp4 [--audio narration.wav] [--workers 4] [--samples 12]
  part:    python render.py --film proof --video part.mp4 --range 6,9
  preview: python render.py --serve          (then open the printed address in a browser)

Needs imageio-ffmpeg, websocket-client and requests: use the v1 venv, ..\\..\\animation\\.venv\\Scripts\\python.
Every frame is seek(frame / fps) in the page, so frames can be rendered in any order and by several workers."""
import argparse
import base64
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import requests
import websocket

HERE = Path(__file__).resolve().parent
EDGE_CANDIDATES = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)
LAUNCH_WIDTH, LAUNCH_HEIGHT = 1920, 1920   # window before the film reports its own frame size
TMP = Path.home() / "AppData/Local/Temp/agam_anim_v2"
FIRST_DEBUG_PORT = 9510
EDGE_START_TRIES = 60
PAGE_READY_TRIES = 1500   # the full film loads many textures; four tabs at once can take minutes
POLL_SECONDS = 0.2
VIDEO_CRF = "17"
AUDIO_BITRATE = "192k"
AUDIO_RATE = "48000"


def find_edge():
    for path in EDGE_CANDIDATES:
        if path.exists():
            return path
    raise RuntimeError("Microsoft Edge not found; looked in: " + ", ".join(str(p) for p in EDGE_CANDIDATES))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript"}

    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start_server(port=0):
    """Serves the engine folder on localhost only (ES modules do not load from file://). Returns (server, base url)."""
    handler = functools.partial(QuietHandler, directory=str(HERE))
    # Four tabs load a film of many modules and pictures at once: the default backlog of 5 waiting connections
    # drops some of those requests ("failed to fetch module"), so make the queue long.
    class Server(http.server.ThreadingHTTPServer):
        request_queue_size = 256
        daemon_threads = True
    server = Server(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def free_ports(count):
    """Free local ports, all different (the probes stay open together, so the system cannot hand one out twice).
    Every Edge instance gets its own: several renders can then run at the same time without sharing a tab."""
    import socket
    probes = [socket.socket() for _ in range(count)]
    try:
        for probe in probes:
            probe.bind(("127.0.0.1", 0))
        return [probe.getsockname()[1] for probe in probes]
    finally:
        for probe in probes:
            probe.close()


def free_port():
    return free_ports(1)[0]


class Page:
    """One headless Edge tab showing the player in render mode."""

    def __init__(self, port, url):
        self.port, self.calls = port, 0
        TMP.mkdir(parents=True, exist_ok=True)
        self.proc = subprocess.Popen(
            [str(find_edge()), "--headless=new", f"--remote-debugging-port={port}", "--remote-allow-origins=*",
             "--hide-scrollbars", f"--window-size={LAUNCH_WIDTH},{LAUNCH_HEIGHT}", "--force-device-scale-factor=1",
             "--ignore-gpu-blocklist", "--enable-unsafe-swiftshader", "--autoplay-policy=no-user-gesture-required",
             f"--user-data-dir={TMP / ('profile' + str(port))}", url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ws = websocket.create_connection(self._tab_socket(), max_size=None)
        self._wait_ready()
        film = self.eval("window.__film")
        self.call("Emulation.setDeviceMetricsOverride", width=film["width"], height=film["height"], deviceScaleFactor=1, mobile=False)

    def _tab_socket(self):
        for _ in range(EDGE_START_TRIES):
            try:
                tabs = requests.get(f"http://127.0.0.1:{self.port}/json", timeout=2).json()
                return [tab for tab in tabs if tab["type"] == "page"][0]["webSocketDebuggerUrl"]
            except (requests.RequestException, IndexError, KeyError):
                time.sleep(POLL_SECONDS * 2)
        self.proc.terminate()
        raise RuntimeError(f"Edge did not open a debugging tab on port {self.port}")

    def _wait_ready(self):
        for _ in range(PAGE_READY_TRIES):
            error = self.eval("window.__error || null")
            if error:
                raise RuntimeError("player failed: " + error)
            if self.eval("window.__ready === true"):
                return
            time.sleep(POLL_SECONDS)
        raise RuntimeError("player never became ready (page title: " + str(self.eval("document.title")) + ")")

    def call(self, method, **params):
        self.calls += 1
        self.ws.send(json.dumps({"id": self.calls, "method": method, "params": params}))
        while True:
            reply = json.loads(self.ws.recv())
            if reply.get("id") == self.calls:
                if "error" in reply:
                    raise RuntimeError(f"{method}: {reply['error']}")
                return reply.get("result", {})

    def eval(self, expression):
        result = self.call("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in result:
            raise RuntimeError(json.dumps(result["exceptionDetails"], ensure_ascii=False)[:800])
        return result["result"].get("value")

    def frame(self, t):
        self.eval(f"seek({t!r})")
        # The first screenshot after a seek can show the HTML layer (subtitles) of the frame before: the canvas and
        # the HTML reach the compositor one frame apart. A throw-away capture first makes both current.
        self.call("Page.captureScreenshot", format="jpeg", quality=1, clip={"x": 0, "y": 0, "width": 8, "height": 8, "scale": 1})
        return base64.b64decode(self.call("Page.captureScreenshot", format="png")["data"])

    def close(self):
        try:
            self.ws.close()
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def player_url(base, film, samples, shutter, only=""):
    extra = f"&only={only}" if only else ""
    return f"{base}/player.html?film={film}&render=1&samples={samples}&shutter={shutter}{extra}"


def render_frames(job):
    """Worker: renders the given frame numbers to PNG files."""
    port, url, frames, fps, outdir = job
    page = Page(port, url)
    try:
        for index in frames:
            (outdir / f"f{index:05d}.png").write_bytes(page.frame(index / fps))
    finally:
        page.close()
    return len(frames)


def render_stills(url, times, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    page = Page(free_port(), url)
    try:
        print("renderer:", page.eval(
            "(() => { const gl = document.createElement('canvas').getContext('webgl2');"
            " const info = gl && gl.getExtension('WEBGL_debug_renderer_info');"
            " return info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : 'unknown'; })()"))
        for t in times:
            started = time.time()
            (outdir / f"t{t:07.3f}.png").write_bytes(page.frame(t))
            print(f"still {t} ({time.time() - started:.2f}s)")
    finally:
        page.close()


def film_info(url):
    page = Page(free_port(), url)
    try:
        return page.eval("window.__film")
    finally:
        page.close()


def encode(frames_dir, fps, start_frame, out, audio):
    import imageio_ffmpeg
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-framerate", str(fps), "-start_number", str(start_frame),
               "-i", str(frames_dir / "f%05d.png")]
    if audio:
        command += ["-i", str(audio), "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", AUDIO_RATE, "-af", "apad", "-shortest"]   # pad the sound with silence to the picture's end
    command += ["-c:v", "libx264", "-crf", VIDEO_CRF, "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(fps),
                "-movflags", "+faststart", str(out)]
    subprocess.run(command, check=True, capture_output=True)


def render_video(url, out, workers, audio, time_range):
    info = film_info(url)
    fps = info["fps"]
    first = int(round(time_range[0] * fps)) if time_range else 0
    last = int(round(time_range[1] * fps)) if time_range else info["frames"]
    frames = list(range(first, last))
    if not frames:
        raise ValueError("nothing to render: the range is empty")
    if audio is None and info.get("audio"):
        audio = HERE / info["audio"]
    if audio and not Path(audio).exists():
        raise FileNotFoundError(f"audio file not found: {audio}")
    frames_dir = TMP / f"frames_{os.getpid()}"   # one folder per run: several renders can run at once
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True)
    ports = free_ports(workers)
    jobs = [(ports[w], url, frames[w::workers], fps, frames_dir) for w in range(workers)]
    started = time.time()
    with ProcessPoolExecutor(workers) as pool:
        done = sum(pool.map(render_frames, jobs))
    render_seconds = time.time() - started
    print(f"rendered {done} frames in {render_seconds:.0f}s ({render_seconds / done:.2f}s per frame, {workers} workers)")
    started = time.time()
    encode(frames_dir, fps, first, out, audio)
    print(f"encoded {out} in {time.time() - started:.0f}s")
    shutil.rmtree(frames_dir, ignore_errors=True)   # the frames are large: do not leave them behind


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--film", default="proof", help="folder name under films/")
    parser.add_argument("--stills", help="comma separated times in seconds")
    parser.add_argument("--out", default="stills", help="folder for --stills")
    parser.add_argument("--video", help="output mp4")
    parser.add_argument("--range", help="start,end in seconds (default: the whole film)")
    parser.add_argument("--audio", help="wav/mp3 to mux (default: the timeline's audio, if any)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--samples", type=int, default=12, help="sub-frames per frame (motion blur + smooth edges)")
    parser.add_argument("--shutter", type=float, default=0.5, help="shutter as a fraction of the frame time")
    parser.add_argument("--only", default="", help="film v2: build only these beats, e.g. b03,b04 (faster)")
    parser.add_argument("--serve", action="store_true", help="only serve the player for preview")
    parser.add_argument("--port", type=int, default=8765, help="port for --serve")
    return parser.parse_args()


def main():
    args = parse_args()
    if not (HERE / "films" / args.film / "film.js").exists():
        sys.exit(f"no such film: films/{args.film}/film.js")
    if args.serve:
        _, base = start_server(args.port)
        print(f"preview: {base}/player.html?film={args.film}   (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return
    _, base = start_server()
    url = player_url(base, args.film, args.samples, args.shutter, args.only)
    if args.stills:
        render_stills(url, [float(x) for x in args.stills.split(",")], Path(args.out))
    if args.video:
        time_range = [float(x) for x in args.range.split(",")] if args.range else None
        render_video(url, Path(args.video), args.workers, Path(args.audio) if args.audio else None, time_range)


if __name__ == "__main__":
    main()
