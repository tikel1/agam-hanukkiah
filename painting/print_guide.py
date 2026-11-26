"""Printable painting booklet: one landscape page per ring, Hebrew instructions above both pictures.

Paint counts come from the model (paint_program.face_table) and the bands are drawn with the
maps' own code (bands.py), so the booklet always matches the 1:1 maps in model/out/maps/.
Writes painting/out/painting-booklet.html and, with Microsoft Edge, painting/out/painting-booklet.pdf.

Usage (from agam-hanukkiah/model):  .venv/Scripts/python ../painting/print_guide.py
"""

from __future__ import annotations

import html
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent / "model"
sys.path.insert(0, str(MODEL_DIR))

import bands  # noqa: E402
import paint_program as program  # noqa: E402

OUT_DIR = HERE / "out"
BAND_DIR = OUT_DIR / "bands"
PAGE_W, PAGE_H, PAGE_PAD = 297.0, 210.0, 10.0  # landscape A4, mm
BAND_WIDTH = PAGE_W - 2 * PAGE_PAD
HTML_PATH = OUT_DIR / "painting-booklet.html"
PDF_PATH = OUT_DIR / "painting-booklet.pdf"
EDGE_PATHS = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)
PRINT_TIMEOUT_S = 120

HEBREW = {  # paint name -> (Hebrew name, nearest Posca or "acrylic")
    "white": ("לבן", "White"),
    "yellow": ("צהוב", "Sunshine Yellow"),
    "orange": ("כתום", "Light Orange"),
    "coral": ("אלמוג", "Coral Pink"),
    "brick": ("לבנה", "acrylic: Naphthol Red Deep 399"),
    "rose": ("ורוד סלמון", "Salmon Pink"),
    "lilac": ("לילך", "Lavender"),
    "periwinkle": ("פריווינקל", "acrylic: Ultramarine + Blue Violet + white"),
    "light_blue": ("תכלת", "Light Blue"),
    "blue": ("כחול", "Blue"),
    "navy": ("נייבי", "Navy Blue"),
    "mint": ("מנטה", "Mint"),
    "teal": ("טורקיז", "Emerald Green"),
    "green": ("ירוק", "Green"),
}
# Light first, then mid, then dark (guide §6.4): a slip of a dark paint lands on paint already there.
PAINT_ORDER = (
    "yellow", "mint", "light_blue", "rose", "orange", "coral", "lilac",
    "green", "periwinkle", "teal", "blue", "brick", "navy",
)

RINGS = (
    {
        "name": "drum1_R1", "title": "R1, הטבעת התחתונה",
        "notes": [
            "מעבר צבעים בלי לבן, שחוזר פעמיים מסביב. רצפים של 2 עד 3 שיניים באותו צבע",
            "תמונה B היא אותו מעבר בדיוק, צעד אחד לפני A. לכן אותם טושים לשני הצדדים",
            "פאה נמוכה (18 מ\"מ) וצרה: עדיף טוש דק, <bdi>PC-3M</bdi>",
        ],
    },
    {
        "name": "drum2_R2", "title": "R2",
        "notes": [
            "מעבר צבעים בלי לבן, פעמיים מסביב, כמו R1 אבל בגוונים הקרים",
            "תמונה B היא אותו מעבר, צעד אחד לפני A",
            "נייבי, כחול ולבנה אחרונים בכל צד: הם הכי קשים לתיקון",
            "המדרגה העליונה (שעליה יושבת R3) נשארת לבנה",
        ],
    },
    {
        "name": "drum3_R3", "title": "R3, הטבעת הרחבה עם הנרות",
        "notes": [
            "המדרגה העליונה עם 8 מושבי הנרות לא נצבעת. המושבים ממוסכים",
        ],
        "side_steps": {
            "left": [
                "צהוב על כל הפאות הצהובות, כולל השטח של מגן הדוד והסביבון",
                "שאר הרצפים לפי הטבלה: ורוד, כתום, אלמוג, לילך",
                "ייבוש חצי שעה",
                "מגן דוד בירוק (14) בחזית, פרוסה אחרי פרוסה עד הקו הדק. 2 שכבות",
                "סביבון בכתום (3) מאחור, ב-173°. 2 עד 3 שכבות",
            ],
            "right": [
                "רצפי הצבע לפי הטבלה: לילך, ואחריו פריווינקל. כל השאר לבן, כולל הרצועה הרחבה סביב החזית",
                "ייבוש",
                "האותיות בכחול (10), אות אחרי אות משמאל לימין. כל פאה כחולה לכל הגובה או בפסים אופקיים. 2 שכבות",
                "סופגנייה בכתום (3) מאחור, 194° עד 230°. משאירים לבן את נקודת הריבה",
                "אחרי ייבוש: הריבה בלבנה (5). 2 שכבות",
            ],
        },
    },
    {
        "name": "drum4_R4", "title": "R4",
        "notes": [
            "יש פאות לבנות בשני הצדדים: לא צובעים אותן, הן נשארות מהפריימר",
            "פאה נמוכה: PC-3M",
        ],
    },
    {
        "name": "drum5_R5_dome", "title": "R5, התוף העליון עם השמש",
        "notes": [
            "16 שיניים בלבד: טבעת טובה להתחלה",
            "הכיפה והמדרגה העליונה עם מושב השמש לבנות. לא צובעים",
        ],
    },
)

