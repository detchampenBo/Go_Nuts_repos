"""
A1: compare the four sentence scorers (VADER, Bing, Bing without football words, RoBERTa).

Reads the outputs of a1_sentiment.py from the data folder; changes nothing in them.
  1. results table: one column per method, after - before with bootstrap 95% CI and
     permutation p-value (taken from a1_<method>_results.csv)
  2. sentence-level agreement: join a1_<method>_scores.csv on sentence_row,
     Pearson / Spearman correlation and sign agreement for every pair
  3. strongest disagreements between RoBERTa and the lexicons

Run from the folder with this script:  python a1_compare_methods.py Pilot
Outputs (in the data folder):
  a1_roberta_table.md              four-method results table (markdown)
  a1_roberta_vs_lexicons.csv       pairwise correlations and sign agreement
  a1_roberta_disagreements.csv     sentences where RoBERTa and both lexicons disagree most
  a1_roberta_vs_lexicons.png       after - before by method (95% CI)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

METHODS = {"vader": "VADER", "bing": "Bing", "bing_nofootball": "Bing, no football words",
           "roberta": "RoBERTa"}
ROWS = [("main: no liveblog/matchreport", "all", "All"),
        ("main: no liveblog/matchreport", "young", "Young"),
        ("main: no liveblog/matchreport", "middle", "Middle"),
        ("main: no liveblog/matchreport", "old", "Old"),
        ("type: news", "all", "News"),
        ("type: features", "all", "Features"),
        ("type: comment", "all", "Comment"),
        ("matchreports only", "all", "Match reports")]


def f3(x):
    return f"{x:+.3f}".replace("-", "−")


def fmt_p(p):
    return "p<0.001" if p < 0.001 else f"p={p:.3f}" if p < 0.01 else f"p={p:.2f}"


def results_table(folder):
    res = {m: pd.read_csv(folder / f"a1_{m}_results.csv").set_index(["sample", "group"])
           for m in METHODS}
    lines = ["| | n | " + " | ".join(METHODS.values()) + " |",
             "|---|---|" + "---|" * len(METHODS)]
    long = []
    for sample, group, label in ROWS:
        n = int(res["roberta"].loc[(sample, group), "signings"])
        cells = []
        for m in METHODS:
            r = res[m].loc[(sample, group)]
            if pd.isna(r.get("mean_diff")):
                cells.append("–")
                continue
            cells.append(f"{f3(r.mean_diff)} [{f3(r.ci_low)}, {f3(r.ci_high)}] {fmt_p(r.p_perm)}")
            long.append({"row": label, "method": METHODS[m], "signings": n, **r[[
                "mean_before", "mean_after", "mean_diff", "ci_low", "ci_high", "p_perm"]]})
        lines.append(f"| {label} | {n} | " + " | ".join(cells) + " |")
    return "\n".join(lines), pd.DataFrame(long)


def plot_methods(long, path):
    """Four-method comparison of after - before (95% CI), same style as a1_sentiment.plot."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
    COL = {"VADER": "#2a78d6", "Bing": "#eb6834", "Bing, no football words": "#f2a37f",
           "RoBERTa": "#1baf7a"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                         "text.color": INK})
    labels = [lab for _, _, lab in ROWS]
    fig, ax = plt.subplots(figsize=(9, 6.2), facecolor=SURF)
    ax.set_facecolor(SURF)
    for k in ("top", "right", "left"):
        ax.spines[k].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    off = np.linspace(0.27, -0.27, len(COL))
    for j, (m, c) in enumerate(COL.items()):
        d = long[long.method == m].set_index("row")
        for i, lab in enumerate(labels[::-1]):
            if lab not in d.index:
                continue
            r = d.loc[lab]
            y = i + off[j]
            ax.plot([r.ci_low, r.ci_high], [y, y], color=c, lw=2, solid_capstyle="round")
            ax.plot(r.mean_diff, y, "o", ms=6, color=c, mec=SURF, mew=1.5,
                    label=m if i == 0 else None)
    for i in range(len(labels) - 1):
        ax.axhline(i + 0.5, color=GRID, lw=0.6)
    ax.axvline(0, color=INK2, lw=1)
    n = long.drop_duplicates("row").set_index("row").signings
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([f"{lab} (n={int(n[lab])})" for lab in labels[::-1]], color=INK)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.set_xlabel("after − before, mean per signing (95% CI)")
    ax.set_title("A1: change in tone after the transfer, four sentence scorers", loc="left",
                 fontsize=11)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.01, -0.09), ncol=4, frameon=False, fontsize=9)
    fig.text(0.01, 0.005, "Rows All–Comment: liveblogs and match reports excluded. "
             "Old group (16 signings) too small for conclusions.", fontsize=8, color=INK2)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=200, facecolor=SURF)
    plt.close(fig)


