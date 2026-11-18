"""Paper figure for H2b + coverage: 30+ vs under-30 signings, tone gap and coverage ratio.

Usage: python a1_h2b_figure.py <Full folder> <out png>
Reads a1_h2b_controls.csv and a1_coverage_age.csv (outputs of a1_h2b_controls.py and
a1_coverage_age.py). Three panels:
  A, B  tone gap (30+ minus under 30) before / after the move, four models,
        no controls (hollow grey) vs all controls (filled blue: no quotes, type adjusted,
        fame + market value, season dummies)
  C     coverage ratio (30+ / under 30, articles naming the player), log scale,
        season only (hollow grey) vs + market value (filled blue)
Intervals: obs +- 1.96 SD of the 5,000 within-season shuffles (ratio: exp of that).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

FULL, OUTPNG = Path(sys.argv[1]), Path(sys.argv[2])
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#ffffff"
BASE, CTRL = MUTED, "#2a78d6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "savefig.facecolor": SURF})

h = pd.read_csv(FULL / "a1_h2b_controls.csv", encoding="utf-8-sig")
c = pd.read_csv(FULL / "a1_coverage_age.csv", encoding="utf-8-sig")
MODELS = ["RoBERTa", "VADER", "Bing", "Bing, no football words"]
LABEL = {"RoBERTa": "RoBERTa (main)", "VADER": "VADER", "Bing": "Bing",
         "Bing, no football words": "Bing, no\nfootball words"}
S0, S1 = "1 no controls (as 11 Nov)", "7 all: no quotes, type adjusted, fame + value"
OFF = 0.17


def fp(p):
    return "p<0.001" if p < 0.001 else (f"p={p:.3f}" if p < 0.01 else f"p={p:.2f}")


def point(ax, y, x, lo, hi, filled, col):
    ax.plot([lo, hi], [y, y], color=col, lw=1.6, solid_capstyle="round", zorder=2)
    ax.plot(x, y, "o", ms=5.5, mfc=col if filled else SURF, mec=col, mew=1.6, zorder=3)


fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.75), gridspec_kw={"width_ratios": [1, 1, 1.05], "wspace": 0.16})
ys = np.arange(len(MODELS))[::-1]
for ax, period, title in [(axes[0], "before", "A  Tone, year before the move"),
                          (axes[1], "after", "B  Tone, year after the move")]:
    for y, m in zip(ys, MODELS):
        for spec, dy, filled, col in [(S0, OFF, False, BASE), (S1, -OFF, True, CTRL)]:
            r = h[(h.model == m) & (h.spec == spec) & (h.period == period)].iloc[0]
            point(ax, y + dy, r.gap_30plus_minus_under30, r.ci_lo, r.ci_hi, filled, col)
            ax.text(0.165, y + dy, fp(r.p_within_season), va="center", ha="right", fontsize=6.3,
                    color=INK if (filled and r.p_within_season < 0.05) else MUTED)
    ax.axvline(0, color=INK2, lw=0.8, zorder=1)
    ax.set_xlim(-0.2, 0.17)
    ax.set_xticks([-0.1, 0, 0.1])
    ax.set_xticklabels(["−0.1", "0", "+0.1"])
    ax.set_title(title, loc="left", fontsize=8, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([LABEL[m] for m in MODELS] if period == "before" else [])
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.6, len(MODELS) - 0.4)

ax = axes[2]
rows = [("before", "Before"), ("after", "After"), ("change", "Growth,\nafter / before")]
cy = np.arange(len(rows))[::-1]
for y, (period, lab) in zip(cy, rows):
    for spec, dy, filled, col in [("season only", OFF, False, BASE), ("+ market value", -OFF, True, CTRL)]:
        r = c[(c.articles == "all article types") & (c.spec == spec) & (c.period == period)].iloc[0]
        point(ax, y + dy, r.ratio_30plus_vs_under30, r.ratio_lo, r.ratio_hi, filled, col)
        ax.text(r.ratio_hi * 1.1, y + dy, f"{r.ratio_30plus_vs_under30:.2f}×", va="center", fontsize=6.3,
                color=INK if filled else MUTED)
ax.axvline(1, color=INK2, lw=0.8, zorder=1)
ax.set_xscale("log")
ax.set_xlim(0.4, 9)
ax.set_xticks([0.5, 1, 2, 4])
ax.set_xticklabels(["0.5×", "1×", "2×", "4×"])
ax.minorticks_off()
ax.set_yticks(cy)
ax.set_yticklabels([r[1] for r in rows])
ax.yaxis.tick_right()
ax.tick_params(axis="y", length=0)
ax.set_ylim(-0.6, len(rows) - 0.4)
ax.grid(axis="x", color=GRID, lw=0.6)
ax.set_axisbelow(True)
ax.set_xlabel("Guardian articles, 30+ / under 30")
ax.set_title("C  Coverage volume", loc="left", fontsize=8, fontweight="bold")

leg1 = [Line2D([], [], marker="o", ls="-", color=BASE, mfc=SURF, mew=1.6, ms=5.5, label="no controls"),
        Line2D([], [], marker="o", ls="-", color=CTRL, mew=1.6, ms=5.5,
               label="all controls (fame, market value, article type, no quotes)")]
leg2 = [Line2D([], [], marker="o", ls="-", color=BASE, mfc=SURF, mew=1.6, ms=5.5, label="season only"),
        Line2D([], [], marker="o", ls="-", color=CTRL, mew=1.6, ms=5.5, label="+ market value")]
fig.legend(handles=leg1, loc="lower left", bbox_to_anchor=(0.06, -0.02), ncol=2, frameon=False, fontsize=6.8)
fig.legend(handles=leg2, loc="lower right", bbox_to_anchor=(0.97, -0.02), ncol=2, frameon=False, fontsize=6.8)
fig.text(0.39, 0.155, "Tone gap, 30+ minus under 30 (mean sentence tone, scale −1 to 1)", ha="center", color=INK2, fontsize=7.5)
n0 = h[(h.spec == S0) & (h.model == "RoBERTa")].iloc[0]
fig.text(0.06, -0.075, f"Tone: {n0.n_30plus} vs {n0.n_under30} signings (all controls: 65 vs 728); coverage: 88 vs 1,244. "
         "All models adjust for transfer season. Bars: 95% interval from 5,000 shuffles of the 30+ label within season; "
         "p two-sided.", fontsize=6, color=INK2)
fig.subplots_adjust(left=0.115, right=0.93, top=0.9, bottom=0.27)
fig.savefig(OUTPNG, dpi=300, bbox_inches="tight")
print("saved", OUTPNG)
