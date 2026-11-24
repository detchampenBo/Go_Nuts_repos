"""Render actual PDF in colour/grayscale and inspect export structure."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pymupdf
from PIL import Image


output = Path(__file__).resolve().parent.parent
pdf = pymupdf.open(output / "rank_frequency.pdf")
assert len(pdf) == 1
page = pdf[0]
assert page.rotation == 0
assert abs(page.rect.width / 72 - 3.58) < 1e-6
assert abs(page.rect.height / 72 - 3.2) < 1e-6
fonts = page.get_fonts(full=True)
assert fonts and all("Arial" in font[3] for font in fonts)
font_bytes = [len(pdf.extract_font(font[0])[3]) for font in fonts]
assert all(font_bytes)
assert not page.get_images(full=True)
assert page.get_drawings()
text = page.get_text()
for label in ("Token rank (linear scale)", "Relative frequency (linear scale)",
              "Observed tokens", "1/r reference (rank-1 anchored)"):
    assert label in text
spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block
         for line in block["lines"] for span in line["spans"]]
assert min(span["size"] for span in spans) >= 8
for span in spans:
    assert page.rect.contains(pymupdf.Rect(span["bbox"]))
for filename, colorspace in (("actual_pdf_preview.png", pymupdf.csRGB),
                             ("actual_pdf_preview_grayscale.png", pymupdf.csGRAY)):
    page.get_pixmap(dpi=200, colorspace=colorspace).save(output / "qa" / filename)
with Image.open(output / "rank_frequency.png") as png:
    dpi, pixels = png.info["dpi"], png.size
    assert all(abs(value - 600) < 0.01 for value in dpi)
svg = ET.parse(output / "rank_frequency.svg")
svg_text = svg.findall(".//{http://www.w3.org/2000/svg}text")
assert svg_text
assert any("Arial" in node.attrib.get("style", "") for node in svg_text)
assert not svg.findall(".//{http://www.w3.org/2000/svg}image")
report = {
    "scope": "ACTUAL Guardian selected-corpus figure",
    "renderer": "existing PyMuPDF fallback; Poppler unavailable; no installs",
    "pymupdf_version": pymupdf.VersionBind,
    "pages": len(pdf), "rotation": page.rotation,
    "width_inches": page.rect.width / 72, "height_inches": page.rect.height / 72,
    "fonts": fonts, "embedded_font_bytes": font_bytes,
    "raster_images": len(page.get_images(full=True)),
    "vector_drawings": len(page.get_drawings()),
    "minimum_text_fontsize": min(span["size"] for span in spans),
    "all_text_within_page": True, "png_dpi": dpi, "png_pixels": pixels,
    "svg_editable_text": True, "svg_embedded_raster_images": 0,
    "colour_and_grayscale_previews": ["actual_pdf_preview.png", "actual_pdf_preview_grayscale.png"],
    "visual_review": "pending direct image inspection",
}
(output / "qa/actual_plot_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
