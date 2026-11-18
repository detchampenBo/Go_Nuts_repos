# File guide: `pnas_report/` (text part, plus where the network part goes)

This guide lists every folder and file the text part adds to `pnas_report/`, in the order you'd usually need them. It covers upload package v2 and the plotting kit (both from 18 Nov 2026). Paths are relative to `pnas_report/`.

**Quick start**
- **To read the results:** `notes/findings.md`, then `paper/main.pdf`.
- **To make or restyle a figure:** `figures/plotting/README.md`.
- **To count articles or build something new from the coverage:** `data/dataset_nlp/data/article_player_notext.csv.gz`, one row per article × signing.
- **To check a number in the paper:** find it in `data/dataset_nlp/results/` (the table below says which CSV holds what).
- **To rerun the analysis from scratch:** `data/dataset_nlp/README.md` ("how to run"). This needs a Guardian API key and about 1.7 GB of downloads; see "Not in the repo" at the end.

**Words used throughout**
- **Signing:** one player joining a Premier League club on one date. `signing_id` = `<player_id>_<YYYYMMDD>`.
- **30+ / under 30:** age at the transfer. The older grouping, used in a few files, is young 18–24 / middle 25–29 / old 30–36, and "old" is the same as 30+.
- **Before / around / after:** articles from −365 to −8 days, −7 to +7 days, and +8 to +365 days from the transfer. "Around" is left out of the tests.
- **Main sample:** the 820 signings (67 aged 30+, 753 under 30) that have at least 5 scored sentences both before and after the move. Liveblogs and match reports are not counted.
- **Models:** `roberta` (main instrument), `vader`, `bing`, and `bing_nofootball` (Bing without 21 football words).
- **H1:** network part (teammates). **H2:** does the tone change across the move differ for 30+ signings? **H2b:** at the same fame and price, is the tone toward 30+ signings lower?

---

## Top level

| Path | What it is |
|---|---|
| `FILE_GUIDE.md` | This file. The same guide is also in `FILE_GUIDE.yaml` (machine-readable) and `FILE_GUIDE.pdf` / `FILE_GUIDE.tex` (printable). |
| `notes/` | The research question and the findings, written up in plain text. |
| `data/dataset_graph/` | Network data (teammates; not part of this upload). |
| `data/dataset_nlp/` | Everything for the text part: pipeline, sentiment scripts, labelled samples, results. |
| `figures/` | Finished figures, plus `plotting/` for the group's own versions. |
| `paper/` | PNAS LaTeX source and the compiled draft. |

## `notes/`

| File | Contents |
|---|---|
| `question.md` | The research question as adopted. Covers H1, H2 and H2b, framed as access (H1) versus reception (H2, H2b), with a worked example of how H2 and H2b differ, the null models and the support rules. |
| `findings.md` | Every text-part result with its number, P value and source CSV: validation (B8, B9), H2, H2b with controls, and coverage volume. H1 is left blank for the teammates. |

## `data/dataset_nlp/` (text part)

| Path | Contents |
|---|---|
| `README.md` | Dataset description in the course template: sources, collection date, what one row is, the fields of every file (including those not uploaded), selection rules, and how to run. |
| `decisions.md` | Every choice and check with its reason: selection and loan returns, name handling and the wrong-person fix (B5), the focus rule and both focus checks, the sentiment check, known limitations. |
| `requirements.txt` | Python packages (pandas, numpy, requests, matplotlib, vaderSentiment; transformers and torch only for RoBERTa). |
| `.gitignore` | Keeps the large and text-bearing files out of git (see the last section). It ignores `data/*.csv.gz` (the Transfermarkt downloads) but makes an exception for `data/article_player_notext.csv.gz`. |

### `data/dataset_nlp/pipeline/`: getting the data

| File | Contents |
|---|---|
| `get_guardian_articles.py` | The data pipeline (B5 version, md5 `2e10c82c…`) with four steps: `select` picks the 1,332 signings from Transfermarkt, `fetch` queries the Guardian API once per signing (key read from `$env:GUARDIAN_API_KEY`, never stored), `build` writes the article–signing links and the sentences naming the player, and `validate` runs the checks and draws the labelling samples. |
| `pipeline_spec.yaml` | The spec the pipeline implements: selection, periods, name rules, focus rule, outputs and analysis plan. |
| `tests/test_pipeline.py` | 66 checks (name matching, who-is-who rules, periods, loan returns, never overwriting a labelled sample). Run with `python -m pytest`. |

