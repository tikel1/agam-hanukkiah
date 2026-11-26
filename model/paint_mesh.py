"""Paint name for every triangle of an assembled part mesh, from the colour program.

Used by render.py (painted previews) and glb_export.py (one material per paint)."""

from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import config as cfg
import fountain
import paint_program as program

TOP_NORMAL = 0.7  # |normal z| above this = a top or bottom face
_SLICED: dict[tuple[str, int], pv.PolyData] = {}


def cell_geometry(mesh: pv.PolyData) -> tuple[np.ndarray, np.ndarray]:
    normals = mesh.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=False)["Normals"]
    return normals, mesh.cell_centers().points


def split_pleated_side(name: str, mesh: pv.PolyData) -> tuple[pv.PolyData, pv.PolyData]:
    """(the pleat faces and ridges, everything else: tops, bottoms, holes, the top lip)."""
    normals, centers = cell_geometry(mesh)
    drum = program.drum_by_name(name)
    tip = fountain.drum_diameter(drum) / 2
    root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    z0 = fountain.stack_heights()[name]
    radius = np.hypot(centers[:, 0], centers[:, 1])
    on_side = (np.abs(normals[:, 2]) < TOP_NORMAL) & (radius > root - 1.0) & (centers[:, 2] < z0 + fountain.drum_height(drum) + 0.01)
    on_side &= distance_to_outline(name, centers[:, :2]) < 0.05  # guide relief stands off the faces: keep it
    side = mesh.extract_cells(np.flatnonzero(on_side)).extract_surface(algorithm="dataset_surface")
    rest = mesh.extract_cells(np.flatnonzero(~on_side)).extract_surface(algorithm="dataset_surface")
    return side, rest


def distance_to_outline(name: str, points: np.ndarray) -> np.ndarray:
    """Plan distance (mm) from each point to the ring's pleated outline (with its ridges)."""
    import profiles

    drum = program.drum_by_name(name)
    outline = np.array(profiles.ridged_sawtooth_points(fountain.drum_diameter(drum) / 2, program.teeth_of(name), cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH))
    a, b = outline, np.roll(outline, -1, axis=0)
    best = np.full(len(points), np.inf)
    for start in range(0, len(points), 4000):
        chunk = points[start : start + 4000][:, None, :]
        d = (b - a)[None, :, :]
        t = np.clip(np.einsum("ijk,ijk->ij", chunk - a[None], d) / np.einsum("ijk,ijk->ij", d, d), 0.0, 1.0)
        nearest = a[None] + t[..., None] * d
        best[start : start + 4000] = np.linalg.norm(chunk - nearest, axis=2).min(axis=1)
    return best


def face_coordinate(name: str, point: np.ndarray, side: str, k: int) -> float:
    """Where a plan point sits across face k of a set: 0 at the first edge of the face, 1 at
    its last (by angle, so the ridges at either end fall just outside or on 0 and 1)."""
    lo, hi = program.face_span(name, side, k)
    angle = float(program.concept_angle(math.atan2(point[1], point[0])))
    offset = (angle - lo + 180.0) % 360.0 - 180.0
    return offset / (hi - lo)


def strip_pieces(regions: tuple, u0: float, u1: float, height: float, ground: str) -> list:
    """The strip u0..u1 x 0..height of one face, cut along the motif outlines into painted pieces."""
    from shapely.geometry import box
    from shapely.ops import unary_union

    strip = box(min(u0, u1), 0.0, max(u0, u1), height)
    pieces, covered = [], []
    for region, ink in reversed(regions):  # later motifs paint over earlier ones
        piece = region.intersection(strip)
        if covered:
            piece = piece.difference(unary_union(covered))
        if not piece.is_empty and piece.area > 1e-5:
            pieces.append((piece, ink))
        covered.append(region)
    rest = strip.difference(unary_union(covered)) if covered else strip
    if not rest.is_empty and rest.area > 1e-5:
        pieces.append((rest, ground))
    return pieces


def triangles_of(geometry) -> list:
    """Constrained triangulation (holes respected) of a shapely (multi)polygon: (3, 2) arrays."""
    import shapely

    return [np.asarray(triangle.exterior.coords)[:3] for triangle in shapely.constrained_delaunay_triangles(geometry).geoms]


