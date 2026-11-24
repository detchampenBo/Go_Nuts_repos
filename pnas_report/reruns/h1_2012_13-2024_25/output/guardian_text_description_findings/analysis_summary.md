# Guardian corpus: rank frequencies, Zipf reference and notable words

## Corpus and plot

The selected corpus contains **99,976 linked sentence records** from **820 Premier
League signings**. Liveblogs and match reports are excluded. The base stream has
**3,870,272 tokens**, **42,779 distinct token forms** and **13,022 forms occurring
once**. Tokens are lowercase surface forms with punctuation and whitespace
removed; names, numbers, currency symbols and inflections remain. Shared text and
repeated article/signing contributions are preserved.

The [rank-frequency plot](rank_frequency_loglog.pdf) shows **raw token frequency**
against **frequency rank**, with both axes logarithmic. Rank 1 is the most frequent
token. The upper-right legend identifies the observed counts and the dashed
reference, **“ideal Zipf, s = 1”**. The figure follows the project's Arial,
brown-palette and publication-size plotting conventions.

## Does the plot follow Zipf's law?

For the displayed exponent `s = 1`, the reference count at rank `r` is:

```text
reference_count(r) = count(rank 1) / r = 150,246 / r
```

This reference is anchored to the count of **the**, the most frequent token. Its
height is not fitted to the other ranks, and its total is not constrained to equal
the observed token total. Changing from relative frequency to raw counts scales
both curves by the same corpus total, so their shape and relative departures do
not change.

The distribution has a broadly Zipf-like pattern: a few forms are very frequent
and many are rare. However, **it does not closely follow the displayed, rank-1-
anchored `s = 1` curve across the full vocabulary**. The observed curve sits above
the reference through much of the head and middle, bends downward, and falls
below it in the rare tail. Selected ranks illustrate the departures:

| Rank | Observed count | Reference count | Observed/reference |
| ---: | ---: | ---: | ---: |
| 1 | 150,246 | 150,246.00 | 1.00 |
| 10 | 29,321 | 15,024.60 | 1.95 |
| 100 | 4,863 | 1,502.46 | 3.24 |
| 1,000 | 562 | 150.25 | 3.74 |
| 10,000 | 19 | 15.02 | 1.26 |
| 42,779 | 1 | 3.51 | 0.28 |

The tail forms steps because token counts are integers and many forms have tied
counts. The **13,022 singleton types are 30.4% of the observed vocabulary**. Their
horizontal plateau is a feature of the finite observed counts, rather than a
smooth continuation of the ideal line.

The supported conclusion is therefore **a broad rank-frequency concentration with
clear departures from this particular ideal Zipf reference**. The plot alone
neither establishes nor formally rejects the broader family of Zipf models. No
exponent, vocabulary cutoff or normalisation constant was fitted, and no
goodness-of-fit test was performed.

## Words and tokens of interest

The [top-ten comparison](top_ten_words.md) reports exact counts and relative
frequencies for the base and stopword-filtered streams. Each stream uses its own
denominator: **3,870,272** and **2,336,122**, respectively. Removing stopwords makes
the football-specific vocabulary easier to see, while leaving the original
surface-token rules intact.

| Tokens | Counts | Why they are of interest |
| --- | --- | --- |
| **the, and, to, a, in** | 150,246; 86,037; 85,471; 74,360; 58,569 | These are the five most frequent base-stream tokens. They chiefly describe grammatical usage, with little football-specific meaning on their own. |
| **season** | 17,521 | The most frequent retained token after stopword removal; it points to the seasonal framing of football coverage. |
| **city, united, chelsea, manchester** | 11,627; 11,265; 10,557; 10,280 | Club names and name components are prominent. These unigrams do not uniquely identify a club: for example, “city” and “united” can appear in several names. |
| **£, m** | 15,740; 14,903 | These are useful when reading financial and transfer-related language. Currency symbols and shorthand fragments remain under the token rules; the table is not restricted to alphabetic words. Their separate counts do not establish how often a particular fee expression occurs. |
| **form, injured** | 10,093; 9,960 | These highlight performance and availability vocabulary. Their frequency alone does not show negative sentiment toward the player or an age difference. |
| **unknown** | 10,439 | An unusually prominent token worth checking in context. It occurs in 1,186 selected sentence records. Inspected examples contain list-style injury/availability information with unknown return timings; this shows how article format can contribute repeated vocabulary. It should not automatically be interpreted as uncertainty in the journalist's attitude toward a player. |

These observations describe the pooled corpus. Longer linked documents and
repeated/shared prose contribute more tokens, so frequent words can reflect
article format, club mentions and topic selection. The counts do not identify the
sentiment target or establish age bias. The original sentence-score alignment
check was omitted at the user's request; direct text selection matches every
saved signing-period sentence count, but this alone does not prove identity with
the unavailable scored rows.

## Sources and reproducibility

The [saved frequency tables and corpus provenance](corpus_summary.json),
[presentation verification](qa/loglog_presentation_verification.json) and
[context-check aggregates](qa/word_context_check.json) support this summary.
The analytical corpus, tokenisation and original linear plots are unchanged.
The revised log–log presentation is reproduced from the repository root with:

```powershell
& 'C:/Users/victo/Anaconda3/python.exe' -B 'pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_guardian_h2_loglog.py'
```

The user approved a brief prose addition in the manuscript's Results, Methods
and Discussion on 24 November 2026, resolving Issue9.1. This fuller summary,
plots and top-ten table remain repository artifacts; no new manuscript display
was selected. Final manuscript fit remains for Issues13–14.
