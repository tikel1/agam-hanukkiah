r"""Stage 5: edge-tts per sentence -> fit to scene windows -> narration.wav (48 kHz) + subtitles into timeline.json + subtitles.srt.
Run with the animation venv:  ..\animation\.venv\Scripts\python build_narration.py [--voice he-IL-HilaNeural]
Only narration sentences from narration_lines.json are sent to the TTS service (no names)."""
import argparse, asyncio, json, math, subprocess, wave
from pathlib import Path
import numpy as np, edge_tts, imageio_ffmpeg

HERE = Path(__file__).resolve().parent
TL_PATH = HERE.parent / "animation" / "timeline.json"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
LEAD, TAIL, GAP = 0.45, 0.35, 0.28       # seconds: inside-scene lead-in, tail, between sentences
MUSIC_DB, DUCK_DB = -16, -6
MAX_RATE, CUE_PAD, MAX_TEMPO = 14, 0.08, 1.15
LINE_CHARS = 32
DARK_SCENES, DARK_PANEL_CENTER_X = {11}, 520


def load_lines():
    lines = json.loads((HERE / "narration_lines.json").read_text(encoding="utf-8"))
    spoken = json.loads((HERE / "spoken_overrides.json").read_text(encoding="utf-8")) if (HERE / "spoken_overrides.json").exists() else {}
    return lines, spoken


CLIPS = {"dir": "clips"}
PACE_NOTE = "speaking a little faster than usual, brisk natural pace"
NOTES = json.loads((Path(__file__).resolve().parent / "delivery_notes.json").read_text(encoding="utf-8")) if (Path(__file__).resolve().parent / "delivery_notes.json").exists() else {}
ELEVEN_MODEL = "eleven_v4"
ENGINE = {"name": "edge"}                  # set from --engine in main()


def synth_eleven(text, voice_id, rate, out_mp3):
    """ElevenLabs TTS. Key comes from the ELEVEN_API_KEY env var only (never stored in the repo).
    The speed setting stands in for edge-tts' rate percentage."""
    import os, urllib.request
    key = os.environ.get("ELEVEN_API_KEY")
    if not key:
        raise SystemExit("ELEVEN_API_KEY is not set")
    body = json.dumps({"text": text, "model_id": ELEVEN_MODEL, "language_code": "he"}).encode("utf-8")   # v4 ignores speed/style
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                                 data=body, headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        Path(out_mp3).write_bytes(r.read())


async def synth(text, voice, rate, out_mp3):
    if ENGINE["name"] == "eleven":
        out = Path(out_mp3)
        if not out.exists():               # re-runs reuse clips: no repeat spend
            synth_eleven(text, voice, rate, out)
        return
    await edge_tts.Communicate(text, voice, rate=f"{rate:+d}%").save(str(out_mp3))


def to_wav(mp3, wav):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", str(SR), "-ac", "1",
                    "-af", "silenceremove=start_periods=1:start_threshold=-48dB,areverse,silenceremove=start_periods=1:start_threshold=-48dB,areverse,apad=pad_dur=0.05",
                    str(wav)], check=True)


