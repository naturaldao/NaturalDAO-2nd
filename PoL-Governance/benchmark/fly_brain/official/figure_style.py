"""Shared, final-size scientific figure style based on Nature's artwork guide.

Reference: https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels
This is a local plotting convention, not a journal endorsement.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

MM = 1 / 25.4
INK = "#222222"
GRAY = "#767676"
LIGHT = "#D9D9D9"
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
VERMILLION = "#D55E00"
SKY = "#56B4E9"
WONG = (BLUE, VERMILLION, GREEN, PURPLE, ORANGE, SKY)


def apply_style():
    """Use actual Arial; fail rather than silently substitute a different font."""
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 7,
        "axes.titlesize": 7, "axes.titleweight": "normal",
        "axes.labelsize": 7, "axes.labelpad": 3,
        "axes.edgecolor": INK, "axes.labelcolor": INK,
        "axes.linewidth": .5, "axes.grid": False,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": matplotlib.cycler(color=WONG),
        "text.color": INK, "xtick.color": INK, "ytick.color": INK,
        "xtick.labelsize": 6, "ytick.labelsize": 6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": .5, "ytick.major.width": .5,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.minor.width": .4, "ytick.minor.width": .4,
        "lines.linewidth": .8, "lines.markersize": 3,
        "legend.fontsize": 6, "legend.frameon": False,
        "legend.handlelength": 1.6, "legend.handletextpad": .5,
        "legend.borderaxespad": .3,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white", "figure.facecolor": "white",
        "axes.facecolor": "white", "savefig.dpi": 600,
        "hatch.linewidth": .5,
    })


def panel_label(ax, letter, x=-.12, y=1.06):
    return ax.text(x, y, letter, transform=ax.transAxes,
                   fontsize=8, fontweight="bold", fontstyle="normal",
                   color=INK, ha="left", va="bottom", clip_on=False)


def save_figure(fig, stem, title):
    """Preserve final physical dimensions and editable text in PDF/SVG."""
    stem = Path(stem).with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    width, height = fig.get_size_inches() * 25.4
    if width > 183.01 or height > 170.01:
        raise ValueError(f"Oversized figure: {width:g} × {height:g} mm")
    paths = []
    for suffix in (".png", ".pdf", ".svg"):
        path = stem.with_suffix(suffix)
        kwargs = {"dpi": 600}
        if suffix == ".pdf":
            kwargs["metadata"] = {"Title": title, "Author": "PoL2 research"}
        elif suffix == ".svg":
            kwargs["metadata"] = {"Title": title, "Creator": "PoL2 research"}
        fig.savefig(path, **kwargs)
        if suffix == ".svg":
            # Matplotlib appends spaces to path-coordinate lines. Removing
            # them keeps generated XML friendly to repository whitespace checks.
            content = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n",
                            encoding="utf-8", newline="\n")
        paths.append(path)
    return paths
