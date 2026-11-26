"""Name plaque: a white curved base over the front of the round foot, with sunken guides for the
separately printed letters and dots.

The plaque is a 1.6 mm skin on the foot's side (0.3 mm off it), rising 3.3 mm above the disc,
with a rim that lies on the disc's top edge. Its top corners are rounded. It stands on the table
and hangs on its rim; a dab of glue keeps it put. Both lines of the logo (plaque_art.py) sit on
its face: "חנוכיית אש ומים" with the coloured dots, and "מחווה לאמן יעקב אגם" under it.

Two ways to print. plaque_one_piece: everything in one white print to paint (letters 0.6 proud,
dots 1.2), upside down, no supports. Or apart: the white base (upside down, its top on the bed, no supports), the letters and
the dots. Every piece has a flat back and prints back down on the bed. The base carries a 0.4 mm
sunken footprint of every piece, so each one shows where it goes and settles into place. Letters
are 1.0 thick (0.6 proud), dots 1.6 (1.2 proud), so the dots stand above the letters and each
level is easy to paint. Glue with ABS cement (acetone) or thin CA.

Usage: python plaque.py   (the model .venv)
Writes out/name_plaque/{plaque_one_piece,plaque_base,letters,dots,assembly}.3mf, out/plaque_in_place.stl and preview parts in out/_plaque_preview/.
"""

from __future__ import annotations

import math

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import MultiPolygon, box
from shapely.ops import unary_union

import plaque_art as art

OUT = art.HERE / "out"
PLAQUE_DIR = OUT / "name_plaque"
PREVIEW_DIR = OUT / "_plaque_preview"

# --- the foot it sits on (config.py: PLINTH_DIAMETER, PLINTH_HEIGHT, PLINTH_EDGE_ROUND) ---
FOOT_RADIUS = 56.0
FOOT_HEIGHT = 14.5
FOOT_ROUND = 4.0
CLEARANCE = 0.3  # room for paint or glue on both parts

# --- plaque ---
THICKNESS = 1.6
HEIGHT = 17.8  # 3.3 above the disc
RIM_REACH = 51.0  # the rim's inner edge (radius); the disc's flat top ends at r 52
SIDE_MARGIN = 4.0  # plain face beyond the artwork on each side
CORNER_RADIUS = 4.0  # top corners
ARC_STEPS = 12
SECTIONS = 720

# --- pockets and pieces ---
POCKET_DEPTH = 0.4  # the sunken footprints that show where each piece goes
POCKET_CLEAR = 0.12  # per side, for ABS shrink and glue
EMBED = 0.3  # one-piece version: how far the relief sinks into the face, so the union is solid
LETTER_THICKNESS = 1.0  # 0.6 proud
DOT_THICKNESS = 1.6  # 1.2 proud: the dots stand 0.6 above the letters
EDGE_MARGIN = 1.0  # artwork pockets keep this far from the plaque's edges
SIMPLIFY = 0.01  # drops near-duplicate outline points that break the extrusion
MAX_EDGE = 0.5  # artwork meshes are split this fine before they are bent round the plaque
PLATE_GAP = 4.0  # between the name and the tribute line on the navy plate

INNER_R = FOOT_RADIUS + CLEARANCE
OUTER_R = INNER_R + THICKNESS
FRONT_DEG = -90.0  # the plaque faces -Y (the hanukkiah's front)


def prisms(shape, height: float) -> trimesh.Trimesh:
    polygons = list(shape.geoms) if isinstance(shape, MultiPolygon) else [shape]
    return trimesh.util.concatenate([trimesh.creation.extrude_polygon(p.simplify(SIMPLIFY), height) for p in polygons if not p.is_empty])


def bend(shape, base_radius: float, height: float) -> trimesh.Trimesh:
    """Extrude a face-mm shape (u along the face, v up) radially from base_radius, round the foot."""
    flat = prisms(shape, height)
    vertices, faces = trimesh.remesh.subdivide_to_size(flat.vertices, flat.faces, max_edge=MAX_EDGE)
    u, v, w = vertices.T
    radius = base_radius + w
    angle = np.radians(FRONT_DEG) + u / OUTER_R
    return trimesh.Trimesh(np.column_stack([radius * np.cos(angle), radius * np.sin(angle), v]), faces, process=True)


