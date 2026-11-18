"""
A1 - sentiment before vs after the transfer (per player), pipeline_spec.yaml 'supports'.

  unit       sentence -> score in [-1, 1] -> averaged per (signing, period)
  input      sentences.csv (+ article_player.csv for flags); period before/after,
             'around' reported separately
  filter     article_type not in [liveblog, matchreport]; matchreports analysed separately
  comparison paired within signing: after minus before; permutation test on period
             labels, shuffled between ARTICLES within a signing (sentences of one
             article are not independent)

Scorers (choose with --scorer)
  vader    VADER compound score                               pip install vaderSentiment
  bing     Bing Liu opinion lexicon (Hu & Liu 2004):
           (n_positive - n_negative) / (n_positive + n_negative), 0 if no lexicon word.
           Lexicon from nltk (nltk.download('opinion_lexicon')) or the folder
           opinion_lexicon/ next to this script.
  roberta  transformer classifier, score = P(positive) - P(negative)
           default model cardiffnlp/twitter-roberta-base-sentiment-latest (3 classes);
           --model distilbert-base-uncased-finetuned-sst-2-english = the course's
           DistilBERT. pip install transformers torch. Scores are cached in
           a1_cache_<model>.csv, so an interrupted run continues where it stopped.

Run (from the folder with this script):
  python a1_sentiment.py Pilot --scorer vader   --signings signings.csv
  python a1_sentiment.py Pilot --scorer bing    --signings signings.csv
  python a1_sentiment.py Pilot --scorer roberta --signings signings.csv
Jupyter:
  import a1_sentiment as a1;  res = a1.run("Pilot", "roberta", "signings.csv")
Outputs go to the data folder: a1_<scorer>_results.csv, a1_<scorer>_per_signing.csv,
a1_<scorer>_scores.csv (one score per sentence) and a1_<scorer>.png
"""
import argparse
import hashlib
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MIN_SENTENCES = 5           # per period, for a signing to enter the paired comparison
N_PERM = 5000
SEED = 2805
EXCLUDE_TYPES = ["liveblog", "matchreport"]
GROUPS = ["young", "middle", "old"]
ROBERTA_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
BATCH_SIZE = 32
MAX_TOKENS = 128            # longer sentences are truncated

# Bing words that mostly carry football meaning, not opinion (robustness check)
BING_FOOTBALL_WORDS = {"free", "defeat", "fans", "fan", "lead", "leading", "attack",
                       "attacks", "attacking", "penalty", "penalties", "foul", "fouls",
                       "clean", "top", "like", "well", "fine", "miss", "missed", "loss"}


# ------------------------------------------------------------------ scorers
def score_vader(texts):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    return np.array([sia.polarity_scores(t)["compound"] for t in texts])


def bing_lexicon():
    folder = HERE / "opinion_lexicon"
    if (folder / "positive-words.txt").exists():
        def read(name):
            with open(folder / name, encoding="latin-1") as f:
                return {w.strip() for w in f if w.strip() and not w.startswith(";")}
        return read("positive-words.txt"), read("negative-words.txt")
    from nltk.corpus import opinion_lexicon          # needs nltk.download('opinion_lexicon')
    return set(opinion_lexicon.positive()), set(opinion_lexicon.negative())


WORD = re.compile(r"[a-z][a-z'\-+]*")


def score_bing(texts, drop=()):
    pos, neg = bing_lexicon()
    pos, neg = pos - set(drop), neg - set(drop)
    out = np.zeros(len(texts))
    for i, t in enumerate(texts):
        words = WORD.findall(t.lower().replace("’", "'"))
        p = sum(w in pos for w in words)
        n = sum(w in neg for w in words)
        out[i] = (p - n) / (p + n) if p + n else 0.0
    return out