def edge_side(p: np.ndarray, q: np.ndarray, teeth: int) -> tuple[str, int, np.ndarray]:
    """(face set, tooth from the front, outward plan normal) of one outline edge."""
    mid = (p + q) / 2
    normal = np.array([q[1] - p[1], p[0] - q[0]])
    angle = math.atan2(mid[1], mid[0])
    side = "right" if normal @ np.array([-math.sin(angle), math.cos(angle)]) > 0 else "left"
    tooth = int(math.floor((angle % (2 * math.pi)) / (2 * math.pi / teeth)))
    return side, (tooth - program.front_tooth(teeth)) % teeth, normal


def side_mesh(name: str) -> pv.PolyData:
    """The pleated side surface built from the plan outline of the ring. On faces a motif
    crosses, the face is split along the exact outline of the motif, so every triangle carries
    one paint and the edges are smooth curves (only the pleats slice them). Cell data
    'paint_id' indexes PAINTS."""
    import profiles

    drum = program.drum_by_name(name)
    tip, height = fountain.drum_diameter(drum) / 2, fountain.drum_height(drum)
    teeth = program.teeth_of(name)
    outline = np.array(profiles.ridged_sawtooth_points(tip, teeth, cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH))
    z0 = fountain.stack_heights()[name]
    ids = {paint.name: number for number, paint in enumerate(cfg.PAINTS)}
    table = program.face_table(name)
    points, faces, paint_ids = [], [], []
    for p, q in zip(outline, np.roll(outline, -1, axis=0)):
        side, k, normal = edge_side(p, q, teeth)
        u0, u1 = face_coordinate(name, p, side, k), face_coordinate(name, q, side, k)
        for piece, ink in strip_pieces(program.face_regions(name, side, k), u0, u1, height, table[side][k]):
            for tri in triangles_of(piece):
                corners = []
                for u, z in tri:
                    t = 0.5 if abs(u1 - u0) < 1e-12 else (u - u0) / (u1 - u0)
                    xy = p + (q - p) * t
                    corners.append((xy[0], xy[1], z0 + z))
                a, b, c = (np.array(v) for v in corners)
                if np.cross(b - a, c - a)[:2] @ normal < 0:  # keep the triangle facing outward
                    corners = [corners[0], corners[2], corners[1]]
                base = len(points)
                points += corners
                faces.append((3, base, base + 1, base + 2))
                paint_ids.append(ids[ink])
    mesh = pv.PolyData(np.array(points), np.array(faces).ravel())
    mesh.cell_data["paint_id"] = np.array(paint_ids)
    return mesh


def paintable_mesh(name: str, mesh: pv.PolyData) -> pv.PolyData:
    """The mesh with its pleated side rebuilt so the motif edges are exact (see side_mesh)."""
    if name not in cfg.RING_PAINT or not program.has_motifs(name):
        return mesh
    key = (name, mesh.n_cells)
    if key not in _SLICED:
        _, rest = split_pleated_side(name, mesh)
        rest = rest.triangulate()
        rest.cell_data["paint_id"] = np.full(rest.n_cells, -1)
        _SLICED[key] = side_mesh(name).merge(rest, merge_points=False)
    return _SLICED[key]


def paintable_coupon(mesh: pv.PolyData, spec=None) -> pv.PolyData:
    """The coupon (placed as in R3) with its pleat faces rebuilt like R3's (exact motif edges)."""
    import coupon

    name = cfg.DRUMS[cfg.CANDLE_DRUM_INDEX].name
    _, rest = split_pleated_side(name, mesh)
    rest = rest.triangulate()
    rest.cell_data["paint_id"] = np.full(rest.n_cells, -1)
    side = side_mesh(name)
    centers = side.cell_centers().points
    angle = (np.degrees(np.arctan2(centers[:, 1], centers[:, 0])) + 90.0 + 180.0) % 360.0 - 180.0
    lo, hi = coupon.coupon_range(spec or coupon.MAIN)
    side = side.extract_cells(np.flatnonzero((angle > lo) & (angle < hi))).extract_surface(algorithm="dataset_surface")
    return side.merge(rest, merge_points=False)


