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
from matplotlib import font_manager
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd

from figure_style import MM, INK, BLUE, ORANGE, LIGHT, apply_style, panel_label, save_figure


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


def render(brain: pd.DataFrame, spikes: pd.DataFrame, metadata: dict, output: Path):
    """Three final-size panels; statistics and provenance belong in the caption."""
    apply_style()
    width_mm, height_mm = 183.0, 115.0
    fig = plt.figure(figsize=(width_mm * MM, height_mm * MM))
    run_s = metadata["simulation_duration_ms"] / 1000.0

    def axes_mm(left, bottom, width, height):
        return fig.add_axes([left / width_mm, bottom / height_mm,
                             width / width_mm, height / height_mm])

    spatial = brain.loc[brain["x_um"].notna()].copy()
    active = spatial.loc[spatial["spike_count"] > 0]
    if active.empty:
        raise ValueError("The activity figure requires at least one recorded spike")
    lower_rate = 1.0 / run_s
    upper_rate = max(float(active["spikes_per_second"].max()), 2.0 * lower_rate)
    norm = LogNorm(vmin=lower_rate, vmax=upper_rate)
    spatial_specs = (
        ("a", "y", (12, 67, 73, 39), "XY projection", (40, 450), [100, 200, 300, 400],
         {"MN9 L": (650, 420), "MN9 R": (285, 250)}),
        ("b", "z", (12, 29, 73, 30), "XZ projection", (0, 290), [0, 100, 200],
         {"MN9 L": (690, 20), "MN9 R": (285, 20)}),
    )
    for letter, ordinate, box, descriptor, limits, ticks, label_positions in spatial_specs:
        ax = axes_mm(*box)
        # Plot every matched neuron, with no smoothing, synthetic locations,
        # or subsampling. Rasterization affects export only, not the data.
        ax.scatter(spatial["x_um"], spatial[f"{ordinate}_um"], s=.18, c=LIGHT,
                   alpha=.48, edgecolors="none", rasterized=True, zorder=1)
        dots = ax.scatter(active["x_um"], active[f"{ordinate}_um"],
                          c=active["spikes_per_second"], norm=norm, cmap="cividis",
                          s=4.1, alpha=1.0, linewidths=.25, edgecolors=INK,
                          rasterized=True, zorder=3)
        for label, rid in MN9.items():
            selected = spatial.loc[spatial["root_id"] == rid]
            if selected.empty:
                continue
            row = selected.iloc[0]
            point = (row["x_um"], row[f"{ordinate}_um"])
            ax.scatter(*point, marker="o" if label.endswith("L") else "s", s=8,
                       facecolors="white", edgecolors=INK, linewidths=.55, zorder=6)
            ax.annotate(label, point, xytext=label_positions[label], textcoords="data",
                        color=INK, fontsize=6, ha="center", va="center", zorder=7,
                        arrowprops=dict(arrowstyle="-", color=INK, lw=.4,
                                        shrinkA=1.5, shrinkB=2))
        ax.set(xlabel="X (µm)", ylabel=f"{ordinate.upper()} (µm)")
        ax.set(xlim=(50, 950), ylim=limits)
        ax.set_xticks([100, 300, 500, 700, 900])
        ax.set_yticks(ticks)
        ax.set_aspect("equal", adjustable="box")
        ax.set_anchor("NW")
        ax.text(0, 1.055, descriptor, transform=ax.transAxes, fontsize=7,
                ha="left", va="bottom", color=INK)
        panel_label(ax, letter, x=-.15, y=1.055)

    color_ax = axes_mm(24, 21, 50, 2.3)
    colorbar = fig.colorbar(dots, cax=color_ax, orientation="horizontal")
    color_ticks = [value for value in (1, 10, 100, 200) if lower_rate <= value <= upper_rate]
    colorbar.set_ticks(color_ticks)
    colorbar.set_ticklabels([str(value) for value in color_ticks])
    colorbar.ax.minorticks_off()
    colorbar.ax.tick_params(labelsize=6, length=2, width=.5, colors=INK)
    colorbar.set_label("Firing rate (Hz)", fontsize=7, labelpad=2, color=INK)
    colorbar.outline.set_linewidth(.4)

    ax = axes_mm(104, 13, 74, 93)
    active_order = brain.loc[brain["spike_count"] > 0].sort_values("model_index")["root_id"].tolist()
    ranks = {rid: index + 1 for index, rid in enumerate(active_order)}
    # One plotted mark per recorded event; all 393 active neurons remain.
    ax.scatter(spikes["time_ms"], spikes["root_id"].map(ranks), s=.42, color=BLUE,
               alpha=.65, linewidths=0, rasterized=True, zorder=1)
    for label, rid in MN9.items():
        selected = spikes.loc[spikes["root_id"] == rid]
        if rid in ranks:
            ax.scatter(selected["time_ms"], np.full(len(selected), ranks[rid]), marker="|",
                       s=4, color=ORANGE, linewidths=.4, rasterized=True, zorder=3)
    ax.text(0, 1.018, "Spike raster", ha="left", va="bottom",
            transform=ax.transAxes, fontsize=7, color=INK)
    panel_label(ax, "c", x=-.15, y=1.018)
    ax.plot([], [], color=ORANGE, lw=.8, label="MN9")
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.018), borderaxespad=0,
              handlelength=1.2, fontsize=6)
    ax.set(xlim=(0, metadata["simulation_duration_ms"]), xlabel="Time (ms)",
           ylabel="Active neuron rank", ylim=(len(active_order) + .5, .5))
    ax.set_xticks(np.linspace(0, metadata["simulation_duration_ms"], 6))
    ticks = [1] + list(range(100, len(active_order), 100)) + [len(active_order)]
    ax.set_yticks(sorted(set(ticks)))
    metadata["rendering"] = {
        "physical_size_mm": [width_mm, height_mm],
        "panel_count": 3,
        "panels": {"a": "real XY anchor projection", "b": "real XZ anchor projection",
                   "c": "complete recorded raster, all active neurons, one mark per recorded spike"},
        "font": "Arial",
        "font_file": font_manager.findfont("Arial", fallback_to_default=False),
        "text_size_pt": {"descriptors_and_axis_labels": 7, "tick_labels_and_annotations": 6,
                         "lowercase_panel_letters": 8},
        "spatial_aspect": "equal physical scaling on each projection; original coordinate axes retained",
        "background_anchor_marks": int(len(spatial)),
        "active_anchor_marks": int(len(active)),
        "raster_event_marks": int(len(spikes)),
        "spatial_colormap": "cividis",
        "spatial_rate_normalization": "logarithmic",
        "spatial_rate_limits_Hz": [lower_rate, upper_rate],
        "mn9_symbols": {"MN9 L": "small open circle", "MN9 R": "small open square"},
        "raster_mn9_highlight": "orange marks on their actual recorded rows and times",
        "interpolation_or_smoothing": "none",
        "png_dpi": 600,
        "vector_fonts": "PDF TrueType type 42; SVG text retained",
        "caption_policy": "statistics, source attribution and scientific limitations retained in sidecar and external caption, not decorative in-figure text",
    }
    style_path = Path(__file__).with_name("figure_style.py")
    metadata["files"]["figure_style"] = {
        "path": str(style_path.resolve()), "sha256": sha256(style_path), "bytes": style_path.stat().st_size
    }
    stem = output.with_suffix("")
    paths = save_figure(fig, stem, "Real FlyWire v783 anchors and official-model simulated spikes")
    plt.close(fig)
    metadata["outputs"] = {
        path.suffix.lstrip("."): {"path": str(path.resolve()), "sha256": sha256(path),
                                  "bytes": path.stat().st_size}
        for path in paths
    }
    sidecar = stem.with_suffix(".json")
    sidecar.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return sidecar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eon-root", required=True, type=Path)
    parser.add_argument("--coordinates", required=True, type=Path)
    parser.add_argument("--spikes", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Output PNG path; PDF, SVG and JSON use the same stem")
    args = parser.parse_args()
    brain, spikes, metadata = load_data(args.eon_root, args.coordinates, args.spikes)
    sidecar = render(brain, spikes, metadata, args.output)
    print(json.dumps({key: metadata[key] for key in (
        "model_neurons", "matched_model_neurons", "missing_model_coordinates", "recorded_spikes",
        "active_model_neurons", "matched_active_neurons", "mn9", "outputs")}, indent=2))
    print(f"Coverage and source manifest: {sidecar.resolve()}")


if __name__ == "__main__":
    main()