def score_roberta(texts, model=ROBERTA_MODEL, cache_dir=Path(".")):
    """P(positive) - P(negative) per sentence, cached by sentence hash."""
    cache = Path(cache_dir) / f"a1_cache_{model.replace('/', '_')}.csv"
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
    done = {}
    if cache.exists():
        c = pd.read_csv(cache)
        done = dict(zip(c.key, c.score))
    todo = sorted({k: t for k, t in zip(keys, texts) if k not in done}.items())
    print(f"{model}: {len(set(keys)) - len(todo)} sentences cached, {len(todo)} to score")
    if todo:
        import torch
        from transformers import pipeline
        device = 0 if torch.cuda.is_available() else -1
        clf = pipeline("text-classification", model=model, top_k=None, device=device)
        start, chunk = time.time(), 2000
        for i in range(0, len(todo), chunk):
            part = todo[i:i + chunk]
            res = clf([t for _, t in part], batch_size=BATCH_SIZE,
                      truncation=True, max_length=MAX_TOKENS)
            rows = []
            for (k, _), labels in zip(part, res):
                p = {d["label"].lower(): d["score"] for d in labels}
                pos = sum(v for l, v in p.items() if l.startswith("pos") or l == "label_2")
                neg = sum(v for l, v in p.items() if l.startswith("neg") or l == "label_0")
                rows.append((k, pos - neg))
                done[k] = pos - neg
            pd.DataFrame(rows, columns=["key", "score"]).to_csv(
                cache, mode="a", header=not cache.exists(), index=False)
            n = min(i + chunk, len(todo))
            rate = n / (time.time() - start)
            print(f"  {n}/{len(todo)} sentences  ({rate:.0f}/s, ~{(len(todo) - n) / rate / 60:.0f} min left)")
    return np.array([done[k] for k in keys])


# ------------------------------------------------------------------ analysis
def load(folder, scorer="vader", model=ROBERTA_MODEL, drop=()):
    folder = Path(folder)
    s = pd.read_csv(folder / "sentences.csv")
    s = s[s.article_type != "liveblog"].reset_index().rename(columns={"index": "sentence_row"})
    ap = pd.read_csv(folder / "article_player.csv",
                     usecols=["article_id", "signing_id", "overlapping_window",
                              "mixed_age_article", "is_focus_article"])
    s = s.merge(ap, on=["article_id", "signing_id"], how="left")
    texts = s["sentence"].astype(str).tolist()
    if scorer == "vader":
        s["score"] = score_vader(texts)
    elif scorer == "bing":
        s["score"] = score_bing(texts, drop)
    elif scorer == "roberta":
        s["score"] = score_roberta(texts, model, folder)
    else:
        raise ValueError(f"unknown scorer {scorer!r}")
    return s


def per_signing(s, min_sent=MIN_SENTENCES):
    """Mean score per (signing, period) and the paired after-minus-before table."""
    g = (s[s.period.isin(["before", "after"])]
         .groupby(["signing_id", "period"])
         .agg(mean=("score", "mean"), n_sent=("score", "size"),
              n_art=("article_id", "nunique"))
         .unstack("period"))
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.dropna()
    g = g[(g.n_sent_before >= min_sent) & (g.n_sent_after >= min_sent)].copy()
    g["diff"] = g.mean_after - g.mean_before
    return g


def perm_test(s, signings, n_perm=N_PERM, seed=SEED):
    """Observed mean over signings of (after - before) and a two-sided permutation
    p-value; period labels are shuffled between articles within each signing."""
    d = s[s.period.isin(["before", "after"]) & s.signing_id.isin(signings)]
    a = (d.groupby(["signing_id", "article_id", "period"])["score"]
           .agg(["sum", "size"]).reset_index())
    sid = pd.factorize(a.signing_id)[0]
    k = sid.max() + 1
    tot_, n_ = a["sum"].to_numpy(), a["size"].to_numpy()
    lab = (a.period == "after").to_numpy().astype(int)
    base = np.lexsort((np.arange(len(lab)), sid))

    def stat(labels):
        idx = sid * 2 + labels
        tot = np.bincount(idx, tot_, minlength=2 * k).reshape(k, 2)
        cnt = np.bincount(idx, n_, minlength=2 * k).reshape(k, 2)
        with np.errstate(invalid="ignore", divide="ignore"):
            m = tot / cnt
        return np.nanmean(m[:, 1] - m[:, 0])

    obs = stat(lab)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        order = np.lexsort((rng.random(len(lab)), sid))     # random order within signing
        perm = np.empty_like(lab)
        perm[order] = lab[base]
        null[i] = stat(perm)
    return obs, (np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)


