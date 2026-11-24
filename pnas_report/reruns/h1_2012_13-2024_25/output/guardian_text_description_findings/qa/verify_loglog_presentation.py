"""Check the saved-frequency presentation without rerunning corpus analysis."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
import xml.etree.ElementTree as ET

import matplotlib
import numpy
import pymupdf
from PIL import Image


output = Path(__file__).resolve().parent.parent
workspace = output.parents[4]
baseline = json.loads((output / "qa/loglog_core_before.json").read_text())
for filename, expected in baseline.items():
    assert hashlib.sha256((workspace / filename).read_bytes()).hexdigest() == expected, filename

tables = []
for filename in ("token_frequencies.csv", "token_frequencies_no_stopwords.csv"):
    with (output / filename).open(encoding="utf-8", newline="") as handle:
        tables.append(list(csv.DictReader(handle)))
markdown = (output / "top_ten_words.md").read_text(encoding="utf-8")
assert markdown == (output / "top_five_words.md").read_text(encoding="utf-8")
rows = [line for line in markdown.splitlines() if line.startswith("| ")][2:]
assert len(rows) == 10
for index, line in enumerate(rows):
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    assert int(cells[0]) == index + 1
    for source, offset in zip(tables, (1, 4)):
        expected = source[index]
        assert cells[offset] == expected["token"]
        assert int(cells[offset + 1]) == int(expected["count"])
        assert cells[offset + 2] == f"{float(expected['relative_frequency']):.8g}"

analysis = (output / "analysis_summary.md").read_text(encoding="utf-8")
comparisons = [line for line in analysis.splitlines() if re.match(r"\| [\d,]+ \|", line)]
assert len(comparisons) == 6
for line in comparisons:
    cells = [cell.strip().replace(",", "") for cell in line.strip("|").split("|")]
    rank = int(cells[0])
    count = int(tables[0][rank - 1]["count"])
    reference = int(tables[0][0]["count"]) / rank
    assert int(cells[1]) == count
    assert cells[2] == f"{reference:.2f}"
    assert cells[3] == f"{count / reference:.2f}"
context = json.loads((output / "qa/word_context_check.json").read_text())
assert context["whole_word_occurrences"] == int(next(row["count"] for row in tables[1]
                                                   if row["token"] == "unknown"))
assert f"{context['records_containing_term']:,}" in analysis

pdf = pymupdf.open(output / "rank_frequency_loglog.pdf")
assert len(pdf) == 1
page = pdf[0]
assert page.rotation == 0
assert abs(page.rect.width / 72 - 3.58) < 1e-6
assert abs(page.rect.height / 72 - 3.4) < 1e-6
fonts = page.get_fonts(full=True)
assert fonts and all("Arial" in font[3] for font in fonts)
assert all(pdf.extract_font(font[0])[3] for font in fonts)
assert not page.get_images(full=True) and page.get_drawings()
for label in ("Frequency rank", "Frequency (token count)",
              "Observed tokens", "ideal Zipf, s = 1"):
    assert label in page.get_text(), label
spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block
         for line in block["lines"] for span in line["spans"]]
assert min(span["size"] for span in spans) >= 8
assert all(page.rect.contains(pymupdf.Rect(span["bbox"])) for span in spans)
for suffix, colorspace in (("colour", pymupdf.csRGB), ("grayscale", pymupdf.csGRAY)):
    page.get_pixmap(dpi=200, colorspace=colorspace).save(output / f"qa/loglog_{suffix}.png")
with Image.open(output / "rank_frequency_loglog.png") as png:
    dpi, pixels = png.info["dpi"], png.size
    assert all(abs(value - 600) < 0.01 for value in dpi)
svg = ET.parse(output / "rank_frequency_loglog.svg")
assert svg.findall(".//{http://www.w3.org/2000/svg}text")
assert not svg.findall(".//{http://www.w3.org/2000/svg}image")

exporter = output.parents[1] / "notebooks/plot_guardian_h2_loglog.py"
files = ["rank_frequency_loglog.pdf", "rank_frequency_loglog.png", "rank_frequency_loglog.svg",
         "top_ten_words.md", "top_five_words.md", "README.md", "analysis_summary.md",
         "qa/word_context_check.json"]
report = {
    "scope": "presentation only; saved corpus and linear exports unchanged",
    "reproduction_command": f"& '{sys.executable}' -B '{exporter}'",
    "python_version": platform.python_version(), "interpreter": sys.executable,
    "numpy_version": numpy.__version__, "matplotlib_version": matplotlib.__version__,
    "exporter_sha256": hashlib.sha256(exporter.read_bytes()).hexdigest(),
    "source_and_core_hashes_unchanged": baseline,
    "top_ten_both_streams_match_saved_csvs": True,
    "analysis_reference_comparisons_match_saved_counts": True,
    "unknown_context_count_matches_saved_token_count": True,
    "scale": "both axes log10; complete 42,779-type base vocabulary; positive coordinates",
    "y_quantity": "raw token count, not relative frequency",
    "legend": "upper right; ideal Zipf, s = 1",
    "reference": "150246 / rank; no fitting or inference",
    "pdf_inches": [page.rect.width / 72, page.rect.height / 72],
    "pdf_rotation": page.rotation, "pdf_fonts": fonts,
    "pdf_fonts_embedded": True, "pdf_vector_drawings": len(page.get_drawings()),
    "pdf_raster_images": 0, "minimum_fontsize": min(span["size"] for span in spans),
    "all_text_within_page": True, "png_dpi": dpi, "png_pixels": pixels,
    "svg_editable_text": True, "visual_review": "pending colour/grayscale inspection",
    "environment_note": "network_analysis NumPy matrix multiply failed with native exception 0xc06d007f; existing default Python passed matrix multiplication and PDF export; no environment modifications",
    "historical_verification_note": "actual_data_verification.json preserves hashes from original five-row Markdown/README state; this report covers their later presentation update",
    "output_sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in files},
}
(output / "qa/loglog_presentation_verification.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("Saved frequencies/core exports unchanged; top-ten tables, PDF, PNG and SVG checks passed.")
