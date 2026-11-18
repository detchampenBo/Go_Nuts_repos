# Data for making the figures yourselves

(In this kit all files are in `data/`. The raw four-model arc is `a1_h2_arc_4models.csv`, which has the same columns as `a1_age30_arc.csv` described below, plus Bing and Bing without football words, and its model column is called `model`.)

Every figure in the draft comes from one CSV in this folder, so you can restyle the plots without rerunning any analysis. The numbers in the paper text are in the same files.

Conventions:
- **Tone:** mean sentence sentiment, scale −1 (negative) to +1 (positive). RoBERTa is the main model; VADER, Bing and Bing without football words are cross-checks.
- **Periods:** `before` = 365 to 8 days before the transfer; `after` = 8 to 365 days after. The ±7 days around the transfer are left out.
- **Groups:** `30+` = aged 30–36 at the transfer; `Under 30` = 18–29.
- **Main sample:** 820 signings (67 aged 30+). No liveblogs or match reports; at least 5 scored sentences both before and after.

## 1. Tone arc over time, raw (H2) → `a1_age30_arc.csv`
One row per group × month × model.

| Column | Meaning |
|---|---|
| `group` | `30+` or `Under 30` |
| `month` | months from the transfer, −12 … 11. Month k covers days [30.44k, 30.44(k+1)); plot at x = k + 0.5 so x = 0 is the transfer day |
| `signings` | signings with sentences in that month |
| `mean`, `lo`, `hi` | mean tone across signings, with 95% bootstrap band |
| `mean_smooth`, `lo_smooth`, `hi_smooth` | 3-month rolling mean, smoothed separately before and after the transfer (what the figures draw) |
| `method` | model |

Draw the before (month < 0) and after (month ≥ 0) parts as separate lines so the smoothing doesn't bridge the transfer.

## 2. Tone arc, adjusted for the H2b controls → `a1_h2b_arc.csv`
Same layout (`group`, `month`, `mean`, `signings`, `smooth`, `model`), 65 vs 728 signings. Tone has quotes dropped, article type adjusted, and fame, market value and season held at the sample average. The vertical gap between the lines equals the tested H2b gap. Gaps and P-values for the panel titles: file 3, rows with spec `7 all: …`.

## 3. Tone gaps with and without controls (H2b) → `a1_h2b_controls.csv`
One row per model × spec × period.

| Column | Meaning |
|---|---|
| `model` | RoBERTa, VADER, Bing, Bing no football words |
| `spec` | which controls: `1 no controls`, `2 + fame`, `3 + fame + market value`, `4 article type adjusted`, `5 no quoted sentences`, `6 seasons 2016+`, **`7 all`** (main H2b result), `8 all + position`, `9 within news/features/comment` |
| `period` | `before`, `after`, `change` |
| `n_30plus`, `n_under30` | signings in that version |
| `gap_30plus_minus_under30` | the gap (negative = 30+ covered less warmly) |
| `ci_lo`, `ci_hi` | 95% interval (gap ± 1.96 SD of the shuffle distribution) |
| `p_within_season` | two-sided P from 5,000 shuffles of the 30+ label within season |

The draft's dot figure uses specs 1 and 7, periods before and after.

## 4. Coverage volume → `a1_coverage_age.csv`
One row per article scope × spec × period: `ratio_30plus_vs_under30` (30+ get x times the articles), `ratio_lo`, `ratio_hi`, `p_within_season`, plus group medians (`median_articles_30plus`, `median_articles_under30`). Use `articles = all article types`; specs `season only` and `+ market value`. Periods: `before`, `after`, `change` (= growth after / before). Plot ratios on a log axis with a line at 1.

## 5. Validation (Table 1) → `b9_model_scores.csv`
Rows with `subset = all scored` give, per model: `spearman` (with `spearman_lo/hi`), `polarity_acc` (sign right on pos/neg sentences), `acc3`. Other subsets: by note tag, 30+ vs under 30, without unsure. `b9_confusion.csv` has the 3 × 3 counts per model if you want a confusion-matrix plot.

## 6. Anything else → `signing_tone.csv`
One row per signing (all 1,332), for your own plots:
- **Identity:** name, age, `age30plus`, season, clubs, position, market value, fee.
- **Coverage:** `articles_before` / `articles_after`, also without liveblogs.
- **Sample:** `in_main_sample`, plus sentence and article counts in the main sample.
- **Tone:** `<model>_before`, `<model>_after`, `<model>_change` for the four models (empty outside the main sample).

Group means of the RoBERTa columns over the main sample reproduce the paper: 30+ 0.0914 → 0.0838, under 30 0.1253 → 0.1117.

## Colours used so far
- 30+ = orange `#eb6834`; under 30 = blue `#2a78d6`.
- In the dot figure: grey hollow = no controls, blue filled = with controls.
- Keep the 30+ / under-30 colours the same across all figures.
