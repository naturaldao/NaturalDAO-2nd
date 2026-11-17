"""Fetch a documented subset of real FlyWire v783 neurite skeletons.

Only public static downloads are used. The binary decoder follows the
Neuroglancer precomputed skeleton format; no navis/CAVE credentials are needed.
Coordinates stay in native FlyWire/FAFB14.1 nanometres. No neuron is synthesized.
"""
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import threading
import time
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_URL = "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/flywire_skeletons_783"
MN9 = ("720575940660219265", "720575940618238523")
IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_ids(series, label):
    if pd.api.types.is_float_dtype(series.dtype):
        raise ValueError(f"{label} contains floating-point root IDs")
    ids = series.astype("string")
    if ids.isna().any() or not ids.str.fullmatch(r"[0-9]+").all():
        raise ValueError(f"{label} must contain exact decimal root IDs")
    return ids


def decode_skeleton(raw):
    """Return exact source vertices, undirected edges and radius, without repair."""
    if len(raw) < 8:
        raise ValueError("Truncated precomputed skeleton")
    n_vertices, n_edges = struct.unpack_from("<II", raw)
    if not n_vertices or len(raw) != 8 + 16*n_vertices + 8*n_edges:
        raise ValueError("Invalid skeleton byte count or unexpected attributes")
    vertices = np.frombuffer(raw, "<f4", n_vertices*3, 8).reshape(n_vertices, 3).copy()
    edges = np.frombuffer(raw, "<u4", n_edges*2, 8+12*n_vertices).reshape(n_edges, 2).copy()
    radius = np.frombuffer(raw, "<f4", n_vertices, 8+12*n_vertices+8*n_edges).copy()
    if not np.isfinite(vertices).all() or not np.isfinite(radius).all() or (radius < 0).any():
        raise ValueError("Nonfinite positions or invalid radius")
    if n_edges and (edges.max() >= n_vertices or np.any(edges[:, 0] == edges[:, 1])):
        raise ValueError("Skeleton edge references invalid vertices")
    return vertices, edges, radius


def validate_info(info):
    attributes = info["vertex_attributes"]
    if isinstance(attributes, dict):
        attributes = [attributes]
    expected = [{"id": "radius", "data_type": "float32", "num_components": 1}]
    if (info.get("@type") != "neuroglancer_skeletons" or
            info.get("transform") != IDENTITY or attributes != expected):
        raise ValueError("Remote metadata changed; inspect coordinate/attribute schema")


def request_bytes(url, attempts=3):
    error = None
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "PoL2-FlyWire-morphology/1.0",
                                        "Accept-Encoding": "identity"})
            with urlopen(req, timeout=45) as response:
                # Public neurons are small; refuse an unexpected oversized response.
                raw = response.read(32*1024*1024 + 1)
                if len(raw) > 32*1024*1024:
                    raise ValueError("Single skeleton exceeded 32 MiB")
                return raw
        except Exception as exc:
            error = exc
            if attempt+1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Download failed after {attempts} attempts: {url}: {error}")


