# SYNTHETIC FIXTURE ONLY — no Guardian corpus findings

Retained 6 sentence contributions across 2 signings.
All-token stream: N = 33; observed types = 16;
hapax types (count exactly one) = 9.
Without stopwords: N = 26; observed types =
13; hapax types = 7.

## Caption

Pooled token relative frequency by descending frequency rank in the selected H2
sentence corpus. Both axes are linear. The dashed 1/r reference is anchored to
the observed rank-1 relative frequency; it is a visual reference, not a fitted
law or estimated exponent. A linear curve alone cannot establish Zipf's law.

## Corpus and interpretation

Original zero-based sentence rows are joined to saved score rows and checked
against their available article/signing/period/type metadata.
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
& 'C:\Users\victo\Anaconda3\envs\network_analysis\python.exe' -B -m unittest discover -s 'C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\reruns\h1_2012_13-2024_25\notebooks\tests' -v
```

Input paths, SHA-256 hashes and byte sizes, script hash, package versions,
stopword-list hash, font file, sample counts and complete output list are recorded
in `corpus_summary.json`. Production requires original sentences and saved membership;
original scores are required unless --without-score-check is explicitly supplied.
Synthetic fixture outputs cannot substitute for original inputs. Historical
setup/readiness records describe earlier input availability and are preserved.
