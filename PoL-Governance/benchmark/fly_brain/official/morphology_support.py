"""Read and render an explicitly registered anatomical reference atlas.

JFRC2NP.surf.fw.zip is the JFRC2 neuropil atlas registered into FlyWire/FAFB14.1
nanometer coordinates, from fafbseg-data commit
b62bed6572afb98ac6e64e738b8805341e7ee027. It is a reference atlas, not an EM
surface reconstructed from the simulated specimen or from the model neurons.
No surface, vertex, triangle, or missing anatomy is synthesized by this module.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path, PurePosixPath
import zipfile

import numpy as np


ATLAS_SOURCE_COMMIT = "b62bed6572afb98ac6e64e738b8805341e7ee027"
ATLAS_DESCRIPTION = "JFRC2 neuropil reference atlas registered to FlyWire/FAFB14.1; not specimen-specific EM anatomy"


def _parse_ply(raw: bytes, name: str) -> dict:
    stream = io.BytesIO(raw)
    header = []
    for _ in range(100):
        line = stream.readline()
        if not line:
            raise ValueError(f"{name}: missing end_header")
        text = line.decode("ascii").strip()
        header.append(text)
        if text == "end_header":
            break
    else:
        raise ValueError(f"{name}: unexpectedly long PLY header")
    if header[:2] != ["ply", "format binary_little_endian 1.0"]:
        raise ValueError(f"{name}: expected binary little-endian PLY 1.0")
    structural = [line for line in header[2:-1] if not line.startswith(("comment ", "obj_info "))]
    if len(structural) != 6 or not structural[0].startswith("element vertex "):
        raise ValueError(f"{name}: unexpected PLY element/property schema")
    if structural[1:4] != ["property float x", "property float y", "property float z"]:
        raise ValueError(f"{name}: expected float32 x/y/z vertices")
    if not structural[4].startswith("element face ") or structural[5] != "property list int int vertex_indices":
        raise ValueError(f"{name}: expected int32 list count and int32 face indices")
    n_vertices = int(structural[0].split()[-1])
    n_faces = int(structural[4].split()[-1])
    if min(n_vertices, n_faces) <= 0:
        raise ValueError(f"{name}: empty atlas surface")
    offset = stream.tell()
    vertex_bytes = n_vertices * 3 * 4
    face_bytes = n_faces * 4 * 4  # int32 count followed by three int32 indices
    if len(raw) != offset + vertex_bytes + face_bytes:
        raise ValueError(f"{name}: payload size does not match declared triangular mesh")
    vertices = np.frombuffer(raw, dtype="<f4", count=n_vertices * 3, offset=offset).reshape(n_vertices, 3)
    records = np.frombuffer(raw, dtype="<i4", count=n_faces * 4,
                            offset=offset + vertex_bytes).reshape(n_faces, 4)
    if not np.all(records[:, 0] == 3):
        raise ValueError(f"{name}: non-triangular PLY faces are not supported")
    faces = records[:, 1:]
    if not np.isfinite(vertices).all() or faces.min() < 0 or faces.max() >= n_vertices:
        raise ValueError(f"{name}: invalid coordinates or face indices")
    return {"name": name, "vertices_nm": vertices.astype(np.float64), "faces": faces.copy()}


def load_atlas(path: str | Path) -> list[dict]:
    """Load all real PLY surfaces; return names, original nm vertices and faces.

    The official archive uses an int32 list count (not the usual uchar count).
    Resource-fork entries under __MACOSX are ignored; nothing is extracted.
    """
    meshes = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist()
                       if name.lower().endswith(".ply")
                       and "__MACOSX" not in PurePosixPath(name).parts
                       and not PurePosixPath(name).name.startswith("._"))
        if not names:
            raise ValueError("No actual PLY meshes in the supplied atlas archive")
        for name in names:
            meshes.append(_parse_ply(archive.read(name), name))
    return meshes


def draw_atlas(ax, atlas: list[dict], matrix3x3) -> list:
    """Draw all measured atlas triangles beneath neurites in camera XY.

    Geometry is transformed as vertices_nm / 1000 @ matrix.T. All triangles
    from all regions are sorted together by camera Z (small/far first), then
    drawn opaque with subtle, flat normal-based illumination. Rasterization
    affects only the atlas export layer; it does not simplify its geometry.
    """
    from matplotlib.collections import PolyCollection
    matrix = np.asarray(matrix3x3, dtype=float)
    if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
        raise ValueError("A finite 3 by 3 camera matrix is required")
    if not np.allclose(matrix @ matrix.T, np.eye(3), atol=1e-8, rtol=0):
        raise ValueError("Camera transform must preserve Euclidean distances")
    if not atlas:
        raise ValueError("Cannot draw an empty atlas")
    triangles = np.concatenate([
        (mesh["vertices_nm"] / 1000.0 @ matrix.T)[mesh["faces"]]
        for mesh in atlas
    ])
    depths = triangles[:, :, 2].mean(axis=1)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals = np.divide(normals, lengths[:, None], out=np.zeros_like(normals), where=lengths[:, None] > 0)
    light = np.array([-.35, .45, .82])
    light /= np.linalg.norm(light)
    illumination = .12 + .88 * np.abs(normals @ light)
    light_rgb = np.array([238, 241, 244], dtype=float) / 255.0  # #EEF1F4
    shadow_rgb = np.array([205, 213, 222], dtype=float) / 255.0  # #CDD5DE
    colors = shadow_rgb + illumination[:, None] * (light_rgb - shadow_rgb)
    order = np.argsort(depths, kind="stable")
    artist = PolyCollection(triangles[order, :, :2], facecolors=colors[order],
                            edgecolors="none", linewidths=0, antialiased=False,
                            alpha=1.0, rasterized=True, zorder=-10)
    ax.add_collection(artist, autolim=True)
    # This remains inspectable by the parent renderer without changing its API.
    artist.atlas_validation = {
        "description": ATLAS_DESCRIPTION,
        "source_commit": ATLAS_SOURCE_COMMIT,
        "surface_count": len(atlas),
        "vertex_count": int(sum(len(mesh["vertices_nm"]) for mesh in atlas)),
        "triangle_count": int(len(triangles)),
        "degenerate_triangle_count": int((lengths == 0).sum()),
        "imputed_vertex_count": 0,
        "imputed_face_count": 0,
        "coordinate_input_units": "nm",
        "coordinate_display_units": "µm",
        "camera_matrix": matrix.tolist(),
        "camera_xy_bounds_um": [triangles[:, :, :2].min(axis=(0, 1)).tolist(),
                                triangles[:, :, :2].max(axis=(0, 1)).tolist()],
        "global_depth_order": "ascending mean camera Z; all regions sorted together",
        "geometry_simplification": "none",
        "appearance": "opaque pale gray, flat normal-based illumination; no mesh edges",
    }
    return [artist]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figure_style import MM, apply_style
    apply_style()
    atlas = load_atlas(args.atlas)
    fig, ax = plt.subplots(figsize=(183 * MM, 100 * MM))
    artists = draw_atlas(ax, atlas, np.diag([1.0, -1.0, -1.0]))
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.subplots_adjust(left=.02, right=.98, top=.98, bottom=.02)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300)
    plt.close(fig)
    print(json.dumps(artists[0].atlas_validation, indent=2))


if __name__ == "__main__":
    main()
