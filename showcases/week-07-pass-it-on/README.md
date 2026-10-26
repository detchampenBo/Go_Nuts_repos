# Pass it on

A word-squeezing game for Week 7. A player reads a real corpus passage and squeezes
it into 30 words, then 10, then 3. After every edit, TF-IDF and MiniLM retrieval
rank all 303 articles live, so the player sees which cut loses the source article.
The reveal draws the round over the same squeeze run automatically on every
article. The worked example is an authored round with live rankings; it is labeled.

Serve this repository with `python3 -m http.server 8047` and open
`http://localhost:8047/showcases/week-07-pass-it-on/dist/`.
The complete static application is in `dist/`, suitable for GitHub Pages or Sites.
No build, API key, backend, external CDN, or multiplayer service is required.

## Behavior

- Five checked passage prompts from the frozen course Wikipedia snapshot.
- Three squeeze rounds: 30, 10 and 3 words. Each round starts from the previous
  round's text. The source passage stays visible.
- Live ranks for both searches (debounced), with the previous round's rank for
  comparison. A keyword query with no indexed word in common shows "—", not a tied rank.
- Word chips show each word's share of the source article's TF-IDF score, with its
  IDF on hover. Stop words and words outside the vocabulary are marked as ignored.
- Taboo mode bans the passage's five highest-weight TF-IDF query terms; a round
  cannot be locked in while it uses one.
- The reveal shows the four slips with their ranks, the corpus-wide evidence chart,
  and the original top-five results. Switch the searched text between the 3-, 10-
  and 30-word versions and the original passage; change the retrieval unit between
  whole-page means and 180-/60-word passage maxima.
- Save the squeeze, ranks, attribution and current top-five rankings as JSON.
  Everything stays in memory until the player explicitly downloads it.

## Corpus-wide evidence

`prepare_squeeze.py` reads only `dist/data`, so it uses the same vocabulary, IDF
and stored passage vectors as the browser. For each article it takes the first
sentence of 18–45 words, replaces the title with "someone", and squeezes it to 30,
20, 10, 5, 3, 2 and 1 words by three rules: keep the first N words; keep the N
highest-weight TF-IDF words; or ban the five highest-weight words and keep the
rarest N of the rest. It records the source article's rank under TF-IDF and under
MiniLM best-60-word-passage retrieval, and writes median, quartiles and top-5 share
to `dist/data/squeeze-evidence.json`. A zero-overlap keyword query counts as rank 303.

What it found: deleting words favours keyword search. Keeping only the single
rarest word, TF-IDF still ranks the source in the top five for 91% of articles,
MiniLM for 39%. Even in taboo mode at three words it is 57% against 18%. The robot
never paraphrases, and a human player can; the worked example is a paraphrase in which
keyword search slips (#2 → #8 → #13) while meaning search holds (#1 → #1 → #7).

The same script measures the explanations shown on the "What we found" page:

- Fingerprints: 42% of the 25,882 indexed words occur on exactly one page; all 303
  pages have at least one (median 21); 44% of them are names.
- Favourite wrong answers (first-N rule): keyword search's wrong first results are
  short pages (at 1 word, 87% land on the shortest tenth; Bird-Brain alone takes 50
  of 103), meaning search's are long pages (median 6,240 words at 10 words, against
  1,234 for all pages; 49% land on the longest tenth).
- A bug found by reading the evidence: in an earlier build, 138 of 289 one-word
  meaning misses went to Cable through a passage consisting of the word "traveler.".
  The splitter cut over-long sentences at the budget, leaving 1–3-word remainders;
  seven of them won 61% of one-word misses. `prepare_data.py` now merges passages
  under 8 words into the previous passage (or re-splits the pair into balanced
  halves), so no passage is shorter than 8 words.
- Network drift: at 10 words, 15% of keyword and 20% of meaning misses are hyperlink
  neighbours of the source, against 3.1% for a random pair; at 3 words, 4% and 8%.

Rebuild with `.venv/bin/python showcases/week-07-pass-it-on/prepare_squeeze.py`
after `prepare_data.py`. Queries are embedded with the original Sentence
Transformers model; live browser ranks use the quantized copy and can differ by a few places.

