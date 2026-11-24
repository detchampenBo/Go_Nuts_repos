"""Describe the saved main H2 sentence corpus; never score or refit anything.

Run with --sentences PATH and either --scores PATH or --without-score-check.
The latter explicitly omits score-pointer alignment and finite-score validation.
Original CSV row
positions, not filtered/reset positions or sentence strings, identify sentences.
spaCy and matplotlib are imported only when producing outputs.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys


HERE = Path(__file__).resolve().parent
REPORT = HERE.parents[2]
DEFAULT_MEMBERS = REPORT / "data/dataset_nlp/results/a1_roberta_per_signing.csv"
DEFAULT_OUTPUT = HERE.parent / "output/guardian_text_description_findings"
OUTPUTS = ["tokens.json.gz", "token_frequencies.csv",
           "token_frequencies_no_stopwords.csv", "top_five_words.csv",
           "top_five_words.md", "corpus_summary.json", "document_lengths.csv",
           "rank_frequency.pdf", "rank_frequency.png", "rank_frequency.svg", "README.md"]


def read_csv(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        return list(reader)


def integer(value, label):
    number = float(value)
    if not number.is_integer():
        raise ValueError(f"{label}: expected integer, got {value!r}")
    return int(number)


def read_members(path):
    rows = read_csv(path, ["signing_id", "age_at_transfer", "n_sent_before", "n_sent_after"])
    members = {}
    for row in rows:
        sid = row["signing_id"]
        if not sid or sid in members:
            raise ValueError(f"Empty or duplicate membership signing_id: {sid!r}")
        row["age_at_transfer"] = integer(row["age_at_transfer"], "age_at_transfer")
        for period in ("before", "after"):
            key = f"n_sent_{period}"
            row[key] = integer(row[key], key)
            if row[key] < 1:
                raise ValueError(f"{sid}: {key} must be positive")
        members[sid] = row
    return members


def verify_main_members(members):
    observed = (len(members), sum(row["age_at_transfer"] >= 30 for row in members.values()),
                sum(row["n_sent_before"] for row in members.values()),
                sum(row["n_sent_after"] for row in members.values()))
    if observed != (820, 67, 39542, 60434):
        raise ValueError("Main H2 membership must contain 820 signings, 67 aged 30+, "
                         f"39542 before and 60434 after sentences; observed {observed}")
    if any(row[f"n_sent_{period}"] < 5 for row in members.values() for period in ("before", "after")):
        raise ValueError("Main H2 membership requires at least five sentences per signing in each period")


def select_sentences(sentences_path, scores_path, members, *, without_score_check=False):
    """Retain saved paired membership; score checks require the original scores."""
    if (scores_path is None) != without_score_check:
        raise ValueError("Supply scores or explicitly select without_score_check")
    sentences = read_csv(sentences_path, ["sentence", "signing_id", "article_id", "period",
                                           "article_type", "days_from_transfer"])
    if without_score_check:
        candidates = ((index, None) for index in range(len(sentences)))
    else:
        scores = read_csv(scores_path, ["sentence_row", "signing_id", "period", "score"])
        candidates = ((integer(score["sentence_row"], "sentence_row"), score) for score in scores)
    seen, selected, counts = set(), [], Counter()
    for index, score in candidates:
        if index in seen or not 0 <= index < len(sentences):
            raise ValueError(f"Duplicate or out-of-range sentence_row: {index}")
        seen.add(index)
        sentence = sentences[index]
        for key in ("article_id", "signing_id", "period", "article_type"):
            if score is not None and key in score and score[key] != sentence[key]:
                raise ValueError(f"sentence_row {index}: {key} differs between scores and sentences")
        sid, period = sentence["signing_id"], sentence["period"]
        if (sid not in members or period not in ("before", "after")
                or sentence["article_type"] in ("liveblog", "matchreport")):
            continue
        if score is not None:
            try:
                value = float(score["score"])
            except (ValueError, TypeError):
                raise ValueError(f"sentence_row {index}: missing or nonnumeric score") from None
            if not math.isfinite(value):
                raise ValueError(f"sentence_row {index}: nonfinite score")
        days = integer(sentence["days_from_transfer"], f"sentence_row {index} days_from_transfer")
        low, high = (-365, -8) if period == "before" else (8, 365)
        if not low <= days <= high:
            raise ValueError(f"sentence_row {index}: {period} day {days} outside [{low}, {high}]")
        if not sentence["article_id"] or not sentence["sentence"].strip():
            raise ValueError(f"sentence_row {index}: missing article_id or sentence text")
        selected.append(dict(sentence, sentence_row=index))
        counts[sid, period] += 1
    for sid, member in members.items():
        for period in ("before", "after"):
            expected = member[f"n_sent_{period}"]
            if counts[sid, period] != expected:
                raise ValueError(f"{sid} {period}: retained {counts[sid, period]} sentences; "
                                 f"saved membership requires {expected}")
    # Stable original-row order preserves repeated/shared article contributions.
    return sorted(selected, key=lambda row: row["sentence_row"])


def token_strings(doc):
    """Lowercase surface forms; retain names, inflections, numbers and symbols."""
    return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]


def frequency_rows(tokens):
    counts = Counter(tokens)
    total = sum(counts.values())
    return [{"rank": rank, "token": token, "count": count, "relative_frequency": count / total}
            for rank, (token, count) in enumerate(
                sorted(counts.items(), key=lambda item: (-item[1], item[0])), 1)]


def stream_summary(rows):
    return {"n_tokens": sum(row["count"] for row in rows), "n_types": len(rows),
            "n_hapax": sum(row["count"] == 1 for row in rows)}


def top_five_rows(all_rows, no_stop_rows):
    rows = []
    for index in range(min(5, max(len(all_rows), len(no_stop_rows)))):
        row = {"rank": index + 1}
        for source, suffix in ((all_rows, ""), (no_stop_rows, "_no_stopwords")):
            word = source[index] if index < len(source) else {}
            row.update({"word" + suffix: word.get("token", ""),
                        "count" + suffix: word.get("count", ""),
                        "relative_frequency" + suffix: word.get("relative_frequency", "")})
        rows.append(row)
    return rows


def write_csv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def file_info(path):
    path = Path(path).resolve()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def load_tokenizer():
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    nlp = spacy.blank("en")
    metadata = {"spacy_version": spacy.__version__, "language": "en", "pipeline": [],
                "tokenizer": "spacy.blank('en').tokenizer",
                "stopword_source": "spacy.lang.en.stop_words.STOP_WORDS",
                "stopword_count": len(STOP_WORDS),
                "stopword_sha256": hashlib.sha256(
                    "\n".join(sorted(STOP_WORDS)).encode("utf-8")).hexdigest(),
                "stopword_hash_encoding": "UTF-8, sorted entries joined by newline, no final newline"}
    return nlp.tokenizer, STOP_WORDS, metadata


def plot_rank_frequency(rows, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font = font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.labelsize": 9.5,
                         "legend.fontsize": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                         "svg.hashsalt": "guardian-h2-corpus-description",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.6, "text.color": "#333333",
                         "axes.labelcolor": "#333333", "axes.edgecolor": "#333333"})
    fig, ax = plt.subplots(figsize=(3.58, 3.2))
    ranks = [row["rank"] for row in rows]
    frequencies = [row["relative_frequency"] for row in rows]
    ax.plot(ranks, frequencies, color="#372107", linewidth=1.1, label="Observed tokens")
    ax.plot(ranks, [frequencies[0] / rank for rank in ranks], color="#895211",
            linestyle="--", linewidth=1.0, label="1/r reference (rank-1 anchored)")
    ax.set(xlabel="Token rank (linear scale)", ylabel="Relative frequency (linear scale)",
           xlim=(0, max(1, len(rows))), ylim=(0, frequencies[0] * 1.05))
    ax.grid(color="#B0B0B0", linewidth=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5, width=0.6, labelsize=9)
    legend = ax.legend(loc="upper right", framealpha=1, edgecolor="#BBBBBB")
    legend.get_frame().set_linewidth(0.6)
    fig.subplots_adjust(left=0.23, right=0.97, bottom=0.19, top=0.97)
    fig.savefig(output / "rank_frequency.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(output / "rank_frequency.png", dpi=600)
    fig.savefig(output / "rank_frequency.svg", metadata={"Date": None})
    plt.close(fig)
    return {"matplotlib_version": matplotlib.__version__, "font": file_info(font),
            "width_inches": 3.58, "height_inches": 3.2, "png_dpi": 600,
            "axes": "linear", "reference": "observed rank-1 relative frequency / rank"}


def write_outputs(selected, members, output, inputs, command, *, synthetic=False):
    """Write validated observations; synthetic callers must use an isolated QA path."""
    output = Path(output).resolve()
    if synthetic and "synthetic_fixture" not in output.parts:
        raise ValueError("Synthetic outputs must live in a synthetic_fixture directory")
    tokenizer, stopwords, tokenizer_metadata = load_tokenizer()
    tokens, no_stopwords, lengths = [], [], defaultdict(lambda: [0, 0, 0])
    for sentence, doc in zip(selected, tokenizer.pipe(row["sentence"] for row in selected)):
        words = token_strings(doc)
        content = [word for word in words if word not in stopwords]
        tokens.extend(words)
        no_stopwords.extend(content)
        key = sentence["signing_id"], sentence["article_id"], sentence["period"]
        values = lengths[key]
        values[0] += 1
        values[1] += len(words)
        values[2] += len(content)
    if not tokens:
        raise ValueError("Selected corpus contains no retained tokens")
    all_rows, no_stop_rows = frequency_rows(tokens), frequency_rows(no_stopwords)
    summary = stream_summary(all_rows)
    summary.update({key + "_no_stopwords": value
                    for key, value in stream_summary(no_stop_rows).items()})
    period_counts = Counter(row["period"] for row in selected)
    summary["metadata"] = {"status": "SYNTHETIC FIXTURE ONLY" if synthetic else "actual main H2 corpus",
                           "inputs": inputs, "script": file_info(__file__),
                           "python_version": platform.python_version(), "tokenization": tokenizer_metadata,
                           "n_sentences": len(selected), "n_signings": len(members),
                           "n_signings_age30plus": sum(row["age_at_transfer"] >= 30 for row in members.values()),
                           "n_signings_under30": sum(row["age_at_transfer"] < 30 for row in members.values()),
                           "sentence_counts_by_age30": {
                               "under30": sum(members[row["signing_id"]]["age_at_transfer"] < 30
                                              for row in selected),
                               "age30plus": sum(members[row["signing_id"]]["age_at_transfer"] >= 30
                                                for row in selected)},
                           "sentence_counts_by_period": dict(sorted(period_counts.items())),
                           "n_signing_article_period_documents": len(lengths),
                           "sentence_order": "ascending original zero-based sentences.csv row",
                           "rank_ties": "descending count, then lexicographic lowercase token",
                           "reproduction_command": command, "outputs": OUTPUTS}
    score_checked = "scores" in inputs or "scores.csv" in inputs
    summary["metadata"]["score_check"] = {
        "performed": score_checked,
        "selection": "original score row pointers" if score_checked else "original sentence rows",
        "limitation": None if score_checked else (
            "Original sentence-level scores unavailable; score-pointer identity/alignment and "
            "finite-score validity were not checked, at the user's explicit request. "
            "Saved membership and every signing-period count match, but this alone does not "
            "prove sentence-level identity with the scored corpus.")}
    summary["metadata"]["selection_checks"] = {
        "saved_signing_period_counts_exact": True,
        "excluded_article_types": ["liveblog", "matchreport"],
        "before_days_inclusive": [-365, -8], "after_days_inclusive": [8, 365],
        "article_ids_and_sentence_text_nonempty": True}
    output.mkdir(parents=True, exist_ok=True)
    summary["metadata"]["plot"] = plot_rank_frequency(all_rows, output)
    with (output / "tokens.json.gz").open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as handle:
                json.dump(tokens, handle, ensure_ascii=False, separators=(",", ":"))
    fields = ["rank", "token", "count", "relative_frequency"]
    write_csv(output / "token_frequencies.csv", all_rows, fields)
    write_csv(output / "token_frequencies_no_stopwords.csv", no_stop_rows, fields)
    top = top_five_rows(all_rows, no_stop_rows)
    top_fields = ["rank", "word", "count", "relative_frequency", "word_no_stopwords",
                  "count_no_stopwords", "relative_frequency_no_stopwords"]
    write_csv(output / "top_five_words.csv", top, top_fields)
    table = ["| Rank | Word | Count | Relative frequency | Word (no stopwords) | Count | Relative frequency |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in top:
        values = []
        for key in top_fields:
            value = row[key]
            values.append(f"{value:.8g}" if isinstance(value, float) else str(value).replace("|", "&#124;"))
        table.append("| " + " | ".join(values) + " |")
    (output / "top_five_words.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    documents = [dict(zip(["signing_id", "article_id", "period", "n_sentences", "n_tokens",
                          "n_tokens_no_stopwords"], (*key, *values)))
                 for key, values in sorted(lengths.items())]
    write_csv(output / "document_lengths.csv", documents,
              ["signing_id", "article_id", "period", "n_sentences", "n_tokens", "n_tokens_no_stopwords"])
    (output / "corpus_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    label = "SYNTHETIC FIXTURE ONLY — no Guardian corpus findings" if synthetic else "Guardian main H2 corpus description"
    selection_note = (
        "Original zero-based sentence rows are joined to saved score rows and checked\n"
        "against their available article/signing/period/type metadata."
        if score_checked else
        "Selection uses original sentence rows directly, with the user's explicit\n"
        "--without-score-check waiver because original sentence-level scores are unavailable.\n"
        "Score-pointer identity/alignment and finite-score validity were not verified.\n"
        "Exact saved counts alone do not prove sentence-level identity with the scored corpus.")
    readme = f"""# {label}

