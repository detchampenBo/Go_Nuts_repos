# Leiden transfer communities

- [PDF](leiden_transfer_communities.pdf) · [PNG](leiden_transfer_communities.png) · [SVG](leiden_transfer_communities.svg) · [HTML](leiden_transfer_communities.html) — Transfer communities
- [PDF](leiden_transfer_modularity_progress.pdf) · [PNG](leiden_transfer_modularity_progress.png) · [SVG](leiden_transfer_modularity_progress.svg) — Modularity progress
- [PDF](leiden_transfer_communities_and_modularity.pdf) · [PNG](leiden_transfer_communities_and_modularity.png) · [SVG](leiden_transfer_communities_and_modularity.svg) · [HTML](leiden_transfer_communities_and_modularity.html) — Combined view
- [club_vertex_mapping.csv](club_vertex_mapping.csv)
- [communities.csv](communities.csv)
- [community_summary.csv](community_summary.csv)
- [final_partitions.csv](final_partitions.csv)
- [leiden_membership_trace.csv](leiden_membership_trace.csv)
- [leiden_progress.csv](leiden_progress.csv)
- [shuffled_routes.csv](shuffled_routes.csv)
- [Results and versions](leiden_results.json)
- [Captions](leiden_transfer_communities_caption.md)
- [Findings and method](leiden_transfer_communities_summary.md)

From the repository root in the machine-learning environment:

```powershell
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/leiden_transfer_communities.py
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/leiden_transfer_communities.py --plot-only
```

Sources: [Traag, Waltman and Van Eck (2019)](https://arxiv.org/abs/1810.08473) and [leidenalg API](https://leidenalg.readthedocs.io/en/latest/reference.html).
