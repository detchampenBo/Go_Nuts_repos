"""Coverage volume by age: do 30+ signings get more or fewer Guardian articles than under-30 signings,
before and after joining the Premier League?

Usage: python a1_coverage_age.py <Project folder> <out folder>
Reads article_player.csv and signings.csv. Writes a1_coverage_age.csv.

Unit: signing (all 1,332). Count = distinct Guardian articles naming the player (mentions >= 1)
in the period (before: -365..-8 days, after: +8..+365). Counted with all article types and
without liveblogs. Outcome on the log scale, log(1 + articles); the gap is reported as a ratio
exp(gap) ("30+ get x times the articles"). Change = log(1 + after) - log(1 + before).
Gap = 30+ coefficient with season dummies + controls; p from 5,000 shuffles of the 30+ label
within transfer season (seed 2805), as in a1_age30.py / a1_h2b_controls.py.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

P, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
N, SEED = 5000, 2805

sg = pd.read_csv(P / "signings.csv").set_index("signing_id")
sg["old30"] = sg.age_at_transfer >= 30
sg["log_value"] = np.log(sg.market_value_in_eur)
for pos in ["Defender", "Midfield", "Attack"]:
    sg[f"pos_{pos[:3].lower()}"] = (sg.position == pos).astype(float)
ap = pd.read_csv(P / "article_player.csv", usecols=["article_id", "signing_id", "period", "mentions", "article_type"])
ap = ap[ap.mentions >= 1]


def counts(a):
    c = a[a.period.isin(["before", "after"])].groupby(["signing_id", "period"]).article_id.nunique().unstack()
    c = c.reindex(sg.index).fillna(0)
    return pd.DataFrame({"before": np.log1p(c["before"]), "after": np.log1p(c["after"]),
                         "n_before": c["before"], "n_after": c["after"]})


def gap_test(t, y, controls=()):
    d = t.join(sg[["old30", "season", *[c for c in controls if c in sg.columns]]])
    yv, old, seasons = d[y].to_numpy(float), d.old30.to_numpy(), d.season.to_numpy()
    Z = np.column_stack([pd.get_dummies(d.season).to_numpy(float)] + ([d[list(controls)].to_numpy(float)] if controls else []))
    M = np.eye(len(d)) - Z @ np.linalg.pinv(Z)
    My = M @ yv

    def stat(o):
        mo = M @ o.astype(float)
        return (mo @ My) / (mo @ mo)
    obs = stat(old)
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(seasons == s) for s in np.unique(seasons)]
    null = np.empty(N)
    for i in range(N):
        lab = old.copy()
        for g in groups:
            lab[g] = rng.permutation(old[g])
        null[i] = stat(lab)
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (N + 1)
    return obs, p, obs - 1.96 * null.std(), obs + 1.96 * null.std()


rows = []
for scope, a in [("all article types", ap), ("no liveblogs", ap[ap.article_type != "liveblog"])]:
    t = counts(a)
    t["change"] = t["after"] - t["before"]
    t["before_ctl"] = t["before"]                    # used as a control for 'after'
    for spec, ctl in [("season only", ()), ("+ market value", ("log_value",)),
                      ("+ market value + position", ("log_value", "pos_def", "pos_mid", "pos_att"))]:
        for y in ["before", "after", "change"]:
            gap, p, lo, hi = gap_test(t, y, ctl)
            old = sg.old30.reindex(t.index).to_numpy(bool)
            rows.append({"articles": scope, "spec": spec, "period": y, "n_30plus": int(old.sum()),
                         "n_under30": int((~old).sum()),
                         "median_articles_30plus": t.loc[old, f"n_{y}"].median() if y != "change" else np.nan,
                         "median_articles_under30": t.loc[~old, f"n_{y}"].median() if y != "change" else np.nan,
                         "gap_log": gap, "ratio_30plus_vs_under30": np.exp(gap),
                         "ratio_lo": np.exp(lo), "ratio_hi": np.exp(hi), "p_within_season": p})
            r = rows[-1]
            print(f"{scope:18s} {spec:28s} {y:7s} ratio {r['ratio_30plus_vs_under30']:.2f} "
                  f"[{r['ratio_lo']:.2f}, {r['ratio_hi']:.2f}] p={p:.4f}")
    # after, holding coverage before fixed: does the move add less coverage for 30+?
    gap, p, lo, hi = gap_test(t, "after", ("log_value", "before_ctl"))
    rows.append({"articles": scope, "spec": "+ market value + coverage before", "period": "after",
                 "gap_log": gap, "ratio_30plus_vs_under30": np.exp(gap), "ratio_lo": np.exp(lo),
                 "ratio_hi": np.exp(hi), "p_within_season": p})
    print(f"{scope:18s} {'+ value + coverage before':28s} after   ratio {np.exp(gap):.2f} [{np.exp(lo):.2f}, {np.exp(hi):.2f}] p={p:.4f}")

pd.DataFrame(rows).to_csv(OUT / "a1_coverage_age.csv", index=False, float_format="%.4f", encoding="utf-8-sig")
