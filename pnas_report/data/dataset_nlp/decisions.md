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

## Check: is the article really about the player? (`data/check_focus_sample_labelled.csv`)
100 random links, hand-labelled:
- **y**: he's a main subject
- **n**: passing mention
- **x**: wrong person (same name, different player)

Labelling rules:
- **Swap test:** if the article still works with his name replaced by a description ("their former striker"), it's **n**.
- **Match coverage** (reports, liveblogs, talking points): **y** if several sentences judge his performance, even when someone else made the headline. **n** for the line-up or one action.
- **Team news / fitness / "may start":** **n** unless the article is mainly about him.
- **Name lists:** **n**. **Interviews or post-match quotes where he's the main voice:** **y**.

Result (99 labelled: 22 y, 75 n, 2 x):

| Focus rule | Right when it says "focus" | Real "about him" articles caught |
|---|---|---|
| Current: name in headline, or ≥10% of sentences | 10/18 = 56% | 10/22 = 45% |
| Name in headline, or named in ≥3 sentences | 18/26 = 69% | 18/22 = 82% |

- The ≥3-mentions rule was chosen on this same sample, so it needs a fresh sample to confirm.
- Why the 10% rule fails: a share penalises long articles (liveblogs and features where he's central), and match previews inflate it (the stats block reads as one long sentence).

## Known problems / limitations
- **Wrong person for single-name players:** Neto (the goalkeeper) is matched to Pedro **Neto**; Gabriel (Magalhães) to Gabriel **Martinelli** (and Jesus, Paulista); Emerson (Palmieri) to Emerson **Royal**; likely Fernando too (other Fernandos). To fix: don't count the name when a known other surname follows it.
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
- **Pilot result (4 Nov partial build, 37% of signings):**
  - all methods: tone drops after the transfer, overall and for young signings;
  - the lexicons put the drop mainly in news articles, while RoBERTa's news drop is much smaller;
  - in the strongest disagreements RoBERTa is usually right (negation, football words used as praise).
  - Full-data results to follow.
- **Still to validate:** the 200-sentence hand-labelled sample planned in the spec.
