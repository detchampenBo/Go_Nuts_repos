# Guardian main H2 corpus description

**Paper disposition approved, 24 November 2026:** Issue9.1 is Resolved. The user
approved the short corpus/Zipf Results introduction, matching Methods and
clarified Discussion explanation. Plots/top-ten remain repository artifacts;
no new manuscript figure/table selected. Original score alignment remains
waived/unverified and possible explanations untested. Next is Issue13 assembly,
then14 final fit/requirements/ZIP; the original page targets are unchanged.
Earlier awaiting-review/no-inclusion statements below are historical.

## Log–log plot and top ten, 24 November 2026

At the user's request, the [log–log PDF](rank_frequency_loglog.pdf),
[600-dpi PNG](rank_frequency_loglog.png) and [editable SVG](rank_frequency_loglog.svg)
show the complete base-stream vocabulary with logarithmic axes. The observed
raw token counts and rank-1-anchored `150246/r` reference use the same saved
counts as the preserved linear plot's underlying frequency table. The legend is
upper right, with the reference labelled **ideal Zipf, s = 1**; axes are
**Frequency rank** and **Frequency (token count)**. Arial, the brown palette, major gridlines and
3.58-inch standalone width follow `pnas_report/PLOTTING_STYLE.md`.

The [top-ten table](top_ten_words.md) displays both streams' counts and relative
frequencies using their separate denominators. The existing `top_five_words.md`
link now displays the same ten-row table; `top_five_words.csv` remains the original
five-row export. Full frequency CSVs supply the expanded table.

Proposed caption: Pooled surface-token count by frequency rank in the selected
Guardian corpus, with both axes logarithmic. The dashed ideal Zipf reference has
`s = 1` and count `150246/rank`, anchored to the most frequent token; no exponent
is fitted.

This view exposes departures hidden by linear-axis compression: the observed
curve lies above the reference across much of the head and middle, then bends
downward and falls below it in the sparse tail. The staircase reflects tied
integer token counts, including 13,022 singleton types. This descriptive plot
does not establish Zipf's law or an age/sentiment difference.

The [analysis summary](analysis_summary.md) examines these departures with raw
counts and discusses notable tokens, including football/club vocabulary,
financial notation and injury/availability wording. It distinguishes a broad
Zipf-like concentration from agreement with the displayed ideal line.

Reproduce the presentation from the saved frequency tables, without loading or
retokenising original sentences:

```powershell
& 'C:/Users/victo/Anaconda3/python.exe' -B 'pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_guardian_h2_loglog.py'
```

The already installed default Python environment exports this presentation.
The `network_analysis` environment failed even on a NumPy matrix multiplication
probe with native exception `0xc06d007f`; no packages or environments were changed.
[Presentation verification](qa/loglog_presentation_verification.json) records
versions, source/output hashes, top-ten checks and PDF/PNG/SVG QA. Original corpus
outputs, linear plots and original analytical producer are unchanged. The earlier
`qa/actual_data_verification.json` retains hashes from the original five-row
Markdown/README state; the presentation verification covers their later updates.
Original score alignment remains unverified as previously authorised. No
manuscript addition is selected.

Retained 99,976 sentence contributions across 820 signings.
All-token stream: N = 3,870,272; observed types = 42,779;
hapax types (count exactly one) = 13,022.
Without stopwords: N = 2,336,122; observed types =
42,469; hapax types = 13,017.

## Caption

Pooled token relative frequency by descending frequency rank in the selected H2
sentence corpus. Both axes are linear. The dashed 1/r reference is anchored to
the observed rank-1 relative frequency; it is a visual reference, not a fitted
law or estimated exponent. A linear curve alone cannot establish Zipf's law.

## Corpus and interpretation

