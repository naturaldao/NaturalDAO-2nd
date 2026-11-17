"""Redraw two publication figures from saved official FlyVis responses only.

No model imports, response recomputation, normalization, smoothing, or fitted
curves are used. The original 24 x 485 x 65 traces remain unchanged. Peak QA
independently checks every saved peak with the upstream default rectification
and stimulus-window convention; the two spatial center values are also checked
against the corresponding unmodified temporal traces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from figure_style import (
    BLUE, GREEN, INK, MM, ORANGE, PURPLE,
    apply_style, panel_label, save_figure,
)
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CELLS = ("T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d")
ANGLES = (0, 90, 180, 270)
COLORS = (BLUE, ORANGE, GREEN, PURPLE)
LINESTYLES = ("solid", (0, (3, 1.4)), (0, (1, 1.2)), (0, (4, 1.2, 1, 1.2)))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_saved(results):
    with np.load(results / "moving_edge_activity.npz", allow_pickle=False) as z:
        data = {key: z[key].copy() for key in z.files}
    metrics = json.loads((results / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    assert data["center_responses"].shape == (24, 485, 65)
    assert data["spatial_activity"].shape == (2, 721)
    assert data["params"].shape == (24, 5)
    assert data["time"].shape == (485,)
    assert data["center_types"].tolist() == metrics["all_center_types"]
    assert metrics["stimulus_count"] == 24
    assert manifest["n_nodes"] == 45669 and manifest["n_edges"] == 1513231
    assert data["spatial_angles"].tolist() == [90, 270]
    assert all(np.isfinite(data[key]).all() for key in
               ("center_responses", "spatial_activity", "time", "params"))

    table = metrics["stimulus_table"]
    columns = tuple(table[0])
    assert set(columns) == {"angle", "width", "intensity", "t_stim", "speed"}
    assert all(tuple(row) == columns for row in table)
    expected = np.array([[row[key] for key in columns] for row in table])
    np.testing.assert_array_equal(expected, data["params"])
    np.testing.assert_allclose(np.diff(data["time"]), metrics["dt"], atol=1e-14, rtol=0)
    assert data["time"][200] == 0
    assert len(set(zip(data["spatial_u"], data["spatial_v"]))) == 721
    u, v = data["spatial_u"], data["spatial_v"]
    assert np.all(np.maximum.reduce((np.abs(u), np.abs(v), np.abs(u + v))) <= 15)

    # Upstream peak_responses() defaults here to the stimulus interval, clips
    # negative activity to zero, and takes the maximum over its existing frames.
    recomputed_peaks = np.stack([
        np.maximum(data["center_responses"][sample,
            (data["time"] >= 0) & (data["time"] <= row["t_stim"])], 0).max(axis=0)
        for sample, row in enumerate(table)
    ])
    np.testing.assert_array_equal(recomputed_peaks, metrics["official_peak_responses"])
    ci = data["center_types"].tolist().index("T4c")
    snapshot_frames = []
    center_site = np.flatnonzero((u == 0) & (v == 0))
    assert len(center_site) == 1
    for k, angle in enumerate(data["spatial_angles"]):
        i = next(i for i, row in enumerate(table)
                 if row["angle"] == angle and row["intensity"] == 1)
        # Matches the immutable runner's prespecified midpoint selection.
        frame = int((-data["time"][0] + table[i]["t_stim"] / 2) / metrics["dt"])
        snapshot_frames.append(frame)
        np.testing.assert_array_equal(data["spatial_activity"][k, center_site[0]],
                                      data["center_responses"][i, frame, ci])
    assert snapshot_frames == [242, 242]
    data["snapshot_frames"] = snapshot_frames
    return data, metrics


def center_figure(data, metrics, output):
    fig, axes = plt.subplots(2, 4, figsize=(183 * MM, 103 * MM),
                             sharex=True, sharey=True)
    fig.subplots_adjust(left=.082, right=.987, bottom=.115, top=.865,
                        wspace=.20, hspace=.36)
    table, types = metrics["stimulus_table"], data["center_types"].tolist()
    plotted = []
    for ax, cell, label in zip(axes.flat, CELLS, "abcdefgh"):
        ni = types.index(cell)
        polarity = int(cell.startswith("T4"))
        for angle, color, linestyle in zip(ANGLES, COLORS, LINESTYLES):
            samples = [i for i, row in enumerate(table)
                       if row["angle"] == angle and row["intensity"] == polarity]
            assert len(samples) == 1
            values = data["center_responses"][samples[0], :, ni]
            plotted.append(values)
            line, = ax.plot(data["time"], values, color=color,
                            linestyle=linestyle, linewidth=.8)
            np.testing.assert_array_equal(line.get_ydata(), values)
        ax.axhline(0, color="#BDBDBD", linewidth=.35, zorder=0)
        ax.axvline(0, color=INK, linewidth=.55, linestyle=(0, (2.2, 2.2)), zorder=0)
        ax.set_title(f"{cell}  {'ON' if polarity else 'OFF'}", pad=5)
        panel_label(ax, label, x=-.10, y=1.04)
        ax.set_xlim(data["time"][0], data["time"][-1])
        ax.set_ylim(-.8, 1.8)
        ax.set_xticks((-1, 0, 1))
        ax.set_yticks((-.5, 0, .5, 1, 1.5))
        ax.tick_params(pad=2)
    assert np.min(plotted) >= -.8 and np.max(plotted) <= 1.8
    legend_handles = [Line2D([], [], color=c, linestyle=s, linewidth=.8,
                            label=f"{angle}\N{DEGREE SIGN}")
                      for angle, c, s in zip(ANGLES, COLORS, LINESTYLES)]
    legend_handles.append(Line2D([], [], color=INK, linewidth=.55,
                           linestyle=(0, (2.2, 2.2)), label="Edge onset"))
    fig.legend(handles=legend_handles, ncol=5, loc="upper center",
               bbox_to_anchor=(.54, .992), columnspacing=1.7,
               handlelength=2.0, borderpad=0)
    fig.supxlabel("Time from edge onset (s)", x=.535, y=.021, fontsize=7)
    fig.supylabel("Model activity (a.u.)", x=.012, y=.49, fontsize=7)
    paths = save_figure(fig, output / "flyvis-center-responses-20261117",
                        "Saved official FlyVis central T4/T5 responses")
    plt.close(fig)
    return paths


def spatial_figure(data, output):
    fig, axes = plt.subplots(1, 2, figsize=(183 * MM, 88 * MM),
                             sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.845, bottom=.16, top=.86, wspace=.12)
    # Official hex_utils.hex_to_pixel(..., mode='default') convention. These
    # are lattice coordinates, not soma locations or physical micrometers.
    u, v = data["spatial_u"], data["spatial_v"]
    x = 1.5 * v
    y = -np.sqrt(3) * (u + v / 2)
    angles = np.arange(6) * np.pi / 3
    unit_hexagon = np.column_stack((np.cos(angles), np.sin(angles)))
    vertices = np.stack((x, y), axis=1)[:, None, :] + unit_hexagon[None, :, :]
    norm = TwoSlopeNorm(vmin=-.5, vcenter=0, vmax=1.6)
    assert data["spatial_activity"].min() >= norm.vmin
    assert data["spatial_activity"].max() <= norm.vmax
    for ax, label, angle, values, frame in zip(
            axes, "ab", data["spatial_angles"], data["spatial_activity"],
            data["snapshot_frames"]):
        cells = PolyCollection(vertices, array=values, cmap="RdBu_r", norm=norm,
                               edgecolors="white", linewidths=.25, rasterized=False)
        ax.add_collection(cells)
        assert len(cells.get_paths()) == 721
        np.testing.assert_array_equal(cells.get_array(), values)
        ax.set_xlim(-24, 24)
        ax.set_ylim(-28, 28)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks((-20, 0, 20))
        ax.set_yticks((-20, 0, 20))
        ax.set_title(f"T4c ON {angle}\N{DEGREE SIGN}  \N{MIDDLE DOT}  {data['time'][frame]:.3f} s", pad=7)
        panel_label(ax, label, x=-.10, y=1.04)
        ax.tick_params(pad=2)
    fig.supxlabel("Hex-lattice x", x=.46, y=.025, fontsize=7)
    fig.supylabel("Hex-lattice y", x=.012, y=.50, fontsize=7)
    cax = fig.add_axes((.886, .22, .014, .57))
    cb = fig.colorbar(cells, cax=cax, ticks=(-.5, 0, .5, 1, 1.5))
    cb.outline.set_linewidth(.5)
    cb.ax.tick_params(width=.5, length=2.5, pad=2, labelsize=6)
    cb.set_label("Model activity (a.u.)", fontsize=7, labelpad=4)
    paths = save_figure(fig, output / "flyvis-spatial-activity-20261117",
                        "Saved official FlyVis T4c spatial activity at fixed midpoint")
    plt.close(fig)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=HERE / "results/flyvis-moving-edge-20261117")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "Research/Brain/figures")
    args = parser.parse_args()
    immutable = [args.results / name for name in
                 ("moving_edge_activity.npz", "metrics.json", "manifest.json",
                  "t4_t5_center_responses.png", "t4c_spatial_activity.png")]
    immutable.append(HERE / "run_official.py")
    before = {str(p): digest(p) for p in immutable}
    apply_style()
    plt.rcParams["path.simplify"] = False
    data, metrics = load_saved(args.results)
    paths = center_figure(data, metrics, args.output_dir)
    paths += spatial_figure(data, args.output_dir)
    assert before == {str(p): digest(p) for p in immutable}, "Original evidence changed"
    print(json.dumps({"source_npz_sha256": digest(immutable[0]),
        "qa": {"traces_shape": list(data["center_responses"].shape),
               "all_1560_saved_peaks_match": True,
               "params_columns": list(metrics["stimulus_table"][0]),
               "two_spatial_center_values_match": True,
               "no_input_or_runner_changes": True,
               "time_samples_per_trace": len(data["time"]),
               "snapshot_frames": data["snapshot_frames"],
               "snapshot_time_seconds": [float(data["time"][i]) for i in data["snapshot_frames"]]},
        "figures": {"center": {"panels": 8, "size_mm": [183, 103],
                                  "common_y_limits": [-.8, 1.8]},
                    "spatial": {"panels": 2, "sites_each": 721, "size_mm": [183, 88],
                                   "common_color_limits": [-.5, 1.6],
                                   "coordinates": "x=1.5v, y=-sqrt(3)(u+v/2); lattice, no physical units"}},
        "outputs": [str(p) for p in paths]}, indent=2))


if __name__ == "__main__":
    main()