### `data/dataset_nlp/sentiment/`: scoring and analysis
Scripts take the Project folder and an output folder as arguments (see each docstring). They read the large local files (`sentences.csv`, `article_player.csv`, `a1_*_scores.csv`), so they need a full local build.

| Script | What it does | Writes (in `results/` or `figures/`) |
|---|---|---|
| `a1_sentiment.py` | Scores every sentence with one model and averages per signing and period. Tests after − before with 5,000 period shuffles. | `a1_<model>_results.csv`, `a1_<model>_per_signing.csv` (+ the sentence scores `a1_<model>_scores.csv`, not uploaded) |
| `a1_compare_methods.py` | Puts the four models side by side and measures how often they agree, sentence by sentence. | comparison table (Pilot) |
| `a1_age30.py` | **H2:** change for 30+ vs under 30, gap tested by shuffling the 30+ label within season. Also the robustness samples. | `a1_age30_results.csv` |
| `a1_age30_arc.py` | Monthly tone arc −12…+11 months, with bootstrap bands. | `a1_age30_arc.csv` |
| `a1_age30_arc_numbers.py` | An earlier version of the arc figure with the numbers printed under the panels. It is replaced by the next script. | `a1_age30_levels_pct.csv` |
| `a1_age30_arc_sentiment.py` | The H2 arc figure as used: no bands, months at their midpoints, one legend per panel. | `figures/fig_h2_arc_sentiment.png` |
| `a1_h2b_controls.py` | **H2b:** level gap before and after the move. It refits an OLS 30+ coefficient (season dummies plus controls for fame, market value, article type, quotes, seasons 2016+ and position) on each of 5,000 within-season shuffles. | `a1_h2b_controls.csv`, `a1_h2b_signings.csv` |
| `a1_coverage_age.py` | Coverage volume: how many articles 30+ signings get compared with under-30 signings, before and after, with and without market value. | `a1_coverage_age.csv` |
| `a1_h2b_arc.py` | Monthly arc with tone adjusted for the H2b controls. Checks that the gaps equal the tested coefficients. | `a1_h2b_arc.csv`, `figures/fig_h2b_arc_controls.png` |
| `a1_h2b_arc_paper.py` | Paper-size PDF of the adjusted arc (Fig. 2). | `paper/figures/fig_h2b_arc_paper.pdf` |
| `a1_h2b_figure.py` | Dot-and-interval figure: tone gaps and coverage ratio (Fig. 3). | `figures/fig_h2b_tone_coverage.png` (+ paper PDF) |
| `b8_focus.py` | Scores the focus rule against focus check 2 (weighted by stratum) and re-checks check 1. | `b8_focus_rule_scores.csv` |
| `b9_score.py` | Scores the four models against the 200 hand-labelled sentences: Spearman ρ, accuracy, sign accuracy, the age-bias check. | `b9_model_scores.csv`, `b9_confusion.csv`, `b9_labels_joined.csv` |
| `b10_signing_tone.py` | Builds one tidy row per signing: tone for the four models, coverage and controls. | `signing_tone.csv` |
| `opinion_lexicon/` | The Bing (Hu & Liu) word lists: `positive-words.txt`, `negative-words.txt`, and their README with the citation. | |

### `data/dataset_nlp/data/`: inputs, the link table and hand-labelled samples
None of these files contains article text: the labelled samples had their sentence and text columns removed. The labels can be matched back to a local build through `article_id` and `sentence_row`.

