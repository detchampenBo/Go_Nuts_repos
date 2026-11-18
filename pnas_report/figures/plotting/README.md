# Plotting kit: text-part figures (H2, H2b, coverage)

Everything needed to remake and restyle the text-part figures. The kit holds only small CSVs: no Guardian text, no raw data, and nothing is recomputed. Repo location: `pnas_report/figures/plotting/`.

## Run

```
pip install pandas matplotlib
python plot_h2_arc.py
python plot_h2b_arc.py
python plot_h2b_gaps_coverage.py
```

Each script reads `data/` next to it and writes a PDF (for the paper) and a PNG (300 dpi) to `out/`. All three are 17.8 cm wide (PNAS full width). `out/` already holds the current versions for reference.

| Script | Figure | Reads |
|---|---|---|
| `plot_h2_arc.py` | Raw sentiment by month from the transfer, 30+ vs under 30, four models (H2). Same numbers as `fig_h2_arc_sentiment.png` | `a1_h2_arc_4models.csv`, `signing_tone.csv` |
| `plot_h2b_arc.py` | Same arcs, tone adjusted for fame, market value, season, article type and quotes; the gap between the lines is the tested H2b gap (paper Fig. 2) | `a1_h2b_arc.csv`, `a1_h2b_controls.csv` |
| `plot_h2b_gaps_coverage.py` | Tone gap before/after without and with controls, plus coverage ratio (paper Fig. 3) | `a1_h2b_controls.csv`, `a1_coverage_age.csv` |

## Data files (`data/`)

| File | What |
|---|---|
| `a1_h2_arc_4models.csv` | Monthly raw tone per model × group × month: `signings`, `mean` with bootstrap `lo`/`hi`, and the 3-month smoothed `mean_smooth`, `lo_smooth`, `hi_smooth` (what the arcs draw) |
| `a1_h2b_arc.csv` | Monthly adjusted tone per model × group × month: `mean`, `signings`, `smooth` |
| `a1_h2b_controls.csv` | Every tested gap: `model`, `spec` (1 no controls … 7 all controls … 9 within article type), `period` (before / after / change), `gap_30plus_minus_under30`, `ci_lo`, `ci_hi`, `p_within_season` |
| `a1_coverage_age.csv` | Coverage ratio 30+ / under 30 per period and spec, with interval, P and group medians |
| `signing_tone.csv` | One row per signing (1,332): age group, season, clubs, position, market value, articles before/after, tone before/after/change for four models (main sample only) |
| `b9_model_scores.csv`, `b9_confusion.csv` | Validation against the 200 hand-labelled sentences (Table 1), if you want to plot it |

Column details and conventions: `PLOTTING.md`.

## Conventions to keep across figures
- **Colours:** 30+ = orange `#eb6834`; under 30 = blue `#2a78d6`. In the gaps figure, grey hollow = no controls, blue filled = with controls.
- **Months:** month k covers days [30.44k, 30.44(k+1)) and is drawn at x = k + 0.5, so the dashed line at x = 0 is the transfer day. Draw before (k < 0) and after (k ≥ 0) as separate lines; the ±7 days around the transfer are not in the data.
- **Tone:** scale −1 to +1. RoBERTa is the main model; the others are checks.
- **Gaps:** always 30+ minus under 30, so negative = older players covered less warmly.

## Where the data came from
`make_data/export_h2_arc_4models.py` produced `a1_h2_arc_4models.csv` from the full sentence scores, using the same functions and seed as the original figure script. The other CSVs come from the analysis scripts in `pnas_report/data/dataset_nlp/sentiment/`. Those need the large local data files (sentences, scores), which aren't in the repo; you don't need them to make plots.
