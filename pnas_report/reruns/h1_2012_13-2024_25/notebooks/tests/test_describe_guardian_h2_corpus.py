"""Synthetic-only QA; no original Guardian text or saved score analysis is run.

python -B -m unittest discover -s pnas_report/reruns/h1_2012_13-2024_25/notebooks/tests -v

The real-spaCy export test skips clearly if its dependencies are unavailable.
Its retained artifacts live only in output/guardian_text_description_findings/qa/synthetic_fixture.
"""
from collections import namedtuple
import csv
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "describe_guardian_h2_corpus.py"
spec = importlib.util.spec_from_file_location("describe_guardian_h2_corpus", SCRIPT)
corpus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(corpus)
SENTENCE_FIELDS = ["sentence", "signing_id", "article_id", "period", "article_type", "days_from_transfer"]
SCORE_FIELDS = ["sentence_row", "signing_id", "article_id", "period", "article_type", "score"]
MEMBER_FIELDS = ["signing_id", "age_at_transfer", "n_sent_before", "n_sent_after"]


def fixture(folder):
    """Two invented signings, repeated text/shared article and a liveblog row hole."""
    folder.mkdir(parents=True, exist_ok=True)
    values = [
        ("The Ada players scored 2 goals.", "synthetic_A", "shared", "before", "news", -365),
        ("Live updates.", "synthetic_A", "live", "before", "liveblog", -30),
        ("The Ada players scored 2 goals.", "synthetic_A", "shared", "before", "news", -8),
        ("Ada's players score, and win!", "synthetic_A", "a_after", "after", "features", 8),
        ("THE club won 3 games.", "synthetic_A", "a_after", "after", "features", 365),
        ("The Ada players scored 2 goals.", "synthetic_B", "shared", "before", "news", -8),
        ("Zed joined the club.", "synthetic_B", "b_after", "after", "comment", 8),
        ("A match report.", "synthetic_A", "match", "before", "matchreport", -20),
        ("Transfer day.", "synthetic_A", "around", "around", "news", 0),
        ("Outside saved membership.", "synthetic_outside", "other", "after", "news", 12),
    ]
    sentences = [dict(zip(SENTENCE_FIELDS, row)) for row in values]
    scores = [dict(sentence_row=index, score=0.1,
                   **{key: row[key] for key in SCORE_FIELDS if key not in ("sentence_row", "score")})
              for index, row in enumerate(sentences) if index != 1]
    members = [{"signing_id": "synthetic_A", "age_at_transfer": 24, "n_sent_before": 2, "n_sent_after": 2},
               {"signing_id": "synthetic_B", "age_at_transfer": 31, "n_sent_before": 1, "n_sent_after": 1}]
    paths = {name: folder / name for name in ("sentences.csv", "scores.csv", "members.csv")}
    corpus.write_csv(paths["sentences.csv"], sentences, SENTENCE_FIELDS)
    corpus.write_csv(paths["scores.csv"], scores, SCORE_FIELDS)
    corpus.write_csv(paths["members.csv"], members, MEMBER_FIELDS)
    return paths, sentences, scores


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="guardian_synthetic_")
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.paths, self.sentences, self.scores = fixture(self.folder)
        self.members = corpus.read_members(self.paths["members.csv"])

    def select(self):
        return corpus.select_sentences(self.paths["sentences.csv"], self.paths["scores.csv"], self.members)

    def test_original_row_hole_eligibility_shared_text_and_inclusive_boundaries(self):
        selected = self.select()
        self.assertEqual([row["sentence_row"] for row in selected], [0, 2, 3, 4, 5, 6])
        self.assertEqual(sum(row["sentence"] == "The Ada players scored 2 goals." for row in selected), 3)
        self.assertEqual({row["signing_id"] for row in selected}, set(self.members))

    def test_scores_need_not_be_in_original_row_order(self):
        corpus.write_csv(self.paths["scores.csv"], list(reversed(self.scores)), SCORE_FIELDS)
        self.assertEqual([row["sentence_row"] for row in self.select()], [0, 2, 3, 4, 5, 6])

    def test_invalid_day_boundaries_stop(self):
        for index, invalid_day in ((0, -366), (2, -7), (3, 7), (4, 366)):
            with self.subTest(index=index, invalid_day=invalid_day):
                changed = [dict(row) for row in self.sentences]
                changed[index]["days_from_transfer"] = invalid_day
                corpus.write_csv(self.paths["sentences.csv"], changed, SENTENCE_FIELDS)
                with self.assertRaisesRegex(ValueError, "outside"):
                    self.select()

    def test_saved_per_signing_count_mismatch_stops(self):
        self.members["synthetic_A"]["n_sent_before"] = 3
        with self.assertRaisesRegex(ValueError, "retained 2.*requires 3"):
            self.select()

    def test_explicit_no_score_selection_preserves_rows_and_exclusions(self):
        self.paths["scores.csv"].unlink()
        selected = corpus.select_sentences(self.paths["sentences.csv"], None, self.members,
                                            without_score_check=True)
        self.assertEqual([row["sentence_row"] for row in selected], [0, 2, 3, 4, 5, 6])
        self.assertEqual(sum(row["sentence"] == "The Ada players scored 2 goals." for row in selected), 3)
        with self.assertRaisesRegex(ValueError, "explicitly"):
            corpus.select_sentences(self.paths["sentences.csv"], None, self.members)

    def test_no_score_selection_still_requires_exact_counts(self):
        self.members["synthetic_A"]["n_sent_before"] = 3
        with self.assertRaisesRegex(ValueError, "retained 2.*requires 3"):
            corpus.select_sentences(self.paths["sentences.csv"], None, self.members,
                                    without_score_check=True)

    def test_no_score_selection_still_checks_days_and_required_text(self):
        for key, value, message in (("days_from_transfer", -366, "outside"),
                                    ("article_id", "", "missing"), ("sentence", " ", "missing")):
            with self.subTest(key=key):
                changed = [dict(row) for row in self.sentences]
                changed[0][key] = value
                corpus.write_csv(self.paths["sentences.csv"], changed, SENTENCE_FIELDS)
                with self.assertRaisesRegex(ValueError, message):
                    corpus.select_sentences(self.paths["sentences.csv"], None, self.members,
                                            without_score_check=True)

    def test_cli_requires_exactly_one_explicit_score_mode(self):
        for options in ([], ["--scores", "unused.csv", "--without-score-check"]):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--sentences", "unused.csv",
                                     *options], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("--without-score-check", result.stderr)

    def test_join_metadata_must_agree(self):
        for key in ("article_id", "signing_id", "period", "article_type"):
            with self.subTest(key=key):
                changed = [dict(row) for row in self.scores]
                changed[0][key] = "wrong"
                corpus.write_csv(self.paths["scores.csv"], changed, SCORE_FIELDS)
                with self.assertRaisesRegex(ValueError, key + " differs"):
                    self.select()

    def test_duplicate_out_of_range_and_fractional_pointers_stop(self):
        for pointer in (0, -1, len(self.sentences), 2.5):
            with self.subTest(pointer=pointer):
                changed = [dict(row) for row in self.scores]
                changed[-1]["sentence_row"] = pointer
                corpus.write_csv(self.paths["scores.csv"], changed, SCORE_FIELDS)
                with self.assertRaises(ValueError):
                    self.select()

    def test_optional_score_metadata_can_come_from_sentences(self):
        fields = ["sentence_row", "signing_id", "period", "score"]
        corpus.write_csv(self.paths["scores.csv"], [{key: row[key] for key in fields} for row in self.scores], fields)
        self.assertEqual(len(self.select()), 6)

    def test_non_main_members_cannot_run_production(self):
        with self.assertRaisesRegex(ValueError, "Main H2 membership"):
            corpus.verify_main_members(self.members)

    def test_selected_missing_nonnumeric_and_nonfinite_scores_stop(self):
        for value in ("", "unscored", "nan", "inf", "-inf"):
            with self.subTest(value=value):
                changed = [dict(row) for row in self.scores]
                changed[0]["score"] = value
                corpus.write_csv(self.paths["scores.csv"], changed, SCORE_FIELDS)
                with self.assertRaisesRegex(ValueError, "score"):
                    self.select()
        fields = [key for key in SCORE_FIELDS if key != "score"]
        corpus.write_csv(self.paths["scores.csv"], [{key: row[key] for key in fields} for row in self.scores], fields)
        with self.assertRaisesRegex(ValueError, "missing columns.*score"):
            self.select()

    def test_main_aggregate_totals_do_not_allow_an_ineligible_signing(self):
        # Preserve the agreed totals while making one before period shorter than five.
        members = {str(index): {"age_at_transfer": 30 if index < 67 else 24,
                                "n_sent_before": 5, "n_sent_after": 5}
                   for index in range(820)}
        members["0"]["n_sent_before"] += 39542 - 820 * 5
        members["0"]["n_sent_after"] += 60434 - 820 * 5
        corpus.verify_main_members(members)
        members["1"]["n_sent_before"] = 4
        members["0"]["n_sent_before"] += 1
        with self.assertRaisesRegex(ValueError, "at least five"):
            corpus.verify_main_members(members)