def select_roots(eon_root, coordinates, spikes_path, count, seed):
    completeness = eon_root / "data/2025_Completeness_783.csv"
    column = pd.read_csv(completeness, nrows=0).columns[0]
    population = pd.read_csv(completeness, dtype={column: "string"})
    model_ids = exact_ids(population[column], "model IDs").tolist()
    if len(model_ids) != len(set(model_ids)):
        raise ValueError("Duplicate official model IDs")
    spikes = pd.read_parquet(spikes_path, columns=["flywire_id"])
    active = sorted(set(exact_ids(spikes["flywire_id"], "spike IDs")))
    if not set(active).issubset(model_ids):
        raise ValueError("Spike neuron absent from official modeled population")
    benchmark_path = eon_root/"code/benchmark.py"
    tree = ast.parse(benchmark_path.read_text(encoding="utf-8"))
    definitions = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "EXPERIMENTS"
                           for target in node.targets)]
    if len(definitions) != 1:
        raise ValueError("Cannot identify official literal experiment definitions")
    experiments = ast.literal_eval(definitions[0].value)
    input_roots = [str(rid) for rid in experiments["sugar"]["neu_exc"]]
    if len(input_roots) != 21 or not set(input_roots).issubset(model_ids):
        raise ValueError("Official sugar GRN set changed or is outside modeled population")
    locations = pd.read_csv(coordinates, dtype={"root_id": "string"}, usecols=["root_id", "position"])
    locations["root_id"] = exact_ids(locations["root_id"], "anchor IDs")
    locations = locations.drop_duplicates("root_id", keep="first")
    locations = locations[locations.root_id.isin(set(model_ids)-set(active))].copy()
    xyz = np.stack([np.fromstring(v.strip("[]"), sep=" ") for v in locations.position])
    if xyz.shape[1] != 3 or not np.isfinite(xyz).all():
        raise ValueError("Invalid source anchor coordinates")
    # One candidate from each occupied 3D grid cell before cycling to second
    # candidates. Selection describes display coverage, not a density estimate.
    unit = (xyz-xyz.min(0))/np.maximum(np.ptp(xyz, axis=0), 1)
    bins = np.minimum((unit*np.array([12, 8, 6])).astype(int), [11, 7, 5])
    keys = np.ravel_multi_index(bins.T, (12, 8, 6))
    rng = np.random.default_rng(seed)
    groups = {}
    for key in rng.permutation(np.unique(keys)):
        members = locations.root_id.iloc[np.flatnonzero(keys == key)].to_numpy()
        groups[int(key)] = list(rng.permutation(members))
    background = []
    depth = 0
    while len(background) < min(count, len(locations)):
        for members in groups.values():
            if depth < len(members):
                background.append(str(members[depth]))
                if len(background) == count:
                    break
        depth += 1
    selection = {"modeled_population": len(model_ids), "active_roots": active,
                 "background_roots": background, "background_seed": seed,
                 "active_root_ids": active, "context_root_ids": background,
                 "input_root_ids": input_roots,
                 "background_policy": "inactive model IDs; first original anchor; 12x8x6 spatial grid, seeded cell order and within-cell order, round-robin depth; display subset, not a density estimate",
                 "required_MN9": list(MN9)}
    return sorted(set(active+background+input_roots+list(MN9))), selection


class CacheBudget:
    def __init__(self, directory, max_bytes):
        self.maximum = max_bytes
        self.used = sum(p.stat().st_size for p in directory.glob("*") if p.is_file())
        self.lock = threading.Lock()

    def write(self, path, raw):
        with self.lock:
            previous = path.stat().st_size if path.exists() else 0
            proposed = self.used + len(raw)-previous
            if proposed > self.maximum:
                raise RuntimeError("Morphology cache disk budget exceeded")
            temporary = path.with_suffix(path.suffix+".partial")
            temporary.write_bytes(raw)
            temporary.replace(path)
            self.used = proposed


