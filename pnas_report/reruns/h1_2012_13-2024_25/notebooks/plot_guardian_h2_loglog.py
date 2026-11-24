"""Export a log-log view and top-ten tables from saved Guardian H2 frequencies.

Presentation only: no source text, tokenisation, scores, fitting or age tests.
"""

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker


OUTPUT = Path(__file__).resolve().parents[1] / "output/guardian_text_description_findings"


def read_frequencies(filename, summary, suffix=""):
    with (OUTPUT / filename).open(encoding="utf-8", newline="") as handle:
        rows = [{"rank": int(row["rank"]), "token": row["token"],
                 "count": int(row["count"]),
                 "relative_frequency": float(row["relative_frequency"])}
                for row in csv.DictReader(handle)]
    total = summary["n_tokens" + suffix]
    assert len(rows) == summary["n_types" + suffix]
    assert sum(row["count"] for row in rows) == total
    assert sum(row["count"] == 1 for row in rows) == summary["n_hapax" + suffix]
    assert rows == sorted(rows, key=lambda row: (-row["count"], row["token"]))
    assert len({row["token"] for row in rows}) == len(rows)
    for rank, row in enumerate(rows, 1):
        assert row["rank"] == rank and row["count"] > 0
        assert row["relative_frequency"] == row["count"] / total
    assert math.isclose(sum(row["relative_frequency"] for row in rows), 1.0, abs_tol=1e-12)
    return rows


def write_top_ten(base, no_stop, summary):
    lines = ["# Top ten words in the selected Guardian H2 corpus", "",
             f"Relative frequency is count/N: base N = {summary['n_tokens']:,}; "
             f"no-stopword N = {summary['n_tokens_no_stopwords']:,}. "
             "Both streams exclude punctuation and whitespace; ties sort by lowercase token.", "",
             "| Rank | Word | Count | Relative frequency | Word (no stopwords) | Count | Relative frequency |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for first, second in zip(base[:10], no_stop[:10]):
        values = [str(first["rank"])]
        for row in (first, second):
            values.extend([row["token"].replace("|", "&#124;"), str(row["count"]),
                           f"{row['relative_frequency']:.8g}"])
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "`top_ten_words.md` is canonical. `top_five_words.md` contains this same "
              "ten-row table to preserve earlier links. The original `top_five_words.csv` "
              "remains a five-row historical export; both complete frequency CSVs supply this table.", ""]
    table = "\n".join(lines)
    for filename in ("top_ten_words.md", "top_five_words.md"):
        (OUTPUT / filename).write_text(table, encoding="utf-8")


def power_label(value, _position):
    exponent = round(math.log10(value))
    # Plain Arial text keeps every tick at 9 pt, including negative exponents.
    return f"{value:,.0f}" if exponent >= 0 else f"1e−{abs(exponent)}"


def plot(base):
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({"font.family": "Arial", "font.size": 9,
                         "axes.labelsize": 9.5, "legend.fontsize": 8,
                         "pdf.fonttype": 42, "svg.fonttype": "none",
                         "svg.hashsalt": "guardian-h2-loglog",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.6, "text.color": "#333333",
                         "axes.labelcolor": "#333333", "axes.edgecolor": "#333333",
                         "xtick.color": "#333333", "ytick.color": "#333333"})
    fig, ax = plt.subplots(figsize=(3.58, 3.4))
    ranks = [row["rank"] for row in base]
    frequencies = [row["count"] for row in base]
    reference = [frequencies[0] / rank for rank in ranks]
    ax.loglog(ranks, frequencies, color="#372107", linewidth=1.1, label="Observed tokens")
    ax.loglog(ranks, reference, color="#895211", linestyle="--", linewidth=1.0,
              label="ideal Zipf, s = 1")
    ax.set(xlabel="Frequency rank", ylabel="Frequency (token count)",
           xlim=(0.8, len(base) * 1.3),
           ylim=(min(frequencies[-1], reference[-1]) / 1.45, frequencies[0] * 1.65))
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(ticker.LogLocator(base=10))
        axis.set_major_formatter(ticker.FuncFormatter(power_label))
        axis.set_minor_locator(ticker.NullLocator())
    ax.grid(which="major", color="#B0B0B0", linewidth=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5, width=0.6, labelsize=9)
    legend = ax.legend(loc="upper right", framealpha=1, facecolor="white", edgecolor="#BBBBBB")
    legend.get_frame().set_linewidth(0.6)
    fig.subplots_adjust(left=0.25, right=0.97, bottom=0.18, top=0.97)
    fig.savefig(OUTPUT / "rank_frequency_loglog.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(OUTPUT / "rank_frequency_loglog.png", dpi=600)
    fig.savefig(OUTPUT / "rank_frequency_loglog.svg", metadata={"Date": None})
    plt.close(fig)


def main():
    summary = json.loads((OUTPUT / "corpus_summary.json").read_text(encoding="utf-8"))
    base = read_frequencies("token_frequencies.csv", summary)
    no_stop = read_frequencies("token_frequencies_no_stopwords.csv", summary, "_no_stopwords")
    plot(base)
    write_top_ten(base, no_stop, summary)
    print("Exported full-vocabulary log-log plot and both top-ten Markdown tables from saved frequencies.")


if __name__ == "__main__":
    main()