def profile() -> np.ndarray:
    """(radius, z) section: the face, the rim over the disc's top, and a back that follows its round."""
    centre_r, centre_z = FOOT_RADIUS - FOOT_ROUND, FOOT_HEIGHT - FOOT_ROUND
    inner = FOOT_ROUND + CLEARANCE
    angles = np.radians(np.linspace(90.0, 0.0, ARC_STEPS))
    back = [(centre_r + inner * math.cos(a), centre_z + inner * math.sin(a)) for a in angles]
    rim_bottom = centre_z + inner
    return np.array([(INNER_R, 0.0), (OUTER_R, 0.0), (OUTER_R, HEIGHT), (RIM_REACH, HEIGHT),
                     (RIM_REACH, rim_bottom), *back, (INNER_R, 0.0)])


def outline(width: float):
    """The plaque's face outline: square at the table, rounded at the top corners."""
    half, r = width / 2, CORNER_RADIUS
    rounded = box(-half + r, r, half - r, HEIGHT - r).buffer(r, 32)
    return unary_union([rounded, box(-half, 0, half, HEIGHT / 2)])


def plain_plaque(width: float) -> trimesh.Trimesh:
    ring = trimesh.creation.revolve(profile(), sections=SECTIONS)
    trimesh.repair.fix_normals(ring)
    cut_base = RIM_REACH - 1.0
    shape = bend(outline(width), cut_base, OUTER_R + 1.0 - cut_base)
    return trimesh.boolean.intersection([ring, shape], engine="manifold")


def closed(mesh: trimesh.Trimesh, name: str) -> trimesh.Trimesh:
    """Manifold's output as it is: merging its near-coincident vertices can pinch edges."""
    if not mesh.is_watertight:
        raise RuntimeError(f"{name} mesh is not watertight")
    return mesh


def white_plaque(artwork, width: float) -> trimesh.Trimesh:
    """The base for separate pieces: a sunken footprint of every piece."""
    pockets = bend(artwork.buffer(POCKET_CLEAR, join_style="mitre"), OUTER_R - POCKET_DEPTH, POCKET_DEPTH + 1.0)
    return closed(trimesh.boolean.difference([plain_plaque(width), pockets], engine="manifold"), "plaque")


def one_piece(strokes, dot_shapes, width: float) -> trimesh.Trimesh:
    """Everything in one white print to paint: letters 0.6 proud, dots 1.2, as on the assembled plaque."""
    base = OUTER_R - EMBED
    letters = bend(strokes, base, LETTER_THICKNESS - POCKET_DEPTH + EMBED)
    dots = bend(dot_shapes, base, DOT_THICKNESS - POCKET_DEPTH + EMBED)
    return closed(trimesh.boolean.union([plain_plaque(width), letters, dots], engine="manifold"), "one-piece plaque")


def check_fits(artwork, width: float) -> None:
    minx, miny, maxx, maxy = artwork.buffer(POCKET_CLEAR).bounds
    if not outline(width).buffer(-EDGE_MARGIN).contains(artwork.buffer(POCKET_CLEAR)):
        raise ValueError(f"artwork {miny:.1f}..{maxy:.1f} mm does not fit the plaque with a {EDGE_MARGIN} mm margin")
    print(f"artwork {maxx - minx:.1f} x {maxy - miny:.1f} mm on a plaque {width:.1f} mm ({math.degrees(width / OUTER_R):.0f} deg) x {HEIGHT} mm")


def letter_piece(stroke, own_dots, lift: float = 0.0) -> trimesh.Trimesh:
    """One flat piece: the letter at letter height with its dots standing taller on its ends."""
    parts = [prisms(affinity.translate(stroke, 0, lift), LETTER_THICKNESS)]
    parts += [prisms(affinity.translate(dot, 0, lift), DOT_THICKNESS) for dot, _ in own_dots]
    if len(parts) == 1:
        return parts[0]
    piece = trimesh.boolean.union(parts, engine="manifold")
    piece.merge_vertices()
    return piece


