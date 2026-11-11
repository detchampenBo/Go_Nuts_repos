# Reciprocity and the top-five league transfer question

Among transfers out of Europe's top-five leagues, are players aged 30 or older at the time of the move more likely than players under 30 to join a club outside those leagues?

## What the paper models

Durak et al.'s Fast Reciprocal Directed (FRD) generator separates one-way links from reciprocal pairs. It samples one-way sources and destinations using the corresponding degree distributions, and separately generates reciprocal pairs by inserting both directions. The output approximates the observed in-, out-, and reciprocal-degree distributions. The sampler randomly relabels vertices and operates on a simple directed graph. One edge therefore represents a club-to-club route, even if many players used it. The paper's model has no transfer counts, ages, or league labels. [Durak et al. (2013), §§III–IV](https://arxiv.org/pdf/1210.5288v4)

## Primary test for the age question

1. Use the [season-specific league lookup](../data/top_five_league_clubs.csv) to classify both clubs for each recorded transfer. Retain moves with a top-five origin, a real destination club, and a known age. Pool across seasons after classifying the moves. One record counts as one transfer.
2. Compute the outside-top-five share for each age group and the difference in percentage points, 30+ minus under 30.
3. Shuffle age labels within each origin club 999 times, keeping every observed route, transfer count, destination classification, and each club's number of older and younger transfers fixed. Compare the observed difference with the simulated distribution. Report the observed gap, the mean shuffled gap, and the share of draws at least as large as observed with the usual plus-one correction.

This tests whether the observed age gap exceeds what the two groups' different mixes of origin clubs would predict under exchangeable age labels within each club. The shuffle already keeps the entire observed network, including its reciprocal routes. The pooled null can have a nonzero mean.

To ask whether the age gap is linked to established two-way routes, classify a club pair as previously reciprocal only if transfers in **both** directions were observed strictly before the focal transfer date. Use the full cleaned history if possible, since the reduced file omits earlier transfers in seasons when both clubs were outside the top five. Repeat the shuffle within each origin club and prior-reciprocity class. Report whether the excess above the null persists and how many transfers are in strata with both age groups.

## A paper-inspired extension

Ask a separate structural question. **Are distinct routes to outside clubs more concentrated among particular top-five origins than expected given each club's incoming, outgoing, and two-way partner counts?**

1. Build one simple directed graph per season from the [reduced file](../data/dataset_graph/reduced_cleaned_transfers_with_players.csv.gz), collapsing transfers on the same ordered club pair to one route. Keep club identities and that season's league memberships fixed.
2. Borrow FRD's separation of one-way and reciprocal links. In the one-way set, swap the destinations of two arcs, such as `A → B` and `C → D` becoming `A → D` and `C → B`. In the reciprocal set, swap partners of two mutual pairs, such as `A ↔ B` and `C ↔ D` becoming `A ↔ D` and `C ↔ B`. Reject proposed self-links, duplicate routes, or changes that unintentionally create or remove a reciprocal pair. This is a fixed-club rewiring adaptation of the paper's idea. It preserves each club's three degree counts exactly.
3. With the reduced file, also reject swaps that would create an outside-to-outside route. For every simulated set of season graphs, compute the outside-destination share at each top-five origin with outgoing routes. Measure dispersion across origins by averaging the squared deviations from their own season's pooled share, weighted by each origin's number of routes. Compare the observed dispersion with its simulated distribution. Verify all three degree counts are unchanged and check that the rewiring moves sufficiently far from the original graphs.

To test whether the **overall outside-route share** is unusual, use the [full cleaned file](../data/dataset_graph/cleaned_transfers_with_players.csv.gz) and allow outside-to-outside routes. In the reduced graph, every incoming edge to an outside club already comes from a top-five club. Preserving each club's in- and out-degrees fixes the total number of exits and the overall exit share, even when the origins of those exits can change. In the full graph, sum top-five-to-outside routes across seasons and divide by all outgoing routes from top-five clubs. Compare that share with the simulated distribution.

The structural comparison measures whether exit routes are unusually concentrated across origins or, with the full file, unusually common overall. The primary age shuffle measures whether older players use exits disproportionately among observed transfers. The comparisons support different claims because one counts routes and the other counts transfer records.
