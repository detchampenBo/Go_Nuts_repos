"""B9: score the four sentiment models against the 200 hand-labelled sentences.

Usage: python b9_score.py <check_sentiment_sample_200.csv> <Full folder> <out folder>

Reads the labels (tone pos/neu/neg/x, note tags), joins each model's sentence score
from Full/a1_<model>_scores.csv on sentence_row, and writes
  b9_model_scores.csv     one row per subset x model
  b9_confusion.csv        3-class confusion counts per model (all scored rows)
  b9_labels_joined.csv    labels + normalised tags + the four scores (no article text)
Label file is read only; tag spellings are normalised in memory.
"""
import sys, re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

LAB, FULL, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
MODELS = {"roberta": "RoBERTa", "vader": "VADER", "bing": "Bing", "bing_nofootball": "Bing, no football"}
# 3-class cut-offs fixed in advance (not tuned on these labels):
#   VADER: the published +-0.05 convention; RoBERTa (P(pos)-P(neg)): the same +-0.05;
#   Bing: (p-n)/(p+n) is 0 when no lexicon word, so neutral = exactly 0.
CUT = {"roberta": 0.05, "vader": 0.05, "bing": 0.0, "bing_nofootball": 0.0}
TAGS = ["own quote", "quote about him", "contrast", "opponent", "passing mention", "football word",
        "age", "wrong person", "irony", "several sentences merged", "unsure"]
rng = np.random.default_rng(2805)

d = pd.read_csv(LAB, dtype=str, keep_default_na=False)
d["tone"] = d["tone (pos/neu/neg)"].str.strip()
d["sentence_row"] = d["sentence_row"].astype(int)


def tags_of(note):
    out = set()
    for part in note.split(";"):
        part = part.strip().lower()
        for t in TAGS:
            if part.startswith(t):
                out.add(t)
        if "contrast" in part:          # "mildly negative, contrast", "contrasting mention"
            out.add("contrast")
    return out


d["tags"] = d["note"].map(tags_of)
for m in MODELS:
    s = pd.read_csv(FULL / f"a1_{m}_scores.csv", encoding="utf-8-sig", usecols=["sentence_row", "score"])
    d = d.merge(s.rename(columns={"score": m}), on="sentence_row", how="left")
assert d[list(MODELS)].notna().all().all(), "missing scores"

d["age30"] = np.where(d["age_group"] == "old", "30+", "under 30")
d["tags_str"] = d["tags"].map(lambda t: "|".join(sorted(t)))
d.drop(columns=["sentence", "headline"]).to_csv(OUT / "b9_labels_joined.csv", index=False)

S = d[d.tone != "x"].copy()                      # scored rows
S["y"] = S.tone.map({"neg": -1, "neu": 0, "pos": 1})


def cls(x, c):
    return np.where(x > c, 1, np.where(x < -c, -1, 0))


def boot_ci(f, n, B=2000):
    v = [f(rng.integers(0, n, n)) for _ in range(B)]
    return np.nanpercentile(v, [2.5, 97.5])


def metrics(sub, m):
    y, x = sub.y.to_numpy(), sub[m].to_numpy()
    p = cls(x, CUT[m])
    n = len(y)
    pol = y != 0
    r = {"n": n, "n_pos": int((y == 1).sum()), "n_neu": int((y == 0).sum()), "n_neg": int((y == -1).sum())}
    rho = spearmanr(x, y).statistic if n > 2 and len(set(y)) > 1 else np.nan
    r["spearman"] = rho
    if n >= 10 and len(set(y)) > 1:
        lo, hi = boot_ci(lambda i: spearmanr(x[i], y[i]).statistic if len(set(y[i])) > 1 else np.nan, n)
        r["spearman_lo"], r["spearman_hi"] = lo, hi
    r["acc3"] = (p == y).mean()
    f1 = []
    for k in (-1, 0, 1):
        tp = ((p == k) & (y == k)).sum(); fp = ((p == k) & (y != k)).sum(); fn = ((p != k) & (y == k)).sum()
        if (y == k).sum() > 0:
            f1.append(2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0)
    r["macro_f1"] = np.mean(f1)
    r["n_polar"] = int(pol.sum())
    r["polarity_acc"] = (np.sign(x[pol]) == y[pol]).mean() if pol.any() else np.nan   # sign right on human pos/neg
    for k, nm in ((-1, "neg"), (0, "neu"), (1, "pos")):
        r[f"mean_score_{nm}"] = x[y == k].mean() if (y == k).any() else np.nan
    return r


