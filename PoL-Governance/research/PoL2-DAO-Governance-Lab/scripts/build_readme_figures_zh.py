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


def sweep_canvas(font, nrows, title, subtitle):
    from matplotlib import rcParams

    single_row = nrows == 1
    fig, grid = new_figure(nrows=nrows, ncols=2, panel=(5.9, 5.6 if single_row else 4.4))
    rcParams["font.family"] = [font, "DejaVu Sans"]
    fig.subplots_adjust(left=0.10, right=0.966, bottom=0.15 if single_row else 0.085,
                        top=0.63 if single_row else 0.75, wspace=0.26, hspace=0.37)
    fig.text(0.10, 0.955, title, fontsize=24, weight="bold", va="top", color=PALETTE["ink"])
    fig.text(0.10, 0.868 if single_row else 0.900, subtitle, fontsize=14,
             va="top", color=PALETTE["ink_soft"])
    for ax in grid.flat:
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    return fig, grid


def sweep(ax, rows, x_key, metric, label, color, linestyle, marker, *, interval=False):
    rows = sorted(rows, key=lambda row: float(row[x_key]))
    x = [float(row[x_key]) for row in rows]
    y = [float(row[metric]) for row in rows]
    errors = [float(row[f"{metric}_ci"]) for row in rows] if interval else None
    return plot_line(ax, x, y, color=color, ls=linestyle, marker=marker, label=label, err=errors)


def percentage_x(ax, ticks, label):
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlabel(label)


def sweep_legend(fig, ax, *, single_row):
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.090, 0.813 if single_row else 0.870),
               ncol=len(labels), columnspacing=1.25, handletextpad=0.55)


def needs_sensitivity(font):
    rows = table("e14_needs_report.csv")
    fig, (axes,) = sweep_canvas(font, 1, "申报量夸大后，分配规则怎样影响诚实申报者",
                               "E14　虚报者将需求报为实际的两倍，核验情景假设查获概率为 50%")
    rules = (
        ("R1", "按申报量比例配给", PALETTE["neutral_dark"], "--", "s"),
        ("R2", "按共同上限配给", PALETTE["teal"], "-.", "^"),
        ("R3", "按共同上限配给并核验", FOCUS, "-", "o"),
    )
    panels = (
        ("honest_fill", "诚实申报者的需求满足率 ↑", (0.35, 0.85), [0.40, 0.50, 0.60, 0.70, 0.80]),
        ("efficiency", "资源用于真实需求的比例 ↑", (0.90, 1.005), [0.90, 0.92, 0.94, 0.96, 0.98, 1]),
    )
    for ax, (metric, title, limits, ticks) in zip(axes, panels):
        for rule, label, color, linestyle, marker in rules:
            sweep(ax, [row for row in rows if row["rule"] == rule], "f", metric,
                  label, color, linestyle, marker, interval=True)
        ax.set_title(title, loc="left")
        ax.set_ylim(*limits)
        ax.set_yticks(ticks)
        percentage_x(ax, [0, 0.10, 0.20, 0.30, 0.40, 0.50], "把需求报为两倍的主体比例")
    sweep_legend(fig, axes[0], single_row=True)
    finalize_figure(fig, FIGURES / "readme_publicization_needs_sensitivity_zh", tight=False)


def allocation_sensitivity(font):
    rows = table("e16_nonmarket_allocation.csv")
    fig, axes = sweep_canvas(font, 2, "不同虚报比例下，三种轮转规则怎样分配资源",
                            "E16　同级内按申报满足比例和轮转分配。供给骤减时，供给约为真实需求的 10%")
    rules = (
        ("equal_rotation", "全体同级轮转", PALETTE["neutral_dark"], "--", "s"),
        ("floor_then_priority", "供给足够时先保一单位", PALETTE["teal"], "-.", "^"),
        ("needs_priority", "按紧急等级分配", FOCUS, "-", "o"),
    )
    panels = (
        ("critical_fill", "全部轮次紧急需求满足率 ↑", (0.50, 1), [0.50, 0.60, 0.70, 0.80, 0.90, 1]),
        ("shock_critical_fill", "供给骤减时紧急需求满足率 ↑", (0, 0.60), [0, 0.15, 0.30, 0.45, 0.60]),
        ("weighted_fill", "按紧急等级加权的满足率 ↑", (0.50, 0.75), [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]),
        ("real_use", "资源用于真实需求的比例 ↑", (0.75, 1.015), [0.75, 0.80, 0.85, 0.90, 0.95, 1]),
    )
    for ax, (metric, title, limits, ticks) in zip(axes.flat, panels):
        for rule, label, color, linestyle, marker in rules:
            line = sweep(ax, [row for row in rows if row["rule"] == rule], "inflation_share", metric,
                         label, color, linestyle, marker)
            if rule == "floor_then_priority":
                line.set_markersize(12)
                line.set_markerfacecolor("none")
        ax.set_title(title, loc="left")
        ax.set_ylim(*limits)
        ax.set_yticks(ticks)
        percentage_x(ax, [0, 0.10, 0.20, 0.30, 0.40], "把需求报为两倍的主体比例")
    for ax in axes[0]:
        ax.set_xlabel("")
    sweep_legend(fig, axes[0, 0], single_row=False)
    finalize_figure(fig, FIGURES / "readme_publicization_allocation_sensitivity_zh", tight=False)


