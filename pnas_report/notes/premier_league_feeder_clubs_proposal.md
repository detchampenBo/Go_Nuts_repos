# Proposal: feeder routes into the Premier League

## Research question

Do clubs outside the Premier League repeatedly supply particular Premier League clubs, beyond what their overall transfer activity would predict?

This adds a structural question to the existing findings about unequal club connectivity and lower Premier League joining rates among players aged 30+.

## Network

Start with the existing eligible-transfer dataset and retain the **2,882 recorded Premier League arrivals**. Construct a weighted bipartite network:

- One side contains origin clubs outside the Premier League; the other contains Premier League destination clubs.
- Edge weights count recorded transfers along each origin-to-destination route.
- Classify both endpoints using Premier League membership in the transfer season. If a club appears in both roles across seasons, represent its supplying and receiving roles separately.

## Analysis

For each route, measure its transfer count and its share of the origin club's Premier League-bound transfers. These shares describe destination preferences conditional on entering the Premier League, rather than the origin's overall Premier League joining rate.

Compare route counts with a null model that shuffles Premier League destinations among arrival records **within each season**. This preserves each origin's number of Premier League-bound transfers and each destination's recruitment total per season. Use **999 shuffles** and identify unusually strong routes using **unadjusted upper-tail Monte Carlo p-values <= 0.05**, without multiple-comparison correction. Report counts alongside concentration, since one transfer can produce a misleading 100% share. Check whether repeated transfers by the same player drive prominent routes.

Community detection, such as Louvain, is an optional exploration of groups of supplying and receiving clubs that trade strongly with each other. A community may contain several Premier League clubs, so community membership alone does not establish a specific feeder route.

## Proposed visual

Use a two-column network diagram with outside clubs on the left and Premier League destinations on the right. Set line width by transfer count and highlight routes stronger than expected under the null model. If necessary, display a clearly stated subset for readability while retaining all routes in the analysis. A companion origin-by-destination heatmap can show the broader pattern.

## Interpretation

Use "feeder route" to mean a recurring, disproportionately strong connection in the recorded sample. It does not establish a formal partnership or its cause. This analysis concerns which Premier League club receives a transfer, whereas the existing age analysis concerns whether a transfer enters the Premier League at all.

Method references: [bipartite networks](https://networkx.org/documentation/stable/reference/algorithms/bipartite.html) and [Louvain community detection](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html).

## Instructions for an autonomous implementation agent

Implement, run, and verify the route analysis described here. Complete the deliverables below, rather than stopping at a plan or unexecuted code. Use the defaults specified here for routine decisions and document any necessary deviations. Community detection is an optional follow-up; it is not required for this implementation.

### Paths and implementation

All paths below are relative to `C:/Users/victo/Codex/Go_Nuts_repos/pnas_report`.

**Create a Python file in `/notebooks`: `notebooks/premier_league_feeder_routes.py`. Put all generated analysis outputs in `/output`, not in `/notebooks` or `/figures`.** These folder names refer to the project folders, not filesystem-root directories.

Inputs:

- `data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz`: use `from_club_id`, `to_club_id`, `transfer_season`, and `player_id`; inspect available name fields for labels.
- `data/top_five_league_clubs.csv`: use rows with `competition_id == "GB1"` to build membership keyed by `(transfer_season, club_id)`.

Read the existing age-analysis and degree summaries in `output` for context. Keep this analysis separate from their implementations and outputs. Retain all recorded seasons, including partial seasons, and report their coverage. Verify real-club endpoints and non-PL origins, then select PL destinations. Expected snapshot counts are 19,712 input records and 2,882 PL arrivals; investigate and report discrepancies rather than forcing those counts.

Expose an importable function `run_feeder_routes(transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026)` and a runnable script entry point. Resolve default paths relative to `__file__`, so execution works from any working directory. Use existing project dependencies where practical.

### Statistical specification

- Pool route counts across seasons, while shuffling destination IDs only within the same season. Use 999 permutations and seed 2026, with deterministic record ordering.
- For route A to B, calculate its expected count as the sum across seasons of `origin_PL_arrivals_A * destination_arrivals_B / total_PL_arrivals`, using season-specific counts and seasons with arrivals. Record observed count, expected count, observed/expected ratio, origin's PL-bound total, destination share, and distinct players on the route. Destination share means observed count divided by the origin's PL-bound total.
- Define the testing family before examining route strength: all origin/destination pairs with positive expected count, including unobserved routes. For each route, use the upper-tail Monte Carlo p-value `(1 + number of shuffled counts >= observed count) / (1 + n_permutations)`. Include ties. Unobserved routes have p-value 1.
- Use the unadjusted p-value <= 0.05 for the significance flag and highlighting. Do not apply multiple-comparison correction or export adjusted p-values. With 999 shuffles, the minimum p-value and grid spacing are 0.001; include ties and the plus-one correction specified above. Label results and figure legends as unadjusted, and interpret the threshold as a per-route comparison rather than control of false discoveries across all tested routes.
- Include distinct-player counts and flag routes whose transfer counts are inflated by repeated records for the same player. Treat this as a descriptive check, not an independent significance test. Explain that the shuffle controls seasonal transfer volumes, but not geography, ownership, or player characteristics.

### Required outputs in `/output`

| Filename | Contents |
| --- | --- |
| `premier_league_feeder_routes.csv` | Every tested pair, club IDs and available names, route measures above, unadjusted p-value, and significance flag based on unadjusted p-value <= 0.05. |
| `premier_league_feeder_results.json` | Input paths, sample/exclusion counts, season coverage, seed, permutation count, testing-family size, adjustment method recorded as none, unadjusted significant-route count, display-selection rule, and verification results. |
| `premier_league_feeder_network.png` | Two-column weighted network with supplying and receiving roles separated; line width represents transfer count and colour marks routes with unadjusted p-value <= 0.05. |
| `premier_league_feeder_heatmap.png` | Origin-by-destination heatmap of transfer counts, using the same displayed origin clubs as the network. |
| `premier_league_feeder_summary.md` | Methods, key counts, strongest routes under the unadjusted comparison, repeated-player caveat, interpretation limits, and links to both figures and the route table. Report the number of routes with unadjusted p-value <= 0.05 and explicitly state if none meet this threshold. |

For readable figures, display the 20 origins with the most PL-bound transfers and all destinations connected to them; break ties by club ID. Analyse the full sample regardless of this display selection. State this selection in captions and report whether significant routes fall outside it. Export readable PNGs at 300 dpi with legends defining weights and colours. Use club IDs when names are unavailable.

### Verification and completion

1. Check membership coverage for every input season, endpoint eligibility, total selected arrivals, and that edge weights sum to the arrival count.
2. Verify that each permutation preserves origin and destination transfer totals within every season. Check p-value ties, inclusion of the complete testing family, significance flags based directly on unadjusted p-value <= 0.05, and the distinction between role-specific nodes. Confirm that adjusted p-values are absent from the outputs.
3. Run the analysis twice with the same seed and confirm identical statistical outputs. Inspect both saved figures for readable labels, legends, and clipping; correct any layout issues.
4. Finish by reporting the Python file path, output paths, sample size, number of routes meeting the unadjusted p-value threshold, and any limitations. Do not describe a recurring route as evidence of a formal feeder agreement.
