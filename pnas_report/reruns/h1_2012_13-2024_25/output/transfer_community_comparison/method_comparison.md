# Leiden and Louvain transfer communities

Both methods started from the same singleton partition of 1,157 clubs. The common directed graph represents 16,636 eligible transfers across 11,016 routes, with transfer counts as weights. Both methods optimized directed weighted modularity at gamma = 1 using the same observed graph and the same degree-preserving shuffled graph. NetworkX independently scored all four final partitions. Each run used optimizer seed 2026, with reproducibility defined within each implementation.

| Method | Observed Q | Shuffled Q | Observed − shuffled | Observed communities | Shuffled communities |
| --- | ---: | ---: | ---: | ---: | ---: |
| Leiden | 0.448177191 | 0.215408404 | 0.232768787 | 5 | 18 |
| Louvain | 0.445638440 | 0.212515474 | 0.233122965 | 5 | 16 |

Leiden minus Louvain Q was +0.002538752 on the observed graph and +0.002892929 on the shared null. Each progress view uses its own run's optimized null Q. The level threshold governs Louvain and the first iteration without positive returned improvement governs Leiden. Accepted moves and completed iterations measure different operations. The different instrumentation scopes preclude a runtime ranking.

The overlap table contains 15 nonempty intersections spanning all 1,157 observed clubs. It uses shared membership and Jaccard overlap. Community IDs, names and colour swatches apply within each method. Both panels reuse the same node coordinates and sizes. Numbers identify the highest-degree representatives and key to their full names.

| Method | Weakly connected communities | Strongly connected communities |
| --- | ---: | ---: |
| Leiden | 5/5 | 0/5 |
| Louvain | 5/5 | 0/5 |

The connectivity counts describe the induced directed subgraphs. Leiden's refinement phase motivated its selection. Strong connectivity is assessed directly on these transfer routes. [Traag, Waltman and Van Eck (2019)](https://arxiv.org/abs/1810.08473) and [leidenalg API](https://leidenalg.readthedocs.io/en/latest/reference.html). [Blondel et al. (2008)](https://doi.org/10.1088/1742-5468/2008/10/P10008), [Dugué and Perez (2015)](https://hal.science/hal-01231784) and [NetworkX Louvain API](https://networkx.org/documentation/networkx-3.6.1/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html).

The null preserves every club's topological in/out degrees and the global weight multiset. It can change club-specific strengths, seasons, eligibility by season, geography, ownership, reciprocal routes and player trajectories. One seed and one randomized realization support a descriptive modularity comparison. Both methods are heuristic.

- [Leiden findings and figures](../leiden_transfer_communities_findings/README.md)
- [Louvain findings and figures](../louvain_transfer_communities_findings/README.md)
- [Comparison values, sizes and settings](method_comparison.csv)
- [Community overlap](community_overlap.csv)
- [Community connectivity](community_connectivity.csv)
- Paired network · [PDF](louvain_leiden_community_comparison.pdf) · [PNG](louvain_leiden_community_comparison.png) · [SVG](louvain_leiden_community_comparison.svg)
- [Shared metadata](shared_inputs.json) `5fcaa4aca80004746cea36bef29e4e8c02e8d475634ccc6162933cf13880c0a2`
- Eligible transfer input SHA-256 `48247e435eb0256405f778cafcfdba4eea39651a009fa61f88c41c907d36055a`
- [observed_routes.csv](observed_routes.csv) `6a620e2a47fb5b0ca09a7a3085bb85451c7858b77fc5beff963842e842c3565b`
- [shuffled_routes.csv](shuffled_routes.csv) `c46df6888feacb8f2430840d8e85c06854195cc0af24399e0a5c5419fd86b771`
- [layout.csv](layout.csv) `1520fb7c5f7f785f8e099c815ba345f161d655ea8678ab91c60663a5334bcf5b`

Run from the repository root in the machine-learning environment.

```powershell
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/transfer_community_inputs.py
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/leiden_transfer_communities.py
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_communities.py
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/compare_transfer_communities.py
```
