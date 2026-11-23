# Research question

Agreed research question. Wording and scope confirmed by the user on 20 November 2026; the later approved H1 period and rerun requirements are recorded below and in issue 02.

## Final research question

> How does entry into the Premier League differ by player age, and how does the tone of Guardian coverage before and after Premier League signings differ by age?

The user selected phrasing 4 within option A's scope. Its parallel clauses distinguish the recruitment and coverage comparisons, while "before and after" makes the timing of coverage explicit. The age comparison is players aged 30 or older versus those under 30. The question encompasses both differences in tone levels and differences in tone changes, without asserting a causal effect.

## Agreed scope, 20 November 2026

The user selected option A: Premier League entry and Guardian coverage tone, retaining the comparison between players aged 30+ and under 30. H1 and H2 remain central and coverage volume supports interpretation. On 22 November 2026 the user selected the new unadjusted four-model H2 figure and explicitly agreed to omit H2b from the paper. Its narrower, model-dependent contribution does not justify the additional assumptions, explanation and page space here; the [decision and stronger rationale](paper_storyline.md#agreed-figure-2-and-h2b-omission-22-november-2026) record this scope choice. H2b remains exploratory repository work. The research question above is unchanged; earlier inclusion options below are decision history.

The user approved H1 and dependent transfer/network reruns for recorded seasons **2012/13–2024/25**, preserving other eligibility and methods, then verified and accepted the saved results on 21 November 2026. H2 uses its separate Guardian signing sample and date-derived season convention. [Confirmed restricted results](../reruns/h1_2012_13-2024_25/provenance/output_parity_report.md)

## Starting version

Copied from the existing [research question](../notes/question.md).

> Among player transfers that start at a real club outside the Premier League, are players aged 30 or older less likely than players under 30 to join a Premier League club? For those who do join, does the Guardian's tone change differently after the move?

## Existing analytical foundation

- H1 compares Premier League joining rates for transfers involving players aged 30+ and under 30.
- H2 compares the change in Guardian sentiment before and after entry between the age groups.
- Exploratory H2b asks whether older signings received less positive Guardian coverage than younger signings in the year after the move, accounting for prior coverage, market value, transfer season, article type and quotation marks. The before-signing comparison gives context. [Original H2b question](../notes/question.md#question)
- Coverage volume provides additional context for interpreting sentiment.

These descriptions record the existing work. Their agreed roles are recorded above.

**Issue 03 resolved, 21 November 2026.** The user confirmed satisfaction with the H1 interpretation and complete sensitivity passage. The accepted restricted H1 results show lower observed joining rates for 30+ transfers (12.14% versus 14.56%; gap −2.42 percentage points). The within-origin-club/season shuffled mean is −1.31 points and the one-sided p-value is 0.098. Agreed claim boundary: a lower descriptive rate with limited evidence against that conditional null; neither an established age effect nor equal entry rates. The fixed one-transfer-per-player sensitivity also has a negative gap but is conditional on one selection. Its approved motivation explains equal player representation. See the [agreed evidence and wording](evidence_and_sources.md#agreed-paper-wording-and-resolution). This does not change the agreed research question or Issue 02's approved sample description.

## Remaining evidence-dependent details

Follow-up, 21 November 2026: the user agreed to a brief answer to the entry-by-age clause in Results, retaining the numerical comparison and uncertainty, and developing explanations and broader implications in Discussion. Issues 03 and 04 are Resolved. The measurement review supports using sentiment scores to compare the tone of selected Guardian coverage around signings, with uncertainty about age-specific validity. Issue 05 is Resolved after the user approved the Guardian findings and wording. Results briefly answers the coverage-tone clause and notes greater coverage volume for older signings. Discussion develops the interpretation. The H2b model, figure and inclusion decision remain open in [Issue 15](scratch/2026-11-21_15-45-35_15-explain-h2b-model-and-figure.scratch). Issue 06 next reviews which network results support the question. [Guardian measurement evidence](evidence_and_sources.md#issue-04-guardian-tone-measurement-review-21-november-2026)

- Specify the population, observation period, and relationship between the two analysis samples.
- Decide which network findings directly support the question.
- Choose language that reflects the observational evidence and its uncertainty.

## Earlier proposals, 20 November 2026

The initial alternatives below are retained as decision history. The user selected A's scope and subsequently confirmed phrasing 4, recorded as the final research question above. These alternatives retain the comparison between players aged 30+ and under 30. Population and period details remain provisional until issue 02 reconciles the transfer and text samples.

### A. Entry and coverage tone (recommended)

> How is player age associated with entry into the Premier League and with the tone of Guardian coverage around Premier League signings?

This connects recruitment and media coverage through their association with age. The contribution would be to examine whether age differences appear in both outcomes, while distinguishing tone levels from changes around a signing. It does not test whether media coverage explains recruitment decisions or establish age discrimination.

H1 compares Premier League entry rates among eligible recorded transfers from real clubs outside the league. H2 compares changes in tone before and after selected Premier League signings. H2b extends the tone question to age differences in levels and remains explicitly exploratory, having emerged while testing H2. Coverage volume supports interpretation and the prior-coverage control rather than becoming a third central outcome.

### B. Entry and change in coverage tone

> Among recorded transfers from real clubs outside the Premier League, how do Premier League entry rates differ between players aged 30+ and under 30, and how does the change in Guardian tone around selected Premier League signings differ between these age groups?

This stays closest to the original question and keeps H1 and H2 central. H2b is a supporting exploratory finding outside the main question; coverage volume provides context. It offers the narrowest scope for six pages, but the distinction between tone changes and tone levels needs a separate explanation.

### C. Entry, coverage tone, and coverage volume

> How is player age associated with entry into the Premier League and with the tone and volume of Guardian coverage around Premier League signings?

This gives coverage volume a central role alongside entry and tone. It distinguishes how much coverage signings receive from how positive that coverage is. It also requires space for a third outcome within the six-page limit; H2b still remains exploratory.

### Evidence and scope boundaries

- H1 measures recorded transfers. The restricted summary reports a lower observed entry rate for 30+ transfers and a one-sided permutation p-value of 0.098. [Restricted H1 summary](../reruns/h1_2012_13-2024_25/output/age_shuffle_outsideprem_toprem_summary.md)
- The [main H2 table](../data/dataset_nlp/results/a1_age30_results.csv) reports a RoBERTa difference in tone changes of +0.006, with p = 0.7558. This does not establish equal changes across ages.
- The [H2b table](../data/dataset_nlp/results/a1_h2b_controls.csv), RoBERTa specification `7 all: no quotes, type adjusted, fame + value`, reports an after-signing tone-level gap of -0.0349, with p = 0.0390. Several specifications were examined; this finding does not establish that the signing caused a gap to emerge.
- These are checks of saved outputs for wording, not completed evidence audits. Issues 03-05 cover those reviews. The [original question history](../notes/question.md) records H2b's exploratory origin.
- The transfer and text analyses have different selection rules and periods. Do not describe them as following one verified cohort through recruitment and reception before issue 02 checks their relationship. Use "selected Premier League signings" for the text sample until its eligibility is reconciled.
- Guardian tone measures writing about players, including quoted speech where retained. It does not measure fan opinion or directly measure journalists' beliefs.
- Issue 06 will decide which structural network findings advance the agreed question and satisfy the network-science requirement. Issue 07 will establish the literature context; no novelty claim is agreed here.

### Follow-up after agreement

Issue 01 is resolved. Next, issue 02 will compare the two samples' eligibility rules, periods, units, and available matching identifiers. Retain H2b's exploratory status and coverage volume's supporting role when developing the paper. Any evidence-driven need to revise the agreed question should be discussed explicitly.

## Revision record

| Version | Status | Basis |
| --- | --- | --- |
| Starting version | Retained for discussion | Existing question reproduced above |
| A, B, and C, 20 November 2026 | Proposed; awaiting discussion | Compare tone broadly, tone change only, and tone plus volume; retain exploratory history and sample qualifications |
| A, 20 November 2026 | Scope selected; exact wording pending | User chose A and requested equivalent alternative sentence structures |
| A, phrasing 4, 20 November 2026 | Final wording and scope agreed | User selected the parallel two-clause question with explicit before-and-after coverage timing; issue 01 resolved |

Record any subsequent agreed revision and its reason here.
