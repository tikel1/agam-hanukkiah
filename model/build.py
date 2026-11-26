"""Build every part, run the safety checks, export STL (+3MF) to out/, render previews/,
write the painting maps (out/maps/) and the GLB files (out/*.glb, out/GLB.md).

Usage:  .venv/Scripts/python build.py [--no-render] [--only name1,name2]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from build123d import Location, Mesher, export_stl

import config as cfg
import fountain
import glb_export
import hanukkiah
import maps
import parts
import profiles
import render

OUT_DIR = cfg.MODEL_DIR / "out"
PREVIEW_DIR = cfg.MODEL_DIR / "previews"
ASSEMBLY_DIR = OUT_DIR / "_assembly_meshes"  # preview-only meshes, placed as assembled
ANGLE_TEST_SPOTS = (("drum3_R3", 0.0, (30.0, 40.0, 50.0)), ("drum3_R3", 60.0, (40.0,)), ("drum3_R3", 180.0, (40.0,)), ("drum4_R4", 0.0, (40.0,)))  # (ring, concept angle, offsets)  # (ring, concept angle)
ANGLE_TEST_OFFSET = 40.0  # deg either side of head-on
REFERENCE_SKETCH = cfg.MODEL_DIR.parent / "research" / "user-reference-agam-menorah.png"  # style direction (Dana Barlev)


def export_mesh(part, path: Path) -> None:
    export_stl(part, str(path), tolerance=cfg.STL_TOLERANCE, angular_tolerance=cfg.STL_ANGULAR_TOLERANCE)


def export_3mf(part, path: Path) -> None:
    try:
        mesher = Mesher()
        mesher.add_shape(part, linear_deflection=cfg.STL_TOLERANCE, angular_deflection=cfg.STL_ANGULAR_TOLERANCE)
        mesher.write(str(path))
    except Exception as error:  # 3MF is a convenience; STL is the deliverable
        print(f"  3MF skipped for {path.name}: {error}")


def report_part(name: str, part) -> None:
    size = part.bounding_box().size
    fits = size.X <= cfg.BED_SIZE and size.Y <= cfg.BED_SIZE
    valid = "" if part.is_valid else "  INVALID SOLID"
    print(f"  {name:20s} {size.X:6.1f} x {size.Y:6.1f} x {size.Z:6.1f} mm  {part.volume / 1000:6.1f} cm3  {'fits bed' if fits else 'TOO BIG'}{valid}")


def print_safety_report() -> bool:
    print("Safety / halacha checks:")
    all_ok = True
    for label, ok, detail in hanukkiah.safety_report():
        all_ok &= ok
        print(f"  [{'ok' if ok else 'FAIL'}] {label}: {detail}")
    return all_ok


def render_guide_closeup(assembly_paths: dict[str, Path]) -> Path:
    """The subtle guide relief on the white print: HANUKKAH outlines on the right faces."""
    import pyvista as pv

    r3 = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    mesh = pv.read(str(assembly_paths[r3.name]))
    colors = render.relief_colors(mesh, plain_ring_mesh(cfg.CANDLE_DRUM_INDEX), cfg.GUIDE_LINE_HEIGHT / 2)
    tip = fountain.drum_diameter(r3) / 2
    target_deg = 20.0
    world = math.radians(-90 + target_deg)
    target = (tip * math.cos(world), tip * math.sin(world), fountain.stack_heights()[r3.name] + fountain.drum_height(r3) / 2)
    return render.render_closeup(mesh, PREVIEW_DIR / "closeup_guide_relief.png", target, math.degrees(world) + 40.0, 8.0, 110.0, colors)


def plain_ring_mesh(index: int):
    """The same ring without any relief, placed as assembled (for colouring the relief)."""
    import pyvista as pv

    drum = cfg.DRUMS[index]
    plain = Location((0, 0, fountain.stack_heights()[drum.name])) * profiles.pleated_prism(
        fountain.drum_diameter(drum), fountain.drum_height(drum), relief=False
    )
    path = ASSEMBLY_DIR / f"{drum.name}_plain.stl"
    export_mesh(plain, path)
    return pv.read(str(path))


def render_relief_closeups(assembly_paths: dict[str, Path]) -> list[Path]:
    """The two-picture test (each spot from 40 deg left, head-on and 40 deg right), and relief
    close-ups (relief in red): a plain ring's ridges and lip, R3's cup seat, R5's shamash seat."""
    import pyvista as pv

    r3_index, r4_index = cfg.CANDLE_DRUM_INDEX, cfg.CANDLE_DRUM_INDEX + 1
    r3, r4 = cfg.DRUMS[r3_index], cfg.DRUMS[r4_index]
    r3_mesh = pv.read(str(assembly_paths[r3.name]))
    r3_colors = render.relief_colors(r3_mesh, plain_ring_mesh(r3_index), cfg.RIDGE_HEIGHT / 2)
    written = []
    written += render.render_angle_tests(assembly_paths, PREVIEW_DIR, ANGLE_TEST_SPOTS)
    r4_mesh = pv.read(str(assembly_paths[r4.name]))
    r4_colors = render.relief_colors(r4_mesh, plain_ring_mesh(r4_index), cfg.RIDGE_HEIGHT / 2)
    r4_top = fountain.r4_top_z()
    r4_tip = fountain.drum_diameter(r4) / 2
    written.append(render.render_closeup(r4_mesh, PREVIEW_DIR / "closeup_ring_ridges_and_lip.png", (0.0, -r4_tip, r4_top - 6), 270.0, 30.0, 60.0, r4_colors))
    hole = hanukkiah.candle_positions()[0]
    written.append(render.render_closeup(r3_mesh, PREVIEW_DIR / "closeup_r3_step_cup_seat.png", (hole[0], hole[1], fountain.r3_top_z()), 270.0, 50.0, 90.0, r3_colors))
    r5_mesh = pv.read(str(assembly_paths[cfg.DRUMS[-1].name]))
    written.append(render.render_closeup(r5_mesh, PREVIEW_DIR / "closeup_r5_shamash_seat.png", (0.0, 0.0, fountain.shamash_seat_z() - 8), 270.0, 35.0, 110.0))
    return written


