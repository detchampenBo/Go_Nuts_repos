# Age-label shuffle for transfers into the Premier League

## Objective

Among player transfers that start at a real club outside the Premier League, are players aged 30 or older less likely than players under 30 to join a Premier League club?

Implement and run a one-sided permutation test. Keep the observed transfers fixed and shuffle the age-group labels within each origin club and season. Pool the seasons for the final comparison. Each eligible transfer record counts once, including when several players use the same club-to-club route.

The joining rate for each age group is its number of transfers into the Premier League divided by all its eligible transfers starting outside the Premier League. It is not that age group's share of Premier League arrivals. "Outside the Premier League" includes other top-five leagues, other foreign leagues, and lower English divisions. Classify the origin at the recorded transfer season; this does not refer to where a player started their career. The analysis describes the transfers recorded in the reduced dataset.

## Inputs and deliverables

Paths in this document are relative to the `Go_Nuts_repos` workspace root.

| Path | Purpose |
| --- | --- |
| `pnas_report/data/dataset_graph/reduced_cleaned_transfers_with_players.csv.gz` | Transfer records |
| `pnas_report/data/top_five_league_clubs.csv` | Season-specific league membership; use Premier League rows only |
| `pnas_report/notebooks/age_shuffle_outsideprem_toprem.py` | Python module containing the callable analysis function |
| `pnas_report/output/age_shuffle_outsideprem_toprem.png` | Matplotlib figure |
| `pnas_report/output/age_shuffle_outsideprem_toprem_results.json` | Sample counts, test statistics, and simulated gaps |

Expose `run_age_shuffle_outsideprem_toprem(transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026)` as an importable function that runs the analysis, saves both output files, and returns the results. Make the module runnable as a script with the paths above as defaults. Resolve the default paths from the module's location so the script also works from a different working directory. Use NumPy for the shuffle and Matplotlib for the figure. Create the output directory as needed. The existing Anaconda interpreter at `C:\Users\victo\Anaconda3\python.exe` was verified to have both packages installed. Save these new deliverables separately from the existing top-five exit analysis.

## Build the analysis sample

1. Read club IDs consistently across both files. Filter the league lookup to `competition_id == "GB1"` (Premier League), then build a membership lookup keyed by `(transfer_season, club_id)`. Use the recorded `transfer_season` to classify both endpoints of every transfer. Check that every season in the reduced file is covered by the Premier League lookup.
2. Keep transfers whose `from_club_id` does not belong to the Premier League in that season. Exclude origin IDs `515` (Without Club), `123` (Retired), and `2113` (Career break), so each eligible move starts at a real club. Do not restrict origins to the other top-five leagues.
3. Exclude destination IDs `515`, `123`, and `2113`. Use `to_club_id` and the same season lookup to mark the outcome. A move to a Premier League club counts as joining the Premier League. A move to any other real club counts as not joining it. Both outcomes belong in each age group's denominator; do not retain only Premier League arrivals.
4. Exclude records with missing or unusable `age_when_transferred`, including nonnumeric, nonfinite, or negative ages. Use the age at the transfer date and set the older label to `age_when_transferred >= 30`.
5. Keep all recorded seasons with eligible moves in the main analysis. The current snapshot includes 107 eligible records from the partial 2026–27 season. Preserve `player_id` for the repeat-player check.

Use these counts to verify the current snapshot. Apply exclusions in the order above so their counts are sequential and do not overlap. If a source file has changed, investigate discrepancies and report the counts from the version used.

