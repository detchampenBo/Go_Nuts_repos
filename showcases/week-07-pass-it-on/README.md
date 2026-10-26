# Pass it on

A two-person, same-device drawing telephone game for Week 7. A real corpus passage
becomes a drawing, then a short description. TF-IDF and MiniLM search all 303
articles to recover the source. A solo worked example uses authored inputs and
live retrieval; it is labeled as an example.

Serve this repository with `python3 -m http.server 8047` and open
`http://localhost:8047/showcases/week-07-pass-it-on/dist/`.
The complete static application is in `dist/`, suitable for GitHub Pages or Sites.
No build, API key, backend, external CDN, or multiplayer service is required.
It is hot-seat play: the original passage leaves the DOM before handoff, but this
is a friendly game, not a security boundary against developer tools.

## Behavior

- Five checked passage prompts from the frozen course Wikipedia snapshot.
- 90-second drawing round with pointer/touch/stylus input, five colors, brush
  widths, eraser, undo, and clear. An empty drawing cannot be submitted.
- A handoff screen hides the original; the description round has 60 seconds and
  a configurable 30-, 10-, or 3-word budget. Overtime permits completing an empty
  description or trimming one that exceeds the budget.
- The reveal compares original-article rank and top-five results. Click results
  for text evidence and lexical contributions. Change only the retrieval unit
  between whole-page means and 180-/60-word passage maxima. Switch back to the
  original drawing prompt to inspect retrieval without the human handoffs.
- Save the drawing, messages, attribution, and current top-five rankings as JSON.
  Everything stays in memory until the player explicitly downloads it.

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
assets. About 66 MB is served across the complete app; representations load on
demand, and the model starts warming when the game begins.

## Visual direction

A cobalt drawing table, yellow source paper, white sketch paper, and pink
description slips. Bricolage Grotesque carries the playful headings; Caveat
carries handwritten notes. Each folded paper represents one actual handoff.
The source text and players' drawings supply the visual material. The reveal
unfolds the chain and keeps the analytical evidence directly accessible.

Wikipedia text: CC BY-SA 4.0, with per-article links and unedited prompt sources
in the reveal. Font and library licenses are in `dist/vendor/`; the model's
Apache 2.0 license is in `dist/models/LICENSE`.
