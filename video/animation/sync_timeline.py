"""Writes timeline.js (a script-tag copy of timeline.json) so index.html also works from file://.
Run after every edit of timeline.json:  python sync_timeline.py"""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
data = json.loads((here / "timeline.json").read_text(encoding="utf-8"))
(here / "timeline.js").write_text("window.TIMELINE = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
print("wrote timeline.js,", len(data["scenes"]), "scenes,", data["duration"], "s")