class FrequencyTests(unittest.TestCase):
    def test_surface_policy_and_each_streams_denominator(self):
        # These token-like values test policy only; they do not simulate spaCy tokenization.
        Token = namedtuple("Token", "text is_punct is_space")
        words = corpus.token_strings([Token("The", False, False), Token("Players", False, False),
                                      Token("30", False, False), Token(".", True, False),
                                      Token(" ", False, True), Token("players", False, False)])
        self.assertEqual(words, ["the", "players", "30", "players"])
        all_rows = corpus.frequency_rows(words)
        no_stop_rows = corpus.frequency_rows([word for word in words if word not in {"the"}])
        self.assertEqual(all_rows[0]["relative_frequency"], 2 / 4)
        self.assertEqual(no_stop_rows[0]["relative_frequency"], 2 / 3)
        self.assertEqual(corpus.stream_summary(all_rows), {"n_tokens": 4, "n_types": 3, "n_hapax": 2})
        self.assertEqual(corpus.stream_summary([]), {"n_tokens": 0, "n_types": 0, "n_hapax": 0})

    def test_top_five_side_by_side_ties_and_short_second_stream(self):
        full = corpus.frequency_rows(["the", "the", "z", "z", "a", "b", "c", "d"])
        content = corpus.frequency_rows(["z", "z", "a"])
        rows = corpus.top_five_rows(full, content)
        self.assertEqual([row["word"] for row in rows], ["the", "z", "a", "b", "c"])
        self.assertEqual(rows[0]["word_no_stopwords"], "z")
        self.assertEqual(rows[0]["relative_frequency"], 2 / 8)
        self.assertEqual(rows[0]["relative_frequency_no_stopwords"], 2 / 3)
        self.assertEqual(rows[2]["count_no_stopwords"], "")