GENERAL_RULES = [
    "<b>הסדר:</b> קודם טבעת הניסיון (היא כמו R3, בקטן), ואחר כך R5, R4, R1, R2, ובסוף R3. מהקלה אל הקשה",
    "<b>צד אחד בכל מפגש.</b> קודם תמונה A (הפאות השמאליות), ייבוש, ורק אחר כך תמונה B (הימניות). מטים את הטבעת כך שרואים רק את הצד שצובעים",
    "<b>בכל צד: לפי הטבלה, מלמעלה למטה.</b> היא מסודרת מבהיר לכהה, כך שצבע כהה שגולש נוחת על צבע שכבר יבש",
    "<b>צבע אחד בכל פעם:</b> מוצאים בפס את כל הפאות במספר הזה וצובעים אותן מסביב לטבעת. מסמנים ✓ בעיפרון",
    "בפס, כל מלבן בין שני קווים אפורים הוא <b>פאה אחת</b>, והמספר בו הוא מספר הצבע. <b>1 או בלי מספר: לבן, לא צובעים.</b> סמל (מגן דוד, סביבון, אותיות, סופגנייה) מצויר בצבע שלו",
    "הפס מתחיל ב<b>חץ השקוע</b> שעל הטבעת (מאחור) ורץ משמאל לימין. סופרים שיניים מהחץ לפי <bdi>t0, t5, t10</bdi>. ▼ FRONT הוא החזית",
    "הטוש מלמטה למעלה לאורך הפאה, מהעמק עד הקודקוד. <b>הקודקוד הוא קו העצירה</b>",
    "שכבות דקות. 10 עד 15 דקות בין שכבות Posca, 20 עד 30 דקות באקריליק",
    "<b>כל המשטחים העליונים והרגל נשארים לבנים.</b> מושבי הנרות והשמש ממוסכים, בלי צבע ובלי לכה",
]
# Easiest first (guide §6.8): the small rings build confidence before R3 and its emblems.
PAINTING_ORDER = ("drum5_R5_dome", "drum4_R4", "drum1_R1", "drum2_R2", "drum3_R3")


def paint_label(name: str) -> str:
    paint = program.paint(name)
    hebrew, _ = HEBREW[name]
    return f'<span class="chip" style="background:{paint.hex}"></span><b>{paint.number}</b> {hebrew}'


FULL_COVER = 0.95  # a motif piece covering this share of a face replaces its ground (R3's white word band)


def visible_ground(ring_name: str, side: str, k: int) -> str:
    """The paint a face carries before its emblems: the ground, unless a motif covers the whole face."""
    height = bands.ring_geometry(ring_name)[1]
    ground = program.face_table(ring_name)[side][k]
    for region, ink in program.face_regions(ring_name, side, k):
        if region.area >= FULL_COVER * height:
            ground = ink
    return ground


def side_table(ring_name: str, side: str) -> str:
    teeth = program.teeth_of(ring_name)
    counts = Counter(visible_ground(ring_name, side, k) for k in range(teeth))
    painted = [name for name in PAINT_ORDER if counts.get(name)]
    rows = "".join(
        f"<tr><td>{index}</td><td>{paint_label(name)}</td><td>{counts[name]}</td>"
        f"<td class='posca'><bdi dir='ltr'>{html.escape(HEBREW[name][1])}</bdi></td></tr>"
        for index, name in enumerate(painted, start=1)
    )
    white = counts.get("white", 0)
    white_row = f"<tr class='white'><td></td><td>{paint_label('white')}</td><td>{white}</td><td>לא צובעים</td></tr>" if white else ""
    return f"<table><tr><th></th><th>צבע</th><th>פאות</th><th>טוש</th></tr>{rows}{white_row}</table>"


SIDE_TITLES = {"left": "תמונה A: פאות שמאליות (קודם)", "right": "תמונה B: פאות ימניות (אחרי ייבוש)"}


def side_block(ring: dict, side: str) -> str:
    steps = ring.get("side_steps", {}).get(side)
    steps_html = "<ol class='steps'>" + "".join(f"<li>{step}</li>" for step in steps) + "</ol>" if steps else ""
    return f"<div class='side'><h3>{SIDE_TITLES[side]}</h3>{side_table(ring['name'], side)}{steps_html}</div>"


def band_figure(ring_name: str, side: str, scale: float) -> str:
    path = BAND_DIR / f"{ring_name}_{side}.svg"
    width, height = bands.draw_band(ring_name, side, scale, path)
    label = "A" if side == "left" else "B"
    return (f"<div class='band'><span class='band-label'>{label}</span>"
            f"<img src='{path.as_uri()}' style='width:{width:.1f}mm;height:{height:.1f}mm' alt='{ring_name} {label}'></div>")


