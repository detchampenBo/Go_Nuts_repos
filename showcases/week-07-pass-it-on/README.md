# Pass it on

A drawing game for Week 7. A real corpus passage becomes a sketch, and a CLIP
vision model tries to recover its source directly from the pixels. An optional
two-person route passes the drawing to a friend, then compares TF-IDF and MiniLM
retrieval on their description. Worked examples use authored drawings and live
inference; they are labeled as examples.

Serve this repository with `python3 -m http.server 8047` and open
`http://localhost:8047/showcases/week-07-pass-it-on/dist/`.
The complete static application is in `dist/`, suitable for GitHub Pages or Sites.
No build, API key, backend, external CDN, or multiplayer service is required.
The human route is hot-seat play: the original passage leaves the DOM before handoff, but this
is a friendly game, not a security boundary against developer tools.

## Behavior

- Five checked passage prompts from the frozen course Wikipedia snapshot.
- Five-minute drawing round with pointer/touch/stylus input, five colors, brush
  widths, eraser, undo, and clear. An empty drawing cannot be submitted.
- "Let the model guess" reads the drawing pixels with CLIP and ranks all 303
  articles. "Pass to a human instead" keeps the original telephone route.
- A handoff screen hides the original; the description round has five minutes and
  a configurable 30-, 10-, or 3-word budget. Overtime permits completing an empty
  description or trimming one that exceeds the budget.
- The reveal compares original-article rank and top-five results. Click results
  for text evidence and lexical contributions. Change only the retrieval unit
  between whole-page means and 180-/60-word passage maxima. Switch back to the
  original drawing prompt to inspect retrieval without the human handoffs.
- Save the drawing, messages, attribution, and current top-five rankings as JSON.
  Everything stays in memory until the player explicitly downloads it.

## Drawing-only recognition

`vision-worker.js` runs the quantized CLIP ViT-B/32 image encoder in a Web Worker.
Its per-guess input contains only the drawing image, a request ID, and a message
type. It receives neither the target article ID nor the secret passage as a hint.
The drawing is white-padded to a square, resized to 224 × 224, and processed into
a normalized 512-dimensional image embedding. The reveal reconstructs the actual
model input pixels and optionally overlays its 7 × 7 image-patch grid.

`prepare_vision.py` freezes exactly three text prototypes per article before any
drawings are seen: an article-name prompt and two early source sentences selected
with a fixed visual-word rule from the first 800 words. The matching quantized
CLIP text encoder embeds all 909 prototypes with a 77-token limit. Its weights
and tokenizer are used only during preparation; they are not needed at runtime.
Each article gets its maximum candidate cosine. These are corpus-restricted
guesses, not generated captions, probabilities, or general recognition accuracy.

The vision and text encoders share the pinned model revision
`d15189d7028b43f1d3e65039190477f6af591c2a`. The image encoder's 89,117,001 bytes
are distributed in five static parts, each at most 20 MiB. The worker verifies
each part's SHA-256 before reassembling the exact model. The build remains a
static site; drawings never leave the browser. The 512D image/text space is
separate from MiniLM's 384D text space. The reveal inspects all 512 actual
coordinate products for a selected article's winning prototype.

Rebuild with `.venv/bin/python showcases/week-07-pass-it-on/prepare_vision.py`.
It needs NumPy, Transformers, and ONNX Runtime. It downloads pinned ONNX weights
and tokenizer files into `/tmp/pass-it-on-clip-analysis` for preparation. CLIP's
MIT license is in `dist/models/clip-vit-base-patch32/LICENSE`.

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
not proof of semantic preservation. Drawings are interpreted by humans; the
model never reads the image. This is a case-study tool, not an accuracy benchmark.

`download_models.py` vendors the model, pinned runtime, fonts, and licenses.
Run with `python3 showcases/week-07-pass-it-on/download_models.py` if rebuilding
assets. About 161 MB is available across the complete app; representations load
on demand. The image model warms in a worker when a game starts; the first load
reads about 89 MB. The optional text route uses the smaller MiniLM model.

## Visual direction

A cobalt drawing table, yellow source paper, white sketch paper, and pink
description slips. Bricolage Grotesque carries the playful headings; Caveat
carries handwritten notes. Each folded paper represents one actual handoff.
The source text and players' drawings supply the visual material. The reveal
unfolds the chain and keeps the analytical evidence directly accessible.

Wikipedia text: CC BY-SA 4.0, with per-article links and unedited prompt sources
in the reveal. Font and library licenses are in `dist/vendor/`; the model's
Apache 2.0 license is in `dist/models/LICENSE`.