class RealTokenizerExportTests(unittest.TestCase):
    def test_real_spacy_synthetic_exports_and_reproducibility(self):
        try:
            import spacy
            import matplotlib
        except ImportError as error:
            self.skipTest(f"Actual spaCy/export test unavailable: {error}")
        self.assertTrue(spacy.__version__)
        self.assertTrue(matplotlib.__version__)
        output = corpus.DEFAULT_OUTPUT / "qa/synthetic_fixture"
        paths, _, _ = fixture(output / "inputs")
        members = corpus.read_members(paths["members.csv"])
        selected = corpus.select_sentences(paths["sentences.csv"], paths["scores.csv"], members)
        inputs = {key: corpus.file_info(path) for key, path in paths.items()}
        command = f"& '{sys.executable}' -B -m unittest discover -s '{Path(__file__).parent}' -v"
        first = corpus.write_outputs(selected, members, output, inputs, command, synthetic=True)
        repeated = output / "repeat"
        second = corpus.write_outputs(selected, members, repeated, inputs, command, synthetic=True)
        self.assertEqual(first, second)
        for name in corpus.OUTPUTS:
            with self.subTest(file=name):
                self.assertEqual((output / name).read_bytes(), (repeated / name).read_bytes())
        with gzip.open(output / "tokens.json.gz", "rt", encoding="utf-8") as handle:
            tokens = json.load(handle)
        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(token, str) for token in tokens))
        self.assertIn("ada", tokens)
        self.assertIn("players", tokens)
        self.assertIn("scored", tokens)
        self.assertIn("2", tokens)
        self.assertNotIn(".", tokens)
        self.assertNotIn(" ", tokens)
        self.assertEqual(tokens.count("scored"), 3)
        self.assertEqual(len(tokens), first["n_tokens"])
        content = corpus.read_csv(output / "token_frequencies_no_stopwords.csv", ["token"])
        self.assertNotIn("the", [row["token"] for row in content])
        for filename in ("token_frequencies.csv", "token_frequencies_no_stopwords.csv"):
            rows = corpus.read_csv(output / filename, ["relative_frequency"])
            self.assertAlmostEqual(sum(float(row["relative_frequency"]) for row in rows), 1)
        documents = corpus.read_csv(output / "document_lengths.csv", ["n_sentences"])
        self.assertEqual(len(documents), 4)
        self.assertEqual(sum(int(row["n_sentences"]) for row in documents), 6)
        self.assertEqual(sum(int(row["n_tokens"]) for row in documents), len(tokens))
        metadata = first["metadata"]
        self.assertEqual(metadata["status"], "SYNTHETIC FIXTURE ONLY")
        self.assertEqual(metadata["sentence_counts_by_period"], {"after": 3, "before": 3})
        self.assertEqual(metadata["n_signings_age30plus"], 1)
        self.assertEqual(metadata["tokenization"]["pipeline"], [])
        self.assertIn("SYNTHETIC FIXTURE ONLY", (output / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
