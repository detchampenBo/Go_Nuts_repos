# Restricted H1 output verification

**User confirmed on 21 November 2026.** The user verified and accepted the current computations and new results. All 12 rerun issues are Resolved. The verification limits below remain part of the paper handoff.

21 November 2026. The paper evidence handoff covers recorded transfer seasons 2012/13–2024/25. The input has 16,636 records and 4,602 players, with actual event dates from 1 July 2012 through 15 July 2025. The selected seasons follow the source labels. The Guardian analyses use separate samples. [Reduction manifest](reduction_manifest.json)

## Artifact and original-file checks

All 124 frozen original output and figure hashes match. All 124 expected restricted counterparts are present. Every baseline CSV matches the recorded ordered columns, and all baseline JSON fields are present. The backbone JSON adds the explicit `r_parity_passed` field. Eight supplemental outputs comprise three network tables, three feeder compatibility figure formats, the feeder heatmap and the alternate six-transfer-minimum feeder PDF. The audit parsed the publication SVGs, verified the PNG files, opened the one-page PDFs and checked the local links in generated Markdown. [Final SHA-256 manifest](final_outputs_manifest.json)

## Evidence for the paper

| Stage | Verified evidence |
| --- | --- |
| Restricted input and H1 | Exact subset and all 14 H1 artifact hashes verified. Main older-minus-younger gap −2.42 percentage points, one-sided p = 0.098. The fixed one-transfer-per-player analysis gives −1.94 points, p = 0.074. The original permutation verification stands. [H1 summary](../output/age_shuffle_outsideprem_toprem_summary.md) · [Verification](h1_verification.json) |
| Degree and shared graph | 1,157 clubs, 11,016 directed routes and 16,636 transfers. Every club degree and route accounted for. The saved null preserves in-degree, out-degree and the weight multiset. [Degree recap](../output/degree_distribution_recap.md) · [Shared metadata](../output/transfer_community_comparison/shared_inputs.json) |
| Louvain and Leiden | All four saved partitions were independently rescored. The observed Q values are 0.445638440 and 0.448177191. Overlap, connectivity, and the shared layout agree with the saved tables. [Community comparison](../output/transfer_community_comparison/method_comparison.md) |
| Feeder routes | 2,396 arrivals, 11,448 tested pairs, 296 at unadjusted p < 0.05, and 217 recurring selected routes comprising 626 records. Saved p-values agree with the reported shuffle tallies and plus-one calculation. [Feeder summary](../output/premier_league_feeder_summary.md) |
| Ownership and feeder figures | Bounded source screening covers 217 routes, including 28 reviewed in this session. That review covered 68 records and established no additional documented common-equity interval. There are 16 documented pairs, including 15 with 62 transfer-date overlaps. The 17-route plotted group includes two manual inclusions. The refreshed caption explains the distinction, and all three PDF QA renders were visually checked. [Ownership screen](ownership_screen_28_routes.md) · [Results](../output/premier_league_feeder_ownership_results.json) · [Figure index](../output/premier_league_feeder_findings/README.md) |
| Backbone | All 17,695 scoped scores, 606 retention rows, 2,314 layout rows and embedded data were checked. The raw R comparison is 29/30. In scope 1, Grêmio → Sassuolo has an exact score of 0.20 and is excluded by the retained strict rule. R rounds below the cutoff and retains it. The whole-network comparison at 0.20 agrees. [Backbone results](../output/louvain_transfer_backbone_findings/backbone_results.json) · [Boundary diagnosis](backbone_boundary_diagnosis.json) |

## Remaining checks and scope

The user selected the 7-transfer minimum as the primary panel (a) display. That panel shows six routes, four of which are in the joint-ownership group including two manual inclusions. The 6-transfer alternate shows 13 routes, six in the joint-ownership group including the same two manual inclusions. The alternate uses a taller page for label spacing. Both retain all 217 selected routes in panel (b). The publication renders and compatibility exports were checked. [Feeder figure index](../output/premier_league_feeder_findings/README.md)

The independent backbone export verification and arithmetic diagnosis preserve the raw R failure. Two documents included in the backbone's original input hash inventory now have corrected reproduction paths. Their original and final hashes are recorded separately in the manifest. The other 32 recorded inputs match.

The interactive backbone's embedded data and cutoff logic were checked. Live browser QA remains outstanding because Computer Use could not verify the active Windows browser URL. Historical ownership disclosure gaps remain in the additional route review. The next paper task is to review the sample and provenance wording in Issue 02. [Paper Issue 02](../../../paper_simple/scratch/2026-11-19_15-30-34_02-reconcile-samples-and-data-provenance.scratch) · [Paper checkpoint](../../../paper_simple/README.md) · [Execution log](run_log.md)
