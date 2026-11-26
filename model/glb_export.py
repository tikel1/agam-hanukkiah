"""GLB export for a web viewer: the assembled hanukkiah, Y-up, in metres.

out/hanukkiah_painted.glb: one material per paint (colour program in config), one node per
printed part with a child mesh per paint, a `metal` node (washers + cups), a `candles`
node, and empty `flame_*` nodes at the wick of each candle.
out/hanukkiah_white.glb: the same nodes with one white PETG material.
See out/GLB.md (written alongside) for node and material names.

Needs the assembled meshes from `python build.py` (out/_assembly_meshes/).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from trimesh.visual.material import PBRMaterial

import config as cfg
import hanukkiah
import paint_mesh
import paint_program as program
import parts

OUT_DIR = cfg.MODEL_DIR / "out"
ASSEMBLY_DIR = OUT_DIR / "_assembly_meshes"
MM_TO_M = 0.001
Z_UP_TO_Y_UP = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)  # front (-Y) -> +Z
WHITE_PETG = "#F2F1EC"


def to_gltf(points: np.ndarray) -> np.ndarray:
    return (np.asarray(points, dtype=float) @ Z_UP_TO_Y_UP.T) * MM_TO_M


def hex_rgba(hex_value: str) -> list[float]:
    value = hex_value.lstrip("#")
    return [int(value[i : i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0]


def material(name: str, hex_value: str, metallic: float = 0.0, roughness: float = 0.65) -> PBRMaterial:
    return PBRMaterial(name=name, baseColorFactor=hex_rgba(hex_value), metallicFactor=metallic, roughnessFactor=roughness, doubleSided=False)


def paint_material_name(paint_name: str) -> str:
    paint = program.paint(paint_name)
    return f"paint_{paint.number:02d}_{paint.name}"


def flat_mesh(points: np.ndarray, triangles: np.ndarray, mat: PBRMaterial) -> trimesh.Trimesh:
    """Shared vertices, exported WITHOUT normals: the glTF spec tells viewers to shade such
    meshes flat, which keeps the pleats crisp and the file small."""
    used, inverse = np.unique(triangles.ravel(), return_inverse=True)
    mesh = trimesh.Trimesh(vertices=to_gltf(points[used]), faces=inverse.reshape(-1, 3), process=False)
    mesh.visual = trimesh.visual.TextureVisuals(material=mat)
    return mesh


def add_group(scene: trimesh.Scene, name: str, parent: str = "world") -> None:
    scene.graph.update(frame_from=parent, frame_to=name, matrix=np.eye(4))


def add_part(scene: trimesh.Scene, name: str, mesh: pv.PolyData, painted: bool) -> None:
    add_group(scene, name)
    triangles = mesh.faces.reshape(-1, 4)[:, 1:]
    if not painted:
        scene.add_geometry(flat_mesh(mesh.points, triangles, material("petg_white", WHITE_PETG)), node_name=f"{name}__petg_white", geom_name=f"{name}__petg_white", parent_node_name=name)
        return
    paints = paint_mesh.cell_paints(name, mesh)
    for paint_name in sorted(set(paints), key=lambda n: program.paint(n).number):
        label = paint_material_name(paint_name)
        mat = material(label, program.paint(paint_name).hex)
        node = f"{name}__{label}"
        scene.add_geometry(flat_mesh(mesh.points, triangles[paints == paint_name], mat), node_name=node, geom_name=node, parent_node_name=name)


def cylinder(x: float, y: float, z0: float, z1: float, radius: float) -> trimesh.Trimesh:
    shape = trimesh.creation.cylinder(radius=radius, height=z1 - z0, sections=40)
    shape.apply_translation((x, y, (z0 + z1) / 2))
    return shape


def add_props(scene: trimesh.Scene) -> None:
    """Washers and cups, preview candles, and flame anchors (empty nodes)."""
    steel = material("metal_steel", "#B8B8B0", metallic=1.0, roughness=0.35)
    brass = material("metal_brass", "#C9A24A", metallic=1.0, roughness=0.3)
    wax = material("candle_wax", "#F3E6C8", roughness=0.8)
    for group in ("metal", "candles", "flames"):
        add_group(scene, group)
    for number, (x, y, surface, rim) in enumerate(hanukkiah.cup_spots(), start=1):
        label = "shamash" if number > cfg.CANDLE_COUNT else str(number)
        candle_bottom = rim - cfg.CUP_INNER_DEPTH
        pieces = [
            ("metal", f"washer_{label}", cylinder(x, y, surface, surface + cfg.WASHER_T, cfg.WASHER_D / 2), steel),
            ("metal", f"cup_{label}", cylinder(x, y, surface + cfg.WASHER_T, rim, cfg.CUP_OD / 2), brass),
            ("candles", f"candle_{label}", cylinder(x, y, candle_bottom, candle_bottom + cfg.CANDLE_PREVIEW_LENGTH, cfg.CANDLE_PREVIEW_DIAMETER / 2), wax),
        ]
        for group, node, shape, mat in pieces:
            scene.add_geometry(flat_mesh(shape.vertices, shape.faces, mat), node_name=node, geom_name=node, parent_node_name=group)
        anchor = np.eye(4)
        anchor[:3, 3] = to_gltf([[x, y, candle_bottom + cfg.CANDLE_PREVIEW_LENGTH]])[0]
        scene.graph.update(frame_from="flames", frame_to=f"flame_{label}", matrix=anchor)


def build_scene(painted: bool) -> trimesh.Scene:
    scene = trimesh.Scene()
    for spec in parts.all_parts():
        path = ASSEMBLY_DIR / f"{spec.name}.stl"
        if not path.exists():
            raise FileNotFoundError(f"{path} is missing: run `python build.py` first")
        mesh = pv.read(str(path))
        if painted:
            mesh = paint_mesh.paintable_mesh(spec.name, mesh)
        add_part(scene, spec.name, mesh, painted)
    add_props(scene)
    return scene


def export(painted: bool) -> Path:
    path = OUT_DIR / f"hanukkiah_{'painted' if painted else 'white'}.glb"
    data = trimesh.exchange.gltf.export_glb(build_scene(painted), include_normals=False)
    if len(data) > cfg.GLB_MAX_BYTES:
        print(f"  WARNING: {path.name} is {len(data) / 1e6:.1f} MB (limit {cfg.GLB_MAX_BYTES / 1e6:.0f} MB)")
    path.write_bytes(data)
    return path


def write_notes(paths: list[Path]) -> Path:
    used = sorted({n for spec in parts.all_parts() for n in used_paints(spec.name)}, key=lambda n: program.paint(n).number)
    rows = "\n".join(f"| `{paint_material_name(n)}` | {program.paint(n).hex} | {program.paint(n).number} {n} |" for n in used)
    sizes = ", ".join(f"`{p.name}` {p.stat().st_size / 1e6:.1f} MB" for p in paths)
    text = GLB_NOTES.format(sizes=sizes, rows=rows, parts=", ".join(f"`{s.name}`" for s in parts.all_parts()), count=cfg.CANDLE_COUNT, candle=cfg.CANDLE_PREVIEW_LENGTH, depth=cfg.CUP_INNER_DEPTH, above=cfg.CANDLE_PREVIEW_LENGTH - cfg.CUP_INNER_DEPTH)
    notes = OUT_DIR / "GLB.md"
    notes.write_text(text, encoding="utf-8")
    return notes


def used_paints(name: str) -> set[str]:
    path = ASSEMBLY_DIR / f"{name}.stl"
    return set(paint_mesh.cell_paints(name, paint_mesh.paintable_mesh(name, pv.read(str(path)))))


GLB_NOTES = """# GLB files for the web viewer