def paint_relief(name: str, paints: np.ndarray, centers: np.ndarray, stored: np.ndarray) -> None:
    """Guide-relief cells (standing off the pleat faces) take the paint of the spot they sit on:
    the motif colour inside a motif, the ground outside."""
    import profiles
    from shapely.geometry import Point

    drum = program.drum_by_name(name)
    tip = fountain.drum_diameter(drum) / 2
    root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    z0 = fountain.stack_heights()[name]
    radius = np.hypot(centers[:, 0], centers[:, 1])
    candidates = np.flatnonzero((stored < 0) & (radius > root - 1.0) & (centers[:, 2] < z0 + fountain.drum_height(drum) + 0.01))
    if not len(candidates):
        return
    teeth = program.teeth_of(name)
    outline = np.array(profiles.ridged_sawtooth_points(tip, teeth, cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH))
    starts, ends = outline, np.roll(outline, -1, axis=0)
    for index in candidates:
        point = centers[index, :2]
        d = ends - starts
        t = np.clip(np.einsum("ij,ij->i", point - starts, d) / np.einsum("ij,ij->i", d, d), 0, 1)
        nearest = int(np.argmin(np.linalg.norm(starts + t[:, None] * d - point, axis=1)))
        if np.linalg.norm(starts[nearest] + t[nearest] * d[nearest] - point) < 0.05:
            continue  # on the plain surface: already painted
        side, k, _ = edge_side(starts[nearest], ends[nearest], teeth)
        u = face_coordinate(name, point, side, k)
        spot = Point(u, centers[index, 2] - z0)
        paints[index] = program.face_table(name)[side][k]
        for region, ink in program.face_regions(name, side, k):
            if region.buffer(1e-3).contains(spot):
                paints[index] = ink


def cell_paints(name: str, mesh: pv.PolyData) -> np.ndarray:
    """Paint names (numpy object array), one per cell; 'bare' (white PETG) where nothing is painted."""
    normals, centers = cell_geometry(mesh)
    if name in cfg.RING_PAINT:
        paints = ring_paints(name, normals, centers)
        if "paint_id" in mesh.cell_data:  # motif pieces built by side_mesh carry their own paint
            stored = np.asarray(mesh.cell_data["paint_id"])
            names = [paint.name for paint in cfg.PAINTS]
            for index in np.flatnonzero(stored >= 0):
                paints[index] = names[stored[index]]
            paint_relief(name, paints, centers, stored)
        return paints
    if name == "plinth_stem":
        return plinth_stem_paints(normals, centers)
    return np.full(len(centers), "bare", dtype=object)


def ring_paints(ring_name: str, normals: np.ndarray, centers: np.ndarray) -> np.ndarray:
    drum = program.drum_by_name(ring_name)
    tip = fountain.drum_diameter(drum) / 2
    root = tip - cfg.TOOTH_DEPTH_RATIO * cfg.TOOTH_PITCH
    z0 = fountain.stack_heights()[ring_name]
    top_z = z0 + fountain.drum_height(drum)
    radius = np.hypot(centers[:, 0], centers[:, 1])
    paints = side_paints(ring_name, normals, centers, z0)
    paints[radius > tip - 0.5] = "white"  # crest ridge tops stay white primer
    up = normals[:, 2] > TOP_NORMAL
    paints[up | (normals[:, 2] < -TOP_NORMAL)] = "bare"  # every top (and bottom) face stays white PETG
    paints[~up & (centers[:, 2] > top_z + 0.01)] = "bare"  # the paint lip along the top edge
    paints[(radius < root - 0.6) & (centers[:, 2] < top_z + 0.01)] = "bare"  # stud holes, spine hole
    return paints


def side_paints(ring_name: str, normals: np.ndarray, centers: np.ndarray, z0: float) -> np.ndarray:
    """Each triangle takes the ground paint of its face set and tooth (motifs come from side_mesh)."""
    del z0
    teeth = program.teeth_of(ring_name)
    angle = np.arctan2(centers[:, 1], centers[:, 0]) % (2 * math.pi)
    tooth = np.floor(angle / (2 * math.pi / teeth)).astype(int)
    k = (tooth - program.front_tooth(teeth)) % teeth
    tangent = np.stack([-np.sin(angle), np.cos(angle)], axis=1)
    is_right = np.einsum("ij,ij->i", normals[:, :2], tangent) > 0
    table = program.face_table(ring_name)
    paints = np.empty(len(centers), dtype=object)
    for index in range(len(centers)):
        paints[index] = table["right" if is_right[index] else "left"][k[index]]
    return paints


def plinth_stem_paints(normals: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Foot rim in PLINTH_PAINT, the goblet stem in STEM_PAINT; tops and hidden faces white PETG."""
    paints = np.full(len(centers), cfg.PLINTH_PAINT, dtype=object)
    radius = np.hypot(centers[:, 0], centers[:, 1])
    stem = centers[:, 2] > cfg.PLINTH_HEIGHT + fountain.base_z() + 0.05  # everything above the base is the goblet stem
    paints[stem] = cfg.STEM_PAINT
    paints[np.abs(normals[:, 2]) > TOP_NORMAL] = "bare"
    paints[radius < cfg.SPINE_DIAMETER / 2 + 1.0] = "bare"
    return paints
