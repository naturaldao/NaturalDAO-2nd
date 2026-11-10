"""Render the Chinese README figures from the checked-in simulation tables.

Install the project with the plot extra, then run this script from any directory.
Use --font to select an installed Simplified Chinese font explicitly.
"""

import argparse
import csv
from pathlib import Path
import warnings

from matplotlib import font_manager
from matplotlib.ticker import PercentFormatter

from pol2dao.plotstyle import CJK_FONTS, PALETTE, bar, finalize_figure, new_figure, plot_line


LAB = Path(__file__).resolve().parents[1]
TABLES = LAB / "results" / "tables"
FIGURES = LAB / "results" / "figures"
REFERENCE = PALETTE["neutral"]
FOCUS = PALETTE["blue_main"]


def table(name):
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def select(rows, **conditions):
    matches = [row for row in rows if all(row[key] == value for key, value in conditions.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {conditions}, found {len(matches)}")
    return matches[0]


def canvas(font, ncols, panel, title, subtitle, *, top, bottom):
    from matplotlib import rcParams

    fig, grid = new_figure(ncols=ncols, panel=panel, sharey=True)
    rcParams["font.family"] = [font, "DejaVu Sans"]
    fig.subplots_adjust(left=0.094, right=0.977, bottom=bottom, top=top, wspace=0.23)
    fig.text(0.094, 0.940, title, fontsize=24, weight="bold", va="top", color=PALETTE["ink"])
    fig.text(0.094, 0.858, subtitle, fontsize=14, va="top", color=PALETTE["ink_soft"])
    for ax in grid[0]:
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        ax.tick_params(axis="x", length=0, pad=8)
    return fig, grid[0]


def grouped(ax, categories, series, *, places=1):
    width = 0.29
    for index, (label, values, errors, fill) in enumerate(series):
        positions = [x + (index - 0.5) * (width + 0.05) for x in range(len(categories))]
        bars = bar(ax, positions, values, color=fill, width=width, err=errors, label=label)
        for pos, rect, error in zip(positions, bars, errors or [0.0] * len(bars)):
            value = rect.get_height()
            inside = value + error > 0.93
            y = value - 0.035 if inside else value + error + 0.023
            color = PALETTE["white"] if inside and fill == FOCUS else PALETTE["ink"]
            ax.text(pos, y, f"{value:.{places}%}", ha="center",
                    va="top" if inside else "bottom", fontsize=11.5 if inside else 13, color=color)
    ax.set_xticks(range(len(categories)), categories)
    ax.set_xlim(-0.57, len(categories) - 0.43)


def allocation(font):
    e14 = table("e14_needs_report.csv")
    e16 = table("e16_nonmarket_allocation.csv")
    fig, axes = canvas(font, 3, (4.4, 6.0), "公共资源如何按需分配",
                       "E14、E16　合成情景下的分配规则比较", top=0.615, bottom=0.16)

    def series(label, row, keys, fill, *, intervals=False):
        errors = [float(row[f"{key}_ci"]) for key in keys] if intervals else None
        return label, [float(row[key]) for key in keys], errors, fill

    ax = axes[0]
    ax.set_title("按申报量比例配给", loc="left", y=1.18)
    keys = ("honest_fill", "efficiency")
    grouped(ax, ["诚实者的\n需求满足率", "资源用于\n真实需求的比例"], [
        series("无虚报", select(e14, rule="R1", f="0.0"), keys, REFERENCE, intervals=True),
        series("30% 的人虚报", select(e14, rule="R1", f="0.3"), keys, FOCUS, intervals=True),
    ], places=0)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.025, 1.01), ncol=2, columnspacing=0.85,
              handletextpad=0.45, handlelength=1.1)

    ax = axes[1]
    ax.set_title("无虚报时的紧急优先", loc="left", y=1.18)
    keys = ("critical_fill", "shock_critical_fill")
    grouped(ax, ["全部轮次\n紧急满足率", "供给骤减时\n紧急满足率"], [
        series("全体同级", select(e16, rule="equal_rotation", inflation_share="0.0"), keys, REFERENCE),
        series("紧急优先", select(e16, rule="needs_priority", inflation_share="0.0"), keys, FOCUS),
    ], places=0)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.025, 1.01), ncol=2, columnspacing=0.85,
              handletextpad=0.45, handlelength=1.1)

    ax = axes[2]
    ax.set_title("40% 虚报时的基本保障", loc="left", y=1.18)
    keys = ("real_use",)
    grouped(ax, ["资源用于\n真实需求的比例"], [
        series("紧急优先", select(e16, rule="needs_priority", inflation_share="0.4"), keys, REFERENCE),
        series("先保一单位", select(e16, rule="floor_then_priority", inflation_share="0.4"), keys, FOCUS),
    ], places=0)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.025, 1.01), ncol=2, columnspacing=0.85,
              handletextpad=0.45, handlelength=1.1)
    finalize_figure(fig, FIGURES / "readme_publicization_allocation_zh", tight=False)