def load_scores(folder):
    out = None
    for m in METHODS:
        d = pd.read_csv(folder / f"a1_{m}_scores.csv")
        d = d.rename(columns={"score": m})
        out = d if out is None else out.merge(d[["sentence_row", m]], on="sentence_row",
                                              how="inner", validate="1:1")
    return out


def agreement(sc, sample_label):
    rows = []
    ms = list(METHODS)
    for i, a in enumerate(ms):
        for b in ms[i + 1:]:
            x, y = sc[a], sc[b]
            nz = (x != 0) & (y != 0)
            rows.append({"sample": sample_label, "method_a": METHODS[a], "method_b": METHODS[b],
                         "sentences": len(sc),
                         "pearson_r": x.corr(y), "spearman_rho": x.corr(y, method="spearman"),
                         "share_both_nonzero": nz.mean(),
                         "sign_agreement_both_nonzero": (np.sign(x[nz]) == np.sign(y[nz])).mean()})
    return rows


def main(folder):
    folder = Path(folder)
    md, long = results_table(folder)
    (folder / "a1_roberta_table.md").write_text(md + "\n", encoding="utf-8")
    plot_methods(long, folder / "a1_roberta_vs_lexicons.png")
    print("Results table (after − before, 95% CI, permutation p):\n" + md + "\n")

    sc = load_scores(folder)
    sent = pd.read_csv(folder / "sentences.csv", usecols=["sentence", "player"])
    sc = sc.join(sent, on="sentence_row")
    main_s = sc[~sc.article_type.isin(["liveblog", "matchreport"])]
    agr = pd.DataFrame(agreement(sc, "all scored sentences (no liveblogs)")
                       + agreement(main_s, "main sample (no liveblog/matchreport)"))
    agr.round(4).to_csv(folder / "a1_roberta_vs_lexicons.csv", index=False, encoding="utf-8-sig")
    print(agr.round(3).to_string(index=False), "\n")

    # disagreements: VADER and Bing agree on the sign, RoBERTa says the opposite;
    # ranked by the gap between RoBERTa and the lexicon average. Main sample, one row
    # per distinct sentence, sentences of 6-60 words (longer rows are mostly parse junk).
    words = main_s.sentence.astype(str).str.split().str.len()
    d = main_s[(words.between(6, 60))].copy()
    lex = (d.vader + d.bing) / 2
    opp = (np.sign(d.vader) == np.sign(d.bing)) & (d.vader != 0) & (np.sign(d.roberta) == -np.sign(lex))
    d = d[opp].assign(gap=(d.roberta - lex).abs()[opp], lexicons_say=np.where(lex[opp] > 0, "positive", "negative"))
    d = d.sort_values("gap", ascending=False).drop_duplicates("sentence")
    top = pd.concat([d[d.lexicons_say == "positive"].head(10), d[d.lexicons_say == "negative"].head(10)])
    cols = ["sentence_row", "article_type", "player", "lexicons_say", "vader", "bing",
            "bing_nofootball", "roberta", "gap", "sentence"]
    top[cols].round(3).to_csv(folder / "a1_roberta_disagreements.csv", index=False, encoding="utf-8-sig")
    print(f"{len(d)} distinct main-sample sentences where both lexicons agree and RoBERTa has the "
          "opposite sign;\nsaved the 10 largest gaps in each direction to a1_roberta_disagreements.csv")
    return sc, agr, top


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
