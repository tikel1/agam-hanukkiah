"""Offscreen preview renders (pyvista): white print, painted look with washers, cups,
candles and flames (preview-only props), and close-ups that colour the paint-guide relief."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pyvista as pv

import config as cfg
import fountain
import hanukkiah
import paint_mesh
import paint_program

WHITE = "#f4f1ea"
STEEL = "#9a9c9e"
NAVY = "#1b2a6b"
METAL = "#b8b8b0"
BRASS = "#c9a24a"
CANDLE = "#2f6fc4"  # blue candles, as in the style sketch (preview only)
FLAME = "#ffb21e"
RELIEF = "#d8262f"
BACKGROUND = ("#cfd8e3", "#f7f9fb")

VIEWS = {"front": (0.0, 10.0), "three_quarter": (35.0, 24.0), "high": (20.0, 50.0), "top": (0.0, 89.0)}


def rgb(color: str) -> np.ndarray:
    return np.array(pv.Color(color).float_rgb)


def paint_rgb(name: str) -> np.ndarray:
    return rgb(paint_program.paint(name).hex)


def paint(name: str, mesh: pv.PolyData) -> np.ndarray | None:
    """Per-cell RGB from the colour program (config RING_PAINT etc.)."""
    if name not in cfg.RING_PAINT and name != "plinth_stem":
        return None
    names = paint_mesh.cell_paints(name, mesh)
    lookup = {key: paint_rgb(key) for key in set(names)}
    return np.array([lookup[key] for key in names])


def metal_props() -> list[tuple[pv.PolyData, str]]:
    """Tubes, cups, candles and flames (preview only: bought metal parts are not printed)."""
    props = []
    candle_length = cfg.CANDLE_PREVIEW_LENGTH
    for x, y, surface, rim in hanukkiah.cup_spots():
        washer_top = surface + cfg.WASHER_T
        candle_bottom = rim - cfg.CUP_INNER_DEPTH
        props.append((pv.Cylinder(center=(x, y, surface + cfg.WASHER_T / 2), direction=(0, 0, 1), radius=cfg.WASHER_D / 2, height=cfg.WASHER_T), METAL))
        props.append((pv.Cylinder(center=(x, y, (washer_top + rim) / 2), direction=(0, 0, 1), radius=cfg.CUP_OD / 2, height=rim - washer_top), BRASS))
        props.append((pv.Cylinder(center=(x, y, candle_bottom + candle_length / 2), direction=(0, 0, 1), radius=cfg.CANDLE_PREVIEW_DIAMETER / 2, height=candle_length), CANDLE))
        flame_half = cfg.FLAME_PREVIEW_HEIGHT / 2
        props.append((pv.ParametricEllipsoid(3.0, 3.0, flame_half).translate((x, y, candle_bottom + candle_length + flame_half), inplace=False), FLAME))
    return props


def add_colored(plotter: pv.Plotter, mesh: pv.PolyData, colors: np.ndarray | None, fallback: str = WHITE) -> None:
    if colors is None:
        plotter.add_mesh(mesh, color=fallback, specular=0.2, smooth_shading=False)
        return
    colored = mesh.copy()
    colored.cell_data["rgb"] = (colors * 255).astype(np.uint8)
    plotter.add_mesh(colored, scalars="rgb", rgb=True, specular=0.2)


def render_scene(meshes: dict[str, pv.PolyData], painted: bool, path: Path, azimuth: float, elevation: float, props: bool = True) -> None:
    plotter = pv.Plotter(off_screen=True, window_size=cfg.PREVIEW_SIZE)
    plotter.set_background(BACKGROUND[0], top=BACKGROUND[1])
    for name, mesh in meshes.items():
        if painted:
            mesh = paint_mesh.paintable_mesh(name, mesh)
        add_colored(plotter, mesh, paint(name, mesh) if painted else None, STEEL if painted and name == "spine" else WHITE)
    if painted and props:
        for prop, color in metal_props():
            plotter.add_mesh(prop, color=color, specular=0.3)
    plotter.enable_lightkit()
    place_camera(plotter, meshes, azimuth, elevation, extra_height=75.0 if painted and props else 0.0)
    plotter.screenshot(str(path))
    plotter.close()


def render_all(mesh_paths: dict[str, Path], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    meshes = {name: pv.read(str(path)) for name, path in mesh_paths.items()}
    written = []
    for painted in (False, True):
        for view, (azimuth, elevation) in VIEWS.items():
            path = out_dir / f"{'painted' if painted else 'white'}_{view}.png"
            render_scene(meshes, painted, path, azimuth, elevation)
            written.append(path)
    for view, azimuth in (("front", 0.0), ("left", 90.0), ("back", 180.0), ("right", 270.0)):
        path = out_dir / f"reference_bare_{view}.png"  # like the photos: the sculpture alone, eye level
        render_scene(meshes, True, path, azimuth, 6.0, props=False)
        written.append(path)
    return written


def place_camera(plotter: pv.Plotter, meshes: dict[str, pv.PolyData], azimuth: float, elevation: float, extra_height: float) -> None:
    bounds = np.array([m.bounds for m in meshes.values()])
    lo = bounds[:, [0, 2, 4]].min(axis=0)
    hi = bounds[:, [1, 3, 5]].max(axis=0) + np.array([0, 0, extra_height])
    center = (lo + hi) / 2
    radius = float(np.linalg.norm(hi - lo)) * 1.45
    az, el = math.radians(azimuth - 90), math.radians(elevation)
    eye = center + radius * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    plotter.camera_position = [tuple(eye), tuple(center), (0, 0, 1)]
    plotter.camera.view_angle = 30


def relief_colors(mesh: pv.PolyData, base: pv.PolyData, threshold: float) -> np.ndarray:
    """Close-up paint: everything proud of the plain pleats (ridges, lips, emblems) in red;
    stripe faces A blue / B white; tops grey."""
    centers = mesh.cell_centers()
    distance = centers.compute_implicit_distance(base)["implicit_distance"]
    normals, points = paint_mesh.cell_geometry(mesh)
    angle = np.arctan2(points[:, 1], points[:, 0])
    tangent = np.stack([-np.sin(angle), np.cos(angle)], axis=1)
    face_a = np.einsum("ij,ij->i", normals[:, :2], tangent) > 0.2
    colors = np.where(face_a[:, None], rgb("#4f86d9"), rgb(WHITE))
    colors[np.abs(normals[:, 2]) > 0.7] = rgb(STEEL)
    colors[distance > threshold] = rgb(RELIEF)
    return colors


def render_closeup(
    mesh: pv.PolyData,
    path: Path,
    target: tuple[float, float, float],
    view_deg: float,
    elevation_deg: float,
    distance: float,
    colors: np.ndarray | None = None,
) -> Path:
    """Close-up of one spot. view_deg = world direction from the target towards the camera."""
    plotter = pv.Plotter(off_screen=True, window_size=(1400, 900))
    plotter.set_background(BACKGROUND[0], top=BACKGROUND[1])
    add_colored(plotter, mesh, colors)
    plotter.enable_lightkit()
    view, elevation = math.radians(view_deg), math.radians(elevation_deg)
    direction = np.array([math.cos(elevation) * math.cos(view), math.cos(elevation) * math.sin(view), math.sin(elevation)])
    plotter.camera_position = [tuple(np.array(target) + distance * direction), tuple(target), (0, 0, 1)]
    plotter.camera.view_angle = 30
    plotter.screenshot(str(path))
    plotter.close()
    return path


def render_coupon(coupon_path: Path, out_dir: Path, spec=None) -> list[Path]:
    """The painted test coupon from 40 deg left and 40 deg right of its middle (in R3's place)."""
    import coupon

    spec = spec or coupon.MAIN
    prefix = "coupon" if spec is coupon.MAIN else spec.name
    mesh = paint_mesh.paintable_coupon(pv.read(str(coupon_path)), spec)
    colours = paint("drum3_R3", mesh)
    drum = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX]
    tip = fountain.drum_diameter(drum) / 2
    lo, hi = coupon.coupon_range(spec)
    world = math.radians(-90 + (lo + hi) / 2)
    target = (tip * math.cos(world), tip * math.sin(world), fountain.stack_heights()[drum.name] + fountain.drum_height(drum) / 2)
    written = []
    for label, delta in (("left", -40.0), ("right", 40.0)):
        written.append(render_closeup(mesh, out_dir / f"{prefix}_painted_from_{label}.png", target, math.degrees(world) + delta, 15.0, 170.0, colours))
    return written


