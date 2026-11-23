"""Present saved Guardian before/after summaries; never rerun the analysis.

Run: python -B pnas_report/notebooks/plot_guardian_period_comparison.py
"""

import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter
from PIL import Image
import pymupdf


PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data/dataset_nlp/results"
OUT = PROJECT / "output/guardian_period_comparison_findings"
SOURCES = ("a1_age30_levels.csv", "a1_age30_results.csv", "a1_coverage_age.csv")
OLDER, YOUNGER = "#DC831B", "#372107"
WIDTH, HALF_WIDTH, HEIGHT = 17.8 / 2.54, 8.6 / 2.54, 2.8


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(filename, **selectors):
    with (DATA / filename).open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream)
                if all(row[key] == value for key, value in selectors.items())]
    if len(rows) != 1:
        raise ValueError(f"Expected one {filename} row for {selectors}; found {len(rows)}")
    return rows[0]


def load_saved_values():
    tone = [select(SOURCES[0], model="RoBERTa", what=p) for p in ("before", "after")]
    result = select(SOURCES[1], method="RoBERTa", sample="main")
    coverage = [select(SOURCES[2], articles="all article types", spec="season only", period=p)
                for p in ("before", "after")]
    values = {
        "tone": {"older": [float(r["30plus"]) for r in tone],
                 "younger": [float(r["under30"]) for r in tone],
                 "n_older": int(result["n_30plus"]), "n_younger": int(result["n_under30"])},
        "coverage": {"older": [float(r["median_articles_30plus"]) for r in coverage],
                     "younger": [float(r["median_articles_under30"]) for r in coverage],
                     "n_older": int(float(coverage[0]["n_30plus"])),
                     "n_younger": int(float(coverage[0]["n_under30"]))},
        "h2": {key: float(result[key]) for key in
               ("diff_30plus", "diff_under30", "gap_30plus_minus_under30", "p_gap_within_season")},
    }
    expected = {
        "tone": {"older": [0.0914, 0.0838], "younger": [0.1253, 0.1117],
                 "n_older": 67, "n_younger": 753},
        "coverage": {"older": [27.5, 47.5], "younger": [12.0, 35.0],
                     "n_older": 88, "n_younger": 1244},
        "h2": {"diff_30plus": -0.0076, "diff_under30": -0.0137,
               "gap_30plus_minus_under30": 0.006, "p_gap_within_season": 0.7558},
    }
    if values != expected:
        raise ValueError(f"Saved source identities/values changed: {values}")
    if any((int(float(r["n_30plus"])), int(float(r["n_under30"]))) != (88, 1244)
           for r in coverage):
        raise ValueError("Coverage counts differ between periods")
    return values


def configure_style():
    # A final export requires Arial; fail visibly rather than substituting a font.
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 9.5, "text.color": "#333333",
        "axes.labelcolor": "#333333", "axes.edgecolor": "#333333",
        "axes.linewidth": 0.6, "axes.labelsize": 9.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": "#333333", "ytick.color": "#333333",
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "legend.fontsize": 8, "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none", "figure.facecolor": "white",
        "axes.facecolor": "white", "savefig.facecolor": "white",
    })


