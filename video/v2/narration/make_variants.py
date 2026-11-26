"""Pronunciation variants for the words the narrator stresses wrongly. Each output file holds the variants in order, 1 s apart.
Key via env ELEVEN_API_KEY."""
import subprocess, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "final"))
import build_narration as b
VOICE = "EXAVITQu4vr4xnSDxMaL"
NOTE = "[talking fast, brisk and energetic, like an excited kid telling a story] "
SETS = {
    "var_naomi5": "שלום! אנחנו ליבי ו{}, ואנחנו מאוד אוהבות אמנות.|נֶאוֹ־מִי|נֶעֱמִי|נֶאוֹמִי|נֶאוֹ מִי",
}


def main():
    (HERE / "variants").mkdir(exist_ok=True)
    for name, spec in SETS.items():
        frame, *words = spec.split("|"); parts = []
        for k, w in enumerate(words):
            mp3 = HERE / "variants" / f"{name}_{k}.mp3"; wav = mp3.with_suffix(".wav")
            b.synth_eleven(NOTE + frame.replace("{}", w), VOICE, 0, mp3)
            b.to_wav(mp3, wav); parts += [b.read_wav(wav), np.zeros(b.SR, np.float32)]
        pcm = (np.concatenate(parts) * 32767).astype(np.int16)
        out = HERE / f"{name}.wav"
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(b.SR); w.writeframes(pcm.tobytes())
        subprocess.run([b.FF, "-y", "-loglevel", "error", "-i", str(out), "-b:a", "128k", str(out.with_suffix(".mp3"))], check=True)
        print(name, "ok")


if __name__ == "__main__":
    main()
