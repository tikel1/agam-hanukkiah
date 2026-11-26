"""Preview renders of the name plaque on the foot (painted look).

Usage: python plaque_render.py   (after plaque.py; writes previews/plaque_*.png)
"""

from __future__ import annotations

from pathlib import Path

import pyvista as pv

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PARTS = OUT / "_plaque_preview"
PREVIEWS = HERE / "previews"
WHITE = "#f4f1ea"
NAVY = "#232c5e"
FOOT = "#e9e4da"
BACKGROUND = ("#cfd8e3", "#f7f9fb")
WINDOW = (1400, 900)

# (file, camera position, focal point, view up)
SHOTS = {
    "plaque_front": ((0, -200, 45), (0, -40, 8), (0, 0, 1)),
    "plaque_three_quarter": ((150, -190, 110), (0, -20, 14), (0, 0, 1)),
    "plaque_base_guides": ((0, -150, 20), (0, -56, 9), (0, 0, 1)),
    "plaque_one_piece": ((35, -150, 35), (0, -50, 9), (0, 0, 1)),
}


def painted_meshes() -> list[tuple[pv.PolyData, str]]:
    meshes = [(pv.read(PARTS / "band.stl"), WHITE), (pv.read(PARTS / "navy.stl"), NAVY)]
    for path in sorted(PARTS.glob("dot_*.stl")):
        meshes.append((pv.read(path), "#" + path.stem.split("_")[-1]))
    return meshes


def shoot(name: str, meshes: list[tuple[pv.PolyData, str]]) -> Path:
    position, focal, up = SHOTS[name]
    plotter = pv.Plotter(off_screen=True, window_size=WINDOW)
    plotter.set_background(BACKGROUND[0], top=BACKGROUND[1])
    for mesh, colour in meshes:
        plotter.add_mesh(mesh, color=colour, smooth_shading=False, specular=0.15)
    plotter.camera_position = [position, focal, up]
    plotter.enable_anti_aliasing("ssaa")
    out = PREVIEWS / f"{name}.png"
    plotter.screenshot(str(out))
    plotter.close()
    return out


def main() -> None:
    PREVIEWS.mkdir(exist_ok=True)
    on_foot = [(pv.read(OUT / "plinth_stem.stl"), FOOT), *painted_meshes()]
    print(shoot("plaque_front", on_foot))
    print(shoot("plaque_three_quarter", on_foot))
    print(shoot("plaque_base_guides", [(pv.read(PARTS / "band.stl"), WHITE)]))
    print(shoot("plaque_one_piece", [(pv.read(OUT / "plinth_stem.stl"), FOOT), (pv.read(PARTS / "one_piece.stl"), WHITE)]))


if __name__ == "__main__":
    main()
