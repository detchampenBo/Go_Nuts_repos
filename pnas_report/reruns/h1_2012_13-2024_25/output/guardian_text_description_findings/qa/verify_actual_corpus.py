"""Independent checks of the actual descriptive exports; no scoring or fitting."""
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

import spacy
from spacy.lang.en.stop_words import STOP_WORDS


OUTPUT = Path(__file__).resolve().parent.parent
summary = json.loads((OUTPUT / "corpus_summary.json").read_text(encoding="utf-8"))
metadata = summary["metadata"]


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


assert metadata["score_check"]["performed"] is False
assert "scores" not in metadata["inputs"]
assert "--without-score-check" in metadata["reproduction_command"]
for info in [*metadata["inputs"].values(), metadata["script"]]:
    assert sha256(info["path"]) == info["sha256"]
    assert Path(info["path"]).stat().st_size == info["bytes"]
for name in metadata["outputs"]:
    assert (OUTPUT / name).is_file(), name

members = {row["signing_id"]: row for row in rows(metadata["inputs"]["members"]["path"])}
source = rows(metadata["inputs"]["sentences"]["path"])
selected = []
counts = Counter()
for index, row in enumerate(source):
    if (row["signing_id"] not in members or row["period"] not in ("before", "after")
            or row["article_type"] in ("liveblog", "matchreport")):
        continue
    day = int(row["days_from_transfer"])
    assert (-365 <= day <= -8) if row["period"] == "before" else (8 <= day <= 365)
    assert row["article_id"] and row["sentence"].strip()
    selected.append(row)
    counts[row["signing_id"], row["period"]] += 1
for sid, member in members.items():
    for period in ("before", "after"):
        assert counts[sid, period] == int(float(member["n_sent_" + period]))
assert len(members) == 820 and len(selected) == 99976
assert sum(int(row["age_at_transfer"]) >= 30 for row in members.values()) == 67
assert Counter(row["period"] for row in selected) == {"before": 39542, "after": 60434}

with gzip.open(OUTPUT / "tokens.json.gz", "rt", encoding="utf-8") as handle:
    tokens = json.load(handle)
assert isinstance(tokens, list) and all(isinstance(token, str) for token in tokens)
assert all(token == token.lower() for token in tokens)
tokenizer = spacy.blank("en").tokenizer
offset = 0
documents = defaultdict(lambda: [0, 0, 0])
for row, doc in zip(selected, tokenizer.pipe(row["sentence"] for row in selected)):
    words = [token.text.lower() for token in doc if not token.is_space and not token.is_punct]
    assert tokens[offset:offset + len(words)] == words
    offset += len(words)
    values = documents[row["signing_id"], row["article_id"], row["period"]]
    values[0] += 1
    values[1] += len(words)
    values[2] += sum(word not in STOP_WORDS for word in words)
assert offset == len(tokens)

frequencies = []
stream_checks = {}
for filename, suffix, stream in (
        ("token_frequencies.csv", "", tokens),
        ("token_frequencies_no_stopwords.csv", "_no_stopwords",
         [token for token in tokens if token not in STOP_WORDS])):
    table = rows(OUTPUT / filename)
    expected = sorted(Counter(stream).items(), key=lambda item: (-item[1], item[0]))
    assert [(row["token"], int(row["count"])) for row in table] == expected
    assert [int(row["rank"]) for row in table] == list(range(1, len(table) + 1))
    for row in table:
        assert float(row["relative_frequency"]) == int(row["count"]) / len(stream)
    total_frequency = sum(float(row["relative_frequency"]) for row in table)
    assert abs(total_frequency - 1) < 1e-10
    assert summary["n_tokens" + suffix] == len(stream)
    assert summary["n_types" + suffix] == len(expected)
    assert summary["n_hapax" + suffix] == sum(count == 1 for _, count in expected)
    frequencies.append(table)
    stream_checks[filename] = {"n_tokens": len(stream), "n_types": len(expected),
                               "n_hapax": summary["n_hapax" + suffix],
                               "relative_frequency_sum": total_frequency}

top = rows(OUTPUT / "top_five_words.csv")
assert [int(row["rank"]) for row in top] == [1, 2, 3, 4, 5]
for table, suffix in zip(frequencies, ("", "_no_stopwords")):
    for row, expected in zip(top, table[:5]):
        assert row["word" + suffix] == expected["token"]
        assert row["count" + suffix] == expected["count"]
        assert row["relative_frequency" + suffix] == expected["relative_frequency"]

document_rows = rows(OUTPUT / "document_lengths.csv")
assert len(document_rows) == len(documents) == metadata["n_signing_article_period_documents"]
for row in document_rows:
    key = row["signing_id"], row["article_id"], row["period"]
    assert [int(row[field]) for field in ("n_sentences", "n_tokens", "n_tokens_no_stopwords")] == documents[key]
assert sum(int(row["n_sentences"]) for row in document_rows) == len(selected)
assert sum(int(row["n_tokens"]) for row in document_rows) == len(tokens)
assert sum(int(row["n_tokens_no_stopwords"]) for row in document_rows) == summary["n_tokens_no_stopwords"]

base = frequencies[0]
rank1_count = int(base[0]["count"])
comparisons = []
for rank in (1, 2, 5, 10, 100, 1000, 10000, len(base)):
    row = base[rank - 1]
    comparisons.append({"rank": rank, "token": row["token"], "count": int(row["count"]),
                        "observed_relative_frequency": float(row["relative_frequency"]),
                        "rank1_anchored_reference": rank1_count / len(tokens) / rank,
                        "observed_to_reference_ratio": int(row["count"]) * rank / rank1_count})

report = {
    "scope": "ACTUAL corpus; explicit score-check omission retained",
    "status": "all independent data checks passed",
    "original_source_rows": len(source), "selected_rows": len(selected),
    "signings": len(members), "older_signings": 67,
    "sentence_period_counts": dict(Counter(row["period"] for row in selected)),
    "zero_signing_period_count_mismatches": True,
    "all_tokens_independently_retokenized_in_original_row_order": True,
    "score_alignment_and_finite_score_validity_checked": False,
    "streams": stream_checks, "linked_documents": len(documents),
    "document_totals_and_each_document_independently_verified": True,
    "rank_reference_descriptive_comparisons": comparisons,
    "output_sha256": {name: sha256(OUTPUT / name) for name in metadata["outputs"]},
    "verifier_sha256": sha256(__file__),
}
(OUTPUT / "qa/actual_data_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
