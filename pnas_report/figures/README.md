# Figures

Save candidate figures here. The week 8 brief recommends two or three figures that carry the story, with labeled axes and captions that explain the comparison and the result.

| Figure | Part | What it shows | Made by |
|---|---|---|---|
| `transfer_graphs.png` | network | (teammates) | |
| `fig_h2_arc_sentiment.png` | text, H2 | Monthly sentence tone from 12 months before to 12 after the transfer, 30+ vs under 30, four sentiment models, raw (no controls) | `data/dataset_nlp/sentiment/a1_age30_arc_sentiment.py` |
| `fig_h2b_arc_controls.png` | text, H2b | Same arcs with tone adjusted for fame, market value, season, article type and quotes; the gap between the lines is the tested gap (printed per panel). Paper version: `paper/figures/fig_h2b_arc_paper.pdf` | `a1_h2b_arc.py`, `a1_h2b_arc_paper.py` |
| `fig_h2b_tone_coverage.png` | text, H2b + coverage | Tone gap 30+ minus under 30 before/after the move, without and with controls; coverage ratio 30+ / under 30. Paper version: `paper/figures/fig_h2b_tone_coverage.pdf` | `a1_h2b_figure.py` |
