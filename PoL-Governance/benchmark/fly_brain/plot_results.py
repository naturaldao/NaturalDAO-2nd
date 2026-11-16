"""Render published summaries; this does not fit or evaluate any model."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
MEMORY = json.loads((HERE / "results/memory-eval-20261117/summary.json").read_text())
INTERFACE = json.loads((HERE / "interface/results/eval-20261117/results.json").read_text())
DEST = HERE.parents[2] / "Research/Brain/figures"
ARMS = ("output_gate", "full_reset", "selective", "orthogonal", "random_matched")
LABELS = ("State unchanged", "Full reset", "Selective", "Orthogonal", "Random, matched norm")
COLORS = ("#64748b", "#dc6842", "#217a70", "#3879b5", "#a77a23")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), constrained_layout=True)


def curve(ax, topology, metric, title, ylabel):
    for arm, label, color in zip(ARMS, LABELS, COLORS):
        group = [r for r in MEMORY["summary"] if r["topology"] == topology and r["arm"] == arm]
        x = np.array([r["delay"] for r in group])
        y = np.array([r[metric]["mean"] for r in group])
        sd = np.array([r[metric]["sd_between_seeds"] for r in group])
        ax.plot(x, y, "o-", lw=1.6, ms=3, color=color, label=label)
        ax.fill_between(x, y-sd, y+sd, color=color, alpha=0.1, linewidth=0)
    ax.set(title=title, xlabel="Steps after cancellation", ylabel=ylabel, xticks=[0, 4, 8, 16])
    ax.grid(axis="y", alpha=0.2)


for ax, graph, label in zip(axes[0], ("flyvis_template", "degree_rewired", "random_sparse"),
                           ("A  FlyVis type template", "B  Signed-degree rewiring", "C  Random sparse graph")):
    curve(ax, graph, "a_probe_r2", label, "Withdrawn A: critic R²")
    ax.axhline(0, color="black", lw=.7, alpha=.3)
curve(axes[1, 0], "flyvis_template", "b_probe_r2", "D  B information remains decodable", "Retained B: critic R²")
curve(axes[1, 1], "flyvis_template", "b_mse", "E  Frozen task readout degrades", "Retained B: frozen-head MSE")
ax = axes[1, 2]
names = ("raw", "physical", "start_only", "full_typed", "generic_matched")
values = [INTERFACE["summary"][n]["execution_violations"] for n in names]
bars = ax.bar(range(5), values, color=["#64748b", "#a77a23", "#dc6842", "#217a70", "#3879b5"])
ax.set_xticks(range(5), ["Raw", "Physical", "Selection\nonly", "Full\ntyped", "Matched\ngeneric"])
ax.bar_label(bars, padding=3, fmt="%d", fontsize=10)
ax.set(title="F  Execution-protocol stress test", ylabel="Actions with ≥1 violation", ylim=(0, max(values)*1.2))
ax.text(.97, .95, "1,024 synthetic scenarios\n16 atomic steps each", ha="right", va="top", transform=ax.transAxes, fontsize=9)
ax.grid(axis="y", alpha=.2)
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center", ncol=5, frameon=False)
fig.suptitle("Target-cue cancellation and execution permissions are separate experiments", fontsize=15)
DEST.mkdir(parents=True, exist_ok=True)
fig.savefig(DEST / "fly-brain-results.png", dpi=160)
fig.savefig(DEST / "fly-brain-results.pdf")
print(DEST / "fly-brain-results.png")
