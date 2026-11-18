"""Sentiment arc, 30+ vs under-30 signings, all four models, one colour-coded legend per panel.
(Version 4: no confidence bands; y axis 'Sentiment'; each month plotted at its midpoint so the
transfer day sits exactly at x = 0. Month k = days [30.44k, 30.44(k+1)), plotted at k + 0.5.)
(Version 3 of the arc figure: same arcs and bands as a1_age30_arc_numbers.py, no text under
the panels; each panel's legend gives, per group, the average tone before and after the move
and the change in %.)

Average = mean of each signing's mean sentence tone before (-365 to -8 days) or after
(+8 to +365 days). Change % = after / before - 1 (descriptive only: the sentiment scale is signed).

Run: python a1_age30_arc_legend.py <folder with sentences.csv, a1_<m>_scores.csv, a1_<m>_per_signing.csv>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a1_age30_arc import monthly, arc  # noqa: E402

MODELS = [("roberta", "RoBERTa (main)"), ("vader", "VADER"), ("bing", "Bing"),
          ("bing_nofootball", "Bing, no football words")]
SEED = 2805
INK, INK2, MUTED, SURF, GRID = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def levels(ps):
    old = ps.age_at_transfer >= 30
    out = {}
    for g, mask in [("30+", old), ("Under 30", ~old)]:
        b, a = ps.loc[mask, "mean_before"].mean(), ps.loc[mask, "mean_after"].mean()
        out[g] = {"n": int(mask.sum()), "before": b, "after": a, "pct": 100 * (a / b - 1)}
    return out


def main(folder):
    folder = Path(folder)
    days = pd.read_csv(folder / "sentences.csv", usecols=["days_from_transfer"]).days_from_transfer
    rng = np.random.default_rng(SEED)
    lv, arcs = {}, {}
    for m, _ in MODELS:
        lv[m] = levels(pd.read_csv(folder / f"a1_{m}_per_signing.csv"))
        arcs[m] = arc(monthly(folder, m, days), rng)
        print(m, {g: {k: round(v, 4) for k, v in d.items()} for g, d in lv[m].items()})

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 11.5), facecolor=SURF,
                             gridspec_kw={"hspace": 0.62, "wspace": 0.19})
    for ax, (m, title) in zip(axes.ravel(), MODELS):
        a = arcs[m]
        ax.set_facecolor(SURF)
        ax.axvline(0, color=MUTED, lw=1, ls=(0, (3, 3)))
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for g in ["Under 30", "30+"]:
            for side in (False, True):
                d = a[(a.group == g) & ((a.month >= 0) == side)]
                ax.plot(d.month + 0.5, d.mean_smooth, color=COL[g], lw=1.6, alpha=0.9)
        ax.set_xlim(-12.4, 12.4)
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 12])
        ax.set_xlabel("Months from the transfer")
        ax.set_ylabel("Sentiment")
        handles = []
        for g, name in [("30+", "30+"), ("Under 30", "Below 30")]:
            s = lv[m][g]
            pct = f"{s['pct']:+.1f}%".replace("-", "\u2212")
            for lab in [f"{name}, avg sentiment before: {s['before']:.3f}",
                        f"{name}, avg sentiment after: {s['after']:.3f}",
                        f"{name}, \u0394 after vs before: {pct}"]:
                handles.append(Line2D([], [], color=COL[g], lw=2.4, label=lab))
        leg = ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.17), ncol=2,
                        frameon=True, fontsize=8.6, handlelength=1.4, columnspacing=1.4,
                        borderpad=0.6, labelspacing=0.5)
        leg.get_frame().set_edgecolor(GRID)
        leg.get_frame().set_facecolor(SURF)
    fig.text(0.01, 0.008, "Lines: 3-month rolling mean of sentence sentiment, each signing once per month, each month plotted at its midpoint; "
             "dashed vertical line: transfer day (±7 days excluded). 30+: 67 signings; below 30: 753.\nAvg = average of each signing's mean sentiment before (−365 to −8 days) "
             "or after (+8 to +365 days). Δ = after / before − 1 (descriptive only: the sentiment scale is signed).",
             fontsize=7.8, color=INK2)
    fig.subplots_adjust(left=0.055, right=0.975, top=0.96, bottom=0.15)
    fig.savefig(folder / "fig_h2_arc_sentiment.png", dpi=200, facecolor=SURF)
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1])
