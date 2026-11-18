"""Tone arc around the transfer (Week 7 'emotional arc' style): 30+ vs under-30 signings.

x = months from the transfer (-12 ... +11), y = sentence tone. Each signing is averaged per
month first, so every signing counts once per month (heavily covered stars don't dominate).
Lines = 3-month rolling mean, smoothed separately before and after the transfer so the break
isn't blurred; bands = 95% bootstrap interval over signings (computed per month, then smoothed).
Same main sample as the H2 test: no liveblogs or match reports, only the 820 signings with
>= 5 sentences before and after, and the +-7-day announcement window left out.

Run: python a1_age30_arc.py <folder with sentences.csv + a1_<method>_scores.csv +
     a1_<method>_per_signing.csv> [methods, default roberta,vader]
Writes fig_h2_arc.png and a1_age30_arc.csv in that folder.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TITLES = {"roberta": "RoBERTa (main)", "vader": "VADER", "bing": "Bing",
          "bing_nofootball": "Bing, no football words"}
N_BOOT, SEED, MIN_SIGNINGS = 2000, 2805, 5
INK, INK2, MUTED, SURF, GRID = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def monthly(folder, method, days):
    sc = pd.read_csv(folder / f"a1_{method}_scores.csv")
    keep = set(pd.read_csv(folder / f"a1_{method}_per_signing.csv").signing_id)
    ps = pd.read_csv(folder / f"a1_{method}_per_signing.csv").set_index("signing_id")
    s = sc[sc.signing_id.isin(keep) & sc.period.isin(["before", "after"])
           & ~sc.article_type.isin(["liveblog", "matchreport"])].copy()
    s["days"] = days.reindex(s.sentence_row).to_numpy()
    s["month"] = np.floor(s.days / 30.44).clip(-12, 11).astype(int)
    s["group"] = np.where(ps.age_at_transfer.reindex(s.signing_id).to_numpy() >= 30, "30+", "Under 30")
    return s.groupby(["group", "month", "signing_id"]).score.mean().reset_index()


def arc(sm, rng):
    rows = []
    for (g, mo), d in sm.groupby(["group", "month"]):
        x = d.score.to_numpy()
        lo, hi = (np.percentile(rng.choice(x, (N_BOOT, len(x))).mean(1), [2.5, 97.5])
                  if len(x) >= MIN_SIGNINGS else (np.nan, np.nan))
        rows.append({"group": g, "month": mo, "signings": len(x), "mean": x.mean(), "lo": lo, "hi": hi})
    a = pd.DataFrame(rows).sort_values(["group", "month"])
    out = []
    for (g, side), d in a.groupby([a.group, a.month >= 0]):          # smooth each side separately
        d = d.copy()
        for c in ["mean", "lo", "hi"]:
            d[c + "_smooth"] = d[c].rolling(3, center=True, min_periods=2).mean()
        out.append(d)
    return pd.concat(out).sort_values(["group", "month"])


def main(folder, methods):
    folder = Path(folder)
    days = pd.read_csv(folder / "sentences.csv", usecols=["days_from_transfer"]).days_from_transfer
    rng = np.random.default_rng(SEED)
    arcs = {m: arc(monthly(folder, m, days), rng) for m in methods}
    pd.concat([a.assign(method=TITLES[m]) for m, a in arcs.items()]).round(4).to_csv(
        folder / "a1_age30_arc.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, len(methods), figsize=(5.6 * len(methods), 4.3), facecolor=SURF,
                             sharex=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, methods):
        a = arcs[m]
        ax.set_facecolor(SURF)
        ax.axvline(-0.5, color=MUTED, lw=1, ls=(0, (3, 3)))
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for g in ["Under 30", "30+"]:
            for side in (False, True):                                  # draw before/after apart
                d = a[(a.group == g) & ((a.month >= 0) == side)]
                ax.fill_between(d.month, d.lo_smooth, d.hi_smooth, color=COL[g], alpha=0.14, lw=0)
                ax.plot(d.month, d.mean_smooth, color=COL[g], lw=2,
                        label=g if not side else None)
        ax.set_title(TITLES[m], loc="left", fontsize=11)
        ax.set_xlabel("Months from the transfer")
        ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 11])
        ax.text(-0.3, 1.0, "transfer", transform=ax.get_xaxis_transform(), fontsize=8,
                color=INK2, va="top")
    axes[0].set_ylabel("Sentence tone (3-month rolling mean)")
    n = arcs[methods[0]].groupby("group").signings.max()
    handles, labels = axes[0].get_legend_handles_labels()
    labels = [f"{l} ({'753' if l == 'Under 30' else '67'} signings)" for l in labels]
    fig.legend(handles, labels, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=2,
               fontsize=9)
    fig.text(0.01, 0.01, "Each signing averaged per month, then averaged across signings; bands = 95% "
             "bootstrap interval over signings. Liveblogs, match reports and the ±7 days around "
             "the transfer left out.", fontsize=8, color=INK2)
    plt.tight_layout(rect=(0, 0.05, 1, 0.92))
    fig.savefig(folder / "fig_h2_arc.png", dpi=200, facecolor=SURF)
    plt.close(fig)
    for m, a in arcs.items():
        print(TITLES[m]); print(a.pivot(index="month", columns="group", values="signings").T.to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2].split(",") if len(sys.argv) > 2 else ["roberta", "vader"])