def bootstrap_ci(x, n=5000, seed=SEED):
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    return np.percentile(rng.choice(x, (n, len(x))).mean(axis=1), [2.5, 97.5])


def summarise(s, label, age):
    t = per_signing(s)
    rows = []
    for g in ["all"] + GROUPS:
        sub = t if g == "all" else t[t.index.isin(age[age == g].index)]
        if len(sub) < 3:
            rows.append({"sample": label, "group": g, "signings": len(sub)})
            continue
        obs, p = perm_test(s, sub.index)
        lo, hi = bootstrap_ci(sub["diff"])
        rows.append({"sample": label, "group": g, "signings": len(sub),
                     "mean_before": sub.mean_before.mean(), "mean_after": sub.mean_after.mean(),
                     "mean_diff": obs, "ci_low": lo, "ci_high": hi,
                     "median_diff": sub["diff"].median(),
                     "share_more_positive": (sub["diff"] > 0).mean(), "p_perm": p})
    return pd.DataFrame(rows), t


def analyse(s):
    age = s.groupby("signing_id")["age_group_at_transfer"].first()
    main_s = s[~s.article_type.isin(EXCLUDE_TYPES)]
    res, table = summarise(main_s, "main: no liveblog/matchreport", age)
    parts = [res,
             summarise(main_s[~main_s.overlapping_window.astype(bool)],
                       "robust: drop overlapping_window", age)[0],
             summarise(main_s[main_s.is_focus_article.astype(bool)],
                       "robust: focus articles only", age)[0]]
    for t in ["news", "features", "comment"]:
        parts.append(summarise(main_s[main_s.article_type == t], f"type: {t}", age)[0])
    parts.append(summarise(s[s.article_type == "matchreport"], "matchreports only", age)[0])
    results = pd.concat(parts, ignore_index=True)
    around = (main_s.groupby(["age_group_at_transfer", "period"])["score"].mean()
              .unstack().reindex(index=GROUPS, columns=["before", "around", "after"]))
    return results, around, table.join(age.rename("age_group"))


# ------------------------------------------------------------------ figure
def plot(s, results, title, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
    COL = {"young": "#2a78d6", "middle": "#eb6834", "old": "#1baf7a"}
    m = s[~s.article_type.isin(EXCLUDE_TYPES)].copy()
    m["month"] = np.floor(m.days_from_transfer / 30.44).clip(-12, 11).astype(int)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                         "text.color": INK})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.3),
                                   gridspec_kw={"width_ratios": [1.6, 1]}, facecolor=SURF)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURF)
        for k in ("top", "right", "left"):
            ax.spines[k].set_visible(False)
        ax.grid(axis="y" if ax is ax1 else "x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)

    ns = m.groupby("age_group_at_transfer").signing_id.nunique()
    ys = []
    for g in GROUPS:
        d = (m[m.age_group_at_transfer == g].groupby("month").score.agg(["sum", "size"])
             .reindex(range(-12, 12), fill_value=0))
        y = (d["sum"].rolling(3, center=True, min_periods=2).sum()
             / d["size"].rolling(3, center=True, min_periods=2).sum())
        if y.isna().all():
            continue
        ys.append(y)
        ax1.plot(y.index, y.values, color=COL[g], lw=2, ls="-" if g != "old" else (0, (4, 2)),
                 label=f"{g} ({ns.get(g, 0)} signings)")
    lo = min(np.nanmin(y.values) for y in ys)
    hi = max(np.nanmax(y.values) for y in ys)
    pad = (hi - lo) * 0.15
    ax1.set_ylim(lo - pad, hi + pad * 2.2)
    ax1.axvline(0, color=INK2, lw=1)
    ax1.text(0.25, hi + pad * 2.0, "transfer", color=INK2, fontsize=9, va="top")
    ax1.set_xlim(-12, 11.5)
    ax1.set_xticks(range(-12, 12, 3))
    ax1.set_xlabel("months from transfer (3-month rolling mean)", labelpad=4)
    ax1.set_ylabel("mean sentiment per sentence")
    ax1.legend(title="Age group at transfer:", loc="upper left", bbox_to_anchor=(-0.01, -0.14),
               ncol=4, frameon=False, fontsize=9, title_fontsize=9, alignment="left")
    ax1.set_title(f"{title}: tone by month around the transfer", loc="left", fontsize=11)

    order = [("main: no liveblog/matchreport", "All (main sample)"), ("type: news", "News"),
             ("type: features", "Features"), ("type: comment", "Comment")]
    r = results[results.group == "all"].set_index("sample")
    R = [(lab,) + tuple(r.loc[k, ["mean_diff", "ci_low", "ci_high", "signings"]])
         for k, lab in order if k in r.index and pd.notna(r.loc[k, "mean_diff"])][::-1]
    span = max(abs(x) for row in R for x in row[1:4])
    for i, (lab, mu, lo_, hi_, n) in enumerate(R):
        ax2.plot([lo_, hi_], [i, i], color="#2a78d6", lw=2, solid_capstyle="round")
        ax2.plot(mu, i, "o", ms=8, color="#2a78d6", mec=SURF, mew=2)
        ax2.text(span * 1.25, i, f"{mu:+.3f}  (n={int(n)})", va="center", fontsize=9, color=INK2)
    ax2.axvline(0, color=INK2, lw=1)
    ax2.set_yticks(range(len(R)))
    ax2.set_yticklabels([x[0] for x in R], color=INK)
    ax2.set_xlim(-span * 1.15, span * 2.3)
    ax2.set_xticks([t for t in ax2.get_xticks() if -span * 1.15 <= t <= span * 1.15])
    ax2.set_xlabel("after − before, mean per signing (95% CI)")
    ax2.set_title("Change by article type", loc="left", fontsize=11)
    fig.text(0.01, 0.005, "Liveblogs and match reports excluded. Right panel: signings with "
             f"≥{MIN_SENTENCES} sentences in both periods.", fontsize=8, color=INK2)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=200, facecolor=SURF)
    plt.close(fig)


