"""Aligns film v2 to the recorded narration.

Reads ../narration/timings.json (the real start and end of every narration row, plus the time the script planned
for it) and writes films/v2/narration.js with:
  - anchors: [real time, planned time] per row. The film plays its picture at the planned time that belongs to the
    real time (a smooth time warp), so every beat stays under its own sentence without re-timing the animation;
  - subtitles: the cues in real time (a row with two cues is split by the length of its text);
  - duration: the real length of the film (the end card keeps its planned hold after the last word);
  - audio: the narration file, relative to the engine folder.

Run it again whenever the narration is re-recorded:   python sync_narration.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIMINGS = HERE.parent / "narration" / "timings.json"
AUDIO = "../narration/narration_v2.wav"
OUT = HERE / "films" / "v2" / "narration.js"
SRT = HERE / "films" / "v2" / "subtitles.srt"   # the same cues as a SubRip file, for players and uploads
PLANNED_DURATION = 129.5
FPS = 30
END_CARD_COMPLETE = 126.8   # planned time at which the end card has finished building (beats/b10.js)
END_CARD_HOLD = 1.6        # seconds the finished end card stays when the sound is shorter than the picture
MIN_END_HOLD = 1.0      # seconds the end card must stay after the last word
CUE_GAP = 0.04          # seconds between two cues of one row
CUE_TAIL = 0.1          # a cue stays this long after its last word
NIGHT_ROWS = {"6.1", "6.2", "6.3", "6.4", "10.1", "10.2", "10.3", "10.4"}   # light text on a dark slat

# The on-screen lines of every narration row: one or two cues, two lines each (max 820 px at 60 px Secular One).
CUES = {
    "1.1": [["שלום! אנחנו ליבי ונעמי,", "ואנחנו מאוד אוהבות אמנות."]],
    "1.2": [["תכירו את", "יעקב אגם!"]],
    "2.1": [["הוא היה אמן ישראלי,", "מפורסם בכל העולם,"], ["ואחד ממייסדי", "האמנות הקינטית."]],
    "2.2": [["זו אמנות שזזה,", "או שמשתנה כשזזים לידה."]],
    "2.3": [["הסוד שלו:", "קפלים, כמו במניפה."]],
    "2.4": [["על צד אחד", "תמונה אחת,"], ["ועל הצד השני,", "תמונה אחרת."]],
    "2.5": [["כל צעד,", "ציור חדש!"]],
    "3.1": [["ויש לו יצירה גדולה, בכיכר דיזנגוף", "בתל אביב: המזרקה ״אש ומים״."]],
    "3.2": [["היו בה חמש טבעות ענקיות,", "עם פאות משוננות."]],
    "3.3": [["פעם, הטבעות שבאמצע הסתובבו לאט,", "המים רקדו, ולמעלה בערה אש."]],
    "3.4": [["אש ומים,", "ביחד!"]],
    "4.1": [["והאש הזאת הזכירה לנו את חנוכה,", "חג האור!"]],
    "4.2": [["וגם אגם עצמו עיצב חנוכייה, בניו יורק.", "היא נחשבת לגדולה בעולם."]],
    "4.3": [["ביוני השנה, יעקב אגם הלך לעולמו,", "ורצינו לעשות לו מחווה."]],
    "4.4": [["ואז עלה לנו רעיון: להפוך", "את המזרקה שלו לחנוכייה!"]],
    "5.1": [["קודם כול,", "ישבנו ללמוד."]],
    "5.2": [["קראנו על אגם, ולמדנו על הסגנון", "המיוחד שלו, שאין עוד אחד כמוהו."]],
    "6.1": [["ואז הגיע", "תור ה־AI."]],
    "6.2": [["ביקשנו ממנו עזרה, והוא בנה לנו", "דגמים בתלת־ממד לכל החלקים."]],
    "6.3": [["הוא גם הראה לנו", "איך החנוכייה תיראה בסוף,"], ["וכתב הוראות צביעה", "לכל פס."]],
    "6.4": [["ואפילו הסרט הזה, שאתם רואים עכשיו,", "נעשה בעזרת AI!"]],
    "7.1": [["ומה יצא? חנוכייה שהיא", "מחווה למזרקה:"], ["חמש טבעות עם פאות משוננות,", "כמו שלה."]],
    "7.2": [["ובתוך הפאות, הסתרנו", "סמלים של חג החנוכה."]],
    "7.3": [["מצד אחד מתגלים", "מגן דוד וסביבון,"], ["ומהצד השני,", "המילה חנוכה וסופגנייה."]],
    "7.4": [["כל פעם שזזים, מגלים משהו אחר,", "בדיוק כמו באמנות הקינטית של אגם!"]],
    "8.1": [["ועכשיו,", "מהמחשב לעולם האמיתי:"], ["הדפסנו את כל החלקים במדפסת", "תלת־ממד, מפלסטיק ממוחזר."]],
    "9.1": [["והחלק הכי כיפי?", "לצבוע!"]],
    "9.2": [["צבענו ביד", "ארבע מאות ושמונה פסים."]],
    "9.3": [["ובסוף הרכבנו הכול, טבעת על טבעת,", "כמו במזרקה."]],
    "10.1": [["וכך נולדה", "חנוכיית ״אש ומים״."]],
    "10.2": [["החנוכייה שלנו היא מחווה,", "מתנה קטנה מאיתנו ליעקב אגם,"]],
    "10.3": [["כדי שהאש שלו תמשיך לבעור,", "נר אחרי נר."]],
    "10.4": [["חג חנוכה", "שמח!"]],
}


def load_rows() -> list[dict]:
    if not TIMINGS.exists():
        raise FileNotFoundError(f"narration timings not found: {TIMINGS}")
    rows = json.loads(TIMINGS.read_text(encoding="utf-8"))["rows"]
    missing = [row["id"] for row in rows if row["id"] not in CUES]
    if missing:
        raise ValueError(f"no on-screen lines for narration rows: {missing} (add them to CUES)")
    return rows


def row_cues(row: dict, next_start: float | None) -> list[dict]:
    """Cues of one row in real time: the row's span shared by the length of each cue's text."""
    cues = CUES[row["id"]]
    weights = [sum(len(line) for line in cue) for cue in cues]
    span = row["end"] - row["start"]
    out, passed = [], 0.0
    for index, (cue, weight) in enumerate(zip(cues, weights)):
        start = row["start"] + span * passed / sum(weights)
        passed += weight
        is_last = index == len(cues) - 1
        end = row["start"] + span * passed / sum(weights) - CUE_GAP
        if is_last:
            end = row["end"] + CUE_TAIL
            if next_start is not None:
                end = min(end, next_start - CUE_GAP)
        # user note: a line does not end with a full stop (commas, colons, ! and ? stay)
        item = {"start": round(start, 3), "end": round(end, 3), "lines": [line[:-1] if line.endswith(".") else line for line in cue]}
        if row["id"] in NIGHT_ROWS:
            item["dark"] = True
        out.append(item)
    return out


def to_srt(subtitles: list[dict]) -> str:
    def stamp(seconds: float) -> str:
        millis = round(seconds * 1000)
        return f"{millis // 3600000:02d}:{millis // 60000 % 60:02d}:{millis // 1000 % 60:02d},{millis % 1000:03d}"
    blocks = [f"{index}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n" + "\n".join(cue["lines"]) + "\n"
              for index, cue in enumerate(subtitles, 1)]
    return "\n".join(blocks)


def sound_seconds() -> float | None:
    """Length of the mixed narration (wav next to the timings), or None if it is not there."""
    import wave
    path = TIMINGS.parent / "narration_v2.wav"
    if not path.exists():
        return None
    with wave.open(str(path), "rb") as sound:
        return sound.getnframes() / sound.getframerate()


def main() -> int:
    rows = load_rows()
    anchors = [[0.0, 0.0]] + [[row["start"], row["plan"][0]] for row in rows if row["start"] > 0]
    for (real0, plan0), (real1, plan1) in zip(anchors, anchors[1:]):
        if real1 <= real0 or plan1 <= plan0:
            raise ValueError(f"narration rows out of order near {real1} s")
    shift = anchors[-1][0] - anchors[-1][1]
    duration = round(PLANNED_DURATION + shift, 3)
    # the film never runs longer than its sound: the end card is cut where the music ends (no silent tail)
    sound = sound_seconds()
    if sound is not None and sound < duration:
        duration = round(int(sound * FPS) / FPS, 3)
        # the end card then has less time: play its build-up faster, so it is complete END_CARD_HOLD before the end
        anchors.append([round(duration - END_CARD_HOLD, 3), END_CARD_COMPLETE])
    if duration < rows[-1]["end"] + MIN_END_HOLD:
        raise ValueError(f"the film would end {duration} s, less than {MIN_END_HOLD} s after the last word ({rows[-1]['end']} s)")
    subtitles = []
    for index, row in enumerate(rows):
        next_start = rows[index + 1]["start"] if index + 1 < len(rows) else None
        subtitles.extend(row_cues(row, next_start))
    body = (
        "/* GENERATED by sync_narration.py from ../narration/timings.json. Do not edit by hand: run the script again. */\n"
        "export default "
        + json.dumps({"duration": duration, "audio": AUDIO, "anchors": anchors, "subtitles": subtitles}, ensure_ascii=False, indent=1)
        + ";\n"
    )
    OUT.write_text(body, encoding="utf-8", newline="\n")
    SRT.write_text(to_srt(subtitles), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(rows)} rows, {len(subtitles)} cues, film length {duration} s (planned {PLANNED_DURATION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
