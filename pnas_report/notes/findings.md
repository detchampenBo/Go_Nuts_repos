# Findings

For each result, note the number, its comparison or check, and the figure that supports it.

## Main finding


## Dataset consistency and report focus

The analyses can use nested samples without creating a dataset inconsistency. According to the [degree-distribution recap](../output/degree_distribution_recap.md), `exploration_v3.ipynb` uses the 19,712 eligible transfers originating outside the Premier League, including transfers to non-PL destinations. It does not represent the entire football transfer network.

| Analysis | Sample | Question |
| --- | --- | --- |
| Degree distributions | All 19,712 eligible transfers; 1,254 clubs and 12,794 directed links | How unevenly are distinct transfer partners distributed across clubs? |
| Age and PL entry | The same 19,712 eligible transfers | Are players aged 30+ less likely than younger players to enter the Premier League? |
| Proposed feeder-route analysis | The 2,882 PL arrivals within that sample | Among PL arrivals, do particular origins disproportionately supply particular destinations? |

The feeder analysis conditions on reaching the Premier League. The age analysis requires both PL and non-PL destinations to calculate joining rates, so restricting it to arrivals would remove its comparison group. Different subsets are appropriate when their inclusion rules, denominators, and questions are explicit.

Dataset consistency does not by itself establish a tight research story. Feeder routes introduce a second substantive question about club-to-club recruitment relationships alongside the existing question about age and league entry. The feeder analysis is currently a proposal, not an established finding; see the [implementation proposal](premier_league_feeder_clubs_proposal.md).

### Recommended scope for the six-page report

- Keep age and Premier League entry as the main research question and analysis.
- Use the degree distributions as brief network context. Degree counts distinct partner clubs, rather than transfer records.
- Develop the feeder-route visual as an exploratory extension. Include it in the main report only if its findings clearly strengthen the central story; otherwise place it in supplementary material.

If feeder routes become equally central, a possible overarching question is: "How is access to the Premier League structured by origin club and player age?" This broader framing requires an explicit analytical connection between the club and age results. Presenting the analyses side by side does not establish that connection.

## Limitations


## Related literature