Generated by `model/glb_export.py` (run `python build.py`, or `python glb_export.py` after a build).
Files: {sizes}.

## Frame and units
* **Y-up, metres.** The model's front (concept angle 0, where HANUKKAH is) faces **+Z**. +X is the viewer's right.
* Origin: centre of the plinth's underside, on the table. Overall about 0.18 m wide and 0.19 m tall with candles.
* Geometry is baked in place (all node transforms are identity), so nodes can be shown, hidden or recoloured freely.
* No normals are stored: per the glTF spec, viewers shade such meshes flat (three.js does), which keeps the pleats crisp.
  Each paint cell on R3 is its own set of triangles (faces are cut into 3 columns x 1 mm rows where the pictures are).

## Nodes (same names in both files)
* One group node per printed part: {parts}.
  * `hanukkiah_painted.glb`: each part has one child mesh per paint, named `<part>__<material>`, e.g. `drum3_R3__paint_08_cobalt`.
  * `hanukkiah_white.glb`: each part has one child mesh `<part>__petg_white`.
* `metal`: `washer_1` ... `washer_{count}`, `washer_shamash` (stainless heat-shield washers Ø 16 × 1, `metal_steel`) and `cup_1` ... `cup_shamash`
  (cups Ø 12 × 10, `metal_brass`). The 8 ring cups sit on R3's top step at r 81 mm, the shamash on R5's top centre.
* `candles`: `candle_1` ... `candle_shamash`, simple {candle:.0f} mm preview candles (`candle_wax`). Hide them to show empty cups.
* `flames`: empty nodes `flame_1` ... `flame_{count}`, `flame_shamash` at the top of each preview candle (wick). Candle 1 is at the front
  (+Z), then counter-clockwise seen from above (towards +X first). Each candle sinks {depth:.0f} mm into its cup, so the cup rim is
  {above:.0f} mm below each anchor.

## Materials (`hanukkiah_painted.glb`)
One PBR material per paint (metallic 0, roughness 0.65). `paint_00_bare` is unpainted white PETG (every top face, washer seats,
undersides and joints). The colour program lives in `model/config.py` (RING_PAINT, EMBLEM_PAINT, PAINTS).

| Material | Base colour | Paint |
|---|---|---|
{rows}
| `metal_steel` | #B8B8B0, metallic 1, roughness 0.35 | washers |
| `metal_brass` | #C9A24A, metallic 1, roughness 0.3 | cups |
| `candle_wax` | #F3E6C8 | preview candles |
| `petg_white` | #F2F1EC (white file only) | everything printed |
"""


def main() -> None:
    paths = [export(painted=True), export(painted=False)]
    notes = write_notes(paths)
    for path in paths + [notes]:
        print(f"  {path.relative_to(cfg.MODEL_DIR)}")


if __name__ == "__main__":
    main()