def draw_panel(ax, kind, values):
    data = values[kind]
    ax.set_xlim(-0.28, 1.28)
    ax.set_xticks([0, 1], ["Before", "After"])
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E4E4E4", linewidth=0.45)
    if kind == "tone":
        ax.set_ylim(0, 0.16)
        ax.yaxis.set_major_locator(FixedLocator([0, 0.04, 0.08, 0.12, 0.16]))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.set_ylabel("Mean tone (score units)", labelpad=6)
    else:
        ax.set_ylim(0, 65)
        ax.yaxis.set_major_locator(FixedLocator([0, 15, 30, 45, 60]))
        ax.set_ylabel("Median articles per signing", labelpad=6)
    annotations, handles = [], []
    for group, color, marker in (("older", OLDER, "o"), ("younger", YOUNGER, "s")):
        ax.plot([0, 1], data[group], color=color, marker=marker, markersize=5,
                markeredgewidth=0, linewidth=1.3, zorder=3)
        for x, y in enumerate(data[group]):
            label = f"+{y:.4f}" if kind == "tone" else f"{y:g}"
            above = (group == "younger") if kind == "tone" else (group == "older")
            annotations.append(ax.annotate(label, (x, y), xytext=(0, 8 if above else -9),
                                           textcoords="offset points", ha="center",
                                           va="bottom" if above else "top", fontsize=9,
                                           color=color))
        name = "30+" if group == "older" else "Under 30"
        handles.append(Line2D([], [], color=color, marker=marker, markersize=5,
                              markeredgewidth=0, linewidth=1.3,
                              label=f"{name} (n = {data['n_' + group]:,})"))
    legend = ax.legend(handles=handles, loc="lower left" if kind == "tone" else "upper left",
                       frameon=True, fancybox=True, facecolor="white", framealpha=1,
                       edgecolor="#BBBBBB", borderpad=0.55, labelspacing=0.4,
                       handlelength=1.8, borderaxespad=0.6)
    legend.get_frame().set_linewidth(0.6)
    return annotations, legend


def export(fig, stem, panels):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    checks = []
    for ax, annotations, legend in panels:
        boxes = [a.get_window_extent(renderer) for a in annotations]
        legend_box = legend.get_window_extent(renderer)
        overlaps = any(a.overlaps(b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
        overlaps |= any(b.overlaps(legend_box) for b in boxes)
        in_axes = all(ax.get_window_extent(renderer).contains(b.x0, b.y0)
                      and ax.get_window_extent(renderer).contains(b.x1, b.y1) for b in boxes)
        if overlaps or not in_axes:
            raise ValueError(f"Annotation collision or clipped point label in {stem}")
        checks.append({"point_labels": [a.get_text() for a in annotations],
                       "point_label_overlap": False, "point_labels_within_axes": True,
                       "legend": [t.get_text() for t in legend.get_texts()],
                       "title": ax.get_title(loc="left"), "xscale": ax.get_xscale(),
                       "yscale": ax.get_yscale(), "yticks": [float(t) for t in ax.get_yticks()]})
    for extension in ("pdf", "png", "svg"):
        fig.savefig(OUT / f"{stem}.{extension}", dpi=600 if extension == "png" else None)
    plt.close(fig)
    return checks


def inspect_exports(stem, width):
    path = OUT / f"{stem}.pdf"
    with pymupdf.open(path) as doc:
        page = doc[0]
        fonts = [{"name": f[3], "type": f[2], "embedded_bytes": len(doc.extract_font(f[0])[3])}
                 for f in page.get_fonts()]
        spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                 for line in b["lines"] for s in line["spans"]]
        directions = sorted({tuple(line["dir"]) for b in page.get_text("dict")["blocks"]
                             if "lines" in b for line in b["lines"]})
        text_within_page = all(page.rect.contains(pymupdf.Rect(word[:4]))
                               for word in page.get_text("words"))
        report = {"page_count": len(doc), "size_inches": [page.rect.width / 72, page.rect.height / 72],
                  "rotation": page.rotation, "fonts": fonts, "raster_images": len(page.get_images()),
                  "vector_drawing_objects": len(page.get_drawings()),
                  "pdf_text": page.get_text(), "text_line_directions": directions,
                  "all_text_within_page": text_within_page,
                  "font_sizes_pt": sorted({round(s["size"], 2) for s in spans})}
        if (len(doc) != 1 or page.rotation != 0 or abs(page.rect.width / 72 - width) > 0.001
                or abs(page.rect.height / 72 - HEIGHT) > 0.001 or page.get_images()
                or not text_within_page or not set(directions) <= {(1.0, 0.0), (0.0, -1.0)}
                or not fonts or not all("Arial" in f["name"] and f["embedded_bytes"] > 0 for f in fonts)):
            raise ValueError(f"PDF publication checks failed: {stem}")
        # Include 72-dpi physical-size previews and 144-dpi detail renders.
        for dpi in (72, 144):
            for grayscale in (False, True):
                pixmap = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY if grayscale else pymupdf.csRGB)
                pixmap.save(OUT / "qa" / f"{stem}{'_grayscale' if grayscale else ''}_{dpi}dpi.png")
    with Image.open(OUT / f"{stem}.png") as image:
        report["png"] = {"size_pixels": list(image.size), "dpi": list(image.info["dpi"])}
        if any(abs(d - 600) > 0.1 for d in image.info["dpi"]):
            raise ValueError("PNG is not 600 dpi")
    svg = ET.parse(OUT / f"{stem}.svg").getroot()
    report["svg_editable_text_elements"] = len(svg.findall(".//{http://www.w3.org/2000/svg}text"))
    if not report["svg_editable_text_elements"]:
        raise ValueError("SVG text was converted to outlines")
    report["files"] = {ext: {"bytes": (OUT / f"{stem}.{ext}").stat().st_size,
                             "sha256": sha256(OUT / f"{stem}.{ext}")}
                       for ext in ("pdf", "png", "svg")}
    return report