Selection uses original sentence rows directly, with the user's explicit
--without-score-check waiver because original sentence-level scores are unavailable.
Score-pointer identity/alignment and finite-score validity were not verified.
Exact saved counts alone do not prove sentence-level identity with the scored corpus.
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
& 'C:\Users\victo\Anaconda3\envs\network_analysis\python.exe' '-B' 'C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\reruns\h1_2012_13-2024_25\notebooks\describe_guardian_h2_corpus.py' '--sentences' 'C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\data\dataset_nlp\data\sentences.csv' '--without-score-check' '--members' 'C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\data\dataset_nlp\results\a1_roberta_per_signing.csv' '--output' 'C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\reruns\h1_2012_13-2024_25\output\guardian_text_description_findings'
```

Input paths, SHA-256 hashes and byte sizes, script hash, package versions,
stopword-list hash, font file, sample counts and complete output list are recorded
in `corpus_summary.json`. Production requires original sentences and saved membership;
original scores are required unless --without-score-check is explicitly supplied.
Synthetic fixture outputs cannot substitute for original inputs. Historical
setup/readiness records describe earlier input availability and are preserved.

## Verified findings for review, 24 November 2026

Candidate corpus sentence (not added to the manuscript): "The selected sentence
corpus contained 3,870,272 lowercase surface tokens, comprising 42,779 distinct
types, of which 13,022 occurred once."

The selection retains 39,542 before and 60,434 after sentence contributions across
820 saved signings (67 aged 30+), grouped into 56,158 linked documents. Every
signing-period sentence count matches the saved membership table. Without
stopwords, the corresponding totals are 2,336,122 tokens, 42,469 types and 13,017
hapax types. The base stream supplies the primary corpus description.

The base top five are `the`, `and`, `to`, `a`, `in`; the no-stopword top five are
`season`, `£`, `m`, `city`, `united`. Currency symbols and fragments such as `m`
remain under the agreed non-punctuation surface-token policy. These frequencies
describe the selected text and are not sentiment labels or age comparisons.

The complete linear plot shows a steep head and a long low-frequency tail;
42,779 observed types include 13,022 singletons. The curves meet at rank 1 by
construction. Selected empirical/reference ratios are 1.145 at rank 2, 1.949 at
rank 5, 3.237 at rank 100, 3.741 at rank 1,000, 1.265 at rank 10,000 and 0.285 at
the final rank (42,779). Thus the empirical frequencies depart from the anchored
1/r reference, lying above it at these early/middle ranks and below it at the
final rank. These are descriptive point comparisons, not a fitted exponent or
goodness-of-fit test. Both curves and most deviations are strongly compressed
near the axes at the full linear vocabulary scale; a declining curve does not
establish Zipf's law.

## Verification and remaining limitation

All 17 synthetic tests passed with the existing `network_analysis` interpreter,
including the original 13 and four checks of explicit score-mode choice,
score-free exclusions/order, exact count mismatches, day boundaries and required
text/IDs. No package or environment was changed.

[Independent data verification](qa/actual_data_verification.json) reselected the
corpus from all 303,530 source rows, checked every saved signing-period count,
retokenized every selected sentence in original order, matched the complete
ordered token list, and checked both Counters, ranks, hapax totals, separate
denominators, top-five tables and every linked-document length. Each relative
frequency table sums to 1.0. The verifier records output hashes and descriptive
reference comparisons; [its source](qa/verify_actual_corpus.py) is retained.

[Actual plot verification](qa/actual_plot_verification.json) confirms embedded
ArialMT, vector PDF with no raster images, editable SVG text and a 2,148 by 1,920
PNG at approximately 600 dpi. The actual PDF was rendered in
[colour](qa/actual_pdf_preview.png) and [grayscale](qa/actual_pdf_preview_grayscale.png)
using existing PyMuPDF (Poppler unavailable), and both previews were inspected:
axes and legend are readable, with no clipping and no embedded caption/title.
The [plot verifier](qa/verify_actual_plot.py) is retained. Synthetic QA remains
separate in `qa/synthetic_fixture/` and is not corpus evidence.

The original sentence-level score file was unavailable, and the user explicitly
requested proceeding without that sanity check. Score-row identity/alignment and
finite-score validity remain unverified. Exact membership/count reconciliation
does not establish sentence-level identity with the scored corpus. This current
result supersedes the input-availability stage in the preserved dated setup and
readiness records. No scoring, article fetching, age tests, fitted Zipf model or
existing H1/H2/network analysis was run. Manuscript inclusion awaits review.
