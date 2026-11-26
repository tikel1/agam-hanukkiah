"""Contact sheet of stills: python contact.py <stills folder> <out.png> [columns]. Needs Pillow or imageio's ffmpeg."""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

TILE_WIDTH = 960


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    folder, out = Path(sys.argv[1]), Path(sys.argv[2])
    columns = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    files = sorted(folder.glob("*.png"))
    if not files:
        sys.exit(f"no png files in {folder}")
    rows = -(-len(files) // columns)
    listing = folder / "_list.txt"
    listing.write_text("".join(f"file '{f.resolve().as_posix()}'\nduration 1\n" for f in files), encoding="utf-8")
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
               "-vf", f"scale={TILE_WIDTH}:-1,tile={columns}x{rows}:padding=8:color=0x888888", "-frames:v", "1", str(out)]
    result = subprocess.run(command, capture_output=True, text=True)
    listing.unlink()
    if result.returncode:
        sys.exit(result.stderr[-800:])
    print("wrote", out)


if __name__ == "__main__":
    main()