def write_readme(hashes):
    table = "\n".join(f"| `{name}` | `{digest}` |" for name, digest in hashes.items())
    (OUT / "README.md").write_text(f"""# Guardian before/after presentation candidate

This saved-results-only presentation candidate has not been selected as a manuscript figure. It supplements the existing monthly tone view for comparison. No statistical analysis, fitting, permutation, bootstrap or source-data aggregation is run by this producer.

| View | Exports |
| --- | --- |
| Combined | [PDF](combined.pdf) · [PNG, 600 dpi](combined.png) · [SVG, editable text](combined.svg) |
| Mean RoBERTa tone | [PDF](mean_roberta_tone.pdf) · [PNG, 600 dpi](mean_roberta_tone.png) · [SVG, editable text](mean_roberta_tone.svg) |
| Median article counts | [PDF](median_article_counts.pdf) · [PNG, 600 dpi](median_article_counts.png) · [SVG, editable text](median_article_counts.svg) |

Combined width: 17.8 cm. Standalone width: 8.6 cm. All are 2.8 inches high. Arial is embedded in PDFs; SVG text remains editable. The tone axis shows signed score units, not percentage change; the displayed positive levels occupy a linear axis starting at zero. Connecting lines join the two saved period summaries and do not represent monthly trajectories. No uncertainty ranges are displayed.

Reproduce from the repository root:

```powershell
python -B pnas_report/notebooks/plot_guardian_period_comparison.py
```

## Draft self-contained caption

**Guardian coverage before and after selected Premier League signings.** (a) Mean RoBERTa tone, scored as P(positive) minus P(negative) on a -1 to +1 scale, for 820 signings with at least five scored sentences in each period after excluding liveblogs and match reports (67 aged 30+, 753 under 30). Scores are averaged within each signing-period and then across signings with equal signing weight. Older signings average +0.0914 before and +0.0838 after; younger signings average +0.1253 and +0.1117. The saved H2 changes are -0.0076 and -0.0137, respectively, with an older-minus-younger change gap of +0.0060 score units (two-sided within-season age-label permutation p = 0.7558). The small older sample limits sensitivity to smaller differences; this result does not establish equal changes across groups. (b) Median distinct Guardian article counts naming the player, including all article types and signings with zero articles, for the separate, broader sample of 1,332 signings (88 aged 30+, 1,244 under 30). Medians rise from 27.5 to 47.5 for older signings and from 12 to 35 for younger signings. Both panels use before days -365 through -8 and after days +8 through +365 relative to signing; days -7 through +7 are excluded. Counts refer to signings, not unique players, and signings can share articles. Panel (b) shows unadjusted pooled medians, not model-adjusted article ratios. The panels describe their respective selected samples rather than a causal effect of signing. Lines connect period summaries only; no monthly pattern or uncertainty range is shown.

## Sources and selectors

All inputs are in [data/dataset_nlp/results](../../data/dataset_nlp/results/).

- `a1_age30_levels.csv`: exactly one row for each `model=RoBERTa`, `what=before/after`; only `30plus` and `under30` mean columns are used. Historical interval and p-value columns are ignored.
- `a1_age30_results.csv`: exactly one `method=RoBERTa`, `sample=main` row supplies the tone counts and saved H2 changes, gap and p-value. These saved changes are retained; subtracting already rounded displayed levels need not reproduce their final decimal.
- `a1_coverage_age.csv`: exactly one row for each `articles=all article types`, `spec=season only`, `period=before/after`; only median columns and sample counts are used. The selector identifies the saved rows; plotted medians are unadjusted summaries. No fitted coefficients, ratios, intervals or p-values from this file are plotted.

The producer checks these row identities, every displayed value, both periods' coverage counts and the saved main H2 statistics. It reads only saved CSVs. Eligibility, windows, weighting and measurement definitions above follow the existing approved project evidence; this presentation step does not reconstruct sentence eligibility or independently validate the measurement instrument.

| Input | SHA-256 |
| --- | --- |
{table}

## Verification

[Machine-readable verification](verification.json) records source values/counts, label checks, export dimensions and file hashes, embedded fonts, PDF rotation/vector content, PNG resolution, SVG text, and before/after hashes for every pre-existing PDF under `paper/figures/` and `output/`. [QA renders](qa/) include 72-dpi physical-size previews and 144-dpi detail renders, each in color and grayscale. Visual inspection findings are in [visual review](qa/visual_review.md).
""", encoding="utf-8")