def stability_report(built: dict[str, tuple[float, float]]) -> list[str]:
    """Tip angle with 9 lit candles, from each part's volume and centroid height as assembled."""
    mass = moment = 0.0
    for name, (volume, area, z) in built.items():
        shell = min(volume, area * cfg.PRINT_SHELL_MM)
        infill = cfg.FOOT_INFILL if name == "plinth_stem" else cfg.PRINT_INFILL
        grams = (shell + infill * (volume - shell)) * cfg.PETG_DENSITY / 1000
        mass, moment = mass + grams, moment + grams * z
    for x, y, seat, rim in hanukkiah.cup_spots():
        candle_bottom = rim - cfg.CUP_INNER_DEPTH
        for m, z in ((cfg.WASHER_MASS_G, seat + 0.5), (cfg.CUP_MASS_G, (seat + rim) / 2), (cfg.CANDLE_MASS_G, candle_bottom + cfg.CANDLE_PREVIEW_LENGTH / 2)):
            mass, moment = mass + m, moment + m * z
    radius = cfg.PLINTH_DIAMETER / 2
    lines = []
    for label, extra in (("without ballast", 0.0), (f"with ballast ({cfg.BALLAST_POCKETS} pockets x 4 M10 washers)", cfg.BALLAST_POCKETS * cfg.BALLAST_WASHER_MASS_G)):
        total = mass + extra
        z_com = (moment + extra * cfg.BALLAST_POCKET_DEPTH / 2) / total
        angle = math.degrees(math.atan2(radius, z_com))
        ok = angle >= cfg.STABILITY_MIN_TIP_DEG
        lines.append(f"  [{'ok' if ok else 'FAIL'}] tips at {angle:.0f} deg {label} (>= {cfg.STABILITY_MIN_TIP_DEG:g}): mass ~{total:.0f} g, centre of mass {z_com:.0f} mm up, foot r {radius:.1f}")
    return lines


