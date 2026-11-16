"""Synthetic cue-memory interventions on a FlyVis-template reservoir, not FlyVis.

All dynamics, cue encodings, readouts and permissions are artificial. No
biological or whole-brain interpretation is supported by this experiment.
"""
from __future__ import annotations

import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ASSET_SHA = "bfbb0766251ff09e22723d0ebbf7b14793e70b3ae8ad0eea64eac9d28223351a"
ARMS = ("output_gate", "full_reset", "selective", "orthogonal", "random_matched")
DELAYS = (0, 2, 4, 8, 16)
NOISE = 0.002
RIDGE = 0.01


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_graph():
    path = HERE / "third_party/flyvis/fib25-fib19_v2.2.json"
    assert digest(path) == ASSET_SHA
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [n["name"] for n in data["nodes"]]
    index = {n: i for i, n in enumerate(names)}
    matrix = np.zeros((len(names), len(names)))
    for edge in data["edges"]:
        matrix[index[edge["tar"]], index[edge["src"]]] = (
            edge["alpha"] * sum(float(v) for _, v in edge["offsets"]))
    return matrix, [index[n] for n in data["input_units"]]


def signed_degrees(matrix):
    return np.stack([(matrix > 0).sum(0), (matrix > 0).sum(1),
                     (matrix < 0).sum(0), (matrix < 0).sum(1)])


def topology(original, kind, rng):
    """Rewire nonloops by same-sign directed double swaps; fix all loops.

    Edge weights travel with their source edge; signed degrees and loops are
    exact invariants, weighted degrees are NOT. All graphs are row normalized.
    """
    matrix = original.copy()
    accepted = 0
    if kind == "degree_rewired":
        before = signed_degrees(matrix)
        rows, cols = np.nonzero(matrix)
        edges = [(int(r), int(c)) for r, c in zip(rows, cols) if r != c]
        for _ in range(20000):
            i, j = rng.choice(len(edges), 2, replace=False)
            a, b = edges[i]
            c, d = edges[j]
            if a == c or b == d or a == d or c == b:
                continue
            if np.sign(matrix[a, b]) != np.sign(matrix[c, d]):
                continue
            if matrix[a, d] or matrix[c, b]:
                continue
            u, v = matrix[a, b], matrix[c, d]
            matrix[a, b] = matrix[c, d] = 0
            matrix[a, d], matrix[c, b] = v, u
            edges[i], edges[j] = (a, d), (c, b)
            accepted += 1
        assert np.array_equal(before, signed_degrees(matrix))
        assert np.array_equal(np.diag(matrix), np.diag(original))
        assert accepted > 500
    elif kind == "random_sparse":
        # Same node/edge/sign counts and EXACT original self-loops, not degrees.
        matrix[:] = 0
        np.fill_diagonal(matrix, np.diag(original))
        positions = np.argwhere(~np.eye(len(matrix), dtype=bool))
        positions = positions[rng.permutation(len(positions))]
        weights = original[~np.eye(len(matrix), dtype=bool)]
        weights = weights[weights != 0]
        rng.shuffle(weights)
        for (r, c), w in zip(positions, weights):
            matrix[r, c] = w
    elif kind != "flyvis_template":
        raise ValueError(kind)
    matrix /= np.maximum(np.abs(matrix).sum(1, keepdims=True), 1e-30)
    assert np.max(np.abs(matrix).sum(1)) <= 1 + 1e-12
    return matrix, accepted


def step(h, stimulus, weights, encoding):
    return 0.6 * h + 0.4 * np.tanh(0.85 * (h @ weights.T) + stimulus @ encoding.T)


def prime(cues, duration, weights, encoding):
    h = np.zeros((len(cues), len(weights)))
    for t in range(12):
        updated = step(h, cues, weights, encoding)
        h = np.where((t < duration)[:, None], updated, h)
    return h


def sample(rng, n, weights, encoding):
    cues = rng.uniform(0.3, 1.0, (n, 2)) * rng.choice([-1, 1], (n, 2))
    duration = rng.choice([8, 12], n)
    return cues, duration, prime(cues, duration, weights, encoding)


def fit(x, y):
    mean, scale = x.mean(0), np.maximum(x.std(0), NOISE)
    z = (x - mean) / scale
    center = y.mean(0)
    coef = np.linalg.solve(z.T @ z / len(z) + RIDGE * np.eye(x.shape[1]),
                           z.T @ (y - center) / len(z))
    return mean, scale, center, coef