def ring_page(ring: dict, step: int) -> str:
    teeth = program.teeth_of(ring["name"])
    notes = "".join(f"<li>{note}</li>" for note in ring["notes"])
    scale = bands.band_scale(ring["name"], BAND_WIDTH)
    return f"""
<section class="page text">
  <h2><span class="step">{step}</span> {ring['title']}</h2>
  <p class="meta">{teeth} שיניים, {teeth} פאות בכל צד. הפסים למטה מוקטנים: סופרים שיניים, לא מודדים</p>
  <ul class="notes">{notes}</ul>
  <div class="sides">{side_block(ring, 'left')}{side_block(ring, 'right')}</div>
  {band_figure(ring['name'], 'left', scale)}
  {band_figure(ring['name'], 'right', scale)}
  <p class="check">סיימנו A ☐ &nbsp;&nbsp; סיימנו B ☐ &nbsp;&nbsp; לכה ☐</p>
</section>
"""


def palette_table() -> str:
    rows = "".join(
        f"<tr><td>{paint_label(name)}</td><td class='posca'><bdi dir='ltr'>{html.escape(HEBREW[name][1])}</bdi></td></tr>"
        for name in sorted(HEBREW, key=lambda n: program.paint(n).number)
    )
    return f"<table class='palette'><tr><th>צבע</th><th>טוש / אקריליק</th></tr>{rows}</table>"


def cover_page() -> str:
    rules = "".join(f"<li>{rule}</li>" for rule in GENERAL_RULES)
    return f"""
<section class="page text">
  <h1>חוברת צביעה: חנוכיית "אש ומים"</h1>
  <p class="meta">דף אחד לכל טבעת, לפי סדר הצביעה</p>
  <div class="sides">
    <div class="side"><h3>כללים</h3><ol class="rules">{rules}</ol></div>
    <div class="side"><h3>הצבעים</h3>{palette_table()}</div>
  </div>
</section>
"""


STYLE = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif; color: #222; }
.page { width: 297mm; height: 209mm; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.text { direction: rtl; padding: 9mm 10mm; font-size: 9.5pt; line-height: 1.35; }
h1 { font-size: 18pt; margin: 0 0 1mm; }
h2 { font-size: 16pt; margin: 0 0 0.5mm; }
h3 { font-size: 11pt; margin: 2mm 0 1.5mm; }
.step { display: inline-block; background: #222; color: #fff; border-radius: 50%; width: 8mm; height: 8mm;
        text-align: center; line-height: 8mm; font-size: 12pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.meta { color: #555; margin: 0 0 1.5mm; }
.notes { margin: 0 0 1mm; padding-right: 5mm; }
.rules li, .notes li { margin-bottom: 0.8mm; }
.sides { display: flex; gap: 8mm; }
.side { flex: 1; }
table { border-collapse: collapse; width: 100%; margin-bottom: 1mm; }
th, td { border: 0.3mm solid #bbb; padding: 0.6mm 2mm; text-align: right; }
th { background: #f0eee6; }
td:first-child { width: 6mm; text-align: center; font-weight: bold; }
td:nth-child(3) { width: 13mm; text-align: center; }
.palette td:first-child { width: auto; text-align: right; font-weight: normal; }
.palette td:nth-child(2) { width: auto; text-align: right; }
.posca { color: #444; font-size: 8.5pt; text-align: right; }
.white td { color: #777; }
.chip { display: inline-block; width: 6mm; height: 3.8mm; border: 0.3mm solid #555;
        vertical-align: middle; margin-left: 1.5mm; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.steps { margin: 0; padding-right: 5mm; }
.steps li { margin-bottom: 0.4mm; }
.band { direction: ltr; display: flex; align-items: center; gap: 2mm; margin-top: 1.5mm; }
.band-label { font-weight: bold; font-size: 14pt; width: 6mm; }
.band img { display: block; }
.check { margin: 1mm 0 0; font-size: 10pt; }
"""


def booklet_html() -> str:
    by_name = {ring["name"]: ring for ring in RINGS}
    body = cover_page() + "".join(ring_page(by_name[name], step) for step, name in enumerate(PAINTING_ORDER, start=1))
    return f'<!doctype html><html lang="he"><head><meta charset="utf-8"><title>חוברת צביעה</title><style>{STYLE}</style></head><body>{body}</body></html>'


def find_edge() -> Path:
    for path in EDGE_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("Microsoft Edge not found: open the HTML and print it to PDF by hand")


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    command = [
        str(find_edge()), "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}", html_path.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=PRINT_TIMEOUT_S, check=False)
    if not pdf_path.exists():
        raise RuntimeError(f"Edge did not write the PDF (exit {result.returncode}): {result.stderr[-500:]}")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    HTML_PATH.write_text(booklet_html(), encoding="utf-8")
    print(f"wrote {HTML_PATH}")
    PDF_PATH.unlink(missing_ok=True)
    print_pdf(HTML_PATH, PDF_PATH)
    print(f"wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