def read_wav(p):
    with wave.open(str(p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def delivery(text, sentence):
    """ElevenLabs v4 director's note in square brackets before the sentence (not spoken)."""
    if ENGINE["name"] != "eleven": return text
    note = ", ".join(x for x in (PACE_NOTE, NOTES.get(sentence)) if x)
    return f"[{note}] {text}"


def make_clips(scene, sentences, spoken, voice, rate):
    clips = []
    for k, s in enumerate(sentences):
        (HERE / CLIPS["dir"]).mkdir(exist_ok=True)
        base = HERE / CLIPS["dir"] / f"s{scene:02d}_{k}_r{rate:+d}"
        asyncio.run(synth(delivery(spoken.get(s, s), s), voice, rate, base.with_suffix(".mp3")))
        to_wav(base.with_suffix(".mp3"), base.with_suffix(".wav"))
        clips.append(read_wav(base.with_suffix(".wav")))
    return clips


def fit_scene(sc, sentences, spoken, voice):
    window = sc["end"] - sc["start"] - LEAD - TAIL
    for rate in (range(0, MAX_RATE + 1, 2) if ENGINE["name"] == "edge" else [0]):   # v4 has no speed control
        clips = make_clips(sc["id"], sentences, spoken, voice, rate)
        total = sum(len(c) for c in clips) / SR + GAP * (len(clips) - 1)
        if total <= window:
            return clips, rate, total
    return clips, rate, total          # does not fit: reported by caller


def tempo_fit(sc, sents, clips, window):
    """v4 has no speed control: squeeze clips with ffmpeg atempo (pitch kept), at most MAX_TEMPO."""
    raw = sum(len(c) for c in clips) / SR
    need = raw / max(0.1, window - GAP * (len(clips) - 1))
    if need <= 1.0:
        return clips, 1.0
    f = round(min(MAX_TEMPO, need) + 0.005, 3)
    out = []
    for k, c in enumerate(clips):
        src = HERE / CLIPS["dir"] / f"s{sc['id']:02d}_{k}_r+0.wav"; dst = src.with_name(src.stem + f"_t{f}.wav")
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(src), "-af", f"atempo={f}", str(dst)], check=True)
        out.append(read_wav(dst))
    return out, f


def wrap(text, limit=LINE_CHARS):
    if len(text) <= limit:
        return text
    words, best = text.split(" "), None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, a + "\n" + b)
    return best[1]


def split_long(text):
    """Split sentences that would need >2 lines at a comma / colon."""
    if len(text) <= 2 * LINE_CHARS:
        return [text]
    for sep in (", ", ": "):
        if sep in text:
            a, b = text.split(sep, 1)
            return [a + sep.strip(), b]
    return [text]


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def pad_music(n):
    """Very quiet synthesized pad: slow A-minor / F chords, soft sine stack, long fades. About -34 dBFS."""
    t = np.arange(n) / SR
    chords = [(110.0, 164.81, 220.0, 261.63), (87.31, 130.81, 174.61, 220.0), (98.0, 146.83, 196.0, 246.94), (110.0, 164.81, 220.0, 277.18)]
    seg = 7.5
    out = np.zeros(n, dtype=np.float32)
    for i in range(int(math.ceil(n / SR / seg)) + 1):
        a, b = int(i * seg * SR), min(n, int((i + 1) * seg * SR + 2 * SR))
        if a >= n: break
        tt = t[a:b] - i * seg
        env = np.clip(tt / 2.5, 0, 1) * np.clip((seg + 2 - tt) / 2.5, 0, 1)
        voice = sum(np.sin(2 * np.pi * f * tt + 0.3 * np.sin(2 * np.pi * 0.2 * tt)) for f in chords[i % 4]) / 4
        out[a:b] += (voice * env).astype(np.float32)
    master = np.clip(t / 3, 0, 1) * np.clip((n / SR - t) / 4, 0, 1)
    out *= master.astype(np.float32)
    return out / (np.abs(out).max() + 1e-9) * 10 ** (-34 / 20)


