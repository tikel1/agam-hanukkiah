"""Rhythmic score for v2 that follows the picture: one section per narration row (rows under 3 s are merged forward),
start times read from timings.json. Key via env ELEVEN_API_KEY."""
import json, os, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
BASE = {"1": "bright upbeat groove, claps and shaker, plucked marimba, friendly", "2": "playful rhythmic groove, bouncy marimba and pizzicato, light drums",
        "3": "flowing driving groove, harp arpeggios, steady beat", "4.1": "warm festive groove, glowing, hand claps, modal Jewish folk color",
        "4.2": "warm festive groove, glowing, hand claps, modal Jewish folk color", "4.3": "drums drop out, tender solo piano, quiet respect, gentle",
        "4.4": "groove returns bright and hopeful, sparkle, energy lift", "5": "steady curious groove, plucked strings, light percussion",
        "6": "modern energetic pulse, playful electronic plucks with drums", "7": "upbeat festive dance groove, strings and drums, joyful",
        "8": "mechanical rhythmic pulse, tight ticking percussion, marimba ostinato", "9": "fast fun groove, hand drums, happy crafting energy",
        "10": "warm emotional build, strings and piano with a steady soft beat", "10.4": "joyful triumphant celebration, full groove"}
ACCENT = {"1.2": "drum fill into a bright reveal", "2.3": "sparse, a single playful pluck", "2.5": "quick rising run", "3.3": "water-like flowing arpeggios",
          "3.4": "big swell then a hit", "4.1": "fire whoosh swell", "4.4": "spark and upward lift", "6.4": "playful wink pluck", "7.2": "sparse, curious, quiet percussion",
          "7.3": "reveal hit then bright", "7.4": "full and joyful", "9.2": "accelerating hand drums", "10.4": "triumphant final hit, ends on a sustained warm chord"}


def style(rid):
    base = BASE.get(rid) or BASE.get(rid.split(".")[0]) or BASE["1"]
    return base + (", " + ACCENT[rid] if rid in ACCENT else "")


def sections(rows, total):
    out, cur = [], None
    for r, nxt in zip(rows, [x["start"] for x in rows[1:]] + [total]):
        if cur is None: cur = {"id": r["id"], "a": r["start"] if out else 0.0}
        if nxt - cur["a"] >= 3 or nxt == total:
            out.append({"name": "Row " + cur["id"], "style": style(cur["id"]), "ms": int(round((nxt - cur["a"]) * 1000))}); cur = None
    return out


def main():
    t = json.loads((HERE / "timings.json").read_text(encoding="utf-8"))
    secs = sections(t["rows"], t["total"] + 6)
    plan = {"positive_global_styles": ["upbeat energetic rhythmic documentary underscore for kids", "consistent 116 BPM tempo throughout", "acoustic percussion", "hopeful", "instrumental"],
            "negative_global_styles": ["vocals", "singing", "lyrics", "aggressive", "slow ambient pad"],
            "sections": [{"section_name": s["name"], "positive_local_styles": [s["style"]], "negative_local_styles": ["vocals"], "duration_ms": s["ms"], "lines": []} for s in secs]}
    (HERE / "music_plan_v2.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", data=json.dumps({"composition_plan": plan, "model_id": "music_v1"}).encode(),
                                 headers={"xi-api-key": os.environ["ELEVEN_API_KEY"], "Content-Type": "application/json"})
    (HERE / "music_v2.mp3").write_bytes(urllib.request.urlopen(req, timeout=290).read())
    print("music ok,", len(secs), "sections")


if __name__ == "__main__":
    main()
