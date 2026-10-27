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
18–45-word sentence from the story sections (biography, powers), skipping
publication boilerplate ("Created by … first appeared in …", which describes the
comic and is shared word for word by many pages), replaces the title with
"someone", and squeezes it to 30, 20, 10, 5, 3, 2 and 1 words by three rules: keep
the first N words; keep the N highest-weight TF-IDF words; or ban the five
highest-weight words and keep the rarest N of the rest. It records the source
article's rank under TF-IDF and under MiniLM best-60-word-passage retrieval, and
writes median, quartiles and top-5 share to `dist/data/squeeze-evidence.json`. A
zero-overlap keyword query counts as rank 303.

The headline finding answers "when the message gets lost, where does it end up?".
When a squeeze sends search to the wrong hero, the script checks whether the two pages
link to each other in the course's Wikipedia network. With title masking alone, 28%
of keyword misses at 10 words are neighbours. Applying a capitalisation filter before
taking the first 10 remaining words takes that to 7%. The filter changes both the
query and which articles are missed, so this is not an isolated test of names.
At 5 words after filtering, 26 of 259 meaning-search misses (10.0%) are linked to
the source; keyword search has 12 of 175 (6.9%). Across all distinct article pairs,
3.1% are linked. That simple reference does not account for source degree or frequently
guessed destinations, and the methods fail on different articles. These shares do not
establish that one method makes better mistakes. The findings page provides all 26
linked cases, with five initially shown and a button to expand them in normal page flow.
On mobile, each case stacks its labelled fields without nested table scrolling.

The findings page then pushes the same question further (5 words after capitalisation
filtering, meaning search, unless stated otherwise):

- Link hops: 10% of wrong guesses are directly linked against 3.1% of all pairs.
  Exactly two hops: 35.1% against 30.5%. Same Louvain community (seed 42,
  25 communities): 16.6% against 12.3%. Relative enrichment is smaller beyond a
  direct link, not absent. Four-plus hops includes unreachable pairs.
- Retrieval unit: directly linked wrong guesses fall from 10.0% with 60-word
  passages (259 misses) to 7.0% with 180-word passages (284) and 3.4% with
  whole-page averages (291). This is consistent with dilution of local context,
  but maximum versus average pooling and changing miss sets are also involved.
- Entity-filter sensitivity: spaCy's detected-entity removal gives 6.8%
  (2.2× the all-pairs reference). Neither filter guarantees name removal:
  `(Hulk),` survives the capitalisation heuristic. spaCy removes all detected
  entity types and spaces punctuation tokens, so it changes the query in other
  ways too. Neither run resolves aliases. `prepare_squeeze.py` needs spaCy's
  `en_core_web_sm` and networkx.
- Rare words: 42% of indexed terms occur on one article only. A table compares
  first-word, highest-weight and taboo deletion at 3 words, plus one highest-weight
  word, using the stored top-five results. Selecting TF-IDF words favours that
  method by construction; deletion is not a benchmark of paraphrase retrieval.
- Role reversal: four selectable, hand-written sentence pairs display stored
  MiniLM cosines (0.984–0.993). Reversing who did what can leave vectors very
  similar. The page also reports the fixed-seed word-shuffle check across the corpus.
  These are stress tests of this encoder, not claims about every contextual model.
- Article length: at first 10 words with title masking alone, wrong meaning results
  have a median length of 3,568 words versus 800 for keyword results and 1,234 for
  the corpus. Thirty-three percent of meaning misses land on the longest tenth.
  More passages offer more opportunities for a large maximum score, but topic
  breadth is another possible explanation. Repeated destinations count repeatedly.

Further detail in the evidence file and reveal chart:

- Deleting words favours keyword search: with only the single rarest word, TF-IDF
  ranks the source in the top five for 98% of articles, MiniLM for 48%;
  in taboo mode at three words, 86% against 37%. The robot never paraphrases;
  the worked example is a human paraphrase in which keyword search slips
  (#2 → #8 → #13) while meaning search holds (#1 → #1 → #7).
- Fingerprints: 42% of the 25,882 indexed words occur on exactly one page; all 303
  pages have at least one (median 21); 44% are name-like by a capitalisation heuristic,
  not verified entity labels.
- Favourite wrong answers (first-N rule): keyword search's wrong first results are
  short pages (at 1 word, median 534 words, 46% on the shortest tenth), meaning
  search's are long pages (at 10 words, median 3,568 words against 1,234 for all
  pages; 33% on the longest tenth).
- A bug found by reading the evidence: in an earlier build, 138 of 289 one-word
  meaning misses went to Cable through a passage consisting of the word "traveler.".
  The splitter cut over-long sentences at the budget, leaving 1–3-word remainders;
  seven of them won 61% of one-word misses. `prepare_data.py` now merges passages
  under 8 words into the previous passage (or re-splits the pair into balanced
  halves), so no passage is shorter than 8 words.
- Network drift: at 10 words, 28% of keyword and 22% of meaning misses are hyperlink
  neighbours of the source, against 3.1% for a random pair; at 3 words, 7% and 8%.

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