def predict(model, x):
    mean, scale, center, coef = model
    return (x - mean) / scale @ coef + center


def r2(y, estimate):
    return float(1 - np.mean((y - estimate) ** 2) / np.var(y))


def directions(rng, weights, encoding):
    """Rank-one causal contrasts; no decoder weights or evaluation episodes."""
    nuisance = rng.uniform(-1, 1, 96)
    durations = rng.choice([8, 12], len(nuisance))
    ds = []
    for axis in (0, 1):
        plus = np.zeros((len(nuisance), 2))
        plus[:, axis] = 0.8
        plus[:, 1-axis] = nuisance
        minus = plus.copy()
        minus[:, axis] = -0.8
        ds.append((prime(plus, durations, weights, encoding)
                   - prime(minus, durations, weights, encoding)).mean(0) / 1.6)
    a, b = ds
    perpendicular = a - b * (a @ b) / max(b @ b, 1e-30)
    denom = perpendicular @ a
    if denom < 1e-12:
        raise ValueError("Calibration cue subspaces inseparable; premise failed")
    return a, b, perpendicular / denom


def intervene(h, arm, a, dual, random_unit):
    selective_delta = (h @ dual)[:, None] * a
    if arm == "output_gate":
        return h.copy()
    if arm == "full_reset":
        return np.zeros_like(h)
    if arm == "selective":
        return h - selective_delta
    if arm == "orthogonal":
        return h - (h @ a / (a @ a))[:, None] * a
    if arm == "random_matched":
        return h - np.linalg.norm(selective_delta, axis=1, keepdims=True) * random_unit
    raise ValueError(arm)


def run_model(original, input_indices, kind, seed, split, n_eval):
    # Independent streams; split only changes evaluation data, not fitted model.
    sequence = np.random.SeedSequence(seed).spawn(7)
    rg, re, rt, rc, rp, rd, rv = [np.random.default_rng(s) for s in sequence]
    weights, swaps = topology(original, kind, rg)
    encoding = np.zeros((len(weights), 2))
    basis = re.normal(size=(len(input_indices), 2))
    basis /= np.linalg.norm(basis, axis=0)
    encoding[input_indices] = basis * 1.5
    train, _, train_h = sample(rt, 384, weights, encoding)
    decoder = fit(train_h + rt.normal(0, NOISE, train_h.shape), train)
    a, b, dual = directions(rc, weights, encoding)
    probe_labels, _, probe_h = sample(rp, 256, weights, encoding)
    erng = rd if split == "dev" else rv
    labels, durations, h = sample(erng, n_eval, weights, encoding)
    new_a = erng.uniform(-1, 1, n_eval)
    random_unit = erng.normal(size=h.shape)
    random_unit /= np.linalg.norm(random_unit, axis=1, keepdims=True)
    probe_random = rp.normal(size=probe_h.shape)
    probe_random /= np.linalg.norm(probe_random, axis=1, keepdims=True)
    common_noise = {d: erng.normal(0, NOISE, h.shape) for d in DELAYS}
    probe_noise = {d: rp.normal(0, NOISE, probe_h.shape) for d in DELAYS}
    reauthorization_noise = erng.normal(0, NOISE, h.shape)
    # Critic fits on separate calibration-probe episodes AFTER each intervention.
    # It tests remaining decodability, not the frozen action head alone.
    rows = []
    snapshots = {}
    for arm in ARMS:
        z = intervene(h, arm, a, dual, random_unit)
        p = intervene(probe_h, arm, a, dual, probe_random)
        delta = float(np.mean(np.linalg.norm(z-h, axis=1)))
        for delay in range(max(DELAYS)+1):
            if delay in DELAYS:
                observed = z + common_noise[delay]
                decoded = predict(decoder, observed)
                critic = fit(p + probe_noise[delay], probe_labels)
                critic_pred = predict(critic, observed)
                rows.append({"seed": seed, "topology": kind, "arm": arm,
                    "delay": delay, "n_episodes": n_eval,
                    "a_raw_abs": float(np.abs(decoded[:, 0]).mean()),
                    "a_valid_sham_mse": float(np.mean((decoded[:, 0]-labels[:, 0])**2)),
                    "b_mse": float(np.mean((decoded[:, 1]-labels[:, 1])**2)),
                    "a_probe_r2": r2(labels[:, 0], critic_pred[:, 0]),
                    "b_probe_r2": r2(labels[:, 1], critic_pred[:, 1]),
                    "state_change_l2": delta})
            if delay == 8:
                snapshots[arm] = z.copy()
            z = step(z, np.zeros((n_eval, 2)), weights, encoding)
            p = step(p, np.zeros((len(p), 2)), weights, encoding)
        # Everyone receives the SAME NEW permitted A cue, independent of old A.
        z = snapshots[arm]
        cue = np.column_stack((new_a, np.zeros(n_eval)))
        for _ in range(8):
            z = step(z, cue, weights, encoding)
        decoded = predict(decoder, z + reauthorization_noise)
        for row in rows[-len(DELAYS):]:
            row["reauthorization_a_mse"] = float(np.mean((decoded[:, 0]-new_a)**2))
    meta = {"seed": seed, "topology": kind, "accepted_swaps": swaps,
            "a_b_calibration_cosine": float(a @ b / (np.linalg.norm(a)*np.linalg.norm(b))),
            "initial_gate_a_r2": next(r["a_probe_r2"] for r in rows if r["arm"] == "output_gate" and r["delay"] == 0),
            "initial_gate_b_r2": next(r["b_probe_r2"] for r in rows if r["arm"] == "output_gate" and r["delay"] == 0)}
    premise = [r for r in rows if r["arm"] == "output_gate" and r["delay"] in (0, 8)]
    meta["memory_premise_r2_threshold"] = 0.5
    meta["memory_premise_at_0_and_8"] = all(
        r["a_probe_r2"] >= 0.5 and r["b_probe_r2"] >= 0.5 for r in premise)
    meta["delay_8_gate_probe_r2"] = {axis: next(r[f"{axis}_probe_r2"] for r in premise if r["delay"] == 8)
                                     for axis in ("a", "b")}
    return rows, meta


