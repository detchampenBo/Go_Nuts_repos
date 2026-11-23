# Paper storyline

Agreed section argument and provisional page budget for a fresh paper developed through discussion. Figure 2 is selected and H2b is omitted; final captions and manuscript fit remain under review.

## Agreed Figure 2 and H2b omission, 22 November 2026

The user explicitly agreed to use the [new unadjusted four-instrument H2 monthly figure](../output/h2_monthly_period_means_findings/combined.pdf) in the paper and omit H2b. This is Figure 2, with proposed stable label `fig:h2-monthly-tone`. Retain its four sentiment instruments, age-coloured before/after period-mean markers, numeric-only labels and uniform darker grid. The [source definitions and caption](../output/h2_monthly_period_means_findings/README.md) and [verified production](scratch/2026-11-22_18-56-56_09b-produce-unadjusted-h2-monthly-means.scratch) record the artifact. This decision supersedes earlier conditional H2b and figure-choice wording below.

**Reason for omitting H2b.** Its additional contribution does not justify the assumptions, explanation and page space it requires in this six-page report. H2b asks a narrower, exploratory question about adjusted tone levels at comparable recorded market value, prior coverage and season. It combines covariate adjustment with changes to sentence processing and the analysed sample, making the figure and its interpretation harder to explain. Its statistical evidence is model-dependent: on the same 820 signings, adding market value to season and prior coverage changes the post-signing RoBERTa permutation p-value from 0.1048 to 0.0482. Market value can itself be associated with age, and overlap of the relevant inputs remains unverified. These qualifications do not earn enough additional insight for the paper's central before/after comparison. [Reviewed evidence](evidence_and_sources.md#exploratory-h2b-before--and-after-signing-tone-levels)

