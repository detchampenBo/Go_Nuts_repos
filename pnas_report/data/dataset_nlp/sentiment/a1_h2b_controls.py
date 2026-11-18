"""H2b: is Guardian tone LOWER for 30+ signings than for under-30 signings (level, not change)?
Controls for fame, article type, quoted sentences, seasons 2016+ and position.

Usage: python a1_h2b_controls.py <Project folder> <out folder>
Reads  Full/a1_<model>_scores.csv, sentences.csv (text, to find quotes), article_player.csv,
       signings.csv.  Nothing is re-scored.
Writes a1_h2b_controls.csv (one row per model x spec x period: before, after, change) and a1_h2b_signings.csv
       (per-signing levels + controls, RoBERTa and VADER).

Unit: signing. Level = mean sentence score in the period (before: -365..-8 days, after: +8..+365),
main sample (no liveblogs, no match reports), >=5 sentences in both periods (as a1_age30.py).
Gap = 30+ minus under-30. p: 5,000 shuffles of the 30+ label within transfer season (seed 2805),
as in a1_age30.py; with controls, the gap is the 30+ coefficient of an OLS with those controls
+ season dummies, refitted for every shuffle (controls stay with their signing).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

P, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
MODELS = {"roberta": "RoBERTa", "vader": "VADER", "bing": "Bing", "bing_nofootball": "Bing, no football words"}
EXCLUDE = ["liveblog", "matchreport"]
MIN_SENT, N, SEED = 5, 5000, 2805
QUOTE_CHARS = ["“", "”", '"']   # curly + straight double quotes (single quotes clash with apostrophes)

sg = pd.read_csv(P / "signings.csv").set_index("signing_id")
sg["old30"] = sg.age_at_transfer >= 30

# sentence text -> has a quotation mark; sentence_row in the scores files = row number of sentences.csv
sent = pd.read_csv(P / "sentences.csv", usecols=["article_id", "signing_id", "sentence"])
sent["quoted"] = sent.sentence.fillna("").str.contains("|".join(QUOTE_CHARS), regex=True)

# fame = Guardian articles naming the player (any type, mentions >= 1) in the year before the move
ap = pd.read_csv(P / "article_player.csv", usecols=["article_id", "signing_id", "period", "mentions"])
fame = (ap[(ap.period == "before") & (ap.mentions >= 1)].groupby("signing_id").article_id.nunique())
sg["articles_before"] = fame.reindex(sg.index).fillna(0)
sg["log_fame"] = np.log1p(sg.articles_before)
sg["log_value"] = np.log(sg.market_value_in_eur)


def levels(s, value="score"):
    """Per-signing mean of `value` before / after; keeps signings with >= MIN_SENT in both."""
    g = (s[s.period.isin(["before", "after"])].groupby(["signing_id", "period"])[value]
         .agg(["mean", "size"]).unstack("period"))
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.dropna()
    g = g[(g.size_before >= MIN_SENT) & (g.size_after >= MIN_SENT)]
    return g.rename(columns={"mean_before": "before", "mean_after": "after"})[["before", "after"]]


def gap_test(t, y, controls=()):
    """30+ coefficient (or plain gap) with season dummies + controls; p from within-season shuffles."""
    d = t.join(sg[["old30", "season", *controls]], how="left")
    yv = d[y].to_numpy(float)
    old = d.old30.to_numpy()
    seasons = d.season.to_numpy()
    if controls:
        Z = np.column_stack([pd.get_dummies(d.season).to_numpy(float), d[list(controls)].to_numpy(float)])
        M = np.eye(len(d)) - Z @ np.linalg.pinv(Z)          # residual maker (Frisch-Waugh)
        My = M @ yv

        def stat(o):
            mo = M @ o.astype(float)
            return (mo @ My) / (mo @ mo)
    else:
        def stat(o):
            return yv[o].mean() - yv[~o].mean()
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
    lo, hi = obs - 1.96 * null.std(), obs + 1.96 * null.std()      # interval from the null spread
    return obs, p, lo, hi, int(old.sum()), int((~old).sum())


rows, keep = [], {}
for m, title in MODELS.items():
    s = pd.read_csv(P / "Full" / f"a1_{m}_scores.csv", encoding="utf-8-sig")
    assert (sent.loc[s.sentence_row, "article_id"].to_numpy() == s.article_id.to_numpy()).all()
    assert (sent.loc[s.sentence_row, "signing_id"].to_numpy() == s.signing_id.to_numpy()).all()
    s["quoted"] = sent.loc[s.sentence_row, "quoted"].to_numpy()
    main = s[~s.article_type.isin(EXCLUDE)].copy()
    # article-type adjusted score: subtract the mean of that type in that period (all signings)
    main["score_typeadj"] = main.score - main.groupby(["article_type", "period"]).score.transform("mean") \
        + main.groupby("period").score.transform("mean")
    base = levels(main)
    noq = levels(main[~main.quoted])
    tadj = levels(main, "score_typeadj")
    both = levels(main[~main.quoted], "score_typeadj")
    s16 = base[base.index.map(sg.season) >= 2016]
    specs = [
        ("1 no controls (as 11 Nov)", base, ()),
        ("2 + fame (log articles before)", base, ("log_fame",)),
        ("3 + fame + market value", base, ("log_fame", "log_value")),
        ("4 article type adjusted", tadj, ()),
        ("5 no quoted sentences", noq, ()),
        ("6 seasons 2016+", s16, ()),
        ("7 all: no quotes, type adjusted, fame + value", both, ("log_fame", "log_value")),
        ("8 all + position", both, ("log_fame", "log_value", "pos_def", "pos_mid", "pos_att")),
    ]
    for pos in ["Defender", "Midfield", "Attack"]:
        sg[f"pos_{pos[:3].lower()}"] = (sg.position == pos).astype(float)
    for typ in ["news", "features", "comment"]:
        sub = main[main.article_type == typ]
        g = (sub[sub.period.isin(["before", "after"])].groupby(["signing_id", "period"]).score
             .agg(["mean", "size"]).unstack("period"))
        g.columns = [f"{a}_{b}" for a, b in g.columns]
        specs.append((f"9 within {typ} only (>=3 sentences per period)",
                      g.dropna().query("size_before >= 3 and size_after >= 3")
                      .rename(columns={"mean_before": "before", "mean_after": "after"})[["before", "after"]], ()))
    for name, t, ctl in specs:
        t = t.assign(change=t["after"] - t["before"])
        for y in ["before", "after", "change"]:
            gap, p, lo, hi, n_old, n_young = gap_test(t, y, ctl)
            rows.append({"model": title, "spec": name, "period": y, "n_30plus": n_old, "n_under30": n_young,
                         "under30_mean": t.loc[~t.index.map(sg.old30).astype(bool), y].mean(),
                         "gap_30plus_minus_under30": gap, "ci_lo": lo, "ci_hi": hi, "p_within_season": p})
        print(f"{title:24s} {name:48s} " + " | ".join(f"{r['period']} {r['gap_30plus_minus_under30']:+.3f} p={r['p_within_season']:.3f}"
              for r in rows[-3:]) + f"  (n {n_old}/{n_young})")
    if m in ("roberta", "vader"):
        keep[m] = base.add_prefix(f"{m}_")

res = pd.DataFrame(rows)
res.to_csv(OUT / "a1_h2b_controls.csv", index=False, float_format="%.4f", encoding="utf-8-sig")
ps = keep["roberta"].join(keep["vader"]).join(sg[["player_id", "name", "age_at_transfer", "old30", "season",
                                                   "position", "articles_before", "market_value_in_eur"]])
ps.to_csv(OUT / "a1_h2b_signings.csv", float_format="%.4f", encoding="utf-8-sig")

# context: how fame and quotes differ by age
b = ps
print("\nmedian articles before: 30+", b.loc[b.old30, "articles_before"].median(),
      "under 30", b.loc[~b.old30, "articles_before"].median())
print("share of quoted sentences (main sample, RoBERTa file): 30+ / under 30:",
      main.assign(old=main.signing_id.map(sg.old30)).groupby("old").quoted.mean().round(3).to_dict())