def plate(meshes: list[trimesh.Trimesh]) -> trimesh.Scene:
    """Flat pieces, back down on the bed and seen from above as on the plaque."""
    scene = trimesh.Scene()
    for index, mesh in enumerate(meshes):
        scene.add_geometry(mesh, node_name=f"piece_{index:02d}", geom_name=f"piece_{index:02d}")
    return scene


def export_plates(letters, tribute_parts, loose_dots) -> dict[str, int]:
    tribute_top = max(part.bounds[3] for part in tribute_parts)
    lift = min(stroke.bounds[1] for stroke, _ in letters) - tribute_top - PLATE_GAP
    plates = {"letters": [letter_piece(stroke, own) for stroke, own in letters]
                         + [letter_piece(part, [], lift) for part in tribute_parts],
              "dots": [prisms(dot, DOT_THICKNESS) for dot, _ in loose_dots]}
    for name, meshes in plates.items():
        if not all(mesh.is_watertight for mesh in meshes):
            raise RuntimeError(f"a {name} piece is not watertight")
        plate(meshes).export(PLAQUE_DIR / f"{name}.3mf")
    return {name: len(meshes) for name, meshes in plates.items()}


def upside_down(plaque: trimesh.Trimesh) -> trimesh.Trimesh:
    printable = plaque.copy()
    printable.apply_transform(trimesh.transformations.rotation_matrix(math.pi, (1, 0, 0)))  # top on the bed
    centre = printable.bounds.mean(axis=0)
    printable.apply_translation((-centre[0], -centre[1], -printable.bounds[0][2]))
    return printable


def export_preview(plaque, letters, tribute, dots) -> None:
    """Preview meshes and the assembly (every piece in its place on the base, as separate objects)."""
    for old in PREVIEW_DIR.glob("*.stl"):
        old.unlink()
    base = OUTER_R - POCKET_DEPTH
    navy = bend(unary_union([*[stroke for stroke, _ in letters], tribute]), base, LETTER_THICKNESS)
    dot_meshes = [(bend(shape, base, DOT_THICKNESS), colour) for shape, colour in dots]
    plaque.export(PREVIEW_DIR / "band.stl")
    navy.export(PREVIEW_DIR / "navy.stl")
    assembly = trimesh.Scene()
    assembly.add_geometry(plaque, node_name="base", geom_name="base")
    assembly.add_geometry(navy, node_name="letters", geom_name="letters")
    for index, (mesh, colour) in enumerate(dot_meshes):
        mesh.export(PREVIEW_DIR / f"dot_{index:02d}_{colour.lstrip('#')}.stl")
        assembly.add_geometry(mesh, node_name=f"dot_{index:02d}_{art.COLOUR_NAMES[colour]}", geom_name=f"dot_{index:02d}")
    assembly.export(PLAQUE_DIR / "assembly.3mf")


def main() -> None:
    letters, loose_dots = art.wordmark()
    dots = [*[dot for _, own in letters for dot in own], *loose_dots]
    tribute_parts = art.tribute_letters()
    tribute = unary_union(tribute_parts)
    artwork = unary_union([*[stroke for stroke, _ in letters], tribute, *[shape for shape, _ in dots]])
    minx, _, maxx, _ = artwork.bounds
    width = maxx - minx + 2 * SIDE_MARGIN
    check_fits(artwork, width)
    for directory in (PLAQUE_DIR, PREVIEW_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for old in PLAQUE_DIR.glob("*.3mf"):
        old.unlink()
    plaque = white_plaque(artwork, width)
    plaque.export(OUT / "plaque_in_place.stl")
    upside_down(plaque).export(PLAQUE_DIR / "plaque_base.3mf")
    strokes = unary_union([*[stroke for stroke, _ in letters], tribute])
    single = one_piece(strokes, unary_union([shape for shape, _ in dots]), width)
    upside_down(single).export(PLAQUE_DIR / "plaque_one_piece.3mf")
    counts = export_plates(letters, tribute_parts, loose_dots)
    export_preview(plaque, letters, tribute, dots)
    single.export(PREVIEW_DIR / "one_piece.stl")
    size = plaque.extents
    print(f"base: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, {plaque.volume / 1000:.1f} cm3")
    print("pieces: " + ", ".join(f"{name} {count}" for name, count in counts.items()))


if __name__ == "__main__":
    main()
