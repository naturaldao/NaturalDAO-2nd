"""Run the actual pinned, pretrained FlyVis network, with strict weight checks.

No cached response API is used. Model 000 is fixed before evaluation; all its
T4/T5 directions/polarities are retained, including failed expected contrasts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import zipfile

REVISION = "0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa"
ARCHIVE_SHA256 = "71c78d4070556a536b13b23ee3139cd2788aa2a9d07d430a223b4edead281db1"
TYPES = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, content):
    Path(path).write_text(json.dumps(content, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def verify_archive(archive, model_dir):
    assert archive.is_file() and sha(archive) == ARCHIVE_SHA256, "Official archive checksum mismatch"
    records = {}
    with zipfile.ZipFile(archive) as zipped:
        for relative in ("_meta.yaml", "best_chkpt", "chkpts/chkpt_00000"):
            path = model_dir / relative
            assert path.is_file(), f"Missing required checkpoint/config: {path}"
            payload = zipped.read("results/flow/0000/000/" + relative)
            expected = hashlib.sha256(payload).hexdigest()
            assert sha(path) == expected, f"Extracted file differs from archive: {relative}"
            records[relative] = expected
    return records


def windows_h5_compat():
    """Close HDF5 handles deterministically; upstream unlink-open-file fails on Windows."""
    if os.name != "nt":
        return "not needed"
    from importlib import import_module
    from tempfile import TemporaryDirectory
    import h5py
    import numpy as np
    def write_array(path, value):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(path, libver="latest", mode="w") as handle:
            handle.create_dataset("data", data=np.asarray(value))
            handle.swmr_mode = True
            assert handle.swmr_mode
    checks = []
    with TemporaryDirectory(prefix="flyvis-h5-compat-") as temporary:
        for index, array in enumerate((np.array([b"T4a", b"CT1(Lo1)"], dtype="S8"),
                np.array([[1, 2], [3, 4]], dtype=np.int64),
                np.array([0.25, -1.5], dtype=np.float32), np.array([True, False]))):
            path = Path(temporary) / f"array-{index}.h5"
            write_array(path, array)
            with h5py.File(path, mode="r", swmr=True) as handle:
                recovered = handle["data"][()]
            assert recovered.dtype == array.dtype and recovered.shape == array.shape
            assert np.array_equal(recovered, array), "HDF5 compatibility roundtrip changed values"
            checks.append({"dtype": str(array.dtype), "shape": list(array.shape), "equal": True})
    for module in ("datamate.io", "datamate.directory"):
        import_module(module)._write_h5 = write_array
    return {"description": "runtime HDF5 write/close shim for datamate 1.0.0; no model or weights changed",
            "conversion": "same np.asarray as upstream; native HDF5 dtype handling, no string/object coercion added",
            "roundtrip_checks": checks}


def run(args):
    started = time.perf_counter()
    model_dir = args.results_dir / "flow/0000/000"
    extracted = verify_archive(args.archive, model_dir)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.source, text=True).strip()
    assert commit == REVISION, "Unexpected FlyVis source revision"
    os.environ["FLYVIS_ROOT_DIR"] = str(args.results_dir.parent)
    # Import order avoids this Windows environment's Arrow/Torch DLL conflict.
    import pyarrow  # noqa: F401
    import torch
    import numpy as np
    import flyvis
    from flyvis.network import NetworkView
    compatibility = windows_h5_compat()
    flyvis.device = torch.device(args.device)
    torch.set_default_device(flyvis.device)
    torch.set_num_threads(4)
    view = NetworkView(model_dir)
    assert int(view.dir.config.network.connectome.extent) == 15, "Shrunken connectome rejected"
    checkpoint = Path(view.get_checkpoint("best"))
    assert checkpoint.is_file(), "No actual checkpoint selected; random fallback rejected"
    network = view.init_network("best").to(flyvis.device)
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)["network"]
    published = torch.load(model_dir / "best_chkpt", map_location="cpu", weights_only=False)["network"]
    actual = network.state_dict()
    assert set(saved) == set(actual) == set(published), "Checkpoint tensor-key mismatch"
    checked = {}
    for key in saved:
        assert torch.equal(saved[key].cpu(), actual[key].detach().cpu()), f"Unloaded tensor: {key}"
        assert torch.equal(saved[key].cpu(), published[key].cpu()), f"Nonpublished tensor: {key}"
        checked[key] = {"shape": list(saved[key].shape), "numel": saved[key].numel(), "equal": True}
    assert network.n_nodes == 45669 and network.n_edges > 1000000, "Incomplete connectome"
    counter = {"forward_calls": 0, "integrated_frames": 0}
    original_forward = network.forward
    def counted_forward(*forward_args, **kwargs):
        counter["forward_calls"] += 1
        counter["integrated_frames"] += int(forward_args[0].shape[1])
        return original_forward(*forward_args, **kwargs)
    network.forward = counted_forward
    node_types = network.connectome.nodes.type[:].astype(str)
    u, v = network.connectome.nodes.u[:], network.connectome.nodes.v[:]
    centers = network.connectome.central_cells_index[:]
    center_types = node_types[centers]
    movie = torch.full((1, 20, 1, 721), 0.5, device=flyvis.device)
    movie[:, 5:15] = 1.0
    with torch.inference_mode():
        activity = network.simulate(movie, dt=1/200, initial_state="auto")
    assert tuple(activity.shape) == (1, 20, 45669) and torch.isfinite(activity).all().item()
    delta = float((activity[:, -1] - activity[:, 0]).abs().max().item())
    assert delta > 1e-8 and counter["forward_calls"] >= 2, "No live response computation"
    sampled = activity[0, [0, 5, 10, 15, 19]].cpu().numpy()
    np.savez_compressed(args.output / "smoke_activity.npz", frames=np.array([0, 5, 10, 15, 19]),
                        full_space_activity=sampled, node_types=node_types, u=u, v=v,
                        center_activity=activity[0, :, centers].cpu().numpy())
    smoke = {"input_shape": list(movie.shape), "full_output_shape": list(activity.shape),
             "finite": True, "max_final_minus_initial": delta, **counter}
    del activity, movie, sampled
    manifest = {"scope": "Official pretrained FlyVis visual-system model; distinct from Eon whole-brain LIF simulation",
        "source_commit": commit, "python": platform.python_version(), "interpreter": sys.executable,
        "torch": torch.__version__, "numpy": np.__version__, "flyvis": flyvis.__version__,
        "device": str(flyvis.device), "archive_sha256": sha(args.archive), "archive_files": extracted,
        "checkpoint": checkpoint.name, "checkpoint_sha256": sha(checkpoint), "weights_exactly_loaded": checked,
        "connectome_extent": 15, "n_nodes": network.n_nodes, "n_edges": network.n_edges,
        "script_sha256": sha(__file__), "response_cache_used": False, "smoke": smoke,
        "windows_compatibility": compatibility,
        "selection": "Fixed flow/0000/000 before simulation; no model selection from response results",
        "upstream_license": "MIT; see LICENSE-FlyVis", "phase": args.phase}
    write_json(args.output / "manifest.json", manifest)
    print(json.dumps({"smoke": smoke, "n_nodes": network.n_nodes, "n_edges": network.n_edges}), flush=True)
    if args.phase == "moving-edge":
        metrics = moving_edge(network, args.output, centers, center_types, node_types, u, v)
        manifest.update(final_forward_counter=counter, elapsed_seconds=time.perf_counter()-started)
        write_json(args.output / "metrics.json", metrics)
        write_json(args.output / "manifest.json", manifest)
    return manifest


def moving_edge(network, output, centers, center_types, node_types, u, v):
    import torch
    import numpy as np
    import xarray as xr
    from flyvis.datasets.moving_bar import MovingEdge
    from flyvis.analysis.moving_bar_responses import peak_responses, direction_selectivity_index, preferred_direction
    dataset = MovingEdge(offsets=[-10, 11], intensities=[0, 1], speeds=[19], height=80,
        post_pad_mode="continue", t_pre=1.0, t_post=1.0, dt=1/200,
        angles=list(range(0, 360, 30)), device=str(next(network.parameters()).device))
    assert len(dataset) == 24
    center_records, spatial_records = [], []
    for index, params in dataset.arg_df.iterrows():
        stimulus = dataset[int(index)][None, :, None, :]
        with torch.inference_mode():
            activity = network.simulate(stimulus, dt=dataset.dt, initial_state="auto")
        assert activity.shape[0] == 1 and activity.shape[-1] == 45669
        assert torch.isfinite(activity).all().item(), f"Nonfinite response in stimulus {index}"
        center_records.append(activity[0, :, centers].cpu().numpy())
        if params["intensity"] == 1 and params["angle"] in (90, 270):
            # Fixed stimulus midpoint, selected before seeing response maxima.
            frame = int((dataset.t_pre + float(params["t_stim"])/2) / dataset.dt)
            mask = node_types == "T4c"
            spatial_records.append({"angle": int(params["angle"]), "frame": frame,
                "activity": activity[0, frame, mask].cpu().numpy(), "u": u[mask], "v": v[mask]})
        print(f"moving-edge {index+1}/24 angle={params['angle']} intensity={params['intensity']}", flush=True)
        del activity, stimulus
    traces = np.stack(center_records)
    times = np.arange(traces.shape[1]) * dataset.dt - dataset.t_pre
    coords = {"network_id": [0], "sample": np.arange(24), "frame": np.arange(len(times)),
              "time": ("frame", times), "neuron": centers, "cell_type": ("neuron", center_types),
              **{col: ("sample", dataset.arg_df[col].values) for col in dataset.arg_df.columns}}
    responses = xr.Dataset({"responses": (["network_id", "sample", "frame", "neuron"], traces[None])},
                           coords=coords, attrs={"config": dataset.config.to_dict()})
    peak = peak_responses(responses)
    dsi = direction_selectivity_index(responses)
    direction = preferred_direction(responses)
    metrics = {"stimulus_count": 24, "dt": dataset.dt, "batch_size": 1,
               "full_network_simulated_each_time": True, "all_center_types": center_types.tolist(),
               "official_peak_responses": peak.squeeze("network_id").values.tolist(),
               "peak_axes": ["sample", "center_neuron"],
               "stimulus_table": dataset.arg_df.to_dict(orient="records"), "tuning": []}
    for cell in TYPES:
        ni = int(np.flatnonzero(center_types == cell)[0])
        for polarity in (0, 1):
            metrics["tuning"].append({"cell_type": cell, "intensity": polarity,
                "dsi": float(dsi.sel(neuron=centers[ni], intensity=polarity)),
                "preferred_direction_deg": float(np.degrees(direction.sel(neuron=centers[ni], intensity=polarity))) % 360})
    ci = int(np.flatnonzero(center_types == "T4c")[0])
    def on_peak(angle):
        sample = int(dataset.arg_df.query(f"angle == {angle} and intensity == 1").index[0])
        return float(peak.isel(network_id=0, sample=sample, neuron=ci))
    a90, a270 = on_peak(90), on_peak(270)
    metrics["prespecified_T4c_ON_90_gt_270"] = {"peak_90": a90, "peak_270": a270, "observed": a90 > a270,
        "interpretation": "Reported whether true or false; no model or polarity selected after seeing results"}
    np.savez_compressed(output / "moving_edge_activity.npz", centers=centers, center_types=center_types,
        center_responses=traces, time=times, params=dataset.arg_df.values,
        spatial_angles=np.array([r["angle"] for r in spatial_records]),
        spatial_activity=np.stack([r["activity"] for r in spatial_records]),
        spatial_u=spatial_records[0]["u"], spatial_v=spatial_records[0]["v"])
    make_plots(output, traces, times, dataset.arg_df, center_types, spatial_records)
    return metrics


def make_plots(output, traces, times, params, types, spatial):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(2, 4, figsize=(13, 6), sharex=True)
    for ax, cell in zip(axes.flat, TYPES):
        index = int(np.flatnonzero(types == cell)[0])
        polarity = 1 if cell.startswith("T4") else 0
        for angle in (0, 90, 180, 270):
            sample = int(params.query(f"angle == {angle} and intensity == {polarity}").index[0])
            ax.plot(times, traces[sample, :, index], label=f"{angle} deg")
        ax.set_title(f"{cell} {'ON' if polarity else 'OFF'}")
        ax.axvline(0, color="grey", lw=.7)
        ax.set_xlabel("Time since edge onset (s)")
        ax.set_ylabel("Official model voltage")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Official pretrained FlyVis flow/0000/000 | central T4/T5 responses (not Eon whole brain)")
    fig.tight_layout()
    fig.savefig(output / "t4_t5_center_responses.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharex=True, sharey=True)
    lower = min(float(r["activity"].min()) for r in spatial)
    upper = max(float(r["activity"].max()) for r in spatial)
    for ax, record in zip(axes, spatial):
        x = record["u"] + record["v"]/2
        y = np.sqrt(3)/2 * record["v"]
        scatter = ax.scatter(x, y, c=record["activity"], vmin=lower, vmax=upper, s=25, marker="h")
        ax.set_aspect("equal")
        ax.set_title(f"T4c ON {record['angle']} deg | fixed frame {record['frame']}")
    fig.colorbar(scatter, ax=axes, label="Official model voltage", shrink=.8)
    fig.suptitle("Official pretrained FlyVis spatial activity | full extent 15 (not Eon whole brain)")
    fig.savefig(output / "t4c_spatial_activity.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--phase", choices=("smoke", "moving-edge"), default="smoke")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output directory; runs are never overwritten")
    args.output.mkdir(parents=True)
    try:
        run(args)
    except Exception:
        write_json(args.output / "failure.json", {"traceback": traceback.format_exc(), "script_sha256": sha(__file__)})
        raise


if __name__ == "__main__":
    main()
