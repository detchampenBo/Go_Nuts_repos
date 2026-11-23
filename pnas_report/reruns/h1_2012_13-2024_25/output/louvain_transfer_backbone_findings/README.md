# Louvain transfer backbone outputs

Open the [offline explorable](louvain_transfer_backbone.html) in a browser. Use the community selector to switch directional denominators. The slider starts at 0.20, and the unfiltered control restores every route.

- [Publication PDF](louvain_backbone_alpha_comparison.pdf) · [600 dpi PNG](louvain_backbone_alpha_comparison.png) · [Editable-text SVG](louvain_backbone_alpha_comparison.svg)
- [Scoped route scores](backbone_route_scores.csv) · [Retention and fragmentation](backbone_retention.csv) · [Fixed layouts and R vertex indices](backbone_layout.csv)
- [Checksums, versions and R parity](backbone_results.json) · [Findings and interpretation](backbone_summary.md)

## Figure caption

Directed transfer backbones of the same observed network at three local disparity cutoffs. At α = 0.10, the backbone contains 566 routes, 2,986 transfers and 229 active clubs. At α = 0.20, the backbone contains 1,396 routes, 5,271 transfers and 383 active clubs. At α = 0.30, the backbone contains 2,833 routes, 8,191 transfers and 514 active clubs. Panels use fixed positions and node sizes, with colours and symbols identifying the 5 saved Louvain communities. Arrows run from origin to destination and their shafts widen with transfer count.

## Reproduce from the workspace root

```powershell
conda activate network_analysis
conda run -n machine-learning python pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_backbone.py
python -m unittest discover -s pnas_report/notebooks -p test_louvain_transfer_backbone.py
```

The analysis runs R package parity on all 6 views at five cutoffs before exporting. The retention table includes each slider value and the unfiltered baseline. Missing endpoint scores and unfiltered alpha are blank in the CSV. The layout defines the contiguous one-based R vertex index within each scope.


The R reference agrees in 29 of 30 scope/cutoff comparisons. In scope 1 at α = 0.20, the exact score for Grêmio → Sassuolo equals the cutoff. Python excludes the route under the strict comparison. R's normalized arithmetic rounds the score below the cutoff and retains it. [Saved parity results](backbone_results.json) · [Boundary diagnosis](../../provenance/backbone_boundary_diagnosis.json)