| Check | Expected count |
| --- | ---: |
| All rows in the reduced file | 23,238 |
| Rows with an origin outside the Premier League, before non-club exclusions | 20,110 |
| Those rows starting at one of the three non-club origins | 98 |
| Rows starting at a real club outside the Premier League | 20,012 |
| Those real-club origin rows ending at one of the three non-club destinations | 296 |
| Remaining rows with missing age | 4 |
| Remaining rows with other unusable age | 0 |
| Eligible transfer records | 19,712 |
| Under 30, destination in the Premier League | 2,735 |
| Under 30, destination outside the Premier League | 15,663 |
| Under 30, total eligible transfers | 18,398 |
| Age 30 or older, destination in the Premier League | 147 |
| Age 30 or older, destination outside the Premier League | 1,167 |
| Age 30 or older, total eligible transfers | 1,314 |
| Distinct eligible players | 5,213 |
| Origin-club and season groups with both age labels | 683 |
| Eligible records from the partial 2026–27 season | 107 |

## Run the permutation test

1. First compute each age group's observed Premier League joining rate as its number of Premier League arrivals divided by its total eligible transfers. Report these rates as percentages. The statistic is `100 * (joining_rate_30_plus - joining_rate_under_30)`, where rates in the formula are proportions, so the gap is in percentage points. Use pooled transfer counts across seasons. A negative gap means older players join the Premier League less frequently.
2. Group the transfer records by `(from_club_id, transfer_season)`. In each permutation, shuffle the binary age labels among records within each group. Keep the destination and joining outcome attached to the original record. Each group retains exactly the same number of labels in each age category. Groups with a single age label stay fixed and still contribute to the pooled rates.
3. Recompute the pooled gap for each of 999 permutations. The one-sided Monte Carlo p-value for the older group having a lower joining rate is `(1 + number of simulated gaps <= observed gap) / (1 + number of permutations)`. Include ties. Use this lower-tail comparison because the specified alternative is that older players join less frequently. Report the mean shuffled gap, which can differ from zero because the groups have different club and season mixes.
4. Use a reproducible seed and independent random number streams for the main shuffle, the one-transfer-per-player selection, and the sensitivity shuffle. Check that both age groups exist before calculating their rates.

## Check sensitivity to repeat players

The main analysis describes transfer records. In the current snapshot, 18,430 of the 19,712 eligible records come from players who appear more than once. Their age labels are linked across records, which can undermine the assumption that labels are interchangeable within origin club and season under the null.

After restricting to this analysis's eligible transfers, use the seeded random generator to select one eligible record uniformly per `player_id`. Each of a player's eligible records must have equal selection probability, regardless of its age label or destination. Select the sensitivity sample once and keep it fixed throughout its 999 permutations. The current snapshot should yield 5,213 selected records from 5,213 different players.

Run the same test on those selected records, with the same statistic, shuffle groups, lower-tail alternative, and number of permutations. Report this as a sensitivity check and state whether the observed gap and its position in the null distribution tell a similar story. The main p-value is conditional on the label-shuffle assumption, and the sensitivity check describes one randomly selected sample with one transfer per player.

## Save and verify the outputs

- Use a Matplotlib figure with two panels titled **All eligible transfers** and **One transfer per player**. Plot the distribution of shuffled gaps as blue bars (`#0072B2`), the observed gap as an orange line (`#D55E00`), and the shuffle mean as a dashed green line (`#009E73`). Use a shared x-axis range and a legend identifying all three. Label the x-axis **Premier League joining-rate gap (30+ minus under 30, percentage points)** and the y-axis **Number of shuffles**. Save a readable PNG at 300 dpi.
- In the JSON, record the seed, permutation count, sample and exclusion counts, number of distinct players, repeat-player counts, number of groups containing both age labels, age-group totals and Premier League arrival counts, joining rates as percentages, observed gap, shuffle mean, lower-tail one-sided p-value, and simulated gaps for each analysis. Use field names that make the units clear and record the alternative as `joining_rate_30_plus < joining_rate_under_30`.
- Run the module on the workspace data. Confirm that each analysis has exactly the requested number of simulated gaps and that a second run with the same seed reproduces the JSON results. Check that each shuffle preserves age-group counts within each origin-club/season group and that the p-value includes simulated gaps equal to the observed gap. Inspect the saved plot for a readable legend, labels, and visible reference lines. Summarize the observed joining percentages, gap, null mean, and p-value for both analyses in the completion message, along with the output paths.
