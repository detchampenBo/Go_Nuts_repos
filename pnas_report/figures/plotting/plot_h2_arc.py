"""Raw sentiment arc (H2): 30+ vs under-30 signings, four models, months from the transfer.

Run: python plot_h2_arc.py
Reads data/a1_h2_arc_4models.csv (monthly means, same numbers as fig_h2_arc_sentiment.png) and
data/signing_tone.csv (group averages before / after for the panel subtitles).
Writes out/fig_h2_arc.pdf and out/fig_h2_arc.png (17.8 cm wide, PNAS full width).

No controls here: this is the raw tone. The adjusted version is plot_h2b_arc.py.
Months: month k covers days [30.44k, 30.44(k+1)) and is drawn at x = k + 0.5, so x = 0 is the
transfer day. Before (k < 0) and after (k >= 0) are separate lines; the +-7 days around the
transfer are not in the data.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA, OUTDIR = HERE / "data", HERE / "out"
OUTDIR.mkdir(exist_ok=True)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})

arc = pd.read_csv(DATA / "a1_h2_arc_4models.csv")
st = pd.read_csv(DATA / "signing_tone.csv", encoding="utf-8-sig")
st = st[st.in_main_sample]
MODELS = [("RoBERTa (main)", "roberta"), ("VADER", "vader"), ("Bing", "bing"),
          ("Bing, no football words", "bing_nofootball")]
n_old, n_young = int(st.age30plus.sum()), int((~st.age30plus).sum())

fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.6), gridspec_kw={"hspace": 0.55, "wspace": 0.18})
for ax, (title, col), letter in zip(axes.ravel(), MODELS, "ABCD"):
    a = arc[arc.model == title]
    ax.axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3)))
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for g in ["Under 30", "30+"]:
        for side in (False, True):
            d = a[(a.group == g) & ((a.month >= 0) == side)]
            ax.plot(d.month + 0.5, d.mean_smooth, color=COL[g], lw=1.4)
    old = st[st.age30plus]
    young = st[~st.age30plus]
    sub = (f"30+ {old[col + '_before'].mean():.3f}→{old[col + '_after'].mean():.3f}, "
           f"under 30 {young[col + '_before'].mean():.3f}→{young[col + '_after'].mean():.3f}")
    ax.set_title(f"{letter}  {title}", loc="left", fontsize=8, fontweight="bold", pad=13)
    ax.text(0, 1.02, "avg before→after: " + sub, transform=ax.transAxes, fontsize=6, color=INK2, va="bottom")
    ax.set_xlim(-12.4, 12.4)
    ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 12])
    if letter in "CD":
        ax.set_xlabel("Months from the transfer")
    if letter in "AC":
        ax.set_ylabel("Sentiment")
handles = [Line2D([], [], color=COL["30+"], lw=1.8, label=f"30+ ({n_old} signings)"),
           Line2D([], [], color=COL["Under 30"], lw=1.8, label=f"Under 30 ({n_young} signings)")]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 1.02), ncol=2, frameon=False, fontsize=7)
for ext in ("pdf", "png"):
    fig.savefig(OUTDIR / f"fig_h2_arc.{ext}", bbox_inches="tight", dpi=300)
print("saved out/fig_h2_arc.pdf/.png")