def build_coupon(r3_part, spec) -> Path:
    """Export a test coupon (print orientation, centred on the bed) and an R3-placed copy."""
    import coupon

    piece = coupon.coupon_part(r3_part, spec)
    centre = piece.bounding_box().center()
    on_bed = Location((-centre.X, -centre.Y, 0)) * piece
    report_part(spec.name, on_bed)
    export_mesh(on_bed, OUT_DIR / f"{spec.name}.stl")
    export_3mf(on_bed, OUT_DIR / f"{spec.name}.3mf")
    placed = ASSEMBLY_DIR / f"{spec.name}.stl"
    export_mesh(Location((0, 0, fountain.stack_heights()[cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name])) * piece, placed)
    return placed


def angle_between(a: float, b: float) -> float:
    """Signed a - b in degrees, wrapped to -180..180 (NaN stays NaN)."""
    return (a - b + 180.0) % 360.0 - 180.0


def verify_columns(ring_name: str, side: str, motif, theta, inked) -> tuple[bool, str]:
    """A face-column word, face by face: every face that carries part of a letter has the ink on the
    model, and every gap face has none (the middle 70% of each face, clear of the ridges)."""
    import numpy as np

    import paint_program

    start, columns = paint_program.column_layout(ring_name, motif)
    teeth = paint_program.teeth_of(ring_name)
    pitch = 360.0 / teeth
    first = round((start - paint_program.tooth_start(ring_name, 0)) / pitch)
    wrong = []
    for k, column in enumerate(columns):
        lo, hi = paint_program.face_span(ring_name, side, (first + k) % teeth)
        into = (theta - lo) % 360.0
        margin = 0.15 * (hi - lo)
        has_ink = bool(np.any(inked & (into > margin) & (into < hi - lo - margin)))
        if has_ink != bool(column):
            wrong.append(f"t{(first + k) % teeth}")
    detail = f"{len(columns)} faces from {start:g} deg: " + ("each as in the maps" if not wrong else f"wrong on {', '.join(wrong)}")
    return not wrong, detail


def verify_motif_angles(assembly_paths: dict[str, Path]) -> bool:
    """Every motif: its centre in the maps (the vector shapes they draw) must match where its paint
    lands on the model mesh used by the renders and the GLB. Prints a table; False on mismatch."""
    import numpy as np
    import pyvista as pv

    import paint_mesh
    import paint_program

    ok = True
    print("Motif centres (concept degrees, 0 = front): config | maps | model")
    for ring_name in cfg.RING_PAINT:
        if not paint_program.has_motifs(ring_name):
            continue
        tip = fountain.drum_diameter(paint_program.drum_by_name(ring_name)) / 2
        mesh = paint_mesh.paintable_mesh(ring_name, pv.read(str(assembly_paths[ring_name])))
        paints = paint_mesh.cell_paints(ring_name, mesh)
        normals, centers = paint_mesh.cell_geometry(mesh)
        ground = paint_mesh.side_paints(ring_name, normals, centers, 0.0)
        theta = (np.degrees(np.arctan2(centers[:, 1], centers[:, 0])) + 90.0) % 360.0
        radius = np.hypot(centers[:, 0], centers[:, 1])
        root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
        ridge = cfg.RIDGE_WIDTH / math.sin(math.radians(cfg.TOOTH_INCLUDED_ANGLE / 2))
        on_faces = (np.abs(normals[:, 2]) < 0.7) & (radius > root + 0.5 * ridge) & (radius < tip - 0.5 * ridge)  # face middles
        tangent = np.stack([-np.sin(np.radians(theta - 90.0)), np.cos(np.radians(theta - 90.0))], axis=1)
        is_right = np.einsum("ij,ij->i", normals[:, :2], tangent) > 0
        for side in paint_program.SIDES:
            motifs = getattr(cfg.RING_PAINT[ring_name], side).motifs
            under_band = np.zeros(len(theta), dtype=bool)  # a band repaints the ground (e.g. white under the word)
            for band in (m for m in motifs if m.shape == "band"):
                under_band |= np.abs((theta - band.centre_deg + 180.0) % 360.0 - 180.0) < band.width_deg / 2
            for motif in motifs:
                if motif.shape == "band":
                    continue
                ink = motif.inks[0]
                facing = is_right if side == "right" else ~is_right
                if motif.shape == "columns":
                    good, detail = verify_columns(ring_name, side, motif, theta, (paints == ink) & on_faces & facing)
                    ok &= good
                    print(f"  [{'ok' if good else 'MISMATCH'}] {ring_name.split('_')[1]} {motif.shape:8s} {side:5s} {detail}")
                    continue
                shapes = [g for g, i in paint_program.motif_shapes(ring_name, side) if i == ink and abs(g.centroid.x) < math.pi * tip]
                x0, _, x1, _ = max(shapes, key=lambda g: g.area).bounds
                in_maps = math.degrees((x0 + x1) / 2 / tip)
                offset = (theta - motif.centre_deg + 180.0) % 360.0 - 180.0
                reach = math.degrees((x1 - x0) / 2 / tip) + cfg.MOTIF_ANGLE_SEARCH_MARGIN  # its own width: a same-ink motif nearby stays out
                chosen = (paints == ink) & ((ground != ink) | under_band) & on_faces & facing & (np.abs(offset) < reach)
                lo, hi = np.percentile(offset[chosen], [1, 99]) if chosen.any() else (np.nan, np.nan)
                in_model = motif.centre_deg + (lo + hi) / 2
                in_maps = motif.centre_deg + angle_between(in_maps, motif.centre_deg)  # same turn as config (212, not -148)
                good = abs(angle_between(in_maps, motif.centre_deg)) <= cfg.MOTIF_ANGLE_TOLERANCE and abs(angle_between(in_model, motif.centre_deg)) <= cfg.MOTIF_ANGLE_TOLERANCE
                ok &= bool(good)
                print(f"  [{'ok' if good else 'MISMATCH'}] {ring_name.split('_')[1]} {motif.shape:8s} {side:5s} {motif.centre_deg:7.1f} | {in_maps:7.1f} | {in_model:7.1f}")
    return ok


