# Decisions, checks and limitations (text part)

## Selection
- **1,332 signings: 797 young / 447 middle / 88 old.**
  - The spec expected about 1,250 / 670 / 140. Those numbers were counted before loan returns were removed (pre-filter: 1,312 / 723 / 150).
- **Loan-return rule:** a move counts as a loan return if the player's previous move went the opposite way within 730 days.
  - Exception: a move with a fee is never a loan return. Without it, 74 real signings that came straight after a loan would drop out (Romero, Kovačić, Ødegaard, Porro). `LOAN_RETURN_KEEP_PAID = False` gives the spec rule exactly.
- **Old signings cluster in recent seasons:** 70 of 88 are from 2020 or later, 30 in 2022, none in 2012–2014.
  - The 2022 peak is real (Casemiro, Eriksen, Koulibaly, Aubameyang, 7 old signings by newly promoted Nottingham Forest).
  - The early gap comes from the Kaggle data: it has only 1 old-player Premier League move in each of 2013 and 2014. Likely cause: transfer histories weren't collected for players already retired.
  - → Young vs old comparisons should use 2016+ or compare within seasons.

## Finding the articles (names)
- **Query:** full name + accent-free name + manual `ALIASES` by player_id (Zambo Anguissa, Son Heung-min, Ki Sung-yueng, Bobby Reid, Rasmus Kristensen, Yang Min-hyeok, Adrián, Samir).
- **Apostrophe names:** the Guardian search rejects a curly apostrophe (HTTP 400), and phrases with a straight apostrophe barely match (tested 7 Nov 2026). So the 10 apostrophe signings use broader queries:
  - apostrophe in the first name: search the surname;
  - apostrophe in the surname: the surname without apostrophe, or (first name AND (old club OR new club)).
  - `build` then keeps only their articles that name the player. Kanté went from 3 to 269 / 557 articles.
- **Signings with 0 articles:** Tedić, Bustos and Carreras. All three were signed by Man City / Man Utd and loaned out straight away, so zero is the true answer.

## Coverage properties (from `validate`, full data)
- **Fewer articles before than after:** median per young signing 10 vs 35 (middle 17 / 39, old 28.5 / 48.5). "Before" is often coverage abroad or in lower leagues and transfer rumours.
- **Old players get more coverage at every market-value level** (€40m+: 533 vs 178 median articles). Market value drops with age, so it understates their fame. Control for fame (e.g. articles before the transfer), not market value.
- **Links removed by the default exclusions:** of 125,231 links, 28,981 are liveblogs, 38,069 (30%) mixed-age articles and 10,736 overlapping windows. 53% remain after all three.

## Check: is the article really about the player?
**Focus check 1** (`data/check_focus_sample_labelled.csv`, 100 random links) and **focus check 2** (`data/check_focus_sample_2_labelled.csv`, 50 focus / 50 not, no liveblogs, none from check 1). Labels:
- **y**: he's a main subject
- **n**: passing mention
- **x**: wrong person (same name, different player)

Labelling rules:
- **Swap test:** if the article still works with his name replaced by a description ("their former striker"), it's **n**.
- **Match coverage** (reports, liveblogs, talking points): **y** if several sentences judge his performance, even when someone else made the headline. **n** for the line-up or one action.
- **Team news / fitness / "may start":** **n** unless the article is mainly about him.
- **Name lists:** **n**. **Interviews or post-match quotes where he's the main voice:** **y**.

| Focus rule | Check 1 (random): right / caught | Check 2 (fresh, weighted to the population): right / caught |
|---|---|---|
| Old: name in headline, or ≥10% of sentences | 10/18 = 56% / 10/22 = 45% | |
| **Current (B5): headline or ≥3 mentions** | 18/25 = 72% / 18/22 = 82% | **24/50 = 48% [34, 62] / 56% [36, 86]** |
| Headline or ≥5 mentions (looked at after check 2) | 13/17 = 76% / 59% | 16/21 = 76% / 37% |

