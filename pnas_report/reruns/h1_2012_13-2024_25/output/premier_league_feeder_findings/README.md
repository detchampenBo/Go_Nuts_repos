# Premier League feeder findings

| Plot | PDF | PNG (600 dpi) | SVG |
| --- | --- | --- | --- |
| Combined | [PDF](combined.pdf) | [PNG](combined.png) | [SVG](combined.svg) |
| Frequent transfer routes (section A) | [PDF](frequent_transfer_routes.pdf) | [PNG](frequent_transfer_routes.png) | [SVG](frequent_transfer_routes.svg) |
| Transfer-count exceedance (section B) | [PDF](transfer_count_exceedance.pdf) | [PNG](transfer_count_exceedance.png) | [SVG](transfer_count_exceedance.svg) |

The primary combined figure displays 6 routes with at least 7 recorded transfers. The [alternate PDF](combined_min_6.pdf) displays all 13 routes with at least 6 recorded transfers.

The combined figure is 7.16 inches wide. Standalone plots are 3.58 inches wide with the same Arial typography and colours, and omit titles and subfigure letters. PDFs are vector exports with embedded fonts.

Data, selection and ownership classifications are shared across the plots: 217 selected recurring routes, with groups of 17 and 200. The bounded ownership screen and the two manual inclusions are described in the caption and findings recap. See the [findings recap](../premier_league_feeder_summary.md) for methods and interpretation.

Reproduce with `conda run -n machine-learning --no-capture-output python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_premier_league_feeder_findings.py`.
