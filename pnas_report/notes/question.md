# Research question

## Question
Among player transfers that start at a real club outside the Premier League, are players aged 30 or older less likely than players under 30 to join a Premier League club? For those who do join, does the Guardian's tone change differently after the move?

- **H1 (network):** 30+ players are less likely than under-30 players to join a Premier League club.
The two parts follow older players through two stages: **access** (getting into the league, H1) and **reception** (how the Guardian covers them once there, H2 and H2b).

- **H2 (text) — does joining the Premier League shift the coverage differently for older players?** Each player is compared with himself, before vs after the move. Statistic: mean change (after − before) of 30+ minus under-30 signings.
- **H2b (text, adopted 18 Nov) — is the coverage of older players less warm, at the same fame and price?** The two groups are compared within the same period. In the year after the move, is mean sentence tone toward 30+ signings lower than toward under-30 signings with the same prior coverage (fame), market value and transfer season, with article type and quoted speech accounted for?
  - Null: age group is unrelated to tone level (30+ label exchangeable within transfer season, given the controls).
  - Supported if the after-move gap is negative with P < 0.05 under RoBERTa and has the same sign under at least two of the other three instruments. The before-move gap is reported as context.
  - H2b emerged while testing H2 (11 Nov), so it is reported as exploratory.

Made-up example of the difference: a young player goes 0.12 → 0.10 and an older one 0.08 → 0.06. Both drop by 0.02, so H2 finds no difference; the older player sits 0.04 lower in both periods, so H2b finds one.

## Why these datasets can answer it
- **Transfermarkt transfers (network):** clubs as nodes, transfers as directed edges, with the player's age and both clubs' leagues at the transfer season. This gives every move that starts outside the Premier League and whether it ended inside it.
- **Guardian Content API (text):** every article naming a Premier League signing from 365 days before to 365 days after the transfer (1,332 signings 2012/13–2024/25, market value ≥ €2m, age 18–36; 125,231 article–player links, 303,530 sentences). The same newspaper before and after the move lets us compare coverage of the same player across the transfer.

## Measurement and what it captures
- **H1:** joining rate per age group = transfers into the PL / all eligible transfers from a real non-PL club; statistic = 30+ minus under-30 rate in percentage points.
- **Tone:** mean sentence sentiment per signing in the year before (−365 to −8 days) and after (+8 to +365 days); main sample excludes liveblogs and match reports; ≥5 sentences in both periods (820 signings: 67 aged 30+, 753 under 30). Main instrument RoBERTa (`cardiffnlp/twitter-roberta-base-sentiment-latest`, P(pos) − P(neg)); VADER, Bing and Bing without football words as second methods.
- **Coverage volume:** number of Guardian articles naming the player per period (all 1,332 signings).
- Tone captures how the *writing* treats the player (including quotes of others), not reader or fan opinion.

## Check (null, second method, or hand-labeled sample)
- **Null models:** H1 = 999 age shuffles within origin club and season (one-sided). H2/H2b/coverage = 5,000 shuffles of the 30+ label within transfer season (older signings bunch in 2022). Within-signing change = period label shuffled between articles.
- **Second method:** four sentiment instruments.
- **Hand-labelled samples:** 200 sentences labelled pos/neu/neg/wrong person (B9) — RoBERTa agrees best (Spearman ρ 0.52 vs 0.33–0.36); 100 article links labelled for "about the player" (focus check 2, B8) — the focus rule is right 48% of the time, so it is not used for main results.
- **Controls for H2b:** prior coverage (fame), market value, article type, quoted sentences, seasons 2016+, position.

## Result that would change the conclusion
- H1: if the age gap disappears once origin club and season are held fixed (shuffle within club-season), the lower joining rate is about which clubs sell older players, not age.
- H2b: if the after-move gap disappeared with fame and market value controlled, or appeared only under one instrument, it would reflect who older signings are or a model artefact. It held under RoBERTa, Bing and Bing without football words with all controls (VADER P = 0.10). A model that scored older players lower than human labellers would also undermine it (B9 shows no sign of this, but only 14 of 200 sentences are about 30+ players).