- The ≥3 rule was chosen on check 1 and **did not confirm on check 2**: links with exactly 3 mentions and no headline are mostly passing mentions (6 y / 17 n). The main results don't use the focus rule; focus-only robustness rows mean "articles with more mentions".
- Wrong person: 3 of 100 in check 1 (before B5), 0 of 99 in check 2 (after B5).
- Scripts and numbers: `sentiment/b8_focus.py`, `results/b8_focus_rule_scores.csv`.

## Check: do the sentiment scores match a human reader? (B9, `data/check_sentiment_sample_200_labelled.csv`)
200 sentences (100 before / 100 after, one per article, main sample), labelled blind as pos / neu / neg toward the named player, x = wrong person; notes tag own quotes, quotes about him, contrast, passing mention, football words, age, merged sentences, unsure.

| 196 scored sentences | Spearman ρ (95% CI) | Sign right on pos/neg (85) | 3-class accuracy |
|---|---|---|---|
| RoBERTa | 0.52 [0.38, 0.63] | 82% | 50% |
| VADER | 0.33 [0.21, 0.45] | 68% | 42% |
| Bing | 0.36 [0.22, 0.47] | 59% | 51% |
| Bing, no football words | 0.36 [0.23, 0.49] | 58% | 53% |

- RoBERTa is the main instrument (better than each lexicon, paired bootstrap). All four read neutral sentences as mildly positive and misread contrast sentences.
- Wrong person: 4 of 200 (2.0%). Only 14 sentences concern 30+ players; with the same human label the models do not score them lower (RoBERTa +0.14, P = 0.14).
- Scripts and numbers: `sentiment/b9_score.py`, `results/b9_model_scores.csv`, `results/b9_confusion.csv`.

## Known problems / limitations
- **Wrong person for single-name players:** fixed in B5 (8 Nov): a name inside another person's name never counts (Transfermarkt's 50k names + a checked list), and a bare short name is ignored in articles that also name a namesake. What's left: 2% of labelled sentences; namesakes with no second name in the text (Marquinhos, Danilo) can't be separated.
- **Mentions are undercounted:** writers name a player once, then say "the 23-year-old", "the Portuguese"… The follow-on rule only adds a sentence starting with He/His. Example: Jota's talking point counted 1 mention.
- **The follow-on rule can attach the wrong sentence:** in the Mané liveblog it added a sentence about Martial.
- **Quotes from the player himself count as coverage of him:** e.g. Kulusevski's post-match frustration reads as negative tone, but it's his view, not the Guardian's. Possible check: drop sentences inside quotation marks.
- **Being named together isn't interacting** (relevant for a co-mention network).

## Sentiment (A1)
- **Methods:**
  - lexicons: VADER and Bing, plus Bing without football jargon (*free, defeat, fans, attack, penalty…*);
  - contextual model: RoBERTa (`cardiffnlp/twitter-roberta-base-sentiment-latest`, score = P(pos) − P(neg));
  - TF-IDF + logistic regression not used: no in-domain labelled training data.
- **Unit and test:**
  - each sentence is scored, then averaged per (signing, period);
  - paired after − before;
  - permutation test shuffling the period label between whole articles of a signing (a null model), plus bootstrap 95% CI.
- **Full-data results (9–18 Nov):** see `../../notes/findings.md` and `results/`.
  - Tone drops after the transfer for under-30 signings (RoBERTa −0.014, P = 0.012); 30+ no detectable change; the difference in change (H2) is +0.006, P = 0.76.
  - Tone level (H2b): with fame, market value, article type and quotes controlled, 30+ signings are covered less positively after the move (RoBERTa −0.035, P = 0.04; Bing −0.083; Bing-nf −0.087; VADER −0.041, P = 0.10); the gap before the move is mostly fame and market value.
  - Coverage: 30+ signings get 2.2× the articles before the move and 1.4× after (season fixed).
- **Validated** against 200 hand-labelled sentences (B9, above).
