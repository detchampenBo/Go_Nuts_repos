# Age-label shuffle for football transfers

## Objective

Among player transfers that start in one of Europe’s top-five leagues, are players aged 30 or older more likely than players under 30 to join a club outside those leagues?

Implement and run a one-sided permutation test. Keep the observed transfers fixed and shuffle the age-group labels within each origin club and season. Pool the seasons for the final comparison. Each eligible transfer record counts once, including when several players use the same club-to-club route.

## Inputs and deliverables

Paths in this document are relative to the `Go_Nuts_repos` workspace root.

| Path | Purpose |
| --- | --- |
| `pnas_report/data/dataset_graph/reduced_cleaned_transfers_with_players.csv.gz` | Transfer records |
| `pnas_report/data/top_five_league_clubs.csv` | Season-specific top-five club membership |
| `pnas_report/notebooks/age_shuffle_null_model.py` | Python module containing the callable analysis function |
| `pnas_report/output/age_shuffle_null_model.png` | Matplotlib figure |
| `pnas_report/output/age_shuffle_results.json` | Sample counts, test statistics, and simulated gaps |

Expose `run_age_shuffle_null_model(transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026)` as an importable function that runs the analysis, saves both output files, and returns the results. Make the module runnable as a script with the paths above as defaults. Resolve the default paths from the module’s location so the script also works from a different working directory. Use NumPy for the shuffle and Matplotlib for the figure. Create the output directory as needed. The existing Anaconda interpreter at `C:\Users\victo\Anaconda3\python.exe` was verified to have both packages installed.

## Build the analysis sample

1. Read club IDs consistently across both files. Build a membership lookup keyed by `(transfer_season, club_id)`. Use the recorded `transfer_season` to classify both endpoints of every transfer. Check that every season in the reduced file is covered by the lookup.
2. Keep transfers whose `from_club_id` belongs to a top-five league in that season. Use `to_club_id` and the same season lookup to mark the outcome. A move to a real club outside the top five counts as an exit. A move to another top-five club counts as a move within the top five. Both outcomes belong in each age group’s denominator.
3. Exclude destination IDs `515` (Without Club), `123` (Retired), and `2113` (Career break). Exclude records with missing or unusable `age_when_transferred`. Use the age at the transfer date and set the older label to `age_when_transferred >= 30`.
4. Keep all recorded seasons with eligible moves in the main analysis. The current snapshot includes 74 eligible records from the partial 2026–27 season. Preserve `player_id` for the repeat-player check.

Use these counts to verify the current snapshot. If a source file has changed, investigate discrepancies and report the counts from the version used.

| Check | Expected count |
| --- | ---: |
| All rows in the reduced file | 23,238 |
| Rows with a top-five origin | 14,719 |
| Top-five origin rows ending at one of the three non-club destinations | 391 |
| Remaining top-five origin rows with missing age | 4 |
| Eligible transfer records | 14,324 |
| Under 30, destination in the top five | 6,614 |
| Under 30, destination outside the top five | 6,480 |
| Age 30 or older, destination in the top five | 682 |
| Age 30 or older, destination outside the top five | 548 |
| Distinct eligible players | 4,521 |
| Origin-club and season groups with both age labels | 583 |

## Run the permutation test

1. Compute each age group’s exit rate as its number of exits divided by its total eligible transfers. The statistic is `100 * (exit_rate_30_plus - exit_rate_under_30)`, in percentage points. Use pooled transfer counts across seasons.
2. Group the transfer records by `(from_club_id, transfer_season)`. In each permutation, shuffle the binary age labels among records within each group. Keep the destination and exit outcome attached to the original record. Each group retains exactly the same number of labels in each age category. Groups with a single age label stay fixed and still contribute to the pooled rates.
3. Recompute the pooled gap for each of 999 permutations. The one-sided Monte Carlo p-value for the older group having a higher exit rate is `(1 + number of simulated gaps >= observed gap) / (1 + number of permutations)`. Include ties. Report the mean shuffled gap, which can differ from zero because the groups have different club and season mixes.
4. Use a reproducible seed and independent random number streams for the main shuffle, the one-transfer-per-player selection, and the sensitivity shuffle. Check that both age groups exist before calculating their rates.

## Check sensitivity to repeat players

The main analysis describes transfer records. In the current snapshot, 12,918 of the 14,324 eligible records come from players who appear more than once. Their age labels are linked across records, which can undermine the assumption that labels are interchangeable within origin club and season under the null.

Use the seeded random generator to select one eligible record uniformly per `player_id`. Run the same test on those selected records, with the same statistic, shuffle groups, and number of permutations. Report this as a sensitivity check and state whether the observed gap and its position in the null distribution tell a similar story. The main p-value is conditional on the label-shuffle assumption, and the sensitivity check describes a sample with one transfer per player.

## Save and verify the outputs

- Use a Matplotlib figure with two panels titled **All eligible transfers** and **One transfer per player**. Plot the distribution of shuffled gaps as blue bars (`#0072B2`), the observed gap as an orange line (`#D55E00`), and the shuffle mean as a dashed green line (`#009E73`). Use a shared x-axis range and a legend identifying all three. Label the x-axis **Exit-rate gap (30+ minus under 30, percentage points)** and the y-axis **Number of shuffles**. Save a readable PNG at 300 dpi.
- In the JSON, record the seed, permutation count, sample and exclusion counts, number of distinct players, number of groups containing both age labels, age-group totals and exit counts, exit rates, observed gap, shuffle mean, one-sided p-value, and simulated gaps for each analysis. Use field names that make the units clear.
- Run the module on the workspace data. Confirm that each analysis has exactly the requested number of simulated gaps and that a second run with the same seed reproduces the JSON results. Inspect the saved plot for a readable legend, labels, and visible reference lines. Summarize the observed rates, gap, null mean, and p-value for both analyses in the completion message, along with the output paths.