def summarize(rows):
    summaries = []
    for kind in ("flyvis_template", "degree_rewired", "random_sparse"):
        for arm in ARMS:
            for delay in DELAYS:
                group = [r for r in rows if (r["topology"], r["arm"], r["delay"]) == (kind, arm, delay)]
                item = {"topology": kind, "arm": arm, "delay": delay, "n_seeds": len(group)}
                for metric in ("a_raw_abs", "a_valid_sham_mse", "b_mse", "a_probe_r2", "b_probe_r2", "state_change_l2", "reauthorization_a_mse"):
                    vals = np.array([r[metric] for r in group])
                    item[metric] = {"mean": float(vals.mean()), "sd_between_seeds": float(vals.std(ddof=1)) if len(vals)>1 else None}
                summaries.append(item)
    return summaries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("dev", "eval"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output directory; historical runs are immutable")
    start = time.perf_counter()
    original, inputs = load_graph()
    seeds = range(101, 104) if args.split == "dev" else range(1001, 1013)
    rows, meta = [], []
    for seed in seeds:
        for kind in ("flyvis_template", "degree_rewired", "random_sparse"):
            r, m = run_model(original, inputs, kind, seed, args.split, 64 if args.split == "dev" else 128)
            rows.extend(r)
            meta.append(m)
    args.output.mkdir(parents=True)
    with (args.output / "per_seed.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    result = {"scope": "artificial target-cue memory; no learned permission or biological claims",
        "split": args.split, "public_evaluation": True, "script_sha256": digest(__file__),
        "asset_sha256": ASSET_SHA, "git_commit": commit,
        "config": {"leak": 0.4, "recurrent_gain": 0.85, "contraction_bound": 0.94,
            "observation_noise_sd": NOISE, "ridge": RIDGE, "rank": 1,
            "delays": DELAYS, "train_episodes": 384, "calibration_direction_pairs_per_axis": 96,
            "calibration_probe_episodes": 256, "seeds": list(seeds),
            "evaluation_episodes_per_seed_topology": 64 if args.split == "dev" else 128},
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.system(),
            "blas_threads_requested": os.environ.get("OPENBLAS_NUM_THREADS")},
        "elapsed_seconds": time.perf_counter()-start, "models": meta, "summary": summarize(rows),
        "limits": ["all target semantics and dynamics are synthetic", "row-normalized type aggregation discards space",
            "degree rewiring preserves signed degrees and self loops, not weighted degrees",
            "this script measures memory/readouts only; execution safety is tested in the separate interface experiment",
            "critic R2 diagnoses remaining linearly decodable cue information; not complete memory erasure",
            "SD is across model seeds, not a confidence interval; no significance claim"]}
    (args.output / "summary.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "models": len(meta), "rows": len(rows),
                      "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
