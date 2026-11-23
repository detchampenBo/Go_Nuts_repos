"""Plot saved, unadjusted H2 monthly curves and signing-weighted period means.

Run: python -B pnas_report/notebooks/plot_h2_monthly_period_means.py
No smoothing, bootstrap, shuffle, or sentence-level analysis is run here.
"""

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import pandas as pd
from PIL import Image
import pymupdf


PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "output/h2_monthly_period_means_findings"
RESULTS = PROJECT / "data/dataset_nlp/results"
CURVES = PROJECT / "figures/plotting/data/a1_h2_arc_4models.csv"
MODELS = [("RoBERTa (main)", "RoBERTa", "roberta"), ("VADER", "VADER", "vader"),
          ("Bing", "Bing", "bing"),
          ("Bing, no football words", "Bing, no football words", "bing_nofootball")]
COLORS = {"30+": "#DC831B", "Under 30": "#372107"}
WIDTH, SINGLE_WIDTH = 17.8 / 2.54, 3.58
REFERENCES = [PROJECT / "paper/figures" / name for name in
              ("fig_h2b_arc_paper.pdf", "fig_h2b_tone_coverage.pdf")]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_panel(ax, curve, levels):
    ax.set(xlim=(-12, 12), ylim=(-0.10, 0.27),
           xlabel="Months from the transfer", ylabel="Mean sentiment (score units)")
    ax.set_xticks([-12, -6, 0, 6, 12])
    ax.xaxis.set_minor_locator(MultipleLocator(3))
    ax.yaxis.set_major_locator(MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(MultipleLocator(0.05))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.tick_params(which="minor", length=0)
    ax.set_axisbelow(True)
    ax.grid(which="both", color="#999999", linewidth=0.5)
    ax.axvline(0, color="#777777", linestyle=(0, (3, 3)), linewidth=0.8)
    annotations, markers = [], []
    for group, column in [("30+", "30plus"), ("Under 30", "under30")]:
        for period, x in [("before", -6), ("after", 6)]:
            d = curve[(curve.group == group) & ((curve.month < 0) == (period == "before"))]
            ax.plot(d.month + 0.5, d.mean_smooth, color=COLORS[group], linewidth=1.6)
            y = float(levels.loc[period, column])
            ax.plot([x - 0.75, x + 0.75], [y, y], color="white", linewidth=3.5, zorder=4)
            ax.plot([x - 0.75, x + 0.75], [y, y], color=COLORS[group], linewidth=1.8, zorder=5)
            ax.plot(x, y, "o", color=COLORS[group], markersize=5.8,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=6)
            above = group == "Under 30"
            label = f"{y:.3f}"
            annotations.append(ax.annotate(label, (x, y), xytext=(0, 9 if above else -9),
                                           textcoords="offset points", ha="center",
                                           va="bottom" if above else "top", fontsize=8,
                                           color="#333333", zorder=7,
                                           bbox=dict(facecolor="white", edgecolor="none", pad=0.6)))
            markers.append({"group": group, "period": period, "x": x, "mean": y,
                            "label": label, "segment_half_width_months": 0.75})
    return annotations, markers


def export(fig, stem, panels):
    expected_size = fig.get_size_inches()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax, annotations, _ in panels:
        boxes = [a.get_window_extent(renderer) for a in annotations]
        assert not any(a.overlaps(b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
        assert all(ax.get_window_extent(renderer).contains(b.x0, b.y0)
                   and ax.get_window_extent(renderer).contains(b.x1, b.y1) for b in boxes)
    for extension in ("pdf", "png", "svg"):
        fig.savefig(OUT / f"{stem}.{extension}", dpi=600 if extension == "png" else None)
    plt.close(fig)
    with pymupdf.open(OUT / f"{stem}.pdf") as doc:
        page = doc[0]
        fonts = [{"name": f[3], "type": f[2], "embedded_bytes": len(doc.extract_font(f[0])[3])}
                 for f in page.get_fonts()]
        assert all("Arial" in f["name"] and f["embedded_bytes"] > 0 for f in fonts)
        assert page.rotation == 0 and len(page.get_images()) == 0
        assert abs(page.rect.width / 72 - expected_size[0]) < 1e-5
        assert abs(page.rect.height / 72 - expected_size[1]) < 1e-5
        assert all(page.rect.contains(pymupdf.Rect(word[:4])) for word in page.get_text("words"))
        page.get_pixmap(dpi=144).save(OUT / "qa" / f"{stem}_color.png")
        page.get_pixmap(dpi=144, colorspace=pymupdf.csGRAY).save(OUT / "qa" / f"{stem}_grayscale.png")
        report = {"size_inches": [page.rect.width / 72, page.rect.height / 72],
                  "rotation": page.rotation, "fonts": fonts, "raster_images": 0,
                  "vector_drawing_objects": len(page.get_drawings()),
                  "text_within_page": True, "mean_labels_within_axes": True,
                  "mean_label_box_overlap": False}
    with Image.open(OUT / f"{stem}.png") as im:
        report["png_pixels"], report["png_dpi"] = list(im.size), list(im.info["dpi"])
        assert all(abs(d - 600) < 0.1 for d in im.info["dpi"])
    svg = ET.parse(OUT / f"{stem}.svg")
    report["svg_editable_text_nodes"] = len(svg.findall(".//{http://www.w3.org/2000/svg}text"))
    assert report["svg_editable_text_nodes"] > 0
    report["panels"] = [{"title": ax.get_title(loc="left"), "means": markers}
                        for ax, _, markers in panels]
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "qa").mkdir(exist_ok=True)
    inputs = [CURVES, RESULTS / "a1_age30_levels.csv", RESULTS / "a1_age30_results.csv",
              RESULTS / "a1_age30_arc.csv"]
    hashes_before = {str(p.relative_to(PROJECT)): sha256(p) for p in inputs + REFERENCES}
    arcs, levels, results, original = [pd.read_csv(p) for p in inputs]
    assert len(arcs) == 192 and not arcs.duplicated(["model", "group", "month"]).any()
    for title, model, _ in MODELS:
        d = arcs[arcs.model == title]
        assert len(d) == 48 and set(d.group) == set(COLORS)
        assert all(set(g.month) == set(range(-12, 12)) for _, g in d.groupby("group"))
        r = results[(results.method == model) & (results["sample"] == "main")]
        assert len(r) == 1 and int(r.iloc[0].n_30plus) == 67 and int(r.iloc[0].n_under30) == 753
        assert len(levels[(levels.model == model) & levels.what.isin(["before", "after"])]) == 2
    original = original.rename(columns={"method": "model"}).sort_values(["model", "group", "month"])
    common = arcs[arcs.model.isin(original.model)].sort_values(["model", "group", "month"])
    pd.testing.assert_frame_equal(common[original.columns].reset_index(drop=True),
                                  original.reset_index(drop=True), check_dtype=False, atol=1e-12, rtol=0)
    assert len(common) == 96
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({"font.family": "Arial", "font.size": 9.5, "text.color": "#333333",
                         "axes.labelcolor": "#333333", "axes.edgecolor": "#333333",
                         "axes.linewidth": 0.6, "axes.labelsize": 9.5,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "xtick.color": "#333333", "ytick.color": "#333333",
                         "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "xtick.major.size": 2.5, "ytick.major.size": 2.5,
                         "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                         "legend.fontsize": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                         "figure.facecolor": "white", "axes.facecolor": "white"})
    handles = [Line2D([], [], color=COLORS[g], linewidth=1.6, label=f"{g} (n = {n})")
               for g, n in [("30+", 67), ("Under 30", 753)]]
    handles.append(Line2D([], [], color="#777777", linewidth=1.8, marker="o", markersize=5.8,
                          markeredgecolor="white", markeredgewidth=0.6, label="Period mean"))
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 5.0))
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.10, top=0.88, hspace=0.47, wspace=0.32)
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.52, 0.995), ncol=3,
               frameon=True, facecolor="white", edgecolor="#BBBBBB").get_frame().set_linewidth(0.6)
    panels = []
    for i, (ax, (title, model, _)) in enumerate(zip(axes.flat, MODELS)):
        annotations, markers = draw_panel(ax, arcs[arcs.model == title],
                                          levels[levels.model == model].set_index("what"))
        ax.set_title(f"({chr(97 + i)}) {title}", loc="left", fontsize=10, pad=7)
        panels.append((ax, annotations, markers))
    exports = {"combined": export(fig, "combined", panels)}
    for title, model, stem in MODELS:
        fig, ax = plt.subplots(figsize=(SINGLE_WIDTH, 3.1))
        fig.subplots_adjust(left=0.19, right=0.97, bottom=0.18, top=0.76)
        fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.57, 1.0), ncol=1,
                   frameon=True, facecolor="white", edgecolor="#BBBBBB").get_frame().set_linewidth(0.6)
        annotations, markers = draw_panel(ax, arcs[arcs.model == title],
                                          levels[levels.model == model].set_index("what"))
        exports[stem] = export(fig, stem, [(ax, annotations, markers)])
    assert hashes_before == {str(p.relative_to(PROJECT)): sha256(p) for p in inputs + REFERENCES}
    h2 = results[results["sample"] == "main"][["method", "n_under30", "n_30plus",
                   "diff_under30", "diff_30plus", "gap_30plus_minus_under30", "p_gap_within_season"]]
    verification = {"input_and_reference_sha256_unchanged": hashes_before,
                    "monthly_rows": 192, "common_original_rows_matching": 96,
                    "curve_source_column": "mean_smooth", "no_analysis_recomputed": True,
                    "grid": {"minor_x_months": 3, "minor_y_score_units": 0.05,
                             "major_color": "#999999", "minor_color": "#999999",
                             "major_linewidth_pt": 0.5, "minor_linewidth_pt": 0.5,
                             "behind_data": True},
                    "h2_main_saved_results": h2.to_dict("records"), "exports": exports}
    (OUT / "verification.json").write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