def moving_avg(x, win):
    c = np.cumsum(np.concatenate([np.zeros(win // 2 + 1, np.float32), x, np.zeros(win, np.float32)]), dtype=np.float64)
    return ((c[win:win + len(x)] - c[:len(x)]) / win).astype(np.float32)


def file_music(path, n, voice):
    """Generated score (ElevenLabs Music): decode to 48 kHz mono, fit to n samples, duck under the voice, fade out."""
    tmp = HERE / "_music.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(HERE / path), "-ar", str(SR), "-ac", "1", str(tmp)], check=True)
    m = read_wav(tmp)[:n]; m = np.pad(m, (0, n - len(m)))
    m = m / (np.abs(m).max() + 1e-9) * 10 ** (MUSIC_DB / 20)
    env = moving_avg(np.abs(voice), SR // 10)                                     # voice activity
    env = moving_avg((env > 0.01).astype(np.float32), SR // 2)
    m *= (1 - (1 - 10 ** (DUCK_DB / 20)) * np.clip(env, 0, 1)).astype(np.float32)
    t = np.arange(n) / SR
    return m * np.clip((n / SR - t) / 2.5, 0, 1).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--voice", default="he-IL-HilaNeural"); ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--engine", choices=["edge", "eleven"], default="edge"); ap.add_argument("--clips-dir", default="clips"); ap.add_argument("--music-file", default=None)
    a = ap.parse_args()
    global GAP
    if a.engine == "eleven": GAP = 0.2        # v4 clips already breathe at their ends
    ENGINE["name"] = a.engine; CLIPS["dir"] = a.clips_dir
    tl = json.loads(TL_PATH.read_text(encoding="utf-8"))
    lines, spoken = load_lines()
    n = int(tl["duration"] * SR)
    voice_track = np.zeros(n, dtype=np.float32)
    cues, report = [], []
    for sc in tl["scenes"]:
        sents = lines[str(sc["id"])]
        clips, rate, total = fit_scene(sc, sents, spoken, a.voice)
        window = sc["end"] - sc["start"] - LEAD - TAIL
        if a.engine == "eleven":
            clips, rate = tempo_fit(sc, sents, clips, window)
            total = sum(len(c) for c in clips) / SR + GAP * (len(clips) - 1)
        # spread spare time: start at LEAD, add half the slack as extra gap capped at 0.5 s
        slack = max(0, window - total)
        gap = GAP + min(0.5, slack / max(1, len(clips) - 1) / 2) if len(clips) > 1 else GAP
        t = sc["start"] + LEAD + (min(slack, 0.6) / 2 if len(clips) == 1 else 0)
        for s, c in zip(sents, clips):
            i = int(t * SR); voice_track[i:i + len(c)] += c[:max(0, n - i)]
            parts = split_long(s)
            weights = [len(p) for p in parts]; d = len(c) / SR; tt = t
            for p, w in zip(parts, weights):
                dd = d * w / sum(weights)
                cue = {"start": round(tt - CUE_PAD, 3), "end": round(tt + dd + CUE_PAD + 0.1, 3), "text": wrap(p)}
                if sc["id"] in DARK_SCENES:       # dark panel on the left: plate + centred in the panel
                    cue.update(x=DARK_PANEL_CENTER_X, plate=True, text=wrap(p, 26))
                cues.append(cue)
                tt += dd
            t += len(c) / SR + gap
        end_used = t - gap
        report.append((sc["id"], rate, round(end_used - sc["start"], 2), sc["end"] - sc["start"]))
    for i in range(len(cues) - 1):          # no overlaps
        cues[i]["end"] = round(min(cues[i]["end"], cues[i + 1]["start"] - 0.02), 3)
    mix = voice_track * 0.9
    if not a.no_music:
        mix = mix + (file_music(a.music_file, n, voice_track) if a.music_file else pad_music(n))
    peak = np.abs(mix).max()
    if peak > 0.95: mix *= 0.95 / peak
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(str(HERE / "narration.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    (HERE / "subtitles.srt").write_text("\n".join(f"{i+1}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n" for i, c in enumerate(cues)), encoding="utf-8")
    tl["subtitles"] = cues
    tl["narration"] = "../final/narration.wav"
    TL_PATH.write_text(json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8")
    print("scene, rate%, speech ends at (s into scene), scene length")
    for r in report: print(r, "  <-- TOO LONG" if r[2] > r[3] - 0.2 else "")
    print("cues:", len(cues), "peak", round(float(peak), 2))


if __name__ == "__main__":
    main()
