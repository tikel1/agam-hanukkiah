"""Scaled full-ring test prints of R3 (out/test_ring_R3_<pct>.stl + 3MF + A/B maps + renders).

R3 is REBUILT at each scale, not scaled as a mesh. The sizes that should shrink are scaled:
diameter, height, tooth pitch, cup circle and washer marks. The features that must still print
and paint at a 0.4 nozzle keep their real size: paint ridges 0.8 x 0.6 mm, guide relief 0.3 x
0.6 mm. The pitch never drops below the pitch that keeps the narrowest paint zone (a pleat face
between its ridges) at TEST_RING_MIN_ZONE. The test ring has a flat closed bottom (no spine hole)
and seat marks only (no stud holes), and carries all three motifs, so both pictures can be judged
from 40 deg left and right.

Usage:  .venv/Scripts/python test_ring.py   (after build.py, or on its own)
"""

from __future__ import annotations

import math
from contextlib import contextmanager
from pathlib import Path

import config as cfg
import fountain
import paint_program as program
import profiles

OUT_DIR = cfg.MODEL_DIR / "out"
PREVIEW_DIR = cfg.MODEL_DIR / "previews"
SCALED = ("MAIN_DIAMETER", "CANDLE_RING_RADIUS", "WASHER_D")


def scaled_pitch(scale: float) -> float:
    """Tooth pitch at a scale, clamped so a pleat face keeps TEST_RING_MIN_ZONE between ridges."""
    half_apex = math.radians(cfg.TOOTH_INCLUDED_ANGLE / 2)
    minimum = 2 * (cfg.TEST_RING_MIN_ZONE + cfg.RIDGE_WIDTH) * math.sin(half_apex)
    return max(cfg.TOOTH_PITCH * scale, minimum)


def face_zone(pitch: float) -> float:
    """Paintable width (mm) of one pleat face between its crest and valley ridges."""
    return (pitch * cfg.TOOTH_LEAN) / math.sin(math.radians(cfg.TOOTH_INCLUDED_ANGLE / 2)) - cfg.RIDGE_WIDTH


def clear_caches() -> None:
    import paint_mesh

    for function in (program.motif_shapes, program.face_regions, program.face_table, program.motif_outlines):
        function.cache_clear()
    paint_mesh._SLICED.clear()


@contextmanager
def scaled(scale: float):
    """Temporarily rebuild-size the model: scaled sizes, real-size minimum features."""
    saved = {name: getattr(cfg, name) for name in SCALED + ("TOOTH_PITCH",)}
    saved_defaults = profiles.tooth_count.__defaults__
    try:
        for name in SCALED:
            setattr(cfg, name, saved[name] * scale)
        cfg.TOOTH_PITCH = scaled_pitch(scale)
        profiles.tooth_count.__defaults__ = (cfg.TOOTH_PITCH,)
        clear_caches()
        yield
    finally:
        for name, value in saved.items():
            setattr(cfg, name, value)
        profiles.tooth_count.__defaults__ = saved_defaults
        clear_caches()


def label(scale: float) -> str:
    return f"{round(scale * 100):d}"


def summary(scale: float) -> str:
    drum = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    with scaled(scale):
        teeth = profiles.tooth_count(fountain.drum_diameter(drum))
        line = (f"  test ring {label(scale)}%: Ø {fountain.drum_diameter(drum):.0f} x {fountain.drum_height(drum):.1f} mm, "
                f"{teeth} teeth (full size {80}), pitch {cfg.TOOTH_PITCH:.2f} mm, narrowest paint zone {face_zone(cfg.TOOTH_PITCH):.2f} mm")
    return line


def build(scale: float) -> Path:
    """Build, export (STL + 3MF) and return the assembled-position mesh path of one test ring."""
    import build as builder
    import hanukkiah
    from build123d import Location

    with scaled(scale):
        part = hanukkiah.r3_part(with_holes=False)
        name = f"test_ring_R3_{label(scale)}"
        builder.report_part(name, part)
        builder.export_mesh(part, OUT_DIR / f"{name}.stl")
        builder.export_3mf(part, OUT_DIR / f"{name}.3mf")
        placed = builder.ASSEMBLY_DIR / f"{name}.stl"
        drum = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
        builder.export_mesh(Location((0, 0, fountain.stack_heights()[drum.name])) * part, placed)
    return placed


def maps_and_renders(scale: float, placed: Path) -> list[Path]:
    import maps
    import paint_mesh
    import pyvista as pv
    import render

    written = []
    with scaled(scale):
        for side in program.SIDES:
            written += maps.ring_map(cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name, side, stem=f"map_test_ring_R3_{label(scale)}_{'A_left' if side == 'left' else 'B_right'}", title_note=f"test ring {label(scale)}%")
        name = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name
        mesh = paint_mesh.paintable_mesh(name, pv.read(str(placed)))
        colours = render.paint(name, mesh)
        drum = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
        tip = fountain.drum_diameter(drum) / 2
        target = (0.0, -0.45 * tip, fountain.stack_heights()[name] + fountain.drum_height(drum) / 2)  # keeps the whole ring in frame
        for view, delta in (("left", -40.0), ("front", 0.0), ("right", 40.0)):
            path = PREVIEW_DIR / f"test_ring_R3_{label(scale)}_from_{view}.png"
            written.append(render.render_closeup(mesh, path, target, -90.0 + delta, 8.0, 520.0 * scale, colours))
    return written


def main() -> None:
    for scale in cfg.TEST_RING_SCALES:
        print(summary(scale))
        placed = build(scale)
        if scale == cfg.TEST_RING_RENDER_SCALE:
            for path in maps_and_renders(scale, placed):
                print(f"  wrote {path.relative_to(cfg.MODEL_DIR)}")


if __name__ == "__main__":
    main()
