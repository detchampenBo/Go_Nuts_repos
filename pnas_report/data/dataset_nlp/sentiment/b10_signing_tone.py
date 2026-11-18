"""B10: one row per Premier League signing with tone (four models), coverage and controls.

Usage: python b10_signing_tone.py <Project folder> <out csv>
Reads signings.csv, article_player.csv and Full/a1_<model>_per_signing.csv.
All 1,332 signings; tone columns are filled for the 820 in the main sample
(no liveblogs or match reports, >= 5 scored sentences before and after) and empty otherwise.
No article text.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

P, OUT = Path(sys.argv[1]), Path(sys.argv[2])
sg = pd.read_csv(P / "signings.csv")
cols = ["signing_id", "player_id", "name", "age_at_transfer", "age_group", "season", "transfer_date",
        "from_club_name", "to_club_name", "position", "market_value_in_eur", "transfer_fee"]
t = sg[[c for c in cols if c in sg.columns]].copy()
t.insert(5, "age30plus", t.age_at_transfer >= 30)

ap = pd.read_csv(P / "article_player.csv", usecols=["article_id", "signing_id", "period", "mentions", "article_type"])
ap = ap[ap.mentions >= 1]
for per in ["before", "after"]:
    a = ap[ap.period == per].groupby("signing_id").article_id.nunique()
    t[f"articles_{per}"] = t.signing_id.map(a).fillna(0).astype(int)
    a = ap[(ap.period == per) & (ap.article_type != "liveblog")].groupby("signing_id").article_id.nunique()
    t[f"articles_{per}_no_liveblog"] = t.signing_id.map(a).fillna(0).astype(int)

first = True
for m in ["roberta", "vader", "bing", "bing_nofootball"]:
    ps = pd.read_csv(P / "Full" / f"a1_{m}_per_signing.csv", encoding="utf-8-sig").set_index("signing_id")
    if first:
        t["in_main_sample"] = t.signing_id.isin(ps.index)
        for c in ["n_sent_before", "n_sent_after", "n_art_before", "n_art_after"]:
            t[c.replace("n_sent", "main_sentences").replace("n_art", "main_articles")] = t.signing_id.map(ps[c])
        first = False
    t[f"{m}_before"] = t.signing_id.map(ps.mean_before)
    t[f"{m}_after"] = t.signing_id.map(ps.mean_after)
    t[f"{m}_change"] = t.signing_id.map(ps["diff"])

assert len(t) == 1332 and t.in_main_sample.sum() == 820
assert np.allclose((t.roberta_after - t.roberta_before).dropna(), t.roberta_change.dropna(), atol=1e-3)
t.to_csv(OUT, index=False, float_format="%.4f", encoding="utf-8-sig")
print(len(t), "rows,", t.in_main_sample.sum(), "in main sample;", t.age30plus.sum(), "aged 30+;",
      t[t.in_main_sample].age30plus.sum(), "aged 30+ in main sample")
print(t.columns.tolist())
