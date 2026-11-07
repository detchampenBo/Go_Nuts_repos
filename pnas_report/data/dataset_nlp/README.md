# Dataset 2: Guardian coverage of Premier League signings

This folder holds the text side of the project: Guardian articles about every Premier League signing (2012/13–2024/25), from one year before to one year after the transfer, and the sentiment analysis of that coverage.

- **Source and collection date:**
  - Signings: Transfermarkt via Kaggle (dcaribou, *Football Data from Transfermarkt*): `transfers`, `players`, `games`.
  - Articles: the Guardian Open Platform content API (`/search`, section `football`), fetched 4–7 Nov 2026 with `fetch` (query_version 2).
- **What one row represents:**
  - `signings.csv`: one signing, i.e. one player joining a Premier League club on one date (`signing_id` = `<player_id>_<YYYYMMDD>`).
  - `article_player.csv`: one link between a Guardian article and a signing. An article can be linked to several signings.
  - `sentences.csv`: one sentence that names the player, plus the following sentence when it starts with *He/His*.
  - `articles`: one unique article (text, headline, byline, tags).
- **Where links and text come from:**
  - One API query per signing: all of the player's name variants as phrases, from 365 days before to 365 days after the transfer.
  - Every article the query returns is linked to that signing.
  - Sentences are extracted locally by name matching (accents, both apostrophe styles and the surname alone are accepted).
- **Files and fields:**

  | File | Fields |
  |---|---|
  | `signings.csv` | `signing_id, player_id, name, first_name, last_name, name_variants, date_of_birth, age_at_transfer, age_group, position, transfer_date, season, from_club_id, from_club_name, to_club_id, to_club_name, transfer_fee, market_value_in_eur` |
  | `article_player.csv` | `article_id, signing_id, player_id, player, publication_date, days_from_transfer, period (before/around/after), age_at_article, age_group_at_transfer, mentions, total_sentences, share_of_sentences, name_in_headline, n_tracked_players_in_article, is_focus_article, player_sentences, article_type, overlapping_window, mixed_age_article` |
  | `sentences.csv` | `article_id, signing_id, player, period, days_from_transfer, age_at_article, age_group_at_transfer, article_type, match_kind, sentence` |
  | `articles` | `article_id, url, publication_date, headline, byline, wordcount, tones, keywords, article_type, body_text` |

- **Collection or preprocessing choices:**
  - **Signings:**
    - destination club played in the Premier League that season (from `games`);
    - seasons 2012/13–2024/25;
    - market value ≥ €2m;
    - age 18–36 in completed years, grouped young 18–24 / middle 25–29 / old 30–36;
    - same-club moves and loan returns excluded.
  - **Loan returns:** the previous move went the opposite way within 730 days, unless a fee was paid (deviation from the spec, keeps 74 real signings).
  - **Periods:** before < −7 days, around ±7 days, after > 7 days.
  - **Article type** from Guardian tone tags (liveblog, matchreport, interview, comment, features, blog, news, other).
  - **Same-player dedup:** an article linked to two signings of the same player is kept once, for the nearer transfer.
  - **Numbers:** 1,332 signings (797 / 447 / 88), 125,231 article–signing links, 3 signings with no articles.
  - See `decisions.md` for name handling, checks and limitations.

## Contents

| Path | What it is |
|---|---|
| `pipeline/get_guardian_articles.py` | Data pipeline: `select` → `fetch` → `build` → `validate` |
| `pipeline/pipeline_spec.yaml` | The specification the pipeline implements (v2) |
| `pipeline/tests/test_pipeline.py` | Fake-data tests (49 checks, no real API calls) |
| `sentiment/a1_sentiment.py` | Sentiment before vs after the transfer: VADER, Bing lexicon, RoBERTa |
| `sentiment/a1_compare_methods.py` | Compares the sentiment methods (results table, sentence-level agreement) |
| `sentiment/opinion_lexicon/` | Bing Liu opinion lexicon (Hu & Liu 2004), see its README |
| `data/signings.csv` | The 1,332 selected signings (output of `select`) |
| `data/check_zero_articles.csv` | Signings with no Guardian articles (3, all genuine) |
| `data/check_focus_sample_labelled.csv` | 100 article–player links, hand-labelled y / n / x (see `decisions.md`) |
| `decisions.md` | Choices, checks and known limitations |

## Not in the repo (and why)

| File | Size | Reason |
|---|---|---|
| `guardian_cache_v2/` | ~1.7 GB | Raw API responses with full article text |
| `articles.csv` | ~326 MB | Full article text; over GitHub's 100 MB limit |
| `sentences.csv` | ~109 MB | Article sentences; over the limit |
| `article_player.csv` | ~88 MB | Contains article excerpts |
| Transfermarkt CSVs | | Download from Kaggle (dcaribou, *Football Data from Transfermarkt*) |

The Guardian's free developer key doesn't allow republishing article text, so it stays out
of git. Everything can be rebuilt with the scripts and your own key.

## How to run

```
pip install -r requirements.txt
```

The pipeline reads `transfers`, `players` and `games` (.csv or .csv.gz) from `pipeline/data/`. The same Kaggle files are already in this repo under `pnas_report/data/transfermarkt-datasets/`; copy them into `pipeline/data/`. If that copy is a different Kaggle version than the one used here, `select` may give slightly different counts (1,332 signings with the 2026 version used on 4–7 Nov).
Then, from `pipeline/`, in PowerShell:

```
$env:GUARDIAN_API_KEY = "your-key"        # never write the key into a file or notebook
python get_guardian_articles.py select     # -> signings.csv
python get_guardian_articles.py fetch      # ~1,500 API calls; stops cleanly at the daily limit, rerun to continue
python get_guardian_articles.py build      # -> articles, article_player.csv, sentences.csv
python get_guardian_articles.py validate   # checks + check_focus_sample.csv
```

Sentiment, from `sentiment/` (expects a folder with `sentences.csv` and `article_player.csv`):

```
python a1_sentiment.py <data folder> --scorer vader   --signings <signings.csv>
python a1_sentiment.py <data folder> --scorer bing    --signings <signings.csv>
python a1_sentiment.py <data folder> --scorer roberta --signings <signings.csv>   # needs transformers + torch
python a1_compare_methods.py <data folder>
```

Run heavy steps (`build`, RoBERTa) from a terminal, not a notebook: the full build crashed
VS Code out of memory once.

Tests: `python pipeline/tests/test_pipeline.py`