def download_one(rid, directory, budget):
    if not re.fullmatch(r"[0-9]+", rid):
        raise ValueError("Invalid exact decimal root ID")
    raw_path = directory/f"{rid}.precomputed"
    from_cache = raw_path.exists()
    raw = raw_path.read_bytes() if from_cache else request_bytes(f"{BASE_URL}/{rid}")
    vertices, edges, radius = decode_skeleton(raw)
    if not from_cache:
        budget.write(raw_path, raw)
    output = directory/f"{rid}.npz"
    buffer = io.BytesIO()
    np.savez_compressed(buffer, vertices_nm=vertices, edges=edges, radius_nm=radius,
                        root_id=np.array(rid))
    budget.write(output, buffer.getvalue())
    return {"root_id": rid, "source_url": f"{BASE_URL}/{rid}",
            "raw_file": raw_path.name, "raw_bytes": len(raw), "raw_sha256": sha256(raw_path),
            "npz_file": output.name, "npz": output.name, "npz_sha256": sha256(output),
            "sha256": sha256(raw_path),
            "vertices": len(vertices), "edges": len(edges), "from_cache": from_cache,
            "bounds_nm": [vertices.min(0).tolist(), vertices.max(0).tolist()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eon-root", required=True, type=Path)
    parser.add_argument("--coordinates", required=True, type=Path)
    parser.add_argument("--spikes", type=Path, default=HERE/"results/eon-original-20261117/function-1s.parquet")
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--background-count", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--max-cache-mib", type=int, default=500)
    parser.add_argument("--root-id", nargs="+", help="Explicit exact IDs for a small smoke download; overrides normal selection")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if args.background_count < 0 or args.max_cache_mib <= 0:
        parser.error("Counts must be nonnegative and cache budget positive")
    roots, selection = select_roots(args.eon_root, args.coordinates, args.spikes,
                                    args.background_count, args.seed)
    if args.root_id:
        roots = sorted(set(args.root_id))
        if not all(re.fullmatch(r"[0-9]+", rid) for rid in roots):
            parser.error("Root IDs must be exact decimal strings")
        selection["explicit_smoke_override"] = roots
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    plan = {"roots": roots, "selection": selection,
            "source_files": {str(p.resolve()): sha256(p) for p in
                (args.eon_root/"data/2025_Completeness_783.csv", args.coordinates, args.spikes)},
            "input_definitions": {"path": str((args.eon_root/"code/benchmark.py").resolve()),
                                  "sha256": sha256(args.eon_root/"code/benchmark.py"),
                                  "selection": "AST literal EXPERIMENTS['sugar']['neu_exc']; no module import"},
            "downloader_sha256": sha256(__file__), "coordinate_units": "nanometres",
            "coordinate_space": "FlyWire / FAFB14.1; no coordinate transform or alignment fitted",
            "source_doc": "https://fafbseg-py.readthedocs.io/en/latest/_modules/fafbseg/flywire/skeletonize.html",
            "format_doc": "https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/skeletons.md",
            "public_archive": "https://zenodo.org/records/10877326",
            "terms": "Retain FlyWire public-data attribution and terms https://flywire.ai/guidelines . The Schlegel supplemental Zenodo skeleton archive is CC BY 4.0; this per-root Cambridge mirror has no license field in info.json, and byte identity to the archive has not been tested. No first-party relicensing."}
    plan_path = args.cache_dir/"selection.json"
    plan_path.write_text(json.dumps(plan, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"planned": len(roots), "active": len(selection["active_roots"]),
                      "background": len(selection["background_roots"]), "plan": str(plan_path)}), flush=True)
    if args.plan_only:
        return
    info_path = args.cache_dir/"info.json"
    if not info_path.exists():
        info_path.write_bytes(request_bytes(f"{BASE_URL}/info"))
    info = json.loads(info_path.read_text())
    validate_info(info)
    budget = CacheBudget(args.cache_dir, args.max_cache_mib*1024*1024)
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(download_one, rid, args.cache_dir, budget): rid for rid in roots}
        for future in as_completed(pending):
            rid = pending[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({"root_id": rid, "error": str(exc)})
            finished = len(results)+len(failures)
            if finished % 25 == 0 or finished == len(roots):
                print(json.dumps({"finished": finished, "total": len(roots),
                                  "success": len(results), "failed": len(failures)}), flush=True)
    manifest = {**plan, "status": "complete" if not failures else "incomplete",
                "info": info, "info_sha256": sha256(info_path),
                "workers": args.workers, "downloaded_roots": len(results),
                "total_vertices": sum(r["vertices"] for r in results),
                "total_edges": sum(r["edges"] for r in results),
                "cache_bytes": budget.used, "records": sorted(results, key=lambda r: r["root_id"]),
                "failures": failures}
    (args.cache_dir/"download-manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("status", "downloaded_roots", "total_vertices", "total_edges", "cache_bytes")}), flush=True)
    if failures:
        raise SystemExit("Some requested morphologies are missing; inspect download-manifest.json before rendering")


if __name__ == "__main__":
    main()
