"""Make a physical-size figure/caption proof, not a compiled manuscript."""
from pathlib import Path
import json
import re

import pymupdf as pdf


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper_simple"
OUT = ROOT / "output/pdf/issue09_layout"
OUT.mkdir(parents=True, exist_ok=True)
FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
FONT = pdf.Font(fontfile=str(FONT_PATH))
TEX_TO_PDF = 72 / 72.27
WIDTH = 512 * TEX_TO_PDF
LEFT = (72.27 - 35.1) * TEX_TO_PDF
TOP = 33
# Body envelope measured against the supplied compiled template, not a TeX run.
BOTTOM = 733
BODY_HEIGHT = BOTTOM - TOP
CAP_SIZE = 7 * TEX_TO_PDF
CAP_LEADING = 9 * TEX_TO_PDF
story = (PAPER / "paper_storyline.md").read_text(encoding="utf-8")
evidence = (PAPER / "evidence_and_sources.md").read_text(encoding="utf-8")


def section(text, heading):
    return text.split(heading, 1)[1].split("\n##", 1)[0]


def plain(text):
    return text.replace("**", "").strip()


def wrap(text, width, size):
    lines = []
    for paragraph in text.split("\n\n"):
        line = ""
        for word in paragraph.split():
            trial = f"{line} {word}".strip()
            if line and FONT.text_length(trial, fontsize=size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        if line:
            lines.append(line)
        lines.append("")
    return lines[:-1]


def text_block(page, text, x, y, width, size=CAP_SIZE, leading=CAP_LEADING):
    lines = wrap(text, width, size)
    for line in lines:
        if line:
            page.insert_text((x, y + size), line, fontname="arial", fontsize=size)
        y += leading
    return y


def new_page(doc, title):
    page = doc.new_page(width=585, height=782.64)
    page.insert_font(fontname="arial", fontfile=str(FONT_PATH))
    page.insert_font(fontname="arialbold", fontfile=str(FONT_BOLD_PATH))
    page.insert_text((LEFT, 18), title, fontname="arial", fontsize=7, color=(0.4, 0.4, 0.4))
    page.draw_rect(pdf.Rect(LEFT, TOP, LEFT + WIDTH, BOTTOM), color=(0.8, 0.8, 0.8), width=0.3)
    page.insert_text((LEFT, 758), "Layout proof only; final PNAS LaTeX compilation remains pending.",
                     fontname="arial", fontsize=7, color=(0.4, 0.4, 0.4))
    return page


fig1_text = plain(re.search(r"\*\*Figure 1\. Transfer-network structure[^\n]+", story)[0])
fig2_section = section(story, "### Approved Figure 2 caption, 24 November 2026")
fig2_text = plain(fig2_section[fig2_section.index("**Figure 2."):])
table_section = section(evidence, "### Approved validation-table caption and note, 24 November 2026")
table_title = plain(re.search(r"\*\*Table 1\.[^\n]+", table_section)[0])
table_note = plain(re.search(r"\*\*Note:\*\*[^\n]+", table_section)[0])
table_rows = [line.split("|")[1:-1] for line in table_section.splitlines()
              if line.startswith("| ") and not line.startswith("| ---")]

doc = pdf.open()
page = new_page(doc, "Figure 1: requested 90-degree counterclockwise rotation; native scale, side caption")
source = pdf.open(ROOT / "output/backbone_h1_findings/combined.pdf")
fig1_rect = pdf.Rect(LEFT, TOP + 8, LEFT + source[0].rect.width, TOP + 8 + source[0].rect.height)
rotation = source[0].rotation
source[0].set_rotation(0)
page.show_pdf_page(fig1_rect, source, 0, rotate=-rotation)
cap1_end = text_block(page, fig1_text, fig1_rect.x1 + 12, fig1_rect.y0,
                      LEFT + WIDTH - fig1_rect.x1 - 12)
fig1_height = max(fig1_rect.y1, cap1_end) - TOP
source.close()

page = new_page(doc, "Figure 2 and Table 1: current figure scale and complete approved captions/notes")
source = pdf.open(ROOT / "output/h2_monthly_period_means_findings/combined.pdf")
fig2_rect = pdf.Rect(LEFT, TOP + 8, LEFT + source[0].rect.width, TOP + 8 + source[0].rect.height)
page.show_pdf_page(fig2_rect, source, 0)
cap2_end = text_block(page, fig2_text, LEFT, fig2_rect.y1 + 10, WIDTH)
source.close()
table_top = cap2_end + 18
y = text_block(page, table_title, LEFT, table_top, WIDTH, size=8, leading=11)
y += 10
columns = [0, 205, 345, 425]
page.draw_line((LEFT, y), (LEFT + WIDTH, y), width=0.5)
y += 4
for row_index, row in enumerate(table_rows):
    for column, cell in enumerate(row):
        page.insert_text((LEFT + columns[column] + 3, y + 8), cell.strip(),
                         fontname="arialbold" if row_index == 0 else "arial", fontsize=8)
    y += 15
    if row_index == 0:
        page.draw_line((LEFT, y), (LEFT + WIDTH, y), width=0.3)
page.draw_line((LEFT, y), (LEFT + WIDTH, y), width=0.5)
table_end = text_block(page, table_note, LEFT, y + 7, WIDTH)
assert table_end < BOTTOM, (table_end, BOTTOM)
assert fig1_rect.y1 < BOTTOM
proof = OUT / "figure_caption_fit.pdf"
doc.save(proof, garbage=4, deflate=True)
doc.close()

with pdf.open(proof) as checked:
    for index, page in enumerate(checked):
        page.get_pixmap(matrix=pdf.Matrix(1.5, 1.5), alpha=False).save(OUT / f"page_{index + 1}.png")
    extracted = "\n".join(page.get_text() for page in checked)
    for required in ("0.7558", "2.42", "0.098", "85", "196", "0.52"):
        assert required in extracted, required

blocks = {"figure1_with_side_caption": fig1_height,
          "figure2_with_caption": cap2_end - TOP,
          "table1_with_note": table_end - table_top}
report = {"proof": str(proof.relative_to(ROOT)), "template_body_width_pdf_points": WIDTH,
          "body_height_pdf_points_approximate": BODY_HEIGHT,
          "caption_size_TeX_points": 7, "caption_leading_TeX_points": 9,
          "block_heights_pdf_points": blocks,
          "block_page_fractions_approximate": {k: v / BODY_HEIGHT for k, v in blocks.items()},
          "total_graphic_page_equivalent_approximate": sum(blocks.values()) / BODY_HEIGHT,
          "total_with_original_4_50_page_text_allowance": 4.5 + sum(blocks.values()) / BODY_HEIGHT,
          "table_bottom_pdf_points": table_end,
          "limitations": ["PyMuPDF physical-layout proof, not a compiled PNAS manuscript.",
                         "Arial substitutes for the template Helvetica caption family.",
                         "Body height is a measured approximation; float spacing/placement are not simulated.",
                         "Side caption is a proposed layout choice requiring review."]}
(OUT / "layout_measurements.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
