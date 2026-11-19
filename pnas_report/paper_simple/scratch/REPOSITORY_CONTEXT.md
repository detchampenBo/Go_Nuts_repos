# Repository context for paper issues

Snapshot reviewed on 19 November 2026. Check the linked files and Git state when resuming work because this document records the state at that date.

## Purpose and collaboration

The group is developing a fresh paper in `pnas_report/paper_simple`, starting from the existing research question and completed analyses. The user wants to agree the question and storyline before drafting prose, then work through the issues in conversation. Each issue describes proposed work and its completion criteria.

The teammate's earlier draft in `pnas_report/paper/main.tex` provides historical context. The new paper's wording and argument will be developed through the planning files in paper_simple.

The agreed endpoint is a complete first draft in the PNAS template, with a compiled PDF and verified Overleaf ZIP, ready for the group's full review. Read the [goal, completion criteria, and session-resumption process](README.md) before choosing the next issue. The planning work leads into writing the paper through issues 12–14.

## Location and Git state

- Repository root is `C:\Users\victo\Codex\Go_Nuts_repos`.
- Issue files live in `pnas_report/paper_simple/scratch`. Their relative links start from that folder.
- The checked-out branch at this review was `integrate-network-text`, tracking its remote counterpart. The text branch had already been merged into main before this branch was created.
- The paper_simple foundation was untracked at this review. Check `git status --short --branch` and confirm the planning files are present when moving between machines or branches.

## Repository map

| Location relative to this folder | Purpose |
| --- | --- |
| [paper_simple](../) | Current question, storyline, evidence inventory, requirements, and tone guide |
| [paper](../../paper/) | Earlier draft, bibliography, template dependencies, and a separate backbone subsection |
| [data/dataset_graph](../../data/dataset_graph/) | Selected transfer-network inputs |
| [data/top_five_league_clubs.csv](../../data/top_five_league_clubs.csv) | Season-specific league-membership lookup |
| [data/dataset_nlp](../../data/dataset_nlp/) | Guardian pipeline, selected signings, validation labels, analysis scripts, and result tables |
| [notebooks](../../notebooks/) | Network analyses, tests, and current plotting scripts |
| [output](../../output/) | Saved network findings, machine-readable results, interactive views, and publication figures |
| [notes](../../notes/) | Earlier specifications, proposals, source audits, and findings notes |
| [figures/plotting/data](../../figures/plotting/data/) | Copies of derived text tables used by the current text plotting script |

Other top-level folders contain course exercises, showcases, and study materials. Use them when a paper issue identifies a relevant course method or requirement.

## Current research basis

The existing question asks whether transfers involving players aged 30+ are less likely to enter the Premier League, and whether Guardian tone changes differently around entry for those who join.

- H1 measures a difference in Premier League joining rates between age groups.
- H2 measures the age-group difference in the change of sentiment from before to after a signing.
- H2b measures differences in sentiment levels with controls and was developed during exploration.
- Coverage volume is a further outcome whose place in the argument remains to be agreed.

The question in [final_research_question.md](../final_research_question.md) and argument in [paper_storyline.md](../paper_storyline.md) remain working documents. The user has confirmed PNAS as the guideline.

## Data and result snapshot

The eligible transfer input is [outsideprem_toprem_eligible_transfers.csv.gz](../../data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz). Direct inspection found 19,712 records, with season labels from `00/01` through `26/27` and gaps in the earlier coverage. It includes real-club moves originating outside the Premier League and retains destinations inside and outside that league. The saved network summary reports 1,254 clubs and 12,794 directed routes, weighted by transfer counts. This is a selected transfer network whose scope requires explanation.

The text [signings.csv](../../data/dataset_nlp/data/signings.csv) contains 1,332 signings with season values 2012 through 2024. Its documentation describes seasons 2012/13–2024/25, ages 18–36, market value at least EUR 2 million, and exclusions for loan returns and same-club moves. Main sentiment results use 820 signings, including 67 aged 30+. The all-controls H2b result table uses 793 signings, including 65 aged 30+. These samples require an explicit comparison with the network input.

Saved evidence to verify and interpret during the relevant issues includes the following.

- [H1 summary](../../output/age_shuffle_outsideprem_toprem_summary.md) reports joining rates of 14.87% for under-30 transfers and 11.19% for 30+, with a one-sided permutation p-value of 0.045. The sensitivity analysis uses one fixed random transfer per player and reports p = 0.044.
- [H2 table](../../data/dataset_nlp/results/a1_age30_results.csv) reports a main RoBERTa difference in changes of +0.006 with p = 0.7558.
- [H2b table](../../data/dataset_nlp/results/a1_h2b_controls.csv), RoBERTa, specification `7 all: no quotes, type adjusted, fame + value`, period `after`, reports a gap of -0.0349 with p = 0.0390. Several specifications and instruments were examined.
- [Validation table](../../data/dataset_nlp/results/b9_model_scores.csv), subset `all scored`, reports 196 scored human-labelled sentences and RoBERTa Spearman correlation 0.5158. The small older-player validation subset needs discussion.
- The community, feeder-route, ownership, degree, and backbone outputs exist. Their relevance to the new argument awaits the network-scope decision in issue 06.

These values locate the existing evidence. A full audit of statistical interpretation and reproducibility remains part of the issues.

## Source reliability and reproduction

Earlier prose can be incomplete or stale. In particular, the combined findings notes and earlier draft leave H1 as a TODO, despite saved H1 results. Some implementation plans still use future tense despite completed outputs. The graph README is a partial scaffold, and FILE_GUIDE.md includes paths that have changed.

For numerical claims, trace the result row or JSON field, generating code, input selection, and saved metadata together. Resolve disagreements explicitly and record the outcome in [evidence_and_sources.md](../evidence_and_sources.md).

Raw Guardian article bodies, sentence text, and scoring caches are described as held outside the repository. The repository has derived tables, selected signings, labels, and code. Check available inputs before planning a full rerun.

A test attempt in the `network_analysis` environment encountered missing leidenalg, unavailable Rscript, and a NetworkX private-import error. The community comparison instead names `machine-learning` as its environment. Confirm the relevant environment and versions before reproduction. Saved outputs and an executable local rerun are separate facts to verify.

## Agreed paper constraints

Use the [template ZIP](../template/Template_for_preparing_your_research_report_submission_to_PNAS_using_Overleaf__2025_.zip) and [course requirements](../project_requirements.md). The paper has a six-page limit including figures and references, a 150-word Abstract, a two- or three-sentence Significance Statement, the required body sections, and specific author contributions. The course recommends two or three figures carrying one story and requires network science, NLP, and validation.

The desired voice is simple academic English with selected essential numbers, verified citations for method theory, and enough study-specific detail for reproduction. See [tone_of_voice.md](../tone_of_voice.md).

## Resuming any issue

Read the current checkpoint in [paper_simple/README.md](../README.md), then follow the resumption process in [the tracker README](README.md). Each issue's Starting context and Related decisions and first interaction sections identify what to review and discuss for that step.