subsets = {"all scored": S,
           "without unsure": S[~S.tags.map(lambda t: "unsure" in t)],
           "under 30": S[S.age30 == "under 30"], "30+": S[S.age30 == "30+"],
           "before": S[S.period == "before"], "after": S[S.period == "after"],
           "no tag": S[S.tags.map(len) == 0]}
for t in ["own quote", "quote about him", "contrast", "football word", "age",
          "several sentences merged", "passing mention", "unsure"]:
    subsets[f"tag: {t}"] = S[S.tags.map(lambda s, t=t: t in s)]
subsets["tag: any quote"] = S[S.tags.map(lambda s: bool({"own quote", "quote about him"} & s))]
subsets["no quote tags"] = S[S.tags.map(lambda s: not ({"own quote", "quote about him"} & s))]

rows = []
for name, sub in subsets.items():
    for m, lab in MODELS.items():
        rows.append({"subset": name, "model": lab, **metrics(sub, m)})
res = pd.DataFrame(rows)

# age bias: does a model score 30+ sentences lower than under-30 sentences with the SAME human label?
# residual = score - mean score of that human label (all scored rows); gap = 30+ minus under-30 mean residual,
# p from 5,000 shuffles of the 30+ flag within human label.
bias = []
for m, lab in MODELS.items():
    resid = S[m] - S.groupby("y")[m].transform("mean")
    old = (S.age30 == "30+").to_numpy()
    g = resid[old].mean() - resid[~old].mean()
    ys = S.y.to_numpy(); null = []
    for _ in range(5000):
        o = old.copy()
        for k in (-1, 0, 1):
            idx = np.where(ys == k)[0]; o[idx] = rng.permutation(o[idx])
        null.append(resid[o].mean() - resid[~o].mean())
    p = (np.sum(np.abs(null) >= abs(g)) + 1) / 5001
    hum = S.y[old].mean() - S.y[~old].mean()
    bias.append({"subset": "age bias (30+ minus under 30, same human label)", "model": lab,
                 "n": int(old.sum()), "resid_gap": g, "resid_gap_p": p, "human_label_gap": hum})
res = pd.concat([res, pd.DataFrame(bias)], ignore_index=True)
res.to_csv(OUT / "b9_model_scores.csv", index=False, float_format="%.4f")

conf = []
for m, lab in MODELS.items():
    p = cls(S[m].to_numpy(), CUT[m])
    for h in (-1, 0, 1):
        for q in (-1, 0, 1):
            conf.append({"model": lab, "human": {-1: "neg", 0: "neu", 1: "pos"}[h],
                         "model_class": {-1: "neg", 0: "neu", 1: "pos"}[q],
                         "count": int(((S.y == h) & (p == q)).sum())})
pd.DataFrame(conf).to_csv(OUT / "b9_confusion.csv", index=False)

# wrong person
nx = int((d.tone == "x").sum()); n = len(d)
z = 1.96; ph = nx / n
c = (ph + z * z / (2 * n)) / (1 + z * z / n); h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
print(f"wrong person: {nx}/{n} = {ph:.1%}, Wilson 95% CI [{c-h:.1%}, {c+h:.1%}]")
print(d.loc[d.tone == "x", ["item", "player", "age_group", "period", "article_type", "note"]].to_string(index=False))
pd.set_option("display.width", 250)
show = res[res.subset.isin(["all scored", "without unsure", "under 30", "30+"])]
print(show[["subset", "model", "n", "spearman", "spearman_lo", "spearman_hi", "acc3", "macro_f1", "n_polar", "polarity_acc"]].to_string(index=False, float_format="%.3f"))