Retained {len(selected):,} sentence contributions across {len(members):,} signings.
All-token stream: N = {summary['n_tokens']:,}; observed types = {summary['n_types']:,};
hapax types (count exactly one) = {summary['n_hapax']:,}.
Without stopwords: N = {summary['n_tokens_no_stopwords']:,}; observed types =
{summary['n_types_no_stopwords']:,}; hapax types = {summary['n_hapax_no_stopwords']:,}.

## Caption

Pooled token relative frequency by descending frequency rank in the selected H2
sentence corpus. Both axes are linear. The dashed 1/r reference is anchored to
the observed rank-1 relative frequency; it is a visual reference, not a fitted
law or estimated exponent. A linear curve alone cannot establish Zipf's law.

## Corpus and interpretation

{selection_note}
Saved H2 signing
membership and each signing's before/after sentence counts must match exactly.
Only before (-365 through -8 days) and after (+8 through +365 days), inclusive,
are retained; liveblogs and match reports are excluded. Shared article/signing
contributions and repeated sentence strings are preserved. Documents in
`document_lengths.csv` mean signing/article/period groups,
not unique newspaper articles.

spaCy blank English supplies tokenization only. Surface tokens are lowercased;
punctuation and spaces are removed; inflections, player names, numbers and other
non-punctuation tokens remain. The second stream additionally removes spaCy
English stopwords by lowercase surface form. No lemmatization is performed.
Each frequency is count/N using its own stream's N. This relative-frequency
normalisation does not equal-weight unequal-length documents: longer documents
contribute more tokens. The observed-token vocabulary excludes unseen words.
Types count distinct retained tokens; hapax types occur exactly once.
Ties sort lexicographically, so results reproduce across runs.
English contractions and possessives may be separate surface tokens. These counts
describe complete sentence strings, not RoBERTa subword inputs truncated at 128 tokens.

