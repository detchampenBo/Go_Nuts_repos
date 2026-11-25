"""Build the local assets for the three-slide deck.

1. Rasterise the final paper's figure PDFs.
   Source: social_graphs_paper.zip (SHA-256 8648D74B...41754), figures/ folder.
   Crops reproduce the \\includegraphics trim values in the zip's figure_floats.tex
   (left, bottom, right, top in PostScript points).
2. Download the deck's Google Fonts (Latin subsets) and write fonts.css, so the
   HTML renders offline and Chrome's print-to-PDF embeds the right fonts.

Usage: python build_assets.py
"""

import hashlib
import re
import urllib.request
import zipfile
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
ZIP_PATH = HERE.parent / "paper_output_zip" / "social_graphs_paper.zip"
ZIP_SHA256 = "8648D74BCC73474E54C76F6E9CC85AB68631FA84307CF8C7E74B494B49941754"
OUT_DIR = HERE / "bohart_fu_slides-assets"
DPI = 450

FIGURES = {
    "transfer_network_and_entry": (8, 30, 5, 10),
    "guardian_rank_frequency": (0, 13, 0, 4),
    "guardian_sentiment": (10, 8, 0, 5),
}


FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..500;"
    "1,6..72,400..500&family=Hanken+Grotesk:wght@400..700&family=DM+Mono:wght@400;500&display=swap"
)
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def build_fonts() -> None:
    font_dir = OUT_DIR / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)
    css = fetch(FONTS_URL).decode("utf-8")
    blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, flags=re.S)
    kept = []
    for subset, block in blocks:
        if subset not in ("latin", "greek"):
            continue
        family = re.search(r"font-family: '([^']+)'", block).group(1)
        style = re.search(r"font-style: (\w+)", block).group(1)
        weight = re.search(r"font-weight: ([\d ]+);", block).group(1).replace(" ", "-")
        src = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        name = f"{family.replace(' ', '')}-{style}-{weight}-{subset}.woff2"
        (font_dir / name).write_bytes(fetch(src))
        kept.append(block.replace(src, f"fonts/{name}"))
        print(f"font {name}")
    (OUT_DIR / "fonts.css").write_text("\n".join(kept) + "\n", encoding="utf-8")


def main() -> None:
    build_fonts()
    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest().upper()
    if digest != ZIP_SHA256:
        raise SystemExit(f"Unexpected zip hash {digest}")

    OUT_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        for name, (left, bottom, right, top) in FIGURES.items():
            doc = pymupdf.open(stream=archive.read(f"figures/{name}.pdf"), filetype="pdf")
            page = doc[0]
            box = page.rect
            clip = pymupdf.Rect(box.x0 + left, box.y0 + top, box.x1 - right, box.y1 - bottom)
            pix = page.get_pixmap(dpi=DPI, clip=clip, alpha=False)
            out = OUT_DIR / f"{name}.png"
            pix.save(out)
            print(f"{out.name}: {pix.width}x{pix.height}px, page rotation {page.rotation}")


if __name__ == "__main__":
    main()
