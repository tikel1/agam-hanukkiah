"""Contact sheet from rendered stills: python contact.py out.png stills_dir [cols] [tile_width] [from_s] [to_s]
Each tile is labelled with its time in seconds and the scene number."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

here = Path(__file__).resolve().parent
out, folder = Path(sys.argv[1]), Path(sys.argv[2])
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 640
lo = float(sys.argv[5]) if len(sys.argv) > 5 else 0
hi = float(sys.argv[6]) if len(sys.argv) > 6 else 1e9
th = tw * 9 // 16
scenes = json.loads((here / "timeline.json").read_text(encoding="utf-8"))["scenes"]
files = sorted(f for f in folder.glob("t*.png") if lo <= float(f.stem[1:]) <= hi)
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 8) + 8), "#c9c6bb")
font = ImageFont.truetype("arial.ttf", 22)
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    t = float(f.stem[1:])
    sc = next(s["id"] for s in reversed(scenes) if t >= s["start"])
    x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 8)
    sheet.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
    d.rectangle([x, y, x + 150, y + 30], fill="#232C5E")
    d.text((x + 6, y + 3), f"s{sc}  {t:.1f}s", fill="white", font=font)
sheet.save(out)
print("wrote", out, sheet.size)
