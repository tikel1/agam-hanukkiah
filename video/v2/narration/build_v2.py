r"""v2 narration: rows from ../script.md -> ElevenLabs v4 (Sarah) -> placed in sequence -> narration_v2.wav + timings.json + subtitles_v2.srt.
Key only via env ELEVEN_API_KEY. Music: music_v2.mp3 (ElevenLabs Music, plan in music_plan_v2.json, made by make_music_v2.py)."""
import json, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "final"))
import build_narration as b
SR, FF = b.SR, b.FF
VOICE = "EXAVITQu4vr4xnSDxMaL"
TEMPO, GAP = 1.08, 0.12
PACE = "talking fast, brisk and energetic, like an excited kid telling a story"
SLOW = "gentle, slower pace"
NOTES = {"1.1": "bright friendly cheerful greeting", "1.2": "excited, proud introduction, clear", "2.1": "enthusiastic", "2.2": "clear, light",
         "2.3": "playful, clear, one smooth take", "2.4": "curious, amazed", "2.5": "delighted", "3.1": "warm, proud", "3.2": "amazed, building",
         "3.3": "light, cheerful storytelling, same easy tone as the rest, not dramatic", "3.4": "dramatic, bold", "4.1": "excited, glowing", "4.2": "impressed, wide-eyed",
         "4.3": "calm, sincere, natural, a little softer", "4.4": "bright, inspired, energy returns", "5.1": "relaxed, focused", "5.2": "curious",
         "6.1": "excited, announcing", "6.2": "energetic", "6.3": "energetic, impressed", "6.4": "playful, a wink, a little giggle",
         "7.1": "proud, warm", "7.2": "natural, light, matter of fact", "7.3": "excited reveal, delighted", "7.4": "joyful, triumphant",
         "8.1": "upbeat", "9.1": "excited, fun", "9.2": "proud, rhythmic", "9.3": "satisfied, warm", "10.1": "warm, moved, emotional",
         "10.2": "warm, sincere, a soft smile, natural, not dramatic", "10.3": "warm, hopeful, smiling, light", "10.4": "warm, glad, big smile"}
REDO = {}
RETAKE = {"2.5": "_m", "3.3": "_m", "10.2": "_m", "10.3": "_m"}   # 2026-11-27: lighter ending, calmer fountain line
TONE_FIX = {"3.3", "4.3", "7.2"}
PRON_FIX = ("נעמי", "גדולה", "חנוכי", "AI", "צבענו ביד")      # words the narrator mispronounced


def ver(rid, text):
    """Only rows with a reported problem get a new take ("_c"); every other row keeps the take that already worked."""
    if rid in RETAKE:
        return RETAKE[rid]
    plain = NIQQUD.sub("", text)
    if "נעמי" in plain:
        return "_h"
    if "ביוני" in plain:
        return "_k"
    if re.search("חנוכי|חנכי", plain):
        return "_e"
    if any(w in plain for w in PRON_FIX):
        return "_d"
    if rid in TONE_FIX:
        return "_c"
    return {"1.2": "_b", "2.3": "_b"}.get(rid, "")
NIQQUD = re.compile("[֑-ׇ]")
ROW = re.compile(r"^\| (\d+\.\d+) \| ([\d.]+)–([\d.]+) \| (.*?) \|")


def rows():
    found = [ROW.match(ln) for ln in (HERE.parent / "script.md").read_text(encoding="utf-8").splitlines()]
    return [(m[1], float(m[2]), float(m[3]), m[4].strip()) for m in found if m]


def spoken(text):
    out = text.replace("ה־AI", "הָאֵי־אַי").replace("AI", "אֵי־אַי")
    out = re.sub("חֲנֻכִּיָּה|חנוכייה", "חנוכיאָה", out)
    out = out.replace("חֲנֻכִּיַּת", "חנוכיאַת").replace("ביוני השנה", "ב־יוּנִי השנה")
    for plain, fixed in (("נעמי", "נֶאוֹ־מִי"), ("גדולה", "גְּדוֹלָה"), ("צבענו ביד", "צבענו בַּיָּד")):
        out = out.replace(plain, fixed)
    return out


def clip(rid, text):
    raw = NOTES.get(rid, ""); slow = raw.startswith("!")
    note = ", ".join([SLOW if slow else PACE, raw.lstrip("!")])
    mp3 = HERE / "clips" / f"{rid}{ver(rid, text)}.mp3"; wav = mp3.with_suffix(".wav"); (HERE / "clips").mkdir(exist_ok=True)
    if not mp3.exists():
        b.synth_eleven(f"[{note}] {spoken(text)}", VOICE, 0, mp3)
    b.to_wav(mp3, wav)
    fast = HERE / "clips" / f"{rid}{ver(rid, text)}_t.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(wav), "-af", f"atempo={1.0 if slow else TEMPO}", str(fast)], check=True)
    c = b.read_wav(fast); k = int(0.015 * SR); c[:k] *= np.linspace(0, 1, k); c[-k:] *= np.linspace(1, 0, k)
    return c


def phrases(text):
    parts = [p for p in re.split(r"(?<=[,:.!?])\s+", NIQQUD.sub("", text)) if p]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > 40:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + [cur] if cur else out


def main():
    rs = rows(); clips = [clip(r[0], r[3]) for r in rs]
    t, placed, cues = 0.0, [], []
    for (rid, a, e, text), c in zip(rs, clips):
        t = max(a, t + (GAP if placed else 0)); d = len(c) / SR
        placed.append({"id": rid, "start": round(t, 2), "end": round(t + d, 2), "plan": [a, e], "text": NIQQUD.sub("", text)})
        ph = phrases(text); w = [len(p) for p in ph]; tt = t
        for p, wi in zip(ph, w):
            dd = d * wi / sum(w); cues.append((tt, tt + dd, b.wrap(p, 24))); tt += dd
        t += d
    n = int((t + 2.5) * SR); voice = np.zeros(n, np.float32)
    for p, c in zip(placed, clips):
        i = int(p["start"] * SR); voice[i:i + len(c)] += c
    has_music = (HERE / "music_v2.mp3").exists()
    music = b.file_music("../v2/narration/music_v2.mp3", n, voice) if has_music else np.zeros(n, np.float32)
    for name, mix in (("narration_v2", voice * 0.9 + music), ("voice_only_v2", voice * 0.9)):
        pk = np.abs(mix).max(); mix = mix * (0.95 / pk if pk > 0.95 else 1)
        with wave.open(str(HERE / f"{name}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    (HERE / "timings.json").write_text(json.dumps({"total": round(t, 2), "rows": placed}, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "subtitles_v2.srt").write_text("\n".join(f"{i+1}\n{b.srt_time(s)} --> {b.srt_time(e)}\n{x}\n" for i, (s, e, x) in enumerate(cues)), encoding="utf-8")
    print("speech ends", round(t, 1), "s;", len(cues), "cues; max drift", max(round(p["start"] - p["plan"][0], 1) for p in placed))


if __name__ == "__main__":
    main()
