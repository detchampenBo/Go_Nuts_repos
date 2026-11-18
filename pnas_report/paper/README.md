# Paper source

The week 8 brief requires a PDF of at most six pages including references, with Abstract, Significance Statement, Introduction, Results, Discussion, Methods, References, and specific author contributions.

Draft started 18 Nov 2026 in the official PNAS template (the zip in this folder).

| File | What |
|---|---|
| `main.tex` | The draft. Text part (Guardian coverage: validation, H2, H2b, coverage volume) written from the numbers in `data/dataset_nlp/results/`. Red `[TODO: ...]` marks what is still missing: H1 result, figure and methods, authors, contributions, links, acknowledgements. |
| `references.bib` | References. Add the network references here. |
| `main.pdf` | Compiled draft (4 pages, leaving about 2 for H1). |
| `figures/` | Paper-size figures (17.8 cm wide PDFs). Put the H1 figure here and replace the placeholder box in `main.tex` (`\label{fig:h1}`). |
| `pnas-new.cls`, `pnasresearcharticle.sty`, `pnas-new.bst`, `jabbrv*`, `PNAS_Logo.pdf` | Unchanged from the template zip. |

Compile: `pdflatex main && bibtex main && pdflatex main && pdflatex main`, or upload this folder to Overleaf with `main.tex` as the main file. `main.md` is the template's own sample text and isn't used.