## Open the machine

The reveal includes four interactive lessons implemented in `dist/mechanics.js`.
They read the current query, selected article, and real retrieval data. The game
record stays unchanged while players experiment inside a lesson.

- **Words → weights:** click to remove a term from the query. The lesson recomputes
  its normalized TF-IDF vector, article score, and rank. It exposes term counts,
  corpus document frequencies, IDF, unnormalized and normalized weights, and all
  shared-coordinate products. Bars show each term's share of the displayed score;
  numbers give its absolute contribution. Corpus IDF and article vectors stay fixed.
- **Text → vector:** compare editable messages, reversed words, role-swapped
  sentences, or two meanings of "bank". Both sparse and dense similarities are
  calculated live. The lesson displays actual WordPiece input tokens, any input
  truncation, all 384 sentence-vector coordinates, and a coordinate inspector.
  This compares sentence embeddings; it does not claim to expose token-level BERT
  representations or causal attributions for the encoder's decisions.
- **Vectors → score:** inspect the query and selected article's actual stored
  vector, normalized after quantization. The diagram preserves the pairwise angle
  in their spanned plane; it is not a projection using the first two coordinates.
  All 384 coordinate products and their sum are available. An evidence excerpt's
  "Take apart this score" button opens the matching article and lesson.
- **Passages → rank:** compare all three retrieval units for the same query,
  inspect the selected article's passages in source order, and open its actual
  winning passage. It distinguishes a normalized mean of vectors from a mean of
  scores and from maximum-passage retrieval. Maximum scoring's opportunity bias
  toward articles with more passages is stated explicitly.

Vector heatmaps show coordinate order, not semantic geography. Each row's color
intensity is scaled independently for readability; coordinate values remain
available numerically. Cosine is not calibrated confidence or meaning retained.

## Analysis and limitations

`prepare_data.py` reads `notebooks/data/marvel_pages.zip`. Run it from the repo
root using `.venv/bin/python showcases/week-07-pass-it-on/prepare_data.py`.
It requires NumPy, scikit-learn, and sentence-transformers, already available in
this workspace's environment. The MiniLM model must be cached locally.

Passages follow sentence boundaries when possible and never exceed their word
budget or the model's token limit. The 180-word representation contains 4,529
passages; the 60-word representation contains 15,145. These differ from the
course example because overlong sentences are also split and token limits are
enforced. Each passage is normalized. Page vectors average the 180-word passage
vectors and are normalized again. Passage retrieval uses each article's maximum
passage score. Texts remain aligned with vector rows through stable document IDs.

TF-IDF uses sublinear term frequency, English stop words, unigrams, scikit-learn's
smoothed IDF, ASCII word tokens of at least two characters, and L2 normalization.
The browser applies the same query transform. Zero-overlap queries show an empty
result state rather than an arbitrary ranking of tied zero scores.

Live query embeddings run locally with Transformers.js 2.17.2 and the quantized
ONNX `Xenova/all-MiniLM-L6-v2` checkpoint at revision
`751bff37182d3f1213fa05d7196b954e230abad9`. Corpus vectors were prepared with
the original Sentence Transformers encoder and quantized to signed bytes for
storage; the browser renormalizes them. Model and storage quantization introduce
small approximations. Cosines are not calibrated probabilities, and a result is
not proof of semantic preservation. This is a case-study tool, not an accuracy benchmark.

`download_models.py` vendors the model, pinned runtime, fonts, and licenses.
Run with `python3 showcases/week-07-pass-it-on/download_models.py` if rebuilding
assets. Representations load on demand; the MiniLM model warms when a game starts.

## Visual direction

A cobalt table, yellow source paper, and one slip per squeeze: white for 30
words, pink for 10, mint for 3. Bricolage Grotesque carries the playful headings;
Caveat carries handwritten notes. Pink is keyword search and blue is meaning search
throughout, from the live rank tiles to the evidence chart. The reveal lays out the
slips and keeps the analytical evidence directly accessible.

Wikipedia text: CC BY-SA 4.0, with per-article links and unedited prompt sources
in the reveal. Font and library licenses are in `dist/vendor/`; the model's
Apache 2.0 license is in `dist/models/LICENSE`.
