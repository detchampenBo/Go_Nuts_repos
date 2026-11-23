# Paper issue tracker

Keep one Markdown-formatted `.scratch` file per issue encountered while developing the paper. Record research needs, missing evidence, additional findings, citations, LaTeX cross-references, and decisions that need discussion.

The current checkpoint lives in [paper_simple/README.md](../README.md). Refresh it when an issue is completed to the user's satisfaction or a session ends with work in progress.

**Resume Issue 09 after 22 November 2026:** use its updated [standalone continuation prompt](2026-11-19_15-30-34_09-select-figures-and-plan-cross-references.scratch#continuation-prompt). Both figure presentations are produced. Start with the **Figure 1 caption**, followed by Figure 2/validation-table captions, final labels/cross-references, coverage presentation and print fit. Issue 09 and 09c remain Open; 09a/09b are Resolved. The final network-marker scale is 1.5 in width/height with standard legend symbols. H2b omission and Figure 2 selection are settled. This end-of-day handoff supersedes older candidate wording below.

Every issue and the template includes a Checkpoint workflow. Follow it when entering directly through a scratch file so the issue and the current checkpoint stay consistent.

Start a new session by reading the selected issue and [REPOSITORY_CONTEXT.md](REPOSITORY_CONTEXT.md). Each issue includes its own starting context, related decisions, supporting sources, first discussion, and completion criteria. Recheck the dated context against the current files before relying on it.

## Goal and completion criteria

Produce a complete first draft of the paper in the supplied PNAS LaTeX template, developed afresh in paper_simple from the existing results and the evidence and decisions recorded through these issues. Develop the question and storyline with the user, then write and verify the paper through manageable interactions.

The first-draft milestone is reached when all of the following are available.

- An agreed research question and coherent storyline recorded in the planning files.
- Written Abstract, Significance Statement, Introduction, Results, Discussion, Methods, References, and specific author contributions, with confirmed author details.
- Selected figures with complete captions and working citations and cross-references.
- Numerical claims traced to reviewed results, with appropriate uncertainty, exploratory status, and limitations.
- LaTeX source and a visually checked PDF satisfying the course's six-page limit including figures and references, its 150-word Abstract requirement, and the remaining requirements checklist.
- An Overleaf-uploadable ZIP whose contents compile after fresh extraction, with the source, PDF, and ZIP locations recorded in issue 14.

The completed draft is ready for the group's full review and revision. The presentation and reflection are additional submission deliverables tracked in the requirements document.

## Resuming without chat history

1. Read the current checkpoint in [paper_simple/README.md](../README.md), this goal, REPOSITORY_CONTEXT.md, and the current question, storyline, evidence inventory, requirements, and tone guide in paper_simple.
2. Read issue statuses and the latest progress entries. Select the earliest unfinished issue whose prerequisite decisions are ready. Follow dependency links when newer issues require an earlier decision to be revisited.
3. Briefly tell the user the recorded state and propose the next specific discussion or action. Use their guidance to agree substantive choices about the question, scope, analysis, storyline, and interpretation.
4. Complete the agreed step and record its evidence, decisions, changed files, unresolved questions, and exact next step. Update the relevant planning files so the outcome survives the session.
5. Add new scratch issues when research, findings, citations, or cross-reference needs emerge. Link them to the issue and claim they affect, and agree any change in work order with the user.
6. Mark an issue Resolved when its completion criteria are met and its outcome is recorded. Resolve or explicitly account for new issues affecting the draft before declaring the first-draft milestone complete.

The numbered order is a working sequence. Evidence review can lead back to the question or storyline. The sequence remains **09 → 10 → 11 → 11.1 → 12**. On 22 November 2026 the user explicitly selected the new H2 figure and omitted H2b. Issue 11.1, retaining the former Issue 15 filename, now tracks only the disposition of the previously suggested further course-grounded text subanalysis. No replacement analysis is selected or authorised. Incorporate any separately agreed follow-up and reconcile the figure, Methods, Discussion and page plans before drafting. Completing the tracker includes drafting, template assembly, compilation and packaging in Issues 12–14.

## Approved restricted-period rerun batch

The user verified and accepted the restricted H1 and transfer/network results on 21 November 2026. All 12 rerun issues are Resolved. Use the [restricted result handoff](../../reruns/h1_2012_13-2024_25/provenance/output_parity_report.md) for H1, network, and feeder evidence. Guardian results come from the separate [NLP evidence tables](../../data/dataset_nlp/results/). Paper Issues 01–08 are Resolved. The user confirmed the [storyline and provisional six-page budget](../paper_storyline.md#agreed-storyline) on 22 November 2026. Preserve the approved sample and H1 wording, the [agreed Guardian interpretation](../evidence_and_sources.md#issue-05-guardian-tone-and-coverage-findings-21-november-2026) and the [selected literature roles](../evidence_and_sources.md#issue-07-literature-framing-22-november-2026). Next, start Issue 09's figure and caption review, retaining the optional backbone and conditional text-extension decisions. [Issue 11.1, formerly 15](2026-11-21_15-45-35_15-explain-h2b-model-and-figure.scratch) tracks the open H2b follow-up before drafting.

Issue 09 is in progress as of 22 November 2026. The user selected the backbone-H1 pairing for Figure 1 and accepted [the new unadjusted four-model monthly H2 figure](../../output/h2_monthly_period_means_findings/combined.pdf) for Figure 2. They explicitly agreed to omit H2b for the [stronger contribution-versus-complexity reason](../paper_storyline.md#agreed-figure-2-and-h2b-omission-22-november-2026). Issues 09b (accepted production) and 09a (alternative not selected) are Resolved. Issue 09 remains Open for user review of the produced Figure 1, final captions/labels and manuscript fit; next, settle those items and whether coverage needs a panel. The former 0.45-page H2b allowance is unallocated fit margin. Issue 11.1's H2b decision is completed; the possible further text-subanalysis disposition remains open. Earlier conditional H2b wording is history. The original [continuation prompt](2026-11-19_15-30-34_09-select-figures-and-plan-cross-references.scratch#continuation-prompt) supplies background, with these latest decisions taking precedence.

## Creating an issue

Copy [_template.scratch](_template.scratch) and name the copy using the creation time in Europe/Copenhagen and a short description.

`YYYY-MM-DD_HH-mm-ss_short-description.scratch`

Sorting filenames ascending gives the order in which issues were raised. Keep the filename when updating or resolving an issue. If two issues share a timestamp, append `-02` to the second filename.

For a batch of issues created together, prefix each description with `01-`, `02-`, and so on to record the proposed working order. Revisit that order together as the paper develops.

Describe the gap, where it appears, why it matters to the question or storyline, and the next action to discuss. Link relevant repository files using paths relative to this folder.

## Following up

Use the status Open, In progress, Waiting for discussion, or Resolved. Add dated progress entries within the issue so its history stays chronological.

For a citation, record the claim and the source needed to support it. For a `\ref`, record the intended figure, table, or section and its `\label`. For an additional finding, record its source and the checks needed before using it in the paper.

Use these issues to agree on follow-up work together. Once resolved, record the evidence or decision and the affected paper or planning files. Retain resolved issues as part of the paper's development history.

## Initial paper-development issues

1. [Agree on the academic research question](2026-11-19_15-30-34_01-refine-research-question.scratch)
2. [Reconcile transfer and text samples](2026-11-19_15-30-34_02-reconcile-samples-and-data-provenance.scratch)
3. [Verify H1 and the strength of its evidence](2026-11-19_15-30-34_03-verify-age-entry-results.scratch)
4. [Establish what the sentiment measurement supports](2026-11-19_15-30-34_04-review-sentiment-measurement-validation.scratch)
5. [Separate and verify H2, H2b, and coverage findings](2026-11-19_15-30-34_05-verify-text-results-and-exploratory-status.scratch)
6. [Agree which network findings belong in the paper](2026-11-19_15-30-34_06-choose-network-analysis-role.scratch)
7. [Establish the literature context and method citations](2026-11-19_15-30-34_07-research-literature-and-verify-citations.scratch)
8. [Agree the section argument before drafting](2026-11-19_15-30-34_08-agree-storyline-and-page-budget.scratch)
9. [Select figures and define their claims and labels](2026-11-19_15-30-34_09-select-figures-and-plan-cross-references.scratch)
10. [Specify concise and reproducible Methods](2026-11-19_15-30-34_10-plan-reproducible-methods.scratch)
11. [Agree the interpretation and limitations](2026-11-19_15-30-34_11-agree-discussion-and-claim-boundaries.scratch)

    **11.1.** [Record H2b omission and settle the possible further text-subanalysis disposition](2026-11-21_15-45-35_15-explain-h2b-model-and-figure.scratch) — H2b decision completed; only the possible-subanalysis disposition remains Open before Issue 12.

12. [Draft the agreed paper in the requested voice](2026-11-19_15-30-34_12-draft-sections-and-confirm-author-details.scratch)
13. [Assemble the fresh PNAS project and validate references](2026-11-19_15-30-34_13-assemble-pnas-template-and-check-references.scratch)
14. [Review the six-page paper and prepare the Overleaf ZIP](2026-11-19_15-30-34_14-final-review-and-overleaf-zip.scratch)

## Follow-up issues

**09c.** [Produce combined backbone-H1 Figure 1](2026-11-22_20-12-45_09c-produce-backbone-h1-figure.scratch). Open: [combined PDF](../../output/backbone_h1_findings/combined.pdf) produced and checked, with standalone panels and PNG/SVG companions. Saved restricted-period scores/layout and H1 shuffles are preserved; no analytical producer was rerun. Next: user review, then final caption/labels and manuscript fit with Issue 09.

**09b.** [Produce unadjusted monthly H2 curves with period means](2026-11-22_18-56-56_09b-produce-unadjusted-h2-monthly-means.scratch). Resolved: user accepted the produced figure for the paper, with numeric-only age-coloured means and a uniform darker fine grid. Final manuscript captions/fit remain with Issue 09.

**09a.** [Produce and inspect a Guardian period-comparison candidate](2026-11-22_18-45-20_09a-produce-guardian-period-comparison.scratch). Resolved: comparison produced and inspected; the user selected the monthly H2 figure instead. Preserve this unselected alternative in the repository.

The H2b follow-up originally numbered 15 is scheduled as **11.1** above. Historical references to Issue 15 identify the same file. No separate issue has been opened for the possible text subanalysis because the user has not yet chosen whether or what to pursue.
