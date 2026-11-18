"""Paper-size version (17.8 cm wide, PDF) of the adjusted H2b sentiment arc.

Usage: python a1_h2b_arc_paper.py <Full folder> <out.pdf>
Reads a1_h2b_arc.csv (monthly adjusted means, from a1_h2b_arc.py) and a1_h2b_controls.csv
(tested gaps, all-controls spec). Nothing is recomputed: same lines as fig_h2b_arc_controls.png,
compact layout (2 x 2, one shared legend, gap + p under each panel title).
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

FULL, OUT = Path(sys.argv[1]), Path(sys.argv[2])
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
arc = pd.read_csv(FULL / "a1_h2b_arc.csv", encoding="utf-8-sig")
ctl = pd.read_csv(FULL / "a1_h2b_controls.csv", encoding="utf-8-sig")
SPEC = "7 all: no quotes, type adjusted, fame + value"
MODELS = [("RoBERTa (main)", "RoBERTa"), ("VADER", "VADER"), ("Bing", "Bing"),
          ("Bing, no football words", "Bing, no football words")]


def fp(p):
    return "P < 0.001" if p < 0.001 else (f"P = {p:.3f}" if p < 0.01 else f"P = {p:.2f}")


fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.6), gridspec_kw={"hspace": 0.55, "wspace": 0.18})
for ax, (title, key), letter in zip(axes.ravel(), MODELS, "ABCD"):
    a = arc[arc.model == title]
    ax.axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3)))
    ax.axhline(0, color=GRID, lw=0.8)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for g in ["Under 30", "30+"]:
        for side in (False, True):
            d = a[(a.group == g) & ((a.month >= 0) == side)]
            ax.plot(d.month + 0.5, d.smooth, color=COL[g], lw=1.4)
    r = {per: ctl[(ctl.model == key) & (ctl.spec == SPEC) & (ctl.period == per)].iloc[0] for per in ["before", "after"]}
    ax.set_title(f"{letter}  {title}", loc="left", fontsize=8, fontweight="bold", pad=13)
    ax.text(0, 1.02, (f"gap before {r['before'].gap_30plus_minus_under30:+.3f} ({fp(r['before'].p_within_season)}), "
                      f"after {r['after'].gap_30plus_minus_under30:+.3f} ({fp(r['after'].p_within_season)})").replace("-", "−"),
            transform=ax.transAxes, fontsize=6.5, color=INK2, va="bottom")
    ax.set_xlim(-12.4, 12.4)
    ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 12])
    if letter in "CD":
        ax.set_xlabel("Months from the transfer")
    if letter in "AC":
        ax.set_ylabel("Sentiment, adjusted")
handles = [Line2D([], [], color=COL["30+"], lw=1.8, label="30+ (65 signings)"),
           Line2D([], [], color=COL["Under 30"], lw=1.8, label="Under 30 (728 signings)")]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1.02), ncol=2, frameon=False, fontsize=7)
fig.savefig(OUT, bbox_inches="tight")
print("saved", OUT)
