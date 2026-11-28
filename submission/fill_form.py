"""Fills the school's participation form (docx) for the Agam hanukkiah and appends a picture page.

Usage: python fill_form.py <unpacked form dir>
The blank lines of the form are replaced in document.xml; the logo, Agam's photo, a photo of
the hanukkiah and the site's QR code are added as inline pictures on a second page.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
EMU_PER_CM = 360000
FONT = '<w:rFonts w:ascii="David" w:hAnsi="David" w:cs="David"/>'

NAMES = ("נעמי וליבי", "קפלן")
CLASSES = "נעמי: ב'1, ליבי: ד'1"
TITLE = 'חנוכיית "אש ומים": מחווה לאמן יעקב אגם'
MATERIALS = [
    "פלסטיק ממוחזר, בהדפסה תלת־ממדית: בסיס, עמוד וחמש טבעות משוננות.",
    "צבעי אקריליק על בסיס מים.",
]
PROCESS = [
    ("הרעיון: ", "רצינו לעשות מחווה לאמן יעקב אגם, שהלך לעולמו השנה (יוני 2026), ובחרנו ביצירה המוכרת שלו: "
     "מזרקת \"אש ומים\" בכיכר דיזנגוף, עם הטבעות הצבעוניות המסתובבות והאש שפורצת מתוך המים."),
    ("העיצוב: ", "תהליך העיצוב נוצר באמצעות בינה מלאכותית. תיארנו את המזרקה, ויחד עם הבינה המלאכותית בנינו "
     "מודל תלת־ממדי של חמש טבעות משוננות, כמו במזרקה, ותוכנית צבעים לכל אחת מ־408 הפאות. כמו בציורים של "
     "אגם, החנוכייה משתנה כשהולכים סביבה, ובתוך הפסים מסתתרים סמלים של חג החנוכה: סביבון, סופגנייה, "
     "מגן דוד ועוד."),
    ("הייצור: ", "כל החלקים הודפסו בהדפסה תלת־ממדית מפלסטיק ממוחזר."),
    ("הצביעה: ", "נעמי וליבי צבעו ביד כל פאה, טבעת אחרי טבעת, לפי חוברת צביעה שהכנו."),
    ("הקשר לקיימות: ", "החנוכייה עשויה מפלסטיק ממוחזר. בהדפסה תלת־ממדית משתמשים רק בחומר שצריך, בלי פסולת "
     "של חיתוך, והחנוכייה עמידה ותשמש אותנו שנים רבות."),
    ("מצורף: ", "דף הסבר על יעקב אגם, על המזרקה ועל תהליך ההכנה."),
]


def run(text: str, size: int = 24, bold: bool = False) -> str:
    weight = "<w:b/><w:bCs/>" if bold else ""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (f'<w:r><w:rPr>{FONT}{weight}<w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:rtl/></w:rPr>'
            f'<w:t xml:space="preserve">{safe}</w:t></w:r>')


def paragraph(runs: str, after: int = 80, center: bool = False) -> str:
    justify = '<w:jc w:val="center"/>' if center else ""
    return (f'<w:p><w:pPr><w:bidi/><w:spacing w:after="{after}" w:line="300" w:lineRule="auto"/>{justify}'
            f'<w:rPr>{FONT}<w:rtl/></w:rPr></w:pPr>{runs}</w:p>')


def field(label: str, value: str) -> str:
    return paragraph(run(label, 28, bold=True) + run(value, 28), after=200)


def picture(rel_id: str, pic_id: int, path: Path, width_cm: float) -> str:
    with Image.open(path) as image:
        ratio = image.height / image.width
    cx, cy = int(width_cm * EMU_PER_CM), int(width_cm * ratio * EMU_PER_CM)
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{pic_id}" name="pic{pic_id}"/>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{pic_id}" name="{path.name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
            f'</wp:inline></w:drawing></w:r>')


PICTURES = [  # (file, media name, width cm)
    (HERE / "logo.png", "logo.png", 10.5),
    (HERE / "agam_fountain.jpg", "agam.jpg", 7.2),
    (HERE / "photos" / "hanukkiah.jpg", "hanukkiah.jpg", 5.3),
    (HERE.parent / "site" / "qr.png", "qr.png", 4.2),
]
SITE_URL = "https://tikel1.github.io/agam-hanukkiah/"
LINK_ID = "rIdSiteLink"


def add_media(unpacked: Path) -> list[str]:
    rels_path = unpacked / "word" / "_rels" / "document.xml.rels"
    rels = rels_path.read_text(encoding="utf-8")
    ids = []
    for index, (source, name, _) in enumerate(PICTURES):
        rel_id = f"rIdPic{index}"
        (unpacked / "word" / "media" / name).write_bytes(source.read_bytes())
        if rel_id not in rels:
            rels = rels.replace("</Relationships>", f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/'
                                f'officeDocument/2006/relationships/image" Target="media/{name}"/></Relationships>')
        ids.append(rel_id)
    if LINK_ID not in rels:
        rels = rels.replace("</Relationships>", f'<Relationship Id="{LINK_ID}" Type="http://schemas.openxmlformats.org/'
                            f'officeDocument/2006/relationships/hyperlink" Target="{SITE_URL}" TargetMode="External"/></Relationships>')
    rels_path.write_text(rels, encoding="utf-8")
    types_path = unpacked / "[Content_Types].xml"
    types = types_path.read_text(encoding="utf-8")
    for ext, mime in (("png", "image/png"), ("jpg", "image/jpeg")):
        if f'Extension="{ext}"' not in types:
            types = types.replace("<Types ", "<Types ", 1).replace(
                "<Default ", f'<Default Extension="{ext}" ContentType="{mime}"/><Default ', 1)
    types_path.write_text(types, encoding="utf-8")
    return ids


def picture_page(ids: list[str]) -> str:
    (logo, agam, hanukkiah, qr) = [(rel, 100 + i, PICTURES[i][0], PICTURES[i][2]) for i, rel in enumerate(ids)]
    page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    caption = lambda text: paragraph(run(text, 22), after=240, center=True)  # noqa: E731
    linked_qr = f'<w:hyperlink r:id="{LINK_ID}">{picture(*qr)}</w:hyperlink>'  # click the code in the PDF too
    return (page_break
            + paragraph(picture(*logo) + run("      ") + linked_qr, after=40, center=True)
            + paragraph(run("מומלץ! סרטון הסבר: ", 26, bold=True) + f'<w:hyperlink r:id="{LINK_ID}">{run("סרקו את הברקוד", 26)}</w:hyperlink>', after=280, center=True)
            + paragraph(picture(*hanukkiah), after=60, center=True)
            + caption("החנוכייה שלנו, עם דפי הצביעה")
            + paragraph(picture(*agam), after=60, center=True)
            + caption("יעקב אגם (1928 עד 2026) מול מזרקת \"אש ומים\" בכיכר דיזנגוף"))


def fill(document: str, ids: list[str]) -> str:
    body_start = document.index("<w:body>") + len("<w:body>")
    paragraphs = re.findall(r"<w:p [^>]*>.*?</w:p>", document, re.S)
    header = "".join(paragraphs[:3])  # school logo, spacer, title
    sect = document[document.index("<w:sectPr"):document.index("</w:body>")]
    watch_first = (paragraph(run("מומלץ לצפות קודם בסרטון ההסבר שלנו (שתי דקות)", 26, bold=True), after=20, center=True)
                   + paragraph(f'<w:hyperlink r:id="{LINK_ID}">{run("סרקו את הברקוד בעמוד הבא", 26)}</w:hyperlink>', after=120, center=True))
    answers = (paragraph("", after=60) + watch_first
               + field("שם: ", NAMES[0]) + field("משפחה: ", NAMES[1]) + field("כיתה: ", CLASSES)
               + field("שם החנוכייה: ", TITLE)
               + paragraph(run("החומרים ממנה עשויה:", 28, bold=True), after=60)
               + "".join(paragraph(run(line)) for line in MATERIALS)
               + paragraph("", after=60)
               + paragraph(run("תיאור קצר של מהלך העבודה:", 28, bold=True), after=60)
               + "".join(paragraph(run(label, bold=True) + run(text)) for label, text in PROCESS))
    return document[:body_start] + header + answers + picture_page(ids) + sect + "</w:body></w:document>"


def main() -> None:
    unpacked = Path(sys.argv[1])
    ids = add_media(unpacked)
    doc_path = unpacked / "word" / "document.xml"
    doc_path.write_text(fill(doc_path.read_text(encoding="utf-8"), ids), encoding="utf-8")
    print("filled", doc_path)


if __name__ == "__main__":
    main()