def appeals_sensitivity(font):
    rows = table("e17_priority_appeals.csv")
    fig, axes = sweep_canvas(font, 2, "增加申诉复核容量，能否改善紧急需求满足率",
                            "E17　虚报者夸大数量并尝试报为最高等级。四个面板分别显示两档初判错误率与供给情景")
    claims = (
        ("0.0", "无人虚报", PALETTE["neutral_dark"], "--", "s"),
        ("0.15", "15% 的主体虚报", PALETTE["teal"], "-.", "^"),
        ("0.3", "30% 的主体虚报", PALETTE["red_strong"], "-", "o"),
    )
    panels = (
        ("critical_fill", "全部轮次", (0.82, 0.94), [0.82, 0.85, 0.88, 0.91, 0.94]),
        ("shock_critical_fill", "供给骤减轮次", (0.36, 0.52), [0.36, 0.40, 0.44, 0.48, 0.52]),
    )
    for row_axes, error in zip(axes, ("0.1", "0.25")):
        for ax, (metric, title, limits, ticks) in zip(row_axes, panels):
            for claim, label, color, linestyle, marker in claims:
                selected = [row for row in rows if row["classification_error"] == error
                            and row["false_priority_claimants"] == claim]
                line = sweep(ax, selected, "appeal_capacity", metric, label, color, linestyle, marker, interval=True)
                if error == "0.1" and claim == "0.3":
                    for x, y in zip(line.get_xdata()[::2], line.get_ydata()[::2]):
                        offset = -11 if metric == "critical_fill" else -15
                        ax.annotate(f"{y:.1%}", (x, y), xytext=(0, offset), textcoords="offset points",
                                    color=color, ha="center", va="top", fontsize=12)
            ax.set_title(f"初判错误率 {float(error):.0%} · {title}", loc="left")
            ax.set_ylim(*limits)
            ax.set_yticks(ticks)
            ax.set_xlim(-0.022, 0.272)
            percentage_x(ax, [0, 0.10, 0.25], "每轮复核容量（占全部主体的比例）")
    for ax in axes[0]:
        ax.set_xlabel("")
    sweep_legend(fig, axes[0, 0], single_row=False)
    finalize_figure(fig, FIGURES / "readme_publicization_appeals_sensitivity_zh", tight=False)


def oversight(font):
    reviews = table("e15_reviewer_correlation.csv")
    escalation = table("e15_escalation.csv")
    fig, ((left, right),) = sweep_canvas(font, 1, "审核结果高度相关时，增加审核者的收益有限",
                                        "E15　模型计算，正常项目的误拒率控制在 10% 或更低。两种审核安排分别计算")
    for rho, color, linestyle, marker in (
        ("0.0", PALETTE["neutral_dark"], "--", "s"),
        ("0.5", PALETTE["teal"], "-.", "^"),
        ("0.9", PALETTE["red_strong"], "-", "o"),
    ):
        selected = [row for row in reviews if row["rule"] == "mean" and row["rho"] == rho]
        sweep(left, selected, "n", "harmful_passed", f"审核分数相关度 {float(rho):g}", color, linestyle, marker)
    left.set_title("多个审核者的分数取平均", loc="left")
    left.set_xticks([1, 2, 3, 5, 7])
    left.set_xlabel("审核者人数")
    left.set_ylabel("有害项目被放行的比例 ↓")
    sweep(right, escalation, "escalated", "fa", "独立人工复核", FOCUS, "-", "o")
    right.set_title("把不确定的项目交给独立人工", loc="left")
    percentage_x(right, [0, 0.10, 0.20, 0.30, 0.40, 0.50], "实际转交人工复核的比例")
    point = select(escalation, escalation_budget="0.2")
    x, y = float(point["escalated"]), float(point["fa"])
    right.annotate(f"复核 {x:.1%}\n有害放行 {y:.1%}", (x, y), xytext=(25, 24), textcoords="offset points",
                   color=FOCUS, fontsize=12, arrowprops={"arrowstyle": "-", "color": FOCUS})
    for ax in (left, right):
        ax.set_ylim(0, 0.26)
        ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20, 0.25])
    sweep_legend(fig, left, single_row=True)
    finalize_figure(fig, FIGURES / "readme_publicization_oversight_zh", tight=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="installed Simplified Chinese font family")
    parser.add_argument("--detail-only", action="store_true", help="render only the sensitivity and oversight figures")
    args = parser.parse_args()
    available = {font.name for font in font_manager.fontManager.ttflist}
    defaults = ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC", *CJK_FONTS)
    font = args.font or next((candidate for candidate in defaults if candidate in available), None)
    if font not in available:
        parser.error("Install a Simplified Chinese font or specify its family with --font.")
    warnings.filterwarnings("error", message=r"Glyph .* missing from font")
    if not args.detail_only:
        allocation(font)
        appeals(font)
        voice(font)
    needs_sensitivity(font)
    allocation_sensitivity(font)
    appeals_sensitivity(font)
    oversight(font)


if __name__ == "__main__":
    main()
