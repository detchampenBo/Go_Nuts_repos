"""Tone change after a Premier League signing: players aged 30+ vs under 30.

Text part of the research question (11 Nov 2026): among the players who do join the
Premier League, does the Guardian's tone change after the move differ for 30+ signings?

Uses the outputs of a1_sentiment.py (a1_<method>_scores.csv, sentence scores) plus
sentences.csv, article_player.csv and signings.csv. Nothing is re-scored.

For each method and sample:
  * within each age group: mean (after - before) per signing, permutation p (period labels
    shuffled between articles within a signing, as in a1_sentiment.py);
  * between groups: (30+ mean change) - (under-30 mean change); null = 5,000 shuffles of
    the 30+ label among signings WITHIN the same transfer season (old signings bunch in
    2022, so a plain shuffle would mix up age and time).

Run:  python a1_age30.py <folder with sentences.csv, article_player.csv> <folder with
      a1_*_scores.csv> <signings.csv> [methods, e.g. roberta,vader]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a1_sentiment import EXCLUDE_TYPES, perm_test, per_signing, bootstrap_ci  # noqa: E402

METHODS = {"roberta": "RoBERTa", "vader": "VADER", "bing": "Bing",
           "bing_nofootball": "Bing, no football words"}
N_SHUFFLE, SEED = 5000, 2805


def load(data, scores, method):
    sc = pd.read_csv(Path(scores) / f"a1_{method}_scores.csv")
    ap = pd.read_csv(Path(data) / "article_player.csv",
                     usecols=["article_id", "signing_id", "is_focus_article", "overlapping_window",
                              "mixed_age_article"])
    return sc.merge(ap, on=["article_id", "signing_id"], how="left")


def between_test(t, season, n=N_SHUFFLE, seed=SEED):
    """30+ minus under-30 mean change; age label shuffled within season."""
    old = t["old30"].to_numpy()
    d = t["diff"].to_numpy()
    obs = d[old].mean() - d[~old].mean()
    seasons = season.reindex(t.index).to_numpy()
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(seasons == s) for s in np.unique(seasons)]
    null = np.empty(n)
    for i in range(n):
        lab = old.copy()
        for g in groups:
            lab[g] = rng.permutation(old[g])
        null[i] = d[lab].mean() - d[~lab].mean()
    return obs, (np.sum(np.abs(null) >= abs(obs)) + 1) / (n + 1)


def run(data, scores, signings_csv, methods=None):
    sg = pd.read_csv(signings_csv).set_index("signing_id")
    old30 = sg.age_at_transfer >= 30
    rows = []
    for method, title in METHODS.items():
        if methods and method not in methods:
            continue
        if not (Path(scores) / f"a1_{method}_scores.csv").exists():
            print(f"skip {method}: no scores file")
            continue
        s = load(data, scores, method)
        main = s[~s.article_type.isin(EXCLUDE_TYPES)]
        samples = {
            "main": main,
            "focus articles only": main[main.is_focus_article.astype(bool)],
            "no mixed-age articles": main[~main.mixed_age_article.astype(bool)],
            "seasons 2016+": main[main.signing_id.map(sg.season) >= 2016],
        }
        for label, sub in samples.items():
            t = per_signing(sub)
            t["old30"] = old30.reindex(t.index).to_numpy()
            row = {"method": title, "sample": label}
            for name, mask in [("under30", ~t.old30), ("30plus", t.old30)]:
                g = t[mask]
                obs, p = perm_test(sub, g.index)
                lo, hi = bootstrap_ci(g["diff"])
                row.update({f"n_{name}": len(g), f"diff_{name}": obs,
                            f"ci_{name}": f"[{lo:.3f}, {hi:.3f}]", f"p_{name}": p})
            gap, p_gap = between_test(t, sg.season)
            row.update({"gap_30plus_minus_under30": gap, "p_gap_within_season": p_gap})
            rows.append(row)
            print(f"{title:24s} {label:22s} under30 {row['diff_under30']:+.3f} (n={row['n_under30']}, "
                  f"p={row['p_under30']:.3f})  30+ {row['diff_30plus']:+.3f} (n={row['n_30plus']}, "
                  f"p={row['p_30plus']:.3f})  gap {gap:+.3f} p={p_gap:.3f}")
    out = pd.DataFrame(rows)
    out.round(4).to_csv(Path(scores) / "a1_age30_results.csv", index=False, encoding="utf-8-sig")
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",") if len(sys.argv) > 4 else None)
