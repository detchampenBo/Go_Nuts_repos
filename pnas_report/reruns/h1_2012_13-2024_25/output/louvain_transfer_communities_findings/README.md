# Louvain transfer communities

- [PDF](louvain_transfer_communities.pdf) · [PNG](louvain_transfer_communities.png) · [SVG](louvain_transfer_communities.svg) · [HTML](louvain_transfer_communities.html) — Transfer communities
- [PDF](louvain_transfer_modularity_progress.pdf) · [PNG](louvain_transfer_modularity_progress.png) · [SVG](louvain_transfer_modularity_progress.svg) — Modularity progress
- [PDF](louvain_transfer_communities_and_modularity.pdf) · [PNG](louvain_transfer_communities_and_modularity.png) · [SVG](louvain_transfer_communities_and_modularity.svg) · [HTML](louvain_transfer_communities_and_modularity.html) — Combined view
- [communities.csv](communities.csv)
- [community_summary.csv](community_summary.csv)
- [final_partitions.csv](final_partitions.csv)
- [louvain_progress.csv](louvain_progress.csv)
- [louvain_q_evaluations.csv](louvain_q_evaluations.csv)
- [louvain_supernode_mapping.csv](louvain_supernode_mapping.csv)
- [louvain_sweeps.csv](louvain_sweeps.csv)
- [shuffled_routes.csv](shuffled_routes.csv)
- [Results and versions](louvain_results.json)
- [Captions](louvain_transfer_communities_caption.md)
- [Findings and method](louvain_transfer_communities_summary.md)

From the repository root in the machine-learning environment:

```powershell
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_communities.py
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_communities.py --plot-only
```

Sources: [Blondel et al. (2008)](https://doi.org/10.1088/1742-5468/2008/10/P10008), [Dugué and Perez (2015)](https://hal.science/hal-01231784) and [NetworkX Louvain API](https://networkx.org/documentation/networkx-3.6.1/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html).
