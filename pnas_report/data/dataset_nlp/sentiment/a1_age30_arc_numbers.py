"""Tone arc, 30+ vs under-30 signings, all four models, with the gaps stated under each panel.
(Version 2 of a1_age30_arc_gaps.py: no period-mean lines or brackets on the plot; numbers below.)

Per panel (one per sentiment model):
  * the monthly arc (as in a1_age30_arc.py: 3-month rolling mean, each signing once per month,
    95% bootstrap band over signings);
  * each group's period mean (mean of per-signing averages) drawn as a flat line over the before
    and after halves;
  * a box with: before gap and after gap (30+ minus under 30) in tone points and in % of the
    under-30 level, with p (30+ label shuffled within season, 5,000); the change within each group
    from before to after in %; and the gap in change (H2) with p.
Percentages are relative to a positive baseline on a signed scale, so they are descriptive only;
the tests are on the tone points.

Also writes a1_age30_levels_pct.csv and a1_age30_mde.csv (smallest gap detectable with 80% power
at the 5% level, for the real group sizes and for 67 vs 67).

Run: python a1_age30_arc_gaps.py <folder with sentences.csv, a1_<m>_scores.csv, a1_<m>_per_signing.csv>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a1_age30_arc import monthly, arc  # noqa: E402

MODELS = [("roberta", "RoBERTa (main)"), ("vader", "VADER"), ("bing", "Bing"),
          ("bing_nofootball", "Bing, no football words")]
N, SEED = 5000, 2805
INK, INK2, MUTED, SURF, GRID = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def shuffle_p(ps, col):
    d, old, s = ps[col].to_numpy(), (ps.age_at_transfer >= 30).to_numpy(), ps.season.to_numpy()
    obs = d[old].mean() - d[~old].mean()
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(s == x) for x in np.unique(s)]
    null = np.empty(N)
    for i in range(N):
        lab = old.copy()
        for g in groups:
            lab[g] = rng.permutation(old[g])
        null[i] = d[lab].mean() - d[~lab].mean()
    return obs, (np.sum(np.abs(null) >= abs(obs)) + 1) / (N + 1)


def fp(p):
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}"


def mde(sd_old, sd_young, n_old, n_young, z=1.96 + 0.84):
    """Smallest true gap found with 80% power at the 5% level (two-sided, normal approx.)."""
    return z * np.sqrt(sd_old ** 2 / n_old + sd_young ** 2 / n_young)


def main(folder):
    folder = Path(folder)
    days = pd.read_csv(folder / "sentences.csv", usecols=["days_from_transfer"]).days_from_transfer
    rng = np.random.default_rng(SEED)
    rows, mrows, arcs = [], [], {}
    for m, title in MODELS:
        ps = pd.read_csv(folder / f"a1_{m}_per_signing.csv")
        old = ps.age_at_transfer >= 30
        r = {"model": title}
        for col, lab in [("mean_before", "before"), ("mean_after", "after"), ("diff", "change")]:
            gap, p = shuffle_p(ps, col)
            r[f"under30_{lab}"] = ps.loc[~old, col].mean()
            r[f"30plus_{lab}"] = ps.loc[old, col].mean()
            r[f"gap_{lab}"], r[f"p_{lab}"] = gap, p
        for lab in ["before", "after"]:
            r[f"gap_{lab}_pct_of_under30"] = 100 * r[f"gap_{lab}"] / r[f"under30_{lab}"]
        r["change_under30_pct"] = 100 * (r["under30_after"] / r["under30_before"] - 1)
        r["change_30plus_pct"] = 100 * (r["30plus_after"] / r["30plus_before"] - 1)
        rows.append(r)
        for col, lab in [("diff", "change"), ("mean_before", "before")]:
            so, sy = ps.loc[old, col].std(ddof=1), ps.loc[~old, col].std(ddof=1)
            mrows.append({"model": title, "measure": lab,
                          "mde_67_vs_753": mde(so, sy, old.sum(), (~old).sum()),
                          "mde_67_vs_67": mde(so, sy, old.sum(), old.sum()),
                          "observed_gap": r[f"gap_{lab}"]})
        arcs[m] = arc(monthly(folder, m, days), rng)
    res = pd.DataFrame(rows)
    res.round(4).to_csv(folder / "a1_age30_levels_pct.csv", index=False, encoding="utf-8-sig")
    md = pd.DataFrame(mrows)
    md.round(4).to_csv(folder / "a1_age30_mde.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(res.round(3).T.to_string())
    print(md.round(3).to_string(index=False))

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 12), facecolor=SURF,
                             gridspec_kw={"hspace": 0.62, "wspace": 0.16})
    for ax, (m, title) in zip(axes.ravel(), MODELS):
        a, r = arcs[m], res[res.model == title].iloc[0]
        ax.set_facecolor(SURF)
        ax.axvline(-0.5, color=MUTED, lw=1, ls=(0, (3, 3)))
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for g, key in [("Under 30", "under30"), ("30+", "30plus")]:
            for side in (False, True):
                d = a[(a.group == g) & ((a.month >= 0) == side)]
                ax.fill_between(d.month, d.lo_smooth, d.hi_smooth, color=COL[g], alpha=0.12, lw=0)
                ax.plot(d.month, d.mean_smooth, color=COL[g], lw=1.6, alpha=0.9)
        ax.set_xlim(-12.6, 11.6)
        txt = (f"Before the move:  30+ {r['30plus_before']:.3f} vs under 30 {r['under30_before']:.3f}  →  "
               f"gap {r['gap_before']:+.3f} ({r['gap_before_pct_of_under30']:+.0f}%), {fp(r['p_before'])}\n"
               f"After the move:   30+ {r['30plus_after']:.3f} vs under 30 {r['under30_after']:.3f}  →  "
               f"gap {r['gap_after']:+.3f} ({r['gap_after_pct_of_under30']:+.0f}%), {fp(r['p_after'])}\n"
               f"Change (after vs before):  under 30 {r['change_under30_pct']:+.0f}%,  30+ {r['change_30plus_pct']:+.0f}%  →  "
               f"gap in change {r['gap_change']:+.3f}, {fp(r['p_change'])}")
        ax.text(0.0, -0.2, txt, transform=ax.transAxes, va="top", ha="left", fontsize=8.6, color=INK,
                linespacing=1.55)
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 11])
        ax.set_xlabel("Months from the transfer")
        ax.set_ylabel("Sentence tone")
    handles = [Line2D([], [], color=COL["Under 30"], lw=1.8, label="Under 30 (753), monthly arc"),
               Line2D([], [], color=COL["30+"], lw=1.8, label="30+ (67), monthly arc"),
               Patch(color=MUTED, alpha=0.25, label="95% bootstrap band"),
               Line2D([], [], color=MUTED, lw=1, ls=(0, (3, 3)), label="Transfer")]
    fig.legend(handles=handles, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=4, fontsize=9)
    fig.text(0.01, 0.006, "Lines: 3-month rolling mean, each signing once per month. Numbers: average of each signing's "
             "mean tone before (−365 to −8 days) and after (+8 to +365 days); gap = 30+ minus under 30.\n% of gap = gap / under-30 level; "
             "% change = after / before − 1 (descriptive only: the tone scale is signed). p: 30+ label shuffled within season (5,000).",
             fontsize=7.8, color=INK2)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.935, bottom=0.17)
    fig.savefig(folder / "fig_h2_arc_numbers.png", dpi=200, facecolor=SURF)
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1])