def main():
    # Preserve historical compatibility PDFs and any existing output PDFs.
    historical = sorted(set((PROJECT / "paper/figures").rglob("*.pdf"))
                        | {p for p in (PROJECT / "output").rglob("*.pdf") if OUT not in p.parents})
    before = {str(p.relative_to(PROJECT)): sha256(p) for p in historical}
    values = load_saved_values()
    hashes = {name: sha256(DATA / name) for name in SOURCES}
    configure_style()
    (OUT / "qa").mkdir(parents=True, exist_ok=True)
    report = {"source_validation": "passed", "source_sha256": hashes,
              "saved_values": values, "exports": {}}
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, HEIGHT))
    fig.subplots_adjust(left=0.083, right=0.985, bottom=0.17, top=0.88, wspace=0.40)
    panels = []
    for ax, kind, title in zip(axes, ("tone", "coverage"),
                               ("(a) Mean RoBERTa tone", "(b) Median article counts")):
        annotations, legend = draw_panel(ax, kind, values)
        ax.set_title(title, loc="left", fontsize=10, pad=9)
        panels.append((ax, annotations, legend))
    report["exports"]["combined"] = {"panels": export(fig, "combined", panels),
                                              **inspect_exports("combined", WIDTH)}
    for kind, stem in (("tone", "mean_roberta_tone"), ("coverage", "median_article_counts")):
        fig, ax = plt.subplots(figsize=(HALF_WIDTH, HEIGHT))
        fig.subplots_adjust(left=0.185, right=0.97, bottom=0.17, top=0.95)
        annotations, legend = draw_panel(ax, kind, values)
        report["exports"][stem] = {"panels": export(fig, stem, [(ax, annotations, legend)]),
                                    **inspect_exports(stem, HALF_WIDTH)}
    after = {str(p.relative_to(PROJECT)): sha256(p) for p in historical}
    report["historical_pdf_preservation"] = {
        "all_unchanged": before == after, "before_sha256": before, "after_sha256": after}
    if before != after:
        raise ValueError("A historical PDF changed")
    report["execution_scope"] = "Saved CSV summary rows only; no statistical recomputation."
    write_readme(hashes)
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Verified source selections and exported three views to {OUT}")
    print(f"Preserved {len(historical)} historical PDFs; inspect qa/ renders before delivery.")


if __name__ == "__main__":
    main()