# ------------------------------------------------------------------ run
TITLES = {"vader": "VADER", "bing": "Bing lexicon", "roberta": "RoBERTa"}


def run(folder, scorer="vader", signings_csv=None, model=ROBERTA_MODEL, drop=(), tag=None):
    folder = Path(folder)
    if tag is None:
        tag = scorer if scorer != "roberta" or model == ROBERTA_MODEL else model.split("/")[-1].split("-")[0]
    s = load(folder, scorer, model, drop)
    results, around, table = analyse(s)
    if signings_csv:
        sg = pd.read_csv(signings_csv).set_index("signing_id")
        table = table.join(sg[["name", "age_at_transfer", "season", "from_club_name",
                               "to_club_name", "transfer_fee", "market_value_in_eur"]])
    results.round(4).to_csv(folder / f"a1_{tag}_results.csv", index=False, encoding="utf-8-sig")
    table.round(4).to_csv(folder / f"a1_{tag}_per_signing.csv", encoding="utf-8-sig")
    s[["sentence_row", "article_id", "signing_id", "period", "article_type", "score"]].to_csv(
        folder / f"a1_{tag}_scores.csv", index=False, encoding="utf-8-sig")
    title = TITLES.get(scorer, scorer) if scorer != "roberta" else model.split("/")[-1]
    plot(s, results, title + (" (football words removed)" if drop else ""), folder / f"a1_{tag}.png")
    pd.set_option("display.width", 220)
    print(results.round(3).to_string(index=False))
    print("\nMean sentence score by period (main sample):")
    print(around.round(3).to_string())
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="folder with sentences.csv and article_player.csv")
    ap.add_argument("--scorer", choices=["vader", "bing", "roberta"], default="vader")
    ap.add_argument("--signings", help="signings.csv (adds names to the per-signing table)")
    ap.add_argument("--model", default=ROBERTA_MODEL, help="Hugging Face model for --scorer roberta")
    ap.add_argument("--drop-football-words", action="store_true",
                    help="bing only: ignore lexicon words that are football jargon")
    a = ap.parse_args()
    drop = BING_FOOTBALL_WORDS if a.drop_football_words else ()
    run(a.folder, a.scorer, a.signings, a.model, drop,
        tag=f"{a.scorer}_nofootball" if drop else None)
