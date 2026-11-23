# Club transfer network figures

Publication exports from the [executed restricted notebook](../../notebooks/exploration_v3.ipynb), using the original [plotting guide](../../../../PLOTTING_STYLE.md).

| View | PDF | PNG | Editable SVG |
| --- | --- | --- | --- |
| Combined degree distributions | [PDF](club_transfer_degree_distributions.pdf) | [PNG](club_transfer_degree_distributions.png) | [SVG](club_transfer_degree_distributions.svg) |
| In-degree distribution | [PDF](in_degree_distribution.pdf) | [PNG](in_degree_distribution.png) | [SVG](in_degree_distribution.svg) |
| Out-degree distribution | [PDF](out_degree_distribution.pdf) | [PNG](out_degree_distribution.png) | [SVG](out_degree_distribution.svg) |
| Reciprocal-degree distribution | [PDF](reciprocal_degree_distribution.pdf) | [PNG](reciprocal_degree_distribution.png) | [SVG](reciprocal_degree_distribution.svg) |
| Club transfer network | [PDF](club_transfer_network.pdf) | [PNG](club_transfer_network.png) | [SVG](club_transfer_network.svg) |

**Degree distributions.** Each point shows the fraction of all 1,157 clubs with the given in-degree, out-degree, or reciprocal degree. Both axes are logarithmic. The horizontal coordinate is degree plus one so the plots include clubs with degree zero.

**Club transfer network.** The pooled directed graph contains 1,157 clubs, 11,016 routes and 16,636 recorded transfers. Node area increases with total recorded transfers involving the club. Edge width increases with transfers along the route. Labels show the ten clubs with the largest total counts. Arrowheads are omitted for readability. Distances are determined by the weighted layout.

The combined figure is 7.16 by 3.4 inches. Standalone distributions are 3.58 by 3.2 inches, and the network is 3.58 inches square. The exports use Arial, editable SVG text and 600 dpi PNGs. The network uses the weighted spring layout with seed 42 and 30 iterations. For strength `s` and route weight `w`, displayed node area is `0.25 * (4 + 3 * sqrt(s))` points squared and edge width is `0.15 + 0.15 * log1p(w)` points.

[Degree-distribution recap](../degree_distribution_recap.md) · [Compatibility degree figure](../../figures/degree_distributions.png) · [Compatibility network figure](../../figures/transfer_graphs.png)

## Reproduction

From the repository root, execute the cells of the [run-local notebook](../../notebooks/exploration_v3.ipynb) with the machine-learning environment. The saved final cell verifies the restricted graph totals and exports its degree, summary and layout tables.
