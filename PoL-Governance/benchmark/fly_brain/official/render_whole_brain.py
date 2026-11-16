"""Render real v783 community anchors and an observed official-model spike file.

This is a spatial point visualization, not a mesh or reconstructed morphology.
No brain coordinates, spikes, or neuron identities are synthesized here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import numpy as np
import pandas as pd


EON_COMMIT = "a3db62f9436074e485c0278290c2164ed6150808"
EON_URL = f"https://github.com/eonsystemspbc/fly-brain/tree/{EON_COMMIT}"
COORDINATES_URL = (
    "https://storage.googleapis.com/flywire-data/codex/data/fafb/783/coordinates.csv.gz"
)
LICENSE_URL = "https://flywire.ai/guidelines"
MN9 = {"MN9 L": "720575940660219265", "MN9 R": "720575940618238523"}
MN9_SOURCE = "code/paper-phil-drosophila/example.ipynb"
MN9_SOURCE_URL = (
    f"https://github.com/eonsystemspbc/fly-brain/blob/{EON_COMMIT}/{MN9_SOURCE}"
)
INK, MUTED, ACTIVE, MARKER = "#172D40", "#566778", "#267FAD", "#B72D67"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_ids(values: pd.Series, name: str) -> pd.Series:
    if pd.api.types.is_float_dtype(values.dtype):
        raise ValueError(f"{name} was decoded as floating point; root IDs must be exact")
    result = values.astype("string")
    if result.isna().any() or not result.str.fullmatch(r"[0-9]+").all():
        raise ValueError(f"Invalid or missing exact root IDs in {name}")
    return result


def duration_ms(spikes_path: Path) -> tuple[float, str]:
    manifest = spikes_path.parent.parent / "manifest.csv"
    if manifest.exists():
        rows = pd.read_csv(manifest)
        key = f"{spikes_path.parent.name}/{spikes_path.name}"
        matches = rows[
            rows["spike_path"].astype(str).str.replace("\\", "/", regex=False).str.endswith(key)
        ]
        if len(matches) == 1:
            return float(matches.iloc[0]["t_run"]) * 1000.0, str(manifest.resolve())
    match = re.search(r"_t([0-9.]+)s_n[0-9]+", spikes_path.name)
    if not match:
        raise ValueError("Cannot determine actual run duration from manifest or filename")
    return float(match.group(1)) * 1000.0, "official output filename duration"


def load_data(eon_root: Path, coordinates: Path, spikes_path: Path):
    completeness = eon_root / "data/2025_Completeness_783.csv"
    header = pd.read_csv(completeness, nrows=0).columns[0]
    model = pd.read_csv(completeness, dtype={header: "string"})
    model = model.rename(columns={header: "root_id"})
    model["root_id"] = exact_ids(model["root_id"], "completeness.root_id")
    if model["root_id"].duplicated().any():
        raise ValueError("Duplicate neuron IDs in the official completeness list")
    model["model_index"] = np.arange(len(model))

    anchors = pd.read_csv(coordinates, dtype={"root_id": "string", "supervoxel_id": "string"})
    anchors["root_id"] = exact_ids(anchors["root_id"], "coordinates.root_id")
    coordinate_record_count = len(anchors)
    # The file may contain multiple marked coordinates per neuron. Keep the
    # first file-order anchor; do not claim that it is a soma or a centroid.
    anchors = anchors.drop_duplicates("root_id", keep="first").copy()
    xyz_nm = np.stack([np.fromstring(value.strip("[]"), sep=" ") for value in anchors["position"]])
    if xyz_nm.shape != (len(anchors), 3) or not np.isfinite(xyz_nm).all():
        raise ValueError("Every retained anchor must contain three finite measured coordinates")
    for axis, values in zip("xyz", xyz_nm.T):
        anchors[f"{axis}_um"] = values / 1000.0
    brain = model.merge(anchors, on="root_id", how="left", validate="one_to_one", sort=False)

    spikes = pd.read_parquet(spikes_path)
    spikes["root_id"] = exact_ids(spikes["flywire_id"], "spikes.flywire_id")
    if "time_ms" not in spikes or "trial" not in spikes:
        raise ValueError("Expected the official time_ms and trial columns")
    if spikes["trial"].nunique() != 1:
        raise ValueError("This figure requires exactly one recorded trial; do not silently pool trials")
    run_ms, run_duration_source = duration_ms(spikes_path)
    if run_ms <= 0 or not np.isfinite(spikes["time_ms"]).all():
        raise ValueError("Invalid simulation duration or recorded spike times")
    if ((spikes["time_ms"] < 0) | (spikes["time_ms"] >= run_ms + 1e-7)).any():
        raise ValueError("Recorded spikes outside the declared simulation interval")
    unknown_spikes = sorted(set(spikes["root_id"]) - set(model["root_id"]))
    if unknown_spikes:
        raise ValueError(f"Spike IDs missing from the official modeled population: {unknown_spikes[:3]}")
    counts = spikes.groupby("root_id", sort=False).size().rename("spike_count")
    brain = brain.join(counts, on="root_id")
    brain["spike_count"] = brain["spike_count"].fillna(0).astype(int)
    brain["spikes_per_second"] = brain["spike_count"] / (run_ms / 1000.0)
    matched = brain["x_um"].notna()
    active = brain["spike_count"] > 0

    notebook = eon_root / MN9_SOURCE
    notebook_text = notebook.read_text(encoding="utf-8")
    for label, rid in MN9.items():
        if rid not in notebook_text or rid not in set(model["root_id"]):
            raise ValueError(f"Cannot verify {label} ID against the source notebook and modeled IDs")
    metadata = {
        "scope": "real community-anchor spatial projections with spikes from an official-model run; no mesh, soma reconstruction, synthetic layout, or observed animal behavior",
        "model_neurons": int(len(model)),
        "coordinate_records": int(coordinate_record_count),
        "coordinate_unique_neurons": int(len(anchors)),
        "matched_model_neurons": int(matched.sum()),
        "missing_model_coordinates": int((~matched).sum()),
        "model_coordinate_coverage": float(matched.mean()),
        "missing_model_root_ids": brain.loc[~matched, "root_id"].tolist(),
        "recorded_spikes": int(len(spikes)),
        "active_model_neurons": int(active.sum()),
        "matched_active_neurons": int((active & matched).sum()),
        "missing_active_coordinates": int((active & ~matched).sum()),
        "recorded_trial": int(spikes["trial"].iloc[0]),
        "simulation_duration_ms": run_ms,
        "simulation_duration_source": run_duration_source,
        "observed_spike_time_range_ms": [float(spikes["time_ms"].min()), float(spikes["time_ms"].max())],
        "coordinate_policy": "first record in source file for each exact root_id; community-marked anchor, not soma or geometric centroid",
        "coordinate_source_units": "nanometers",
        "display_units": "micrometers; each original coordinate divided by 1000; no imputed locations or spatial warping",
        "raster_order": "active neurons sorted by their index in the official completeness CSV; this order is not an anatomical layout",
        "spike_time_column": "time_ms",
        "rates": "spike count divided by manifest run duration, for one recorded trial",
        "spatial_extent_um": {
            axis: [float(brain.loc[matched, f"{axis}_um"].min()), float(brain.loc[matched, f"{axis}_um"].max())]
            for axis in "xyz"
        },
        "sources": {
            "model": {"url": EON_URL, "commit": EON_COMMIT},
            "coordinates": {
                "url": COORDINATES_URL,
                "license": "CC BY-NC 4.0; original FlyWire data terms retained, not relicensed as first-party project material",
                "license_url": LICENSE_URL,
            },
            "mn9_mapping": {"relative_notebook": MN9_SOURCE, "url": MN9_SOURCE_URL},
        },
        "files": {
            name: {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in {
                "completeness": completeness,
                "coordinates": coordinates,
                "spikes": spikes_path,
                "mn9_notebook": notebook,
                "renderer": Path(__file__),
            }.items()
        },
        "mn9": {},
    }
    for label, rid in MN9.items():
        row = brain.loc[brain["root_id"] == rid].iloc[0]
        metadata["mn9"][label] = {
            "root_id": rid,
            "spikes": int(row["spike_count"]),
            "spikes_per_second": float(row["spikes_per_second"]),
            "coordinate_available": bool(pd.notna(row["x_um"])),
            "first_anchor_um": [float(row[f"{axis}_um"]) for axis in "xyz"] if pd.notna(row["x_um"]) else None,
        }
    return brain, spikes, metadata


def style_axis(ax):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("bottom", "left"):
        ax.spines[spine].set_color("#BAC7D0")
    ax.tick_params(colors=MUTED, labelsize=9, length=3)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)


def render(brain: pd.DataFrame, spikes: pd.DataFrame, metadata: dict, output: Path):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
        "axes.labelsize": 10, "pdf.fonttype": 42, "ps.fonttype": 42,
        "savefig.facecolor": "white", "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(15.6, 9.8), facecolor="white")
    run_s = metadata["simulation_duration_ms"] / 1000.0
    fig.text(.075, .952, "Whole-brain model: real locations, simulated spikes", fontsize=23,
             weight="bold", color=INK, va="top")
    fig.text(.075, .903,
             f"Official Eon / Shiu LIF model  |  FlyWire v783  |  Sugar GRNs at 200 Hz  |  {run_s:g} s, one trial",
             fontsize=11, color=MUTED)
    stats = [
        (f"{metadata['model_neurons']:,}", "modeled neurons"),
        (f"{metadata['matched_model_neurons']:,} / {metadata['model_neurons']:,}", "real spatial anchors matched"),
        (f"{metadata['active_model_neurons']:,}", "neurons with recorded spikes"),
        (f"{metadata['recorded_spikes']:,}", "recorded spikes"),
    ]
    for xpos, (value, label) in zip((.075, .285, .58, .805), stats):
        fig.text(xpos, .854, value, fontsize=21, color=INK, weight="bold")
        fig.text(xpos, .829, label, fontsize=9.5, color=MUTED)

    grid = fig.add_gridspec(2, 2, left=.075, right=.94, top=.785, bottom=.195,
                           height_ratios=(1.0, .90), hspace=.54, wspace=.20)
    spatial = brain.loc[brain["x_um"].notna()].copy()
    active = spatial.loc[spatial["spike_count"] > 0]
    cmap = LinearSegmentedColormap.from_list("spike_rates", ["#276C9B", "#E89339", "#B52E4F"])
    vmax = max(float(active["spikes_per_second"].max()), 2.0)
    norm = LogNorm(vmin=1.0 / run_s, vmax=vmax)
    plots = []
    for column, ordinate, title in ((0, "y", "A   Measured anchors: X-Y projection"),
                                    (1, "z", "B   Measured anchors: X-Z projection")):
        ax = fig.add_subplot(grid[0, column])
        ax.scatter(spatial["x_um"], spatial[f"{ordinate}_um"], s=.48, c="#9BAFBD",
                   alpha=.13, edgecolors="none", rasterized=True)
        dots = ax.scatter(active["x_um"], active[f"{ordinate}_um"],
                          c=active["spikes_per_second"], norm=norm, cmap=cmap,
                          s=5 + 16 * np.sqrt(active["spikes_per_second"] / vmax),
                          alpha=.95, linewidths=.13, edgecolors="white", rasterized=True)
        for label, rid in MN9.items():
            selected = spatial.loc[spatial["root_id"] == rid]
            if selected.empty:
                continue
            row = selected.iloc[0]
            point = (row["x_um"], row[f"{ordinate}_um"])
            ax.scatter(*point, marker="*", s=130, color=MARKER, edgecolors="white",
                       linewidths=.6, zorder=6)
            offset = (-70, 13) if label.endswith("L") else (15, -20)
            ax.annotate(label, point, xytext=offset, textcoords="offset points", color=MARKER,
                        fontsize=9, weight="bold", zorder=7,
                        bbox=dict(boxstyle="round,pad=.18", fc="white", ec="none", alpha=.9),
                        arrowprops=dict(arrowstyle="-", color=MARKER, lw=.7))
        ax.set(xlabel="X (µm)", ylabel=f"{ordinate.upper()} (µm)")
        ax.set_title(title, loc="left", pad=14, color=INK, weight="bold")
        ax.set_aspect("equal", adjustable="box")
        ax.margins(x=.035, y=.07)
        style_axis(ax)
        plots.append(ax)
    color_ax = fig.add_axes([.956, .525, .010, .184])
    colorbar = fig.colorbar(dots, cax=color_ax)
    ticks = [value for value in (1, 10, 100, 200) if 1 / run_s <= value <= vmax]
    colorbar.set_ticks(ticks)
    colorbar.set_ticklabels([str(value) for value in ticks])
    colorbar.ax.tick_params(labelsize=8, colors=MUTED, length=2)
    colorbar.set_label("Recorded spikes / s", color=MUTED, labelpad=8)
    colorbar.outline.set_visible(False)

    ax = fig.add_subplot(grid[1, :])
    active_order = brain.loc[brain["spike_count"] > 0].sort_values("model_index")["root_id"].tolist()
    ranks = {rid: index + 1 for index, rid in enumerate(active_order)}
    ax.scatter(spikes["time_ms"], spikes["root_id"].map(ranks), s=2.0, color=ACTIVE,
               alpha=.52, linewidths=0, rasterized=True)
    mn9_labels = []
    for label, rid in MN9.items():
        selected = spikes.loc[spikes["root_id"] == rid]
        if rid in ranks:
            ax.axhline(ranks[rid], color=MARKER, lw=.7, alpha=.22, zorder=0)
            ax.scatter(selected["time_ms"], np.full(len(selected), ranks[rid]), marker="|",
                       s=28, color=MARKER, linewidths=.75, zorder=3)
        mn9_labels.append(f"{label}: {len(selected)} spikes")
    ax.set_title("C   Recorded spike raster: every active neuron, full simulated interval",
                 loc="left", color=INK, weight="bold", pad=14)
    ax.text(1, 1.045, "  |  ".join(mn9_labels), ha="right", va="bottom",
            transform=ax.transAxes, fontsize=9, color=MARKER, weight="bold")
    ax.set(xlim=(0, metadata["simulation_duration_ms"]), xlabel="Simulation time (ms)",
           ylabel="Active neuron rank\n(model index order)", ylim=(len(active_order) + .5, .5))
    ticks = [1] + list(range(100, len(active_order), 100)) + [len(active_order)]
    ax.set_yticks(sorted(set(ticks)))
    ax.grid(axis="x", color="#DCE5EB", linewidth=.6)
    ax.set_axisbelow(True)
    style_axis(ax)
    fig.text(.075, .145,
             "Grey: all modeled neurons with coordinates. Color: recorded activity. Stars: MN9 L / R. "
             "Positions are first community-marked anchors, not somata.",
             fontsize=9, color=MUTED)
    fig.text(.075, .121,
             "Real coordinates retained (nm → µm); no synthetic layout, mesh, or anatomical interpolation. "
             f"Missing coordinates: {metadata['missing_model_coordinates']:,} modeled / {metadata['missing_active_coordinates']:,} active.",
             fontsize=9, color=MUTED)
    fig.text(.075, .082,
             "Sources: FlyWire / Codex FAFB v783 coordinates (CC BY-NC 4.0; original terms retained); "
             f"Eon fly-brain {EON_COMMIT[:12]} and its MN9 example notebook.",
             fontsize=8.3, color=MUTED)
    fig.text(.075, .059,
             "Activity is from the official-model simulation, not measured animal behavior. "
             "Full source links, file SHA-256 values, and exact-ID coverage accompany this figure.",
             fontsize=8.3, color=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    stem = output.with_suffix("")
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=190)
    fig.savefig(pdf, metadata={"Title": "Real FlyWire v783 anchors and official-model simulated spikes",
                               "Author": "PoL2 research; original FlyWire data attribution retained"})
    plt.close(fig)
    metadata["outputs"] = {
        name: {"path": str(path.resolve()), "sha256": sha256(path), "bytes": path.stat().st_size}
        for name, path in {"png": png, "pdf": pdf}.items()
    }
    sidecar = stem.with_suffix(".json")
    sidecar.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return sidecar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eon-root", required=True, type=Path)
    parser.add_argument("--coordinates", required=True, type=Path)
    parser.add_argument("--spikes", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Output PNG path; PDF and JSON use the same stem")
    args = parser.parse_args()
    brain, spikes, metadata = load_data(args.eon_root, args.coordinates, args.spikes)
    sidecar = render(brain, spikes, metadata, args.output)
    print(json.dumps({key: metadata[key] for key in (
        "model_neurons", "matched_model_neurons", "missing_model_coordinates", "recorded_spikes",
        "active_model_neurons", "matched_active_neurons", "mn9", "outputs")}, indent=2))
    print(f"Coverage and source manifest: {sidecar.resolve()}")


if __name__ == "__main__":
    main()
