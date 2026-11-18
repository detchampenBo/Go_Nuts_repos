# Findings

For each result, note the number, its comparison or check, and the figure that supports it.
Text-part numbers below are from `Project\Full\` outputs, checksum-verified (18 Nov 2026). H1 is for the network teammates to fill in.

## Main finding
**H1 (network):** _TODO teammates: joining rate 30+ vs under 30, gap in percentage points, one-sided P from 999 age shuffles within origin club and season; robustness on origin clubs with earlier PL sales. Figure: share joining the PL by age + shuffle null._

**H2 — tone change across the move does not differ detectably by age.**
- Under 30: RoBERTa −0.014 (P = 0.012); 30+: −0.008 (P = 0.68). Gap +0.006, 95% CI −0.036 to 0.045, P = 0.76 (5,000 within-season shuffles). No instrument significant (P = 0.24–0.76). Smallest detectable gap (80% power) 0.057.
- Files: `a1_age30_results.csv`, `a1_age30_mde.csv`. Figure: `fig_h2_arc_sentiment.png` (raw arcs).

**H2b (adopted 18 Nov) — after the move, 30+ signings are covered less positively at the same fame and market value.** Supported by the rule in `question.md` (RoBERTa negative with P < 0.05; same sign under all three other instruments, significant under two).
- Raw tone before: 30+ 0.091 vs under 30 0.125 (RoBERTa gap −0.034, P = 0.04; all four instruments negative).
- All controls (no quoted sentences, article-type adjusted, log prior coverage, log market value, season): before −0.015 (P = 0.35); **after −0.035 (P = 0.04)**. Bing −0.083 (P = 0.001), Bing without football words −0.087 (P = 0.003), VADER −0.041 (P = 0.10).
- After-move gap under RoBERTa is −0.027 to −0.035 across all control sets (single controls: P = 0.05–0.11). Change (H2) not significant in any version.
- Files: `a1_h2b_controls.csv`, `a1_h2b_signings.csv`. Figures: `fig_h2b_arc_controls.png` (paper version `fig_h2b_arc_paper.pdf`), `fig_h2b_tone_coverage.png`.

**Coverage volume — older signings get more Guardian coverage.**
- Articles naming the player, 30+ vs under 30 (season fixed): before 2.2× (median 27.5 vs 12), after 1.4× (47.5 vs 35); at equal market value 3.6× and 2.2×. Growth across the move 0.65× that of under-30s. All P ≤ 0.003. Same without liveblogs.
- File: `a1_coverage_age.csv`. Figure: panel C of `fig_h2b_tone_coverage.png`.

**Measurement check (B9, 200 hand-labelled sentences).**
- Spearman ρ with labels: RoBERTa 0.52 [0.38, 0.63], VADER 0.33, Bing 0.36, Bing-nf 0.36; sign right on pos/neg sentences 82% vs 58–68%. RoBERTa better than each lexicon (paired bootstrap).
- Files: `b9_model_scores.csv`, `b9_confusion.csv`.

## Limitations
- Few older signings: 88 (67 with enough coverage; 65 with all controls); 30 of 88 in 2022; Kaggle data thin before 2016. Handled by within-season comparisons, not removed.
- Several control sets were tried; the after-move gap is stable in size but reaches P < 0.05 under RoBERTa only with market value included.
- All instruments read neutral sentences as mildly positive and misread contrast sentences ("once struggled, now thriving").
- Age-bias check is weak: only 14 of 200 labelled sentences are about 30+ players (models did not score them lower than the labeller; RoBERTa +0.14, P = 0.14).
- Wrong person: 2.0% of labelled sentences (namesakes); 0 of 99 article links in focus check 2.
- "Focus article" rule (headline or ≥3 mentions) right only 48% of the time on a fresh sample; not used for main results.
- Player's own quotes count as coverage; dropping quoted sentences changes little (17% of sentences in both groups).
- One newspaper; tone of the writing, not of readers.
