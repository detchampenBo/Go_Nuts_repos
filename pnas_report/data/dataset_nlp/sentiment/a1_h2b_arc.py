"""Sentiment arc, 30+ vs under-30 signings, ADJUSTED for the H2b controls (same style as
fig_h2_arc_sentiment.png: four models, no bands, months at their midpoints, legend per panel).

Usage: python a1_h2b_arc.py <Project folder> <Full folder with a1_h2b_controls.csv> <out png> <out csv>

Adjusted tone = the "all controls" version of a1_h2b_controls.py:
  * main sample (no liveblogs, no match reports), sentences with quotation marks dropped;
  * article-type adjusted: score - mean of its article type in its period + mean of the period;
  * signings with >= 5 such sentences before and after (65 aged 30+, 728 under 30);
  * fame (log 1 + articles before), log market value and transfer season held at the sample average:
    per period, OLS of the signing's level on [30+ dummy, season dummies, log fame, log value];
    every monthly value of a signing is shifted by -(its controls' fitted part - the sample mean of it),
    using the before coefficients for months < 0 and the after coefficients for months >= 0.
With this, the gap between the groups' average adjusted level equals the 30+ coefficient tested in
a1_h2b_controls.csv (checked below). Lines: each signing averaged per month, then across signings,
3-month rolling mean, smoothed separately before / after the transfer.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

P, FULL, OUTPNG, OUTCSV = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
MODELS = [("roberta", "RoBERTa (main)", "RoBERTa"), ("vader", "VADER", "VADER"), ("bing", "Bing", "Bing"),
          ("bing_nofootball", "Bing, no football words", "Bing, no football words")]
SPEC = "7 all: no quotes, type adjusted, fame + value"
INK, INK2, MUTED, SURF, GRID = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e4e3df"
COL = {"Under 30": "#2a78d6", "30+": "#eb6834"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "axes.spines.top": False, "axes.spines.right": False})

sg = pd.read_csv(P / "signings.csv").set_index("signing_id")
sg["old30"] = sg.age_at_transfer >= 30
sent = pd.read_csv(P / "sentences.csv", usecols=["article_id", "signing_id", "days_from_transfer", "sentence"])
sent["quoted"] = sent.sentence.fillna("").str.contains("“|”|\"", regex=True)
ap = pd.read_csv(P / "article_player.csv", usecols=["article_id", "signing_id", "period", "mentions"])
sg["log_fame"] = np.log1p(ap[(ap.period == "before") & (ap.mentions >= 1)].groupby("signing_id")
                          .article_id.nunique().reindex(sg.index).fillna(0))
sg["log_value"] = np.log(sg.market_value_in_eur)
ctl = pd.read_csv(FULL / "a1_h2b_controls.csv", encoding="utf-8-sig")


def fp(p):
    return "p < 0.001" if p < 0.001 else (f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}")


out, panels = [], {}
for m, title, key in MODELS:
    s = pd.read_csv(P / "Full" / f"a1_{m}_scores.csv", encoding="utf-8-sig")
    assert (sent.loc[s.sentence_row, "article_id"].to_numpy() == s.article_id.to_numpy()).all()
    s["quoted"] = sent.loc[s.sentence_row, "quoted"].to_numpy()
    s["days"] = sent.loc[s.sentence_row, "days_from_transfer"].to_numpy()
    s = s[~s.article_type.isin(["liveblog", "matchreport"])].copy()
    s["adj"] = s.score - s.groupby(["article_type", "period"]).score.transform("mean") \
        + s.groupby("period").score.transform("mean")
    s = s[~s.quoted & s.period.isin(["before", "after"])]
    lv = s.groupby(["signing_id", "period"]).adj.agg(["mean", "size"]).unstack("period")
    lv.columns = [f"{a}_{b}" for a, b in lv.columns]
    lv = lv.dropna().query("size_before >= 5 and size_after >= 5")
    d = lv.join(sg[["old30", "season", "log_fame", "log_value"]])
    S = pd.get_dummies(d.season, drop_first=True).to_numpy(float)
    C = np.column_stack([S, d[["log_fame", "log_value"]].to_numpy(float)])
    X = np.column_stack([np.ones(len(d)), d.old30.to_numpy(float), C])
    shift, res = {}, {}
    for per in ["before", "after"]:
        beta = np.linalg.lstsq(X, d[f"mean_{per}"].to_numpy(float), rcond=None)[0]
        part = C @ beta[2:]
        shift[per] = pd.Series(part - part.mean(), index=d.index)
        adjlev = d[f"mean_{per}"] - shift[per]
        g = adjlev[d.old30].mean() - adjlev[~d.old30].mean()
        tested = ctl[(ctl.model == key) & (ctl.spec == SPEC) & (ctl.period == per)].iloc[0]
        assert abs(g - beta[1]) < 1e-9 and abs(g - tested.gap_30plus_minus_under30) < 5e-5, (m, per, g, tested)
        res[per] = {"30+": adjlev[d.old30].mean(), "Under 30": adjlev[~d.old30].mean(),
                    "gap": g, "p": tested.p_within_season}
    # monthly arc on the adjusted scores
    t = s[s.signing_id.isin(d.index)].copy()
    t["month"] = np.floor(t.days / 30.44).clip(-12, 11).astype(int)
    sm = t.groupby(["signing_id", "month"]).adj.mean().reset_index()
    sm["adj"] -= np.where(sm.month < 0, sm.signing_id.map(shift["before"]), sm.signing_id.map(shift["after"]))
    sm["group"] = np.where(sm.signing_id.map(sg.old30), "30+", "Under 30")
    a = sm.groupby(["group", "month"]).adj.agg(["mean", "size"]).reset_index()
    a["smooth"] = np.nan
    for (g, side), idx in a.groupby([a.group, a.month >= 0]).groups.items():
        a.loc[idx, "smooth"] = a.loc[idx, "mean"].rolling(3, center=True, min_periods=2).mean()
    a["model"] = title
    out.append(a)
    panels[m] = (a, res, int(d.old30.sum()), int((~d.old30).sum()))
    print(title, {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in res.items()})

pd.concat(out).rename(columns={"size": "signings"}).round(4).to_csv(OUTCSV, index=False, encoding="utf-8-sig")

fig, axes = plt.subplots(2, 2, figsize=(13.5, 11.5), facecolor=SURF, gridspec_kw={"hspace": 0.62, "wspace": 0.19})
for ax, (m, title, _) in zip(axes.ravel(), MODELS):
    a, res, n_old, n_young = panels[m]
    ax.set_facecolor(SURF)
    ax.axvline(0, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for g in ["Under 30", "30+"]:
        for side in (False, True):
            dd = a[(a.group == g) & ((a.month >= 0) == side)]
            ax.plot(dd.month + 0.5, dd.smooth, color=COL[g], lw=1.6, alpha=0.9)
    ax.set_xlim(-12.4, 12.4)
    ax.set_title(title, loc="left", fontsize=11, pad=20)
    gb, ga = res["before"], res["after"]
    ax.text(0, 1.015, f"gap 30+ minus below 30: before {gb['gap']:+.3f} ({fp(gb['p'])}), "
            f"after {ga['gap']:+.3f} ({fp(ga['p'])})".replace("-", "−"),
            transform=ax.transAxes, fontsize=8.6, color=INK2, va="bottom", ha="left")
    ax.set_xticks([-12, -9, -6, -3, 0, 3, 6, 9, 12])
    ax.set_xlabel("Months from the transfer")
    ax.set_ylabel("Sentiment, adjusted")
    handles = []
    for g, name in [("30+", "30+"), ("Under 30", "Below 30")]:
        b, af = res["before"][g], res["after"][g]
        pct = f"{100 * (af / b - 1):+.1f}%".replace("-", "−")
        for lab in [f"{name}, avg sentiment before: {b:.3f}", f"{name}, avg sentiment after: {af:.3f}",
                    f"{name}, Δ after vs before: {pct}"]:
            handles.append(Line2D([], [], color=COL[g], lw=2.4, label=lab))
    leg = ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.17), ncol=2, frameon=True,
                    fontsize=8.6, handlelength=1.4, columnspacing=1.4, borderpad=0.6, labelspacing=0.5)
    leg.get_frame().set_edgecolor(GRID)
    leg.get_frame().set_facecolor(SURF)
fig.text(0.01, 0.008, "Adjusted sentiment: quoted sentences dropped; each sentence compared with its article type (news, features, ...); "
         "coverage before the move, market value and transfer season held at the sample average.\n"
         f"Lines: 3-month rolling mean, each signing once per month, months at their midpoints; dashed line: transfer day (±7 days excluded). "
         f"30+: {n_old} signings; below 30: {n_young}.\nGap p: 5,000 shuffles of the 30+ label within season. "
         "Δ = after / before − 1 (descriptive only).", fontsize=7.8, color=INK2)
fig.subplots_adjust(left=0.055, right=0.975, top=0.95, bottom=0.175)
fig.savefig(OUTPNG, dpi=200, facecolor=SURF)
print("saved", OUTPNG)