## Files and reproduction

[Plot PDF](rank_frequency.pdf), [600-dpi PNG](rank_frequency.png),
[editable-text SVG](rank_frequency.svg), [top five](top_five_words.md),
[full provenance and summary](corpus_summary.json). `tokens.json.gz` is one
flattened JSON list; both complete frequency tables and document lengths are CSVs.
The default output folder's `tokens.json.gz` ignore rule keeps ordered token
exports local, including nested QA outputs. Other tables and summaries are not
automatically ignored. Keep token exports local when overriding the output path.
No manuscript inclusion is implied.

```text
{command}
```

Input paths, SHA-256 hashes and byte sizes, script hash, package versions,
stopword-list hash, font file, sample counts and complete output list are recorded
in `corpus_summary.json`. Production requires original sentences and saved membership;
original scores are required unless --without-score-check is explicitly supplied.
Synthetic fixture outputs cannot substitute for original inputs. Historical
setup/readiness records describe earlier input availability and are preserved.
"""
    (output / "README.md").write_text(readme, encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences", type=Path, required=True, help="Original full sentences.csv")
    score_mode = parser.add_mutually_exclusive_group(required=True)
    score_mode.add_argument("--scores", type=Path, help="Original a1_roberta_scores.csv")
    score_mode.add_argument("--without-score-check", action="store_true",
                            help="Explicitly omit unavailable score-pointer and finite-score checks")
    parser.add_argument("--members", type=Path, default=DEFAULT_MEMBERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    members = read_members(args.members)
    verify_main_members(members)
    selected = select_sentences(args.sentences, args.scores, members,
                                without_score_check=args.without_score_check)
    input_paths = {"sentences": args.sentences, "members": args.members}
    if args.scores is not None:
        input_paths["scores"] = args.scores
    inputs = {}
    for name, path in input_paths.items():
        inputs[name] = file_info(path)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            inputs[name]["columns"] = next(csv.reader(handle))
    argv = [sys.executable, "-B", str(Path(__file__).resolve()),
            "--sentences", str(args.sentences.resolve())]
    argv += (["--without-score-check"] if args.without_score_check else
             ["--scores", str(args.scores.resolve())])
    argv += ["--members", str(args.members.resolve()), "--output", str(args.output.resolve())]
    command = "& " + " ".join("'" + value.replace("'", "''") + "'" for value in argv)
    summary = write_outputs(selected, members, args.output, inputs, command)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