| File | Rows | Contents |
|---|---|---|
| `signings.csv` | 1,332 | The signings: player, date of birth, age at transfer, age group, position, date, season, from and to clubs, fee, market value. **The table the network part can join on** (`player_id`, club ids, season). |
| `article_player_notext.csv.gz` | 125,231 | **All article–signing links** (`article_player.csv` without its `player_sentences` text column; 4.3 MB gzipped, pandas reads it directly with `pd.read_csv(...)`). One row per article × signing: `article_id` (Guardian path), `signing_id`, `player_id`, `player`, `publication_date`, `days_from_transfer`, `period`, `age_at_article`, `age_group_at_transfer`, `mentions`, `total_sentences`, `share_of_sentences`, `name_in_headline`, `n_tracked_players_in_article`, `is_focus_article`, `focus_old_rule`, `name_clash`, `article_type`, `overlapping_window`, `mixed_age_article`. Use it to recount articles per signing or period, filter by article type, or build a co-mention network (players linked through a shared `article_id`). The article itself is at `https://www.theguardian.com/<article_id>`. |
| `check_zero_articles.csv` | 3 | The 3 signings with no Guardian articles (Tedić, Bustos, Carreras), each loaned out straight away. |
| `check_focus_sample_labelled.csv` | 100 | Focus check 1, a random sample of article–signing links. Label `truly_about_player`: y = main subject, n = passing mention, x = wrong person. |
| `check_focus_sample_2_labelled.csv` | 100 | Focus check 2 (B8): 50 focus and 50 non-focus links, no liveblogs, no overlap with check 1. 99 of the 100 are labelled. |
| `check_sentiment_sample_200_labelled.csv` | 200 | Sentiment check (B9): 100 sentences before and 100 after the move, labelled blind with `tone` (pos / neu / neg / x) and a `note` tag (contrast, quote, passing mention, unsure…). |

### `data/dataset_nlp/results/`: every number in the paper
All the derived numbers are small CSVs. Start with `PLOTTING.md`, which gives the columns of the files the figures use.

| File | Rows | What it holds | Used for |
|---|---|---|---|
| `PLOTTING.md` | | Which CSV feeds which figure, column meanings, colours | the figures |
| `signing_tone.csv` | 1,332 | One row per signing: tone before, after and change for the four models (filled for the 820 main-sample signings), article counts, market value, position, age | **the easiest file to start from** |
| `a1_<model>_results.csv` (×4) | 28 | After − before by sample (all, age groups, focus-only, article types, …): mean, 95% CI, median, share more positive, permutation P | the overall tone-change table |
| `a1_<model>_per_signing.csv` (×4) | 820 | Per signing: mean tone before and after, sentence and article counts, difference | input to the H2 tests |
| `a1_age30_results.csv` | 16 | H2: change for under 30 and for 30+, the gap, within-season P (four models × four samples) | H2 result |
| `a1_age30_levels.csv` | 12 | Gap in level before, after and in change, without controls (the first H2b test) | H2b "no controls" row |
| `a1_age30_levels_pct.csv` | 4 | The same gaps expressed as % of the under-30 level (descriptive only) | old arc legends |
| `a1_age30_mde.csv` | 8 | Smallest gap detectable at 80% power (67 vs 753 and 67 vs 67) | the H2 limitation |
| `a1_age30_arc.csv` | 96 | Raw monthly arc, RoBERTa and VADER: mean, band, smoothed | `fig_h2_arc_sentiment.png` |
| `a1_h2b_controls.csv` | 132 | H2b gap for each model × control spec × period: n, gap, CI, P | **H2b result**, Fig. 3 |
| `a1_h2b_signings.csv` | 820 | Per signing: RoBERTa and VADER level before and after, plus the controls | reruns of H2b |
| `a1_h2b_arc.csv` | 192 | Adjusted monthly arc, four models | Fig. 2 |
| `a1_coverage_age.csv` | 20 | Coverage ratio 30+ / under 30 by period and spec, with CI and P | coverage result, Fig. 3C |
| `b8_focus_rule_scores.csv` | 5 | Precision and recall of five focus rules on check 2 (weighted) and check 1 | focus-rule decision |
| `b9_model_scores.csv` | 72 | Each model's score on the 200 sentences, by subset (all, without unsure, 30+, under 30, by tag, before/after) | Table 1 (validation) |
| `b9_confusion.csv` | 36 | Human label × model class counts | validation |
| `b9_labels_joined.csv` | 200 | Labels, cleaned tags and the four model scores per labelled sentence (no text) | validation reruns |

## `figures/`

| Path | Contents |
|---|---|
| `README.md` | Table of the figures, what each shows, and which script made it. |
| `fig_h2_arc_sentiment.png` | H2: raw monthly tone, 30+ vs under 30, four models. |
| `fig_h2b_arc_controls.png` | H2b: the same arcs with tone adjusted for the controls. The gap between the lines is the tested gap. |
| `fig_h2b_tone_coverage.png` | H2b plus coverage: tone gaps without and with controls, and the coverage ratio. |
| `plotting/` | **Kit for the group to restyle the figures.** It runs with no arguments and needs only pandas and matplotlib. |