The decision does not declare regression on sentiment intrinsically invalid or exclude it simply because it was not taught. The [Week 8 guidance](<../../data/week8/Week 8 · Putting it all together · 02805.html#faq>) permits additional methods while asking the project to centre on the course's network science and NLP. The selected H2 figure, four-instrument human validation and signing-level permutation comparison form the clearer course-based argument. Regression adjustment does not itself validate the sentiment measurement. The omission is a scope and explanatory-value decision; preserve H2b code, saved findings, figures and the reviewed sensitivity evidence in the repository as exploratory history.

Omit H2b findings, adjusted plots, regression procedures and its 793-signing sample from the paper's Results, Methods, Discussion, Abstract and sample description. The user's explicit omission authorises removing only the H2b sentence from the previously approved three-paragraph sample wording; all other sample wording and the complete H1 sensitivity passage remain unchanged. The [evidence inventory](evidence_and_sources.md#current-sample-description-for-review-21-november-2026) records that narrow revision and preserves the removed sentence as history. H2 remains inconclusive about age differences in changes (+0.0060 RoBERTa score units, p = 0.7558), with limited sensitivity to smaller differences; unadjusted age gaps are descriptive.

There is no H2b third figure or explanatory-text allocation. The former 0.45-page reserve becomes unallocated fit margin, available for an explicitly agreed reallocation after checking Figure 2 and its caption. No replacement analysis is selected. Issue 11.1's H2b inclusion decision is settled; its remaining question about a possible course-grounded text subanalysis is still open and does not authorise new work. Issue 09 remains open for final captions, Figure 1 presentation and manuscript fit.

## Academic framing

The starting point connects player age with Premier League entry and Guardian coverage around entry. We need to establish the scholarly motivation, the contribution of combining these observations, and the limits of the interpretation.

Use the supplied PNAS template and its writing and citation guidance, together with the course-specific requirements recorded in [project_requirements.md](project_requirements.md). The user confirmed PNAS as the intended guideline.

## Section planning

Use Monsees in the Introduction to motivate the cultural, linguistic and editorial scope of the Guardian analysis, as requested on 22 November 2026. Carry that scope into the Discussion when considering generalisability. The [source evidence and proposed passage](evidence_and_sources.md#issue-07-literature-framing-22-november-2026) record the argument and distinguish its role from the project's sentiment validation.

| Required section | Question to resolve together |
| --- | --- |
| Introduction | Why does this question matter, what does relevant literature establish, and what does our study add? |
| Results | Which findings answer each part of the question, and in what order does the evidence build the argument? |
| Discussion | What interpretation does the combined evidence support, what alternatives remain, and how far can the conclusions extend? |
| Methods | Which data definitions, analysis choices, and checks are necessary to understand and reproduce the results? |
| Abstract | Once the argument is agreed, how can the question, evidence, principal result, and interpretation fit into 150 words? |
| Significance Statement | Why should a reader outside football research care about the contribution? |
| References and author contributions | Which sources support the argument and methods, and who performed each part of the work? |

## Decisions before drafting

- Agree on the central claim that the available evidence can support.
- Establish the relationship between the transfer sample and the selected signings in the text analysis.
- Decide the roles of H1, H2, H2b, coverage volume, and sentiment validation.
- Evaluate whether degree distributions, communities, feeder routes, ownership, or backbones advance that argument.
- Select two or three figures, each tied to a question, comparison, and validation check.
- Allocate the six-page budget across text, figures, and references.

## Agreed storyline

**Agreed, 22 November 2026.** The user accepted the storyline and page distribution, resolving Issue 08, and subsequently selected the backbone–H1 pairing for Figure 1 and the unadjusted four-model monthly H2 plot for Figure 2. H2b is omitted for the reasons recorded above. The former Issue 15 remains scheduled as Issue 11.1, retaining its filename; only the disposition of the previously suggested further text subanalysis remains open there. No replacement analysis is selected. Final captions and manuscript fit remain under review; no manuscript section is drafted by this documentation update.

### Central descriptive claim

Transfers involving players aged 30+ had a lower observed Premier League joining rate than transfers involving younger players, with limited evidence against the origin-club/season null. In a separate sample of selected Premier League signings, Guardian tone changes showed no clear age difference, while older signings received more coverage. Together, these findings describe age patterns in entry and coverage; they do not establish that coverage explains recruitment or that either comparison measures a causal age effect.

### Agreed Results sequence and evidence

1. **Transfer network context.** Define clubs as nodes and directed routes weighted by transfer counts, using the 16,636 eligible events. Briefly introduce the 1,157-club, 11,016-route graph. Retain the agreed exploratory Leiden comparison: both methods found five broadly similar communities, with modularity 0.448 for Leiden and 0.446 for Louvain. Attribute faster runtime to Traag et al.'s evaluation. The saved backbone at α = 0.20, coloured by Louvain, remains a candidate context panel in Issue 09. Transition from the pooled graph to the direct age-entry comparison; community structure itself does not answer the age question.
2. **Entry by age, H1.** Report 12.14% versus 14.56%, gap −2.42 percentage points, mean shuffled gap −1.31 and one-sided p = 0.098. Use the selected all-eligible-transfers permutation panel. Preserve the complete approved one-transfer-per-player passage, including its motivation, 4,602-player result and fixed-selection limitation. This gives the short answer to the first clause of the question. Explicitly introduce the separate Guardian population before changing outcomes.
3. **Measuring Guardian tone.** Begin with signing-anchored before/after windows and the 43,924 collected articles, then explain sentence matching, scoring and signing-period averages. Retain the four-instrument validation table, 196 evaluable labels and the uncertainty from only 14 older-player cases. Establish what the score measures before interpreting an age comparison.
4. **Tone change by age, H2.** Use 820 sufficiently covered signings. Report the older-minus-younger difference in changes of +0.0060 score units, p = 0.7558, with limited sensitivity to smaller differences. Omit the historical unverified between-age interval. This answers the main before/after tone comparison without asserting equal changes.
5. **Coverage volume as context.** End with the all-1,332-signing comparison, including zero coverage. Older signings had higher median article counts before (27.5 versus 12) and after (47.5 versus 35). This distinguishes attention from the tone of sufficiently covered signings and leads into selection and measurement limits in Discussion. H2b has no Results passage or figure in this paper.

The feeder analysis and primary seven-transfer figure stay in the repository. Its optional one- or two-sentence result has no protected space in this budget. If used, retain the within-season route-null and unadjusted-screen qualifications. Ownership, separate degree figures and standalone community comparisons have no additional figure slots proposed here.

### Section purposes and literature placement

- **Introduction:** motivate age differences in recruitment with the approved CIES passage; introduce our comparison independently. Use Dot Grau–Canter for the multiple-newspaper sentiment precedent and Monsees for contextual scope. End with the agreed question, separate-sample design and descriptive contribution. CIES's 10.6% recruit share and H1's 12.14% older-transfer joining rate have different denominators.
- **Results:** follow the sequence above, explaining each comparison before its principal numbers. Give concise answers to both clauses of the question, with uncertainty attached to the findings. Retain network science and sentiment validation even if the candidate backbone panel is omitted.
- **Discussion:** interpret the lower observed entry rate, uncertain age difference in tone change and greater attention together. Discuss separate populations, observational selection, repeated players/shared articles, imperfect target-specific sentiment, limited age-specific validation and limited sensitivity. Carry Monsees's contextual limits into generalisation. Omit H2b's adjusted-level interpretation. Do not infer recruitment motives, discrimination, equal outcomes or a media-to-recruitment mechanism.
- **Methods:** use the approved three-paragraph sample description with only its H2b sentence removed by the user's omission decision. Give the consequential eligibility, season and age definitions; graph construction and selected network procedures; text windows, exclusions, model/checkpoint, sentence and signing aggregation; human validation; H1's origin-club-by-season and H2's season-only shuffles; draw counts, seeds, tails and plus-one calculation; fixed-player selection and available/missing inputs. Use the selected sentiment/network references, Hemerik–Goeman with Phipson–Smyth and Winkler et al., and the agreed exchangeability limitation. Describe the monthly curves and separate signing-period mean markers. Omit H2b-specific regression, processing and citations.
- **Abstract and Significance:** allocate 150 words and two or three sentences, respectively. Write them after the argument is agreed and the body is drafted. Include the separate populations and uncertainty in the overall framing.

### Provisional six-page allocation

Page fractions refer to total printed page area, not fixed page breaks. Visual allocations include captions; the validation table allocation includes its explanatory note. Text allocations include section headings. Counts are planning estimates to be checked in the supplied compiled template, with author details and reference wrapping included.

| Component | Text/front matter/references | Figure/table area | Total pages |
| --- | ---: | ---: | ---: |
| Title, authors, 150-word Abstract and 2–3-sentence Significance | 0.55 | 0 | 0.55 |
| Introduction | 0.50 | 0 | 0.50 |
| Core Results prose, including full H1 sensitivity and validation explanation | 1.00 | 0 | 1.00 |
| Discussion | 0.65 | 0 | 0.65 |
| Core Methods, including exact approved sample description | 1.00 | 0 | 1.00 |
| Specific author contributions | 0.05 | 0 | 0.05 |
| References | 0.75 | 0 | 0.75 |
| Figure 1: agreed backbone–H1 pairing; final presentation subject to Issue 09 | 0 | 0.50 | 0.50 |
| Figure 2: selected four-model unadjusted monthly H2 curves with period means; fit subject to Issue 09 | 0 | 0.35 | 0.35 |
| Four-instrument validation table | 0 | 0.20 | 0.20 |
| **Allocated core** | **4.50** | **1.05** | **5.55** |

H2b is omitted, leaving 0.45 pages of unallocated fit margin within the six-page maximum. Figure 2's current full-width export is five inches tall before its caption, so the 0.35-page placeholder is not a demonstrated fit. Check physical size and captions and explicitly reallocate from the margin if needed; do not silently compress the approved sample/H1 passages or add a replacement analysis. Figure 1's paired export and final layout remain pending. A separate course supplement is not assumed to be permitted.

### Dependencies and next discussion

- **Issue 08:** Resolved following the user's agreement with the storyline and page distribution on 22 November 2026.
- **Issue 09:** both core figures selected; next, review captions, stable labels, Figure 1 paired presentation and physical fit of Figure 2. H2b is omitted.
- **Issue 10:** develop reproducible Methods within the allocation, including the distinct shuffles and exchangeability limitation.
- **Issue 11:** develop the Discussion and enforce the agreed claim boundaries.
- **Issue 11.1 (formerly 15):** H2b omission and removal of its sample-description sentence are settled. Only the disposition of the previously suggested course-grounded text subanalysis remains open; none is selected or authorised. If pursued, agree its question, actual course foundation, inputs, validation and space cost, then complete and incorporate any selected follow-up before drafting.

The agreed sequence remains **09 → 10 → 11 → 11.1 → 12**. H2b is no longer conditional: it is omitted. Before drafting, settle the remaining possible-subanalysis disposition in Issue 11.1 and incorporate any explicitly agreed follow-up. The 0.45-page fit margin is not automatically assigned to another analysis.

No new evidence gap requires a new scratch issue at this stage. The older repository-context handoff and some earlier planning entries still point to Issues 04–07; the current README and dated resolutions establish that Issues 01–07 are Resolved.

## Agreed H1 evidence and presentation, 21 November 2026

The user confirmed satisfaction with Issue 03 and authorised resolution. Its [agreed evidence and wording](evidence_and_sources.md#agreed-paper-wording-and-resolution) report a lower observed PL joining rate for 30+ transfers (12.14% versus 14.56%; gap −2.42 percentage points), with limited evidence against the within-origin-club/season null (mean shuffled gap −1.31 points; one-sided p = 0.098). The fixed one-transfer-per-player sensitivity retains a negative gap (−1.94 points; p = 0.074) but conditions on one selected subset and changes the weighting. Issue 03 is Resolved.

The storyline should preserve uncertainty about H1 rather than choose either binary Discussion alternative in the earlier draft. A nonsignificant result does not establish equal entry rates or that club-season composition fully explains the observed gap. No causal or discrimination claim follows. The earlier proposed restriction to clubs with prior PL sales has no supporting result in the reviewed H1 evidence and cannot be described as completed robustness. No new analysis is proposed as necessary for this qualified claim. The full storyline and figure decisions remain pending.

The user approved the reader-facing motivation for the sensitivity: players can contribute multiple career transfers, so frequent movers receive greater weight in the main comparison; selecting one eligible event uniformly per player gives each player equal representation. Introduce that reason before the sensitivity result so a new reader understands the design choice. The evidence inventory preserves the approved complete passage combining that explanation, the result and fixed-selection limitation.

The user confirmed H1 as the main entry finding and wants its supporting plot in Results. Use the [restricted all-eligible-transfers permutation plot](../reruns/h1_2012_13-2024_25/output/age_shuffle_outsideprem_toprem_findings/age_shuffle_outsideprem_toprem_all_eligible_transfers.pdf) as the primary panel. Cite it where Results gives the two rates and the observed gap. The caption should explain the 999 age-label shuffles within origin club and season, show how to read the observed gap (−2.42 percentage points) against the shuffled mean (−1.31 points), and report the empirical one-sided p = 0.098. Explain that the fitted curve is illustrative and that ±0.83 is one standard deviation of the shuffled gaps. Issue 09 will settle the layout, including any pairing with the candidate backbone panel. The complete sensitivity passage remains part of Results.

## Agreed Figure 1 pairing, 22 November 2026

The user selected the backbone–H1 pairing because it first visualises the transfer data and then uses the permutation comparison to address the entry-by-age research question. Both originate from the same 16,636 eligible transfers in recorded seasons 2012/13–2024/25. H1 uses every eligible event; the full network aggregates them into 11,016 directed routes. The displayed backbone at α = 0.20 retains 1,396 routes carrying 5,271 transfers (31.7%), so the displayed backbone is a filtered view of the H1 sample. The 2,396 Premier League arrivals are H1's outcome subset, rather than its entire denominator.

Use Figure 1(a) for the whole-network backbone at α = 0.20 and Figure 1(b) for the selected all-eligible-transfers permutation plot. The backbone pools ages and destinations; its colours/shapes identify Louvain communities. H1 compares the older-minus-younger joining-rate gap with 999 age-label shuffles within origin club and recorded season. Explain how the observed −2.42-point gap relates to the mean shuffled gap of −1.31 points and empirical one-sided p = 0.098. The answer remains a lower observed older-group rate with limited evidence against this conditional null.

The combined [Figure 1 PDF](../output/backbone_h1_findings/combined.pdf) is now produced for review, with [source definitions, caption and formats](../output/backbone_h1_findings/README.md) and [verification](../output/backbone_h1_findings/verification.json). The full-width export is 17.8 cm by 4 inches; it uses the saved alpha = 0.20 backbone geometry and exact original H1 drawing helper on the saved 999 gaps. No analytical producer, community detection, layout or permutation was rerun. Original figures remain preserved. Production is tracked in [Issue 09c](scratch/2026-11-22_20-12-45_09c-produce-backbone-h1-figure.scratch), which remains Open for user satisfaction.

At the user's request, the current export places panel (a)'s community legend in its upper-right corner, shifts the network slightly left/down and enlarges it to reduce unused bottom space. Its drawing area increased by a further 18.5% in linear scale over the preceding enlargement, preserving frozen positions/frame and all data. The final marker instruction is 1.5 times network-marker width/height (2.25 times the original displayed area), preserving relative activity sizes; keep legend symbols at their standard 5.09 pt size and standard spacing. This supersedes the initial factor-two request. Panel (a)'s title is `Backbone disparity filter (α = 0.20)`; the H1 panel retains its geometry. Proposed labels remain `fig:entry-age`, `fig:transfer-backbone` and `fig:h1-permutation`. Cite panel (a) in the network-context passage and panel (b) alongside the H1 rates and permutation result. Keep the fixed-player sensitivity in prose. The pairing is agreed and the artifact is produced; final caption, labels and manuscript placement still need review. Retain the provisional 0.50-page allocation including caption until physical fit is checked; any reallocation must be explicit.

## Guardian figure preference and comparison, 22 November 2026

The user prefers the existing monthly tone presentation because its temporal trajectory connects with the theory taught in the course. They also authorised a separate before/after period-comparison candidate to inspect alongside it. This records a preference and an authorised comparison, not final Figure 2 selection. The existing monthly PDF displays adjusted H2b tone. The additional candidate displays the core H2 RoBERTa period means and a separate coverage-median panel, using only saved results; H2b inclusion remains with Issue 11.1.

The saved Week 7 sentiment section illustrates temporal sentiment arcs and smoothing, supporting the preference for a trajectory view. Its narrative example does not establish the validity of the H2b adjustment. Keep monthly descriptive curves distinct from H2's signing-level comparison of period changes. Production and verification are tracked in [Issue 09a](scratch/2026-11-22_18-45-20_09a-produce-guardian-period-comparison.scratch). Existing figures are preserved. Review both presentations before choosing the paper figure and reconciling its caption and space allocation.

The authorised alternative is now available as a [combined comparison](../output/guardian_period_comparison_findings/combined.pdf) and [standalone tone plot](../output/guardian_period_comparison_findings/mean_roberta_tone.pdf), with [coverage alone](../output/guardian_period_comparison_findings/median_article_counts.pdf) and PNG/SVG companions. The [output README](../output/guardian_period_comparison_findings/README.md) records exact result selectors, denominators, caption and verification. This is a produced presentation candidate, not a final figure selection or new statistical analysis. The monthly preference and Issue 11.1 dependency remain unchanged; manuscript fit is still pending.

### Requested unadjusted monthly presentation

Later on 22 November 2026 the user requested the core H2 four-model monthly curves and explicitly declined regression-based plots. Add red dots with short horizontal segments to show each age group's before/after period means, labelled by age group. This preserves the multiple-instrument measurement argument and the temporal presentation. Use the saved unadjusted curves, with no quote removal, article-type centring or regression adjustment. Each red marker is a descriptive signing-period mean; the horizontal segment is a fixed visual marker, not an uncertainty interval or a duration. Monthly membership varies, so period means must come from signing-period summaries rather than averaging the smoothed curve.

[Issue 09b](scratch/2026-11-22_18-56-56_09b-produce-unadjusted-h2-monthly-means.scratch) tracks authorised fresh-context production and verification. The four-model unadjusted export has an identified producer in the plotting kit; RoBERTa/VADER also match the separate original monthly table, while Bing lacks a separate matching monthly original and raw reconstruction remains unavailable. This supersedes the earlier open choice of adjusted versus unadjusted plots for this requested figure. H2b's remaining prose/inclusion treatment stays with Issue 11.1; do not infer it has been omitted from the paper merely because regression plots were declined. Final figure satisfaction, captions, labels and manuscript fit still require review.

During production, the user confirmed that each model needs before/after means separately for 30+ and under 30, and invited colours suited to the plot. Use orange mean dots/segments for older signings and dark brown for younger signings, matching the curves. This supersedes the initial red suggestion. Keep four explicitly labelled means per model panel, with marker outlines/size distinguishing summaries from monthly trajectories.

The [requested unadjusted monthly figure](../output/h2_monthly_period_means_findings/combined.pdf) is now produced for review, with [source definitions, caption and formats](../output/h2_monthly_period_means_findings/README.md) and [verification](../output/h2_monthly_period_means_findings/verification.json). It contains four models and four age-specific period means per panel; fixed short segments are descriptive markers, not intervals. The centres at -6 and +6 place whole-period summaries on their corresponding halves, not at monthly estimates. Combined width is 17.8 cm and height 5 inches before caption, so final fit within the provisional 0.35-page Figure 2 allocation is not established; agree any required reallocation explicitly. Production preserves the earlier figures and does not rerun analysis. Await user review before recording final satisfaction with Figure 2.

The user subsequently said they like this plot and requested simpler annotations: show only the mean number centred below each 30+ symbol and above each under-30 symbol. Remove repeated age prefixes from those labels while preserving the age colours, legend, curves and mean values. This supersedes the earlier requirement to repeat age labels beside each mean. They then requested a finer background grid and subsequently a uniform darker treatment: major and minor gridlines now both use `#999999` at 0.5 pt, with minor spacing of three months and 0.05 score units behind the data. Production remains tracked in Issue 09b; final caption and manuscript fit still need review.

## Guardian tone measurement, 21 November 2026

Open with change over time. Each signing provides the date around which coverage can be scored consistently before and after the move. Introduce the Guardian Open Platform API and the 43,924 collected articles, then explain how name matching links sentences to players and how the scores give each qualifying signing one before-and-after comparison. The scores describe selected Guardian language, including passing mentions and published quotes. Explain why several scoring methods were compared and how the human review checked both player identity and tone in a sample. The user supports retaining the scores as a useful but imperfect measure of the selected coverage. State the uncertainty about age-specific comparability. The evidence inventory records the focus-rule check. [Evidence and proposed wording](evidence_and_sources.md#issue-04-guardian-tone-measurement-review-21-november-2026)

Use the earlier draft's “Measuring tone in football writing” prose and four-instrument validation table in Results. The table reports rank agreement, correct sign on positive or negative cases, and three-class accuracy. The draft's “Sentiment instruments and validation” subsection supplies the technical Methods wording. Results can briefly answer the coverage-tone clause using the Issue 05 comparisons. Discussion develops how coverage selection, voice and ambiguity limit broader interpretation. Issue 04 is Resolved. [Earlier draft](../paper/main.tex#L57) · [Adapted prose and table](evidence_and_sources.md#reproducibility-and-proposed-paper-wording) · [Resolution](scratch/2026-11-19_15-30-34_04-review-sentiment-measurement-validation.scratch#resolution-21-november-2026)

## Proposed Guardian results and discussion, 21 November 2026

In Results, start with the signing date and explain how averaging the selected Guardian sentences gives each signing a before score and an after score. Show that H2 compares how far those scores moved for the two groups. Give H2b a short passage that starts with the lower raw tone scores for older signings, explains why the exploratory comparison accounts for differences in players and coverage, and shows how the regression estimates the post-signing gap. Use the before-signing estimate to give that gap context. End with a short count-based comparison of how much attention each group received, including the signings with zero articles. Explain each comparison before giving its main numbers. [Issue 05 proposed wording](evidence_and_sources.md#proposed-paper-wording-and-placement)

In Discussion, develop the coexistence of greater attention and a lower adjusted post-signing tone estimate, what the market-value comparison adds, the limits of comparing signings with similar measured characteristics, and the limited ability to detect smaller differences in change. Tie the interpretation back to the selected Guardian coverage and the small older-player validation sample. Use Methods or the evidence inventory for shuffle procedures, range construction and the definition of modelled coverage ratios. The user approved the placement and wording in Issue 05. Use the H2 estimate and p-value with a clear statement of uncertainty, and omit the historical interval with unverified construction. H2b remains exploratory if retained. [Issue 15](scratch/2026-11-21_15-45-35_15-explain-h2b-model-and-figure.scratch) records the model walkthrough and the candidate H2b figure. [Issue 05](scratch/2026-11-19_15-30-34_05-verify-text-results-and-exploratory-status.scratch)

## Transfer network context, 21 November 2026

The user agreed to carry one whole-network backbone snapshot at α = 0.20 into Issue 09 as a candidate panel to help readers understand the transfer data alongside H1. The snapshot pools ages, includes eligible routes to Premier League and other destinations, and uses colours and shapes for Louvain communities. It shows 383 clubs and routes carrying 31.7% of the recorded transfer volume. If selected, explain the cutoff and coverage in the caption and give the age-entry comparison its own clear presentation. Issue 09 will decide whether the panel earns its space alongside the H1 and Guardian figures. [Issue 06 discussion](scratch/2026-11-19_15-30-34_06-choose-network-analysis-role.scratch#progress-and-resolution) · [Restricted backbone summary](../reruns/h1_2012_13-2024_25/output/louvain_transfer_backbone_findings/backbone_summary.md)

H1 provides the direct answer to the entry-by-age clause. Briefly describe the transfer graph and use median degree if it helps readers understand the uneven connectivity of clubs. The user confirmed satisfaction with keeping the feeder analysis and primary seven-transfer figure in the repository. If space permits, Results can give one or two sentences on where arrivals went across both age groups. The route screen identified 217 recurring pairs carrying 626 of the 2,396 Premier League arrivals. Each selected pair had at least two recorded moves and passed a per-route, unadjusted p < 0.05 threshold among 11,448 tested pairs. Girona → Manchester City illustrates the result with 15 recorded moves versus 1.8 expected from the seasonal sending and receiving totals. Explain the seasonal shuffle and the unadjusted screen briefly if the result is used. The feeder figure, ownership comparison, and standalone community and backbone cutoff comparisons remain in the repository. [Feeder results](../reruns/h1_2012_13-2024_25/output/premier_league_feeder_summary.md) · [Issue 06 resolution](scratch/2026-11-19_15-30-34_06-choose-network-analysis-role.scratch#resolution-21-november-2026)

## Revision record

22 November 2026 — The user confirmed Issue 07 and requested the Issue 08 continuation prompt. Literature roles and the selected wording in the evidence inventory are now the agreed basis for the section argument and six-page budget. [Issue 07 resolution](scratch/2026-11-19_15-30-34_07-research-literature-and-verify-citations.scratch#resolution-22-november-2026) · [Start Issue 08](scratch/2026-11-19_15-30-34_08-agree-storyline-and-page-budget.scratch#continuation-prompt)

22 November 2026 — The user confirmed the [exploratory Leiden passage](evidence_and_sources.md#network-references-and-exploratory-leiden-comparison), including attribution of the faster-runtime result to the original paper and the saved five-community comparison for this project.

22 November 2026 — The user requested a brief mention of Leiden as an exploratory community analysis. Use the [verified passage and source comparison](evidence_and_sources.md#network-references-and-exploratory-leiden-comparison) when allocating space in the storyline. Both methods found five communities with substantial overlap and comparable modularity. Attribute faster runtime to Traag et al.'s original evaluation. The saved project comparison cannot establish a runtime ranking because the instrumentation differs. The candidate backbone uses its saved Louvain partition, with the full community comparison retained in the repository.

21 November 2026 resolution: Issue 06 is Resolved after the user confirmed satisfaction with the network scope. Keep the feeder figure in the repository and consider a short Results mention. Carry one backbone snapshot into Issue 09 as a candidate context panel alongside H1. Next, agree the literature and method-citation scope in Issue 07.

21 November 2026 resolution: Issue 05 is Resolved after the user approved the H2, exploratory H2b and coverage interpretation and wording. Issue 15 remains open for the H2b model explanation, figure and inclusion decision. Issue 06 next reviews the verified network findings for the paper.

21 November 2026 resolution: Issue 04 established RoBERTa as a useful but imperfect measure of how positive or negative selected Guardian coverage reads. The measurement and validation wording and four-instrument table are ready as a basis for drafting. Review H2, exploratory H2b and coverage volume in Issue 05 before interpreting the Guardian findings.

21 November 2026 resolution: the user confirmed satisfaction with the main H1 interpretation, complete sensitivity passage and Results/Discussion framing. Results is oriented to the entry-by-age clause, reporting the comparison and uncertainty; Discussion develops explanations and broader implications. The final synthesis with Guardian findings awaits their evidence reviews. Issue 03 is Resolved. The full storyline and figure decisions remain pending; next is Issue 04's measurement and validation review.

Foundation created. The section argument, result order, and figure selection await our first storyline review.