def main(argv: list[str]) -> None:
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    OUT_DIR.mkdir(exist_ok=True)
    ASSEMBLY_DIR.mkdir(exist_ok=True)
    print_safety_report()
    print("Parts (print orientation):")
    assembly_paths = {}
    built = {}
    r3_built = None
    for spec in parts.all_parts():
        if only and spec.name not in only:
            continue
        part = spec.build()
        report_part(spec.name, part)
        export_mesh(part, OUT_DIR / f"{spec.name}.stl")
        export_3mf(part, OUT_DIR / f"{spec.name}.3mf")
        assembly_paths[spec.name] = ASSEMBLY_DIR / f"{spec.name}.stl"
        assembled = spec.assembly(part)
        export_mesh(assembled, assembly_paths[spec.name])
        built[spec.name] = (assembled.volume, assembled.area, assembled.center().Z)
        if spec.name == cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name:
            r3_built = part
    import coupon

    coupon_paths = {}
    for spec in coupon.COUPONS:
        if r3_built is not None and (only is None or spec.name in only):
            coupon_paths[spec] = build_coupon(r3_built, spec)
    if only is None:
        print("Stability with 9 lit candles:")
        for line in stability_report(built):
            print(line)
    if "--no-render" in argv:
        return
    written = render.render_all(assembly_paths, PREVIEW_DIR)
    for spec, coupon_path in coupon_paths.items():
        written += render.render_coupon(coupon_path, PREVIEW_DIR, spec)
    if REFERENCE_SKETCH.exists():
        written.append(render.render_reference_compare(assembly_paths, PREVIEW_DIR, REFERENCE_SKETCH, "compare_style_sketch", 8.0))
    if only is None:
        import test_ring

        for scale in cfg.TEST_RING_SCALES:
            print(test_ring.summary(scale))
            placed = test_ring.build(scale)
            with test_ring.scaled(scale):
                if not verify_motif_angles({cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name: placed}):
                    print(f"  TEST RING {test_ring.label(scale)}%: MOTIF ANGLES DO NOT MATCH")
            if scale == cfg.TEST_RING_RENDER_SCALE:
                written += test_ring.maps_and_renders(scale, placed)
        written += render_relief_closeups(assembly_paths)
        written.append(render_guide_closeup(assembly_paths))
        if not verify_motif_angles(assembly_paths):
            print("  MOTIF ANGLES DO NOT MATCH: maps and model disagree, do not print or paint from these maps")
        written += maps.write_all()
        glb_export.main()
    for path in written:
        print(f"  wrote {path.relative_to(cfg.MODEL_DIR)}")


if __name__ == "__main__":
    main(sys.argv[1:])