def appeals(font):
    rows = table("e17_priority_appeals.csv")
    fig, (ax,) = canvas(font, 1, (11.5, 5.9), "优先等级判错后，申诉能纠正多少",
                        "E17　初判错误率为 25%，30% 的主体夸报数量并尝试虚报最高等级", top=0.67, bottom=0.16)
    metrics = ("critical_fill", "weighted_fill", "mispriority_units")
    series = []
    for capacity, label, fill in [("0.0", "无复核", REFERENCE), ("0.25", "每轮最多复核 25% 的主体", FOCUS)]:
        row = select(rows, classification_error="0.25", false_priority_claimants="0.3", appeal_capacity=capacity)
        series.append((label, [float(row[key]) for key in metrics],
                       [float(row[f"{key}_ci"]) for key in metrics], fill))
    grouped(ax, ["紧急需求满足率 ↑", "加权需求满足率 ↑", "资源分给等级\n被高估者的比例 ↓"], series)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.01, 1.025), ncol=2)
    finalize_figure(fig, FIGURES / "readme_publicization_appeals_zh", tight=False)


def voice(font):
    rows = table("e0_decomposition.csv")
    steps = {
        "ranked 20/80 free talk": "线性计票\n集中预算\n自由发言",
        "+ equal power": "改为\n等额预算",
        "+ quadratic voting": "改为\n二次方计票",
        "+ turn- taking": "增加\n轮流发言",
        "+ EAP screening": "增加\n伦理筛查",
    }
    fig, (ax,) = canvas(font, 1, (11.5, 6.0), "轮流发言与筛查怎样影响表决结果",
                        "E0　在同一模拟中依次改变一项治理规则", top=0.67, bottom=0.20)
    for scenario, label, color, marker in [
        ("baseline", "没有敌意发言", PALETTE["neutral_dark"], "s"),
        ("hostile", "存在敌意发言", FOCUS, "o"),
    ]:
        selected = [select(rows, scenario=scenario, step=step) for step in steps]
        values = [float(row["minority_win"]) for row in selected]
        errors = [float(row["minority_win_ci"]) for row in selected]
        plot_line(ax, range(len(steps)), values, err=errors, label=label,
                  color=color, marker=marker)
        offset = 0.055 if scenario == "hostile" else -0.070
        ax.text(4, values[-1] + offset, f"{values[-1]:.1%}", color=color, ha="center", va="center")
    ax.set_ylabel("少数派首选胜出的比例 ↑")
    ax.set_xticks(range(len(steps)), list(steps.values()))
    ax.set_xlim(-0.32, 4.32)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.01, 1.025), ncol=2)
    finalize_figure(fig, FIGURES / "readme_publicization_voice_zh", tight=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="installed Simplified Chinese font family")
    args = parser.parse_args()
    available = {font.name for font in font_manager.fontManager.ttflist}
    defaults = ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC", *CJK_FONTS)
    font = args.font or next((candidate for candidate in defaults if candidate in available), None)
    if font not in available:
        parser.error("Install a Simplified Chinese font or specify its family with --font.")
    warnings.filterwarnings("error", message=r"Glyph .* missing from font")
    allocation(font)
    appeals(font)
    voice(font)


if __name__ == "__main__":
    main()
