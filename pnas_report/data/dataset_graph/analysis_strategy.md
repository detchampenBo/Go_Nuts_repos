# Do older players cross transfer community boundaries more often?

Among players transferring out of the same club in the same season, are those aged 30 or older at the time of transfer more likely than those under 30 to join a club outside their origin club’s transfer community?

A transfer community is a group of clubs identified from historical transfer patterns in the directed, weighted club network. A transfer crosses a boundary when its origin and destination belong to different communities in the same historical partition.

## Notebook instructions

Create `pnas_report/notebooks/transfer_communities_age.ipynb`. Read [the dataset context](context.md) and use the [cleaned transfer file](cleaned_transfers_with_players.csv.gz) as the input. Run the notebook from a fresh kernel. Start each section with a short Markdown cell explaining the question it answers. Print named counts and denominators, label plot axes with units, and display compact tables with club names and IDs. Keep the source data read-only.

## 1. Audit the input and split the seasons

- Parse transfer dates and age at transfer. Keep club IDs as identifiers. Cite the [exclusions already applied to the cleaned file](../exclusion_criteria.md). Audit the cleaned file for missing endpoint IDs, invalid dates, and repeated `(player_id, transfer_date, from_club_id, to_club_id)` keys. Inspect any repeats before deciding how to count them.
- Exclude self-transfers and rows touching the known placeholder endpoints `75` (Unknown), `123` (Retired), `515` (Without Club), `2113` (Career break), or `24067` (School Team). Count each remaining transfer record once. Fee values play no role, and the file has no transfer-type field to separate loans from permanent moves.
- Fit the historical graph on recorded seasons **17/18–21/22** with dates from **1 July 2017 through 30 June 2022**. Evaluate on recorded seasons **22/23–24/25** with dates from **1 July 2022 through 30 June 2025**. Require both the recorded season and the date to fit the relevant window. Use the recorded `transfer_season` for the club-season comparison. Print how many rows pass the season filter but fall outside its date window.
- Print a filter ledger with the rows removed and remaining at each step, counts by season in both windows, and counts of missing ages. Keep missing ages in the historical graph. Require known ages for the evaluation.

**Check:** Verify the windows are disjoint and every evaluation date is after the latest historical date. Show the retained date range for each window.

## 2. Build and describe the historical graph

Group historical rows by the ordered pair `(from_club_id, to_club_id)`. Each pair is one directed link and its weight is the number of retained records. Report clubs, directed links, and transfers separately. Plot incoming and outgoing degree (distinct partner clubs) and strength (transfer counts). Show a small table of the largest flows using club names as display labels.

**Check:** Verify that the sum of edge weights equals the number of historical rows. Hand-check a small example with multiple transfers in one direction and a transfer in the reverse direction.

## 3. Define communities and measure who can be compared

- Fit weighted Louvain on the directed historical graph with seed `42` and resolution `1.0`. Fit without using ages or evaluation transfers. Print the number and sizes of communities, weighted modularity, and a few example clubs per large community. Use this partition for the primary result.
- Attach the historical community of both endpoints to each evaluation transfer. Define a crossing as a transfer whose two community IDs differ. Keep only transfers with both endpoints assigned and a known age. Show at least one crossing and one within-community example with club names.
- Form strata by origin club ID and recorded transfer season. Keep strata with at least one eligible transfer in each age group. Print the number of eligible strata and transfers by age group. Separately report how many evaluation transfers are lost at each step, including transfers with an unseen club and those in single-age-group strata. Show the endpoint coverage rate by age group and season so the reviewer can see who the comparison represents.

**Check:** Verify that each historical club has exactly one community and each eligible stratum contains both age groups. Check that clubs absent from the historical graph have no assigned community.

**Input check for this snapshot:** The specified filters retain 34,405 historical records across 5,410 clubs. Of 33,316 evaluation records, 30,753 have a known age and two clubs in the historical graph. The 1,784 mixed-age club-seasons retain 17,748 records.

## 4. Estimate the difference and compare it with a null model

Within each eligible club-season, compute the crossing share for transfers by players aged 30+ and for transfers by players under 30. Average the stratum-level shares using the same weights for both groups. For a stratum with group counts `n_30plus` and `n_under30`, use weight `n_30plus * n_under30 / (n_30plus + n_under30)`. This emphasizes club-seasons where both groups are well represented. The primary effect is the weighted 30+ share minus the weighted under-30 share, in percentage points.

Run 999 reproducible age-group permutations within origin club and season. Keep the observed transfers, their crossings, the community map, and the age-group counts within each stratum fixed. Recompute the same weighted difference for each shuffle. The null models exchangeable age labels within club-season. For the directional question, report the one-sided Monte Carlo p-value `(1 + number of shuffled differences at least as large as observed) / (1 + number of shuffles)`.

**Show:** Print the two weighted rates, the difference, and the p-value alongside the evaluation sample sizes. Plot the null distribution with the observed difference marked. Label the horizontal axis in percentage points.

**Check:** Hand-calculate the statistic for a tiny two-stratum example. Verify shuffles preserve the age-group counts in each stratum and leave the observed crossing outcomes fixed.

## 5. Check how much the answer depends on the boundaries

- Repeat Louvain with seeds `7` and `19` at resolution `1.0` and with seed `42` at resolutions `0.8` and `1.2`. Compare each partition with the primary one using normalized mutual information, which compares club assignments regardless of community labels. Recompute the same age contrast and shuffled baseline on the same evaluation transfers for each partition.
- Try directed, weighted Infomap as a second method if the notebook environment supports it. Use the same historical graph and evaluation sample. If the implementation is unavailable or leaves clubs unassigned, record the limitation and keep the Louvain checks as the reported sensitivity analysis.
- Check repeated players by retaining the earliest evaluation move with a known age and two assigned endpoints per player, breaking date ties by club IDs. Then form the mixed-age strata and repeat the primary comparison. Report the reduced sample alongside the result.

**Show:** Make one sensitivity table with the method, settings, number of communities, agreement with the primary partition, both weighted rates, the difference, and the shuffled comparison. Keep the repeated-player check separate because it changes the sample.

## Review the result

Show the filter ledger and example transfers before interpreting the effect. A positive difference in the upper tail of the shuffled baseline supports the proposed direction for the covered club-seasons. If the difference shrinks or reverses across reasonable partitions, describe the result as sensitive to the community definition. If the primary difference is typical of the shuffled values, report the observed effect size and the limited evidence for the proposed direction.

Interpret a crossing as a move beyond the origin club's historical trading group. A route can be frequently used and still cross a boundary. Report the age comparison as an association within observed transfers.

## Curriculum references

- [Week 1 — Graph representation and degree distributions](../../../data/week1/Week%201%20·%20Networks%20—%2002805.html)
- [Week 2 — Shuffling and null models](../../../data/week2/Week%202%20·%20Models%20%26%20null%20models%20—%2002805.html)
- [Week 3 — Mixing patterns](../../../data/week3/Week%203%20·%20Who%20matters,%20and%20why%20—%2002805.html)
- [Week 4 — Weighted communities and stability](../../../data/week4/Week%204%20·%20Communities%20—%2002805.html)