def render_angle_tests(mesh_paths: dict[str, Path], out_dir: Path, spots: tuple) -> list[Path]:
    """The two-picture test: each (ring, concept angle, offsets) spot seen from each offset to the
    left, head-on and the same offset to the right, at eye level. One combined image per offset."""
    from PIL import Image, ImageDraw

    meshes = {name: pv.read(str(path)) for name, path in mesh_paths.items()}
    painted = {name: paint_mesh.paintable_mesh(name, mesh) for name, mesh in meshes.items()}
    colours = {name: paint(name, mesh) for name, mesh in painted.items()}
    written = []
    for ring_name, concept_deg, offsets in spots:
        for offset in offsets:
            drum = next(d for d in cfg.DRUMS if d.name == ring_name)
            tip = fountain.drum_diameter(drum) / 2
            world = math.radians(-90 + concept_deg)
            target = (tip * math.cos(world), tip * math.sin(world), fountain.stack_heights()[ring_name] + fountain.drum_height(drum) / 2)
            frames = []
            for label, delta in (("from the LEFT", -offset), ("head-on", 0.0), ("from the RIGHT", offset)):
                plotter = pv.Plotter(off_screen=True, window_size=(900, 700))
                plotter.set_background(BACKGROUND[0], top=BACKGROUND[1])
                for name, mesh in painted.items():
                    add_colored(plotter, mesh, colours[name], STEEL if name == "spine" else WHITE)
                plotter.enable_lightkit()
                view = world + math.radians(delta)
                eye = np.array(target) + 420.0 * np.array([math.cos(view), math.sin(view), math.tan(math.radians(6.0))])
                plotter.camera_position = [tuple(eye), target, (0, 0, 1)]
                plotter.camera.view_angle = 30
                frames.append((label, plotter.screenshot(return_img=True)))
                plotter.close()
            strip = Image.new("RGB", (900 * 3, 740), "white")
            draw = ImageDraw.Draw(strip)
            for index, (label, frame) in enumerate(frames):
                strip.paste(Image.fromarray(frame), (900 * index, 40))
                draw.text((900 * index + 20, 10), f"{ring_name.split('_')[1]} at {concept_deg:g} deg, {label} ({offset:g} deg)" if label != "head-on" else f"{ring_name.split('_')[1]} at {concept_deg:g} deg, head-on", fill="black")
            suffix = "" if offset == 40.0 else f"_at{int(offset)}"
            path = out_dir / f"test_two_pictures_{ring_name.split('_')[1]}_{int(concept_deg):03d}{suffix}.png"
            strip.save(path)
            written.append(path)
    return written


def render_reference_compare(mesh_paths: dict[str, Path], out_dir: Path, reference: Path, name: str, elevation: float) -> Path:
    """The painted model (with cups, candles, flames) beside a reference image, same height."""
    from PIL import Image

    meshes = {key: pv.read(str(path)) for key, path in mesh_paths.items()}
    render_path = out_dir / f"_{name}_render.png"
    render_scene(meshes, True, render_path, 0.0, elevation)
    ours = Image.open(render_path).convert("RGB")
    theirs = Image.open(reference).convert("RGB")
    theirs = theirs.resize((round(theirs.width * ours.height / theirs.height), ours.height))
    combined = Image.new("RGB", (theirs.width + ours.width, ours.height), "white")
    combined.paste(theirs, (0, 0))
    combined.paste(ours, (theirs.width, 0))
    path = out_dir / f"{name}.png"
    combined.save(path)
    render_path.unlink()
    return path
