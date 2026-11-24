# Issue 09 physical layout review, 24 November 2026

## Completed rotation

The user specified `pnas_report/output/backbone_h1_findings/combined.pdf`, then explicitly selected **90 degrees counterclockwise**. The entire PDF page is now rotated, not just the network drawing. Current `/Rotate` is 270; display dimensions are 4.000 by 7.008 inches. Original vector content streams and extracted text are unchanged; media/crop boxes match within 0.000001 PDF point.

- [Rotated Figure 1](../../output/backbone_h1_findings/combined.pdf)
- [Preserved original orientation](../../output/backbone_h1_findings/combined_before_rotation_2026-11-24.pdf)
- [Rotation checks and hashes](../../output/backbone_h1_findings/pdf_rotation_verification.json)
- [Inspected rotated preview](../../output/backbone_h1_findings/qa/combined_rotated_90ccw.png)

PNG/SVG companions and standalone panels retain their previous orientation. The original `verification.json` describes the pre-rotation exports; use the separate rotation record for the current combined PDF. No analytical or figure producer was rerun. Running the original producer again would overwrite this PDF rotation.

## Caption-inclusive proof

**Layout accepted, 24 November 2026.** The user agreed to the layout and specified that plot captions must be LaTeX figure captions, not content embedded in the plot PDFs. The proof is only a placement/size demonstration. Both source plot PDFs remain plot-only. The approved text is now in native `\caption{...}` commands in [figure_floats.tex](../figure_floats.tex), using a side caption for Figure 1 and a caption below Figure 2. These floats still require template compilation during assembly.

- [Two-page physical-size proof](../../output/pdf/issue09_layout/figure_caption_fit.pdf)
- [Page 1 preview](../../output/pdf/issue09_layout/page_1.png)
- [Page 2 preview](../../output/pdf/issue09_layout/page_2.png)
- [Measurements](../../output/pdf/issue09_layout/layout_measurements.json)
- [Reproduction script](issue09_layout_check.py): `python pnas_report/paper_simple/scratch/issue09_layout_check.py` from the repository root.

Both proof pages were rendered and visually inspected. Page 1 uses the rotated Figure 1 at its native 4 by 7.008-inch display size, with the complete approved caption alongside it. Page 2 uses Figure 2 at its current 17.8 cm by 5-inch size, its complete approved caption, and the complete approved Table 1 caption, values and note. No approved prose was shortened. Plots remain vector graphics at their original physical scale; their original minimum 8-point text is preserved. Caption text follows the supplied class's 7 TeX-point/9-point-leading definition, with Arial substituted for Helvetica.

The proof uses the supplied template's 512 TeX-point full width (510.09 PDF points), 585 by 782.64 PDF-point page size, and an approximately 700 PDF-point body envelope checked against the supplied compiled example. Figure 1's side-caption layout is accepted, with the caption typeset by LaTeX outside the plot PDF. It avoids expanding the rotated plot to full width, which would make the plot alone about 12.4 inches tall.

| Block | Approximate body-page fraction |
| --- | ---: |
| Figure 1 with side caption | 0.73 |
| Figure 2 with caption | 0.69 |
| Table 1 with caption/note | 0.22 |
| Total graphic material | 1.64 |

The original allowance was 1.05 graphic pages plus 4.50 text/front-matter/reference pages, with 0.45 pages unallocated. The measured graphics exceed that allowance by about 0.59 pages. After using the 0.45-page margin, the unchanged 4.50-page text allowance gives approximately **6.14 pages**, before exact float placement and spacing.

## Confirmed reallocation, 24 November 2026

Reserve **1.70 pages** for the graphic material: Figure 1 0.75, Figure 2 0.70 and Table 1 0.25. Reserve **4.30 pages** for text/front matter/references, reducing the still-undrafted Introduction allowance from 0.50 to 0.40 and Discussion from 0.65 to 0.55 pages. Leave all other text allowances unchanged, including the approved sample description and complete H1 sensitivity passage. Total: 6.00 planned pages.

The user explicitly confirmed this numerical reallocation on 24 November 2026 after accepting the layout and specifying native LaTeX captions outside plot PDFs. The revised budget is now agreed and recorded in the storyline. Issue 09 is Resolved.

## Limits and exact next step

This is a PyMuPDF physical-layout proof, not a compiled PNAS manuscript. No LaTeX compiler was found on PATH or in the checked standard MiKTeX/TeX Live locations; Poppler was also absent on PATH, so PyMuPDF rendered the proof and rotation preview. Final typesetting, actual float placement, author metadata and reference wrapping remain unverified. A six-page full manuscript has not yet been demonstrated.

Issue 09 and 09c are Resolved. Next: Issue 10's reproducible Methods outline. Final whole-manuscript compilation and six-page verification remain with Issues 13-14; this physical proof is not final compliance.
