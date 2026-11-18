# One-transfer-per-player sensitivity sample

The sensitivity plot describes an age-label permutation test on one fixed, randomly selected subset of the eligible transfer records. The sampling and permutation are separate steps.

## What the implementation does

In [`run_age_shuffle_outsideprem_toprem`](../notebooks/age_shuffle_outsideprem_toprem.py), the code first applies the eligibility rules, groups the remaining row indices by `player_id`, and calls `selection_rng.choice(indices)` once for every player. Each player's eligible records have equal selection probability: if player *i* has *m_i* eligible transfers, each has probability *1/m_i*. The selection does not use the record's age label or destination. These conclusions follow from the code and NumPy's documented defaults: `size=None` returns a single selection and omitted `p` gives uniform probabilities across the supplied entries. [NumPy: `Generator.choice`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html).

The procedure can be described as **player-stratified random sampling with one record per stratum**: the eligible records are partitioned by player and a random selection is made within each partition. This terminology is an application of Statistics Canada's definition of stratification, rather than a claim made by that source about this dataset. [Statistics Canada: stratification](https://www150.statcan.gc.ca/n1/pub/81-004-x/def/4068736-eng.htm).

Every distinct eligible player is represented exactly once. This is not a simple random sample of all eligible transfer rows: a transfer belonging to a frequent mover has a smaller inclusion probability than one belonging to a player with only one eligible move. With one draw per player, the default `replace=True` in `choice` cannot create duplicates within that player's selection; the disjoint player groups also prevent selection of the same row across players. [Implementation](../notebooks/age_shuffle_outsideprem_toprem.py); [NumPy: `Generator.choice`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html).

The code constructs `selected` once, then passes it to `_run_test`. Within `_run_test`, destinations, joining outcomes, origins and seasons stay fixed; only age labels are permuted within origin-club/season groups. The transfer subset is therefore **not sampled again for each permutation**. In the current saved run, 5,213 records represent 5,213 players, and that same sample is used for all 999 permutations. [Implementation](../notebooks/age_shuffle_outsideprem_toprem.py); [saved results](../output/age_shuffle_outsideprem_toprem_results.json).

The root seed is 2026. `SeedSequence(seed).spawn(3)` creates separate streams for the main permutation, record selection and sensitivity permutation. NumPy documents spawning as producing streams that are independent with very high probability. [NumPy: parallel random number generation](https://numpy.org/doc/stable/reference/random/parallel.html).

## Plot caption

> Age-label permutation null model  
> on a fixed network with one eligible transfer  
> sampled uniformly at random per player

This wording is retained in the publication caption, with no title inside the standalone plot. It identifies the null operation, the fixed network during permutations, and the actual sampling unit and selection rule. The selected records form a transfer-edge subset of the observed network, not a newly generated or rewired network.

For a methods paragraph:

> After eligibility filtering, we selected one transfer uniformly at random from each player's eligible records. We held this sample fixed and permuted age labels within origin club and season for 999 permutations. The resulting sensitivity analysis is conditional on this one selected sample.

Removing repeated contributions addresses that particular concern; it does not independently establish exchangeability of age labels or account for uncertainty across alternative one-transfer-per-player selections. This limitation follows from the implementation's single fixed selection.
