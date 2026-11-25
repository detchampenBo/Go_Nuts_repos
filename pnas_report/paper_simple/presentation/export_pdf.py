"""Export bohart_fu_slides.html to a three-page 16:9 PDF with headless Chrome.

Replaces the skill's bash/Playwright exporter, which cannot run on this machine.
The deck's print CSS sets one 1920x1080 px page per slide with every element in
its final state. Also writes 1920x1080 PNG renders of each slide to qa/.

Usage: python export_pdf.py
"""

import subprocess
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
HTML = HERE / "bohart_fu_slides.html"
PDF = HERE / "bohart_fu_slides.pdf"
QA = HERE / "qa"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
COMMON = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=10000"]


def main() -> None:
    url = HTML.as_uri()
    subprocess.run(
        [str(CHROME), *COMMON, "--no-pdf-header-footer", f"--print-to-pdf={PDF}", url],
        check=True, capture_output=True,
    )

    QA.mkdir(exist_ok=True)
    doc = pymupdf.open(PDF)
    print(f"{PDF.name}: {doc.page_count} pages")
    for i, page in enumerate(doc, start=1):
        w, h = page.rect.width, page.rect.height
        print(f"  page {i}: {w:.1f} x {h:.1f} pt, ratio {w / h:.4f}, rotation {page.rotation}")
        page.get_pixmap(matrix=pymupdf.Matrix(1920 / w, 1920 / w)).save(QA / f"pdf_page{i}.png")
    fonts = sorted({f[3] for page in doc for f in page.get_fonts()})
    print("  fonts:", ", ".join(fonts))


if __name__ == "__main__":
    main()
