"""B8: score the focus rule against focus check 2 (and re-check candidate rules on check 1).

Usage: python b8_focus.py <Project folder> <out folder>
Check 2 is stratified (50 focus / 50 not, no liveblogs, none of check 1's links), so
recall and the share of "about him" links are weighted by the stratum sizes in article_player.csv.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

P, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2805)

ap = pd.read_csv(P / "article_player.csv", usecols=["article_id", "signing_id", "mentions", "name_in_headline",
                                                    "is_focus_article", "article_type", "name_clash"])
c1 = pd.read_csv(P / "check_focus_sample.csv", dtype=str, keep_default_na=False)
c2 = pd.read_csv(P / "check_focus_sample_2.csv", dtype=str, keep_default_na=False)
c1["lab"] = c1["truly_about_player (y/n)"].str.strip()
c2["lab"] = c2["truly_about_player (y/n/x)"].str.strip()

key = ["signing_id", "article_id"]
c1keys = set(map(tuple, c1[key].to_numpy()))
pop = ap[(ap.article_type != "liveblog") & ~ap[key].apply(tuple, axis=1).isin(c1keys)]
nz = c2.loc[c2.is_focus_article == "FALSE", "mentions"].astype(int).min()
if nz >= 1:   # validate drew the not-focus stratum only from links that still name the player
    pop = pop[pop.mentions >= 1]
N = {True: int(pop.is_focus_article.sum()), False: int((~pop.is_focus_article).sum())}
print(f"population (no liveblogs, not in check 1{', mentions>=1' if nz >= 1 else ''}): focus {N[True]:,}, not {N[False]:,}")

RULES = {
    "now: headline or >=3 mentions": lambda d: d.hl | (d.m >= 3),
    "headline or >=4 mentions": lambda d: d.hl | (d.m >= 4),
    "headline or >=5 mentions": lambda d: d.hl | (d.m >= 5),
    "headline only": lambda d: d.hl,
    "headline or >=3, match reports need headline": lambda d: d.hl | ((d.m >= 3) & (d.article_type != "matchreport")),
}


def prep(c, from_ap):
    d = c.copy()
    if from_ap:   # check 1 was drawn before B5: take mentions/headline from the current build
        d = d.drop(columns=["mentions", "name_in_headline", "is_focus_article"]).merge(
            ap[key + ["mentions", "name_in_headline", "is_focus_article"]], on=key, how="left")
        d["is_focus_article"] = d.is_focus_article.astype(str).str.upper()
        d["name_in_headline"] = d.name_in_headline.astype(str)
    d["m"] = d.mentions.astype(int)
    d["hl"] = d.name_in_headline.astype(str).str.upper() == "TRUE"
    d["stratum"] = d.is_focus_article.astype(str).str.upper() == "TRUE"
    return d[d.lab.isin(["y", "n", "x"])]


def score(d, rule, weighted):
    sel = rule(d).to_numpy(); y = (d.lab == "y").to_numpy(); s = d.stratum.to_numpy()
    if weighted:
        w = np.where(s, N[True] / s.sum(), N[False] / (~s).sum())
    else:
        w = np.ones(len(d))
    tp = (w * (sel & y)).sum(); fp = (w * (sel & ~y)).sum(); fn = (w * (~sel & y)).sum()
    return tp / (tp + fp) if tp + fp else np.nan, tp / (tp + fn) if tp + fn else np.nan, int(sel.sum()), int((sel & y).sum()), int(y.sum())


rows = []
d2 = prep(c2, False)
d1 = prep(c1, True)
for name, rule in RULES.items():
    p2, r2, ns, nt, ny = score(d2, rule, True)
    # bootstrap within strata for check 2
    B = []
    for _ in range(2000):
        parts = [g.sample(len(g), replace=True, random_state=int(rng.integers(1e9))) for _, g in d2.groupby("stratum")]
        B.append(score(pd.concat(parts), rule, True)[:2])
    B = np.array(B)
    p1, r1, ns1, nt1, ny1 = score(d1, rule, False)
    rows.append({"rule": name,
                 "check2_says_focus": ns, "check2_focus_right": nt,
                 "check2_precision_w": p2, "check2_precision_lo": np.nanpercentile(B[:, 0], 2.5), "check2_precision_hi": np.nanpercentile(B[:, 0], 97.5),
                 "check2_recall_w": r2, "check2_recall_lo": np.nanpercentile(B[:, 1], 2.5), "check2_recall_hi": np.nanpercentile(B[:, 1], 97.5),
                 "check1_says_focus": ns1, "check1_focus_right": nt1, "check1_about_him": ny1,
                 "check1_precision": p1, "check1_recall": r1})
res = pd.DataFrame(rows)
res.to_csv(OUT / "b8_focus_rule_scores.csv", index=False, float_format="%.3f")

# composition of check 2
lab = d2.lab
share_y = (N[True] * (lab[d2.stratum] == "y").mean() + N[False] * (lab[~d2.stratum] == "y").mean()) / (N[True] + N[False])
pd.set_option("display.width", 250)
print(pd.crosstab(d2.stratum.map({True: "focus", False: "not focus"}), lab))
print(f"blank labels: {(c2.lab == '').sum()} | wrong person: {(lab == 'x').sum()}/{len(lab)}")
print(f"weighted share of non-liveblog links that are about the player: {share_y:.1%}")
print(res.to_string(index=False, float_format="%.3f"))
print("check 2 focus links, by article type (y/n):")
print(pd.crosstab(d2[d2.stratum].article_type, d2[d2.stratum].lab))
print(pd.crosstab(d2[d2.stratum].m.clip(upper=6).astype(str) + np.where(d2[d2.stratum].hl, " +headline", ""), d2[d2.stratum].lab))