### `figures/plotting/`

| Path | Contents |
|---|---|
| `README.md` | How to run the scripts, a file table, the conventions (colours, month midpoints, what the gaps mean). |
| `PLOTTING.md` | The same column guide as `results/PLOTTING.md`, plus a note on the 4-model arc file. |
| `plot_h2_arc.py` | Raw arcs, four models. |
| `plot_h2b_arc.py` | Adjusted arcs (= paper Fig. 2). |
| `plot_h2b_gaps_coverage.py` | Gaps and coverage (= paper Fig. 3). |
| `data/` | Copies of the seven CSVs the scripts read: `a1_h2_arc_4models.csv` (new, the raw arc for all four models), `a1_h2b_arc.csv`, `a1_h2b_controls.csv`, `a1_coverage_age.csv`, `signing_tone.csv`, `b9_model_scores.csv`, `b9_confusion.csv`. |
| `make_data/export_h2_arc_4models.py` | How `a1_h2_arc_4models.csv` was made: the original arc functions with the same seed. It needs the local build. |
| `out/` | Reference renders (`.pdf` and 300-dpi `.png`) of the three figures. Each script writes here, so compare a restyled version against these. |

## `paper/`

| File | Contents |
|---|---|
| `README.md` | What each file is and how to compile it. |
| `main.tex` | The draft. The text part is written in full and the H1 parts are red `[TODO]` placeholders. The Discussion has two H1 tie-in paragraphs, marked in red: keep the one that matches H1. |
| `main.pdf` | Compiled draft: 5 pages with both tie-in variants (limit 6 including references). |
| `references.bib` | References: VADER, Bing, RoBERTa/TweetEval/TimeLMs, Reagan arcs, Jurafsky & Martin, Phipson & Smyth, Guardian API, the Transfermarkt Kaggle dataset. Add the network references here. |
| `figures/fig_h2b_arc_paper.pdf`, `figures/fig_h2b_tone_coverage.pdf` | Fig. 2 and Fig. 3 at 17.8 cm. The H1 figure goes here too. |
| `pnas-new.cls`, `pnasresearcharticle.sty`, `pnas-new.bst`, `jabbrv*.sty/.ldf`, `PNAS_Logo.pdf` | Template files, unchanged. |

Compile with `pdflatex main && bibtex main && pdflatex main && pdflatex main`, or open the folder in Overleaf.

---

## Not in the repo, and why
These files stay on the laptop in the Project folder. `.gitignore` keeps them out of git.

| File (laptop) | Size | Why it is left out |
|---|---|---|
| `guardian_cache_v2/` (and the older `guardian_cache/`) | ~1.7 GB | The raw API responses with full article bodies. Too large for git, and the Guardian's free developer key does not allow republishing article content. |
| `articles.csv` | 326 MB | One row per article with `body_text`: full article text, so both reasons apply. |
| `sentences.csv` | 106 MB | Every sentence naming a player. These are verbatim Guardian sentences, so republishing them is the same problem as the article text. It is also above GitHub's 100 MB hard limit per file. |
| `article_player.csv` | 87 MB | The 125,231 article–signing links. Its `player_sentences` column holds the sentence text, and the file is above the 25 MB limit for uploads through the GitHub website. **Everything except that column is in the repo** as `data/article_player_notext.csv.gz` (4.3 MB). |
| `a1_<model>_scores.csv` (×4) | ~23 MB each | One score per sentence. There is no text, but the files are large, and on their own they only make sense next to `sentences.csv`. |
| `a1_cache_…roberta….csv` | 9 MB | The RoBERTa score cache, a speed-up for reruns only. It is keyed by sentence text. |
| `data/*.csv.gz` (Transfermarkt) | | Third-party data, downloadable from Kaggle (dcaribou, *Football Data from Transfermarkt*). |
| `Pilot/` | | Frozen partial build from 4 Nov, kept only for history. |

Everything a reader needs to **check** the paper is in the repo: every number is in `results/`, the per-signing tables are there, and the labelled samples can be matched through their ids. To **rebuild** from scratch, you need a free Guardian key (set `$env:GUARDIAN_API_KEY`, never write it in a file) and the Kaggle data, then run `get_guardian_articles.py select → fetch → build → validate` and the sentiment scripts. Those steps recreate every file in this table.
