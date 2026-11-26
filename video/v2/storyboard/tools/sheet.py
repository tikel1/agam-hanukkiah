"""Quick review sheet: python sheet.py out.png name1 name2 ..."""
import sys
from pathlib import Path
from PIL import Image
FR = Path(__file__).resolve().parent.parent / "frames"
out, names = sys.argv[1], sys.argv[2:]
tw, th = 360, 640
cols = min(len(names), 6)
rows = (len(names) + cols - 1) // cols
s = Image.new("RGB", (cols * (tw + 8), rows * (th + 8)), "#777")
for i, n in enumerate(names):
    im = Image.open(FR / f"{n}.png").convert("RGB").resize((tw, th), Image.LANCZOS)
    s.paste(im, ((i % cols) * (tw + 8), (i // cols) * (th + 8)))
s.save(out)
