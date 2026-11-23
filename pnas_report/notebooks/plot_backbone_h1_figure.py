"""Draw Figure 1 from frozen restricted-period backbone and H1 results only."""

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import Line2D
from PIL import Image
import pymupdf as fitz

from age_shuffle_outsideprem_toprem import _draw_shuffle_distribution


REPORT = Path(__file__).resolve().parents[1]
SAVED = REPORT / "reruns/h1_2012_13-2024_25/output"
BACKBONE = SAVED / "louvain_transfer_backbone_findings"
DESTINATION = REPORT / "output/backbone_h1_findings"
WIDTH = 17.8 / 2.54
HEIGHT = 4.0
MARKERS = dict(zip(("1", "2", "3", "4", "5"), ("o", "s", "^", "D", "P")))
STYLE = {
    "font.family": "Arial", "font.size": 9.5, "text.color": "#333333",
    "axes.labelcolor": "#333333", "axes.edgecolor": "#333333",
    "axes.titlecolor": "#333333", "axes.labelsize": 9.5, "axes.titlesize": 10,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": "#333333", "ytick.color": "#333333",
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 8,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
    "savefig.bbox": None,
}


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retained(rows, alpha):
    return [r for r in rows if r["structural_exception"] == "True"
            or (r["min_score"] and float(r["min_score"]) < alpha)]


def draw_backbone(ax, routes, layout, clubs, groups):
    """Keep the original publication geometry and alpha .30 comparison frame."""
    positions = {int(r["club_id"]): np.array([float(r["x"]), float(r["y"])]) for r in layout}
    sizes = {int(r["club_id"]): float(r["node_size"]) for r in layout}
    original_pairs = {(int(r["from_club_id"]), int(r["to_club_id"])) for r in routes}
    frame = {int(r[k]) for r in retained(routes, 0.30) for k in ("from_club_id", "to_club_id")}
    selected = retained(routes, 0.20)
    active = sorted({int(r[k]) for r in selected for k in ("from_club_id", "to_club_id")})
    segments, arrows, widths = [], [], []
    for route in selected:
        u, v = int(route["from_club_id"]), int(route["to_club_id"])
        start, end = positions[u], positions[v]
        direction = end - start
        distance = np.linalg.norm(direction)
        if distance == 0:
            continue
        unit = direction / distance
        normal = np.array([-unit[1], unit[0]])
        shift = normal * 0.008 if (v, u) in original_pairs else 0
        tip = end - unit * min(0.037 + 0.002 * sizes[v], distance * 0.28) + shift
        base = tip - unit * min(0.025, distance * 0.22)
        segments.append([start + shift, tip])
        arrows.append([tip, base + 0.008 * normal, base - 0.008 * normal])
        widths.append(0.14 + 0.11 * math.sqrt(int(route["transfer_count"])))
    ax.add_collection(LineCollection(segments, linewidths=widths, colors="#555555", alpha=0.28))
    ax.add_collection(PolyCollection(arrows, facecolors="#555555", edgecolors="none", alpha=0.38))
    for group, display in groups.items():
        nodes = [i for i in active if clubs[i]["community_id"] == group]
        x, y = zip(*(positions[i] for i in nodes))
        ax.scatter(x, y, s=[sizes[i] * 0.9 * 1.5**2 for i in nodes], marker=MARKERS[group],
                   color=display["color"], linewidths=0.2, edgecolors="#333333", zorder=3)
    frame_x, frame_y = zip(*(positions[i] for i in frame))
    ax.set(xlim=(min(frame_x) - 0.06, max(frame_x) + 0.06),
           ylim=(min(frame_y) - 0.06, max(frame_y) + 0.06), aspect="equal")
    ax.set_axis_off()
    handles = [Line2D([], [], marker=MARKERS[group], linestyle="none", markersize=5.09,
                      markerfacecolor=display["color"], markeredgecolor="#333333",
                      markeredgewidth=0.25, label=display["name"])
               for group, display in groups.items()]
    return handles, len(segments)


def community_legend(ax, handles):
    legend = ax.legend(handles=handles, loc="upper right",
                        ncol=1, fontsize=8, facecolor="white", edgecolor="#BBBBBB",
                        framealpha=1, borderpad=0.55, labelspacing=0.35,
                        handlelength=1.5, handletextpad=0.5)
    legend.get_frame().set_linewidth(0.6)


def draw_h1(ax, analysis):
    # Safe import: the source module runs analysis only through its guarded main.
    # Reuse the exact saved-sample bins, normal moment convention and clear legend strip.
    _draw_shuffle_distribution(ax, analysis, "all_eligible_transfers")
    ax.set_xlabel("Premier League joining-rate gap\n(30+ minus under 30, percentage points)", labelpad=6)


def export(fig, stem):
    for extension in ("pdf", "png", "svg"):
        fig.savefig(DESTINATION / f"{stem}.{extension}", dpi=600)
    plt.close(fig)


def inspect_export(stem):
    """Inspect the actual PDFs and retain publication-size color/grayscale renders."""
    path = DESTINATION / f"{stem}.pdf"
    with fitz.open(path) as document:
        page = document[0]
        fonts = []
        for item in page.get_fonts(full=True):
            extracted = document.extract_font(item[0])
            fonts.append({"name": item[3], "type": item[2], "embedded": bool(extracted[3])})
        spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                 for line in b["lines"] for s in line["spans"]]
        assert len(document) == 1 and page.rotation == 0
        assert fonts and all("Arial" in f["name"] and f["embedded"] for f in fonts)
        assert not page.get_images(full=True)
        assert min(s["size"] for s in spans) >= 7.99
        for gray in (False, True):
            page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72),
                            colorspace=fitz.csGRAY if gray else fitz.csRGB).save(
                                DESTINATION / "qa" / f"{stem}_{'grayscale' if gray else 'color'}.png")
        result = {"page_inches": [page.rect.width / 72, page.rect.height / 72],
                  "rotation_degrees": page.rotation, "fonts": fonts,
                  "minimum_text_pt": min(s["size"] for s in spans),
                  "raster_images": len(page.get_images(full=True)),
                  "vector_paths": len(page.get_drawings()), "text": page.get_text()}
    with Image.open(DESTINATION / f"{stem}.png") as png:
        result["png_pixels"] = list(png.size)
        result["png_dpi"] = list(png.info["dpi"])
    result["svg_editable_text"] = "<text" in (DESTINATION / f"{stem}.svg").read_text(encoding="utf-8")
    assert result["svg_editable_text"]
    return result


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / "qa").mkdir(exist_ok=True)
    sources = [BACKBONE / name for name in (
        "backbone_route_scores.csv", "backbone_layout.csv", "backbone_retention.csv",
        "backbone_summary.md", "backbone_results.json", "louvain_backbone_alpha_comparison.pdf")]
    sources += [SAVED / "louvain_transfer_communities_findings/communities.csv",
                SAVED / "age_shuffle_outsideprem_toprem_results.json",
                SAVED / "age_shuffle_outsideprem_toprem_summary.md",
                SAVED / "age_shuffle_outsideprem_toprem_findings/age_shuffle_outsideprem_toprem_all_eligible_transfers.pdf",
                SAVED / "age_shuffle_outsideprem_toprem_findings/age_shuffle_outsideprem_toprem_all_eligible_transfers.png",
                Path(__file__).with_name("age_shuffle_outsideprem_toprem.py"),
                REPORT / "reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_backbone.py"]
    sources += [p for p in (SAVED / "age_shuffle_outsideprem_toprem_findings").glob("*.pdf")
                if p not in sources]
    before = {p.relative_to(REPORT).as_posix(): digest(p) for p in sources}
    routes = [r for r in read_csv(BACKBONE / "backbone_route_scores.csv") if r["scope"] == "whole"]
    layout = [r for r in read_csv(BACKBONE / "backbone_layout.csv") if r["scope"] == "whole"]
    selected = retained(routes, 0.20)
    clubs = {int(r["club_id"]): r for r in read_csv(sources[6])}
    backbone_results = json.loads((BACKBONE / "backbone_results.json").read_text(encoding="utf-8"))
    groups = backbone_results["communities"]
    h1_results = json.loads((SAVED / "age_shuffle_outsideprem_toprem_results.json").read_text(encoding="utf-8"))
    analysis = h1_results["all_eligible_transfers"]
    simulation = np.array(analysis["simulated_gaps_percentage_points"])
    young, older = (analysis["age_groups"][key] for key in ("under_30", "age_30_plus"))
    active = {int(r[k]) for r in selected for k in ("from_club_id", "to_club_id")}
    retention = next(r for r in read_csv(BACKBONE / "backbone_retention.csv")
                     if r["scope"] == "whole" and r["alpha"] == "0.2")
    assert (len(routes), sum(int(r["transfer_count"]) for r in routes), len(layout)) == (11016, 16636, 1157)
    assert (len(selected), sum(int(r["transfer_count"]) for r in selected), len(active)) == (1396, 5271, 383)
    assert all(int(retention[k]) == v for k, v in (("retained_routes", 1396), ("retained_transfers", 5271), ("active_clubs", 383)))
    assert not any(r["structural_exception"] == "True" for r in routes)
    assert analysis["sample_counts"]["eligible_transfer_records"] == 16636
    assert analysis["sample_counts"]["distinct_players"] == 4602
    assert (young["premier_league_arrival_records"], young["eligible_transfer_records"],
            older["premier_league_arrival_records"], older["eligible_transfer_records"]) == (2267, 15573, 129, 1063)
    for group in (young, older):
        assert np.isclose(group["joining_rate_percent"], 100 * group["premier_league_arrival_records"] / group["eligible_transfer_records"])
    assert np.isclose(analysis["observed_gap_percentage_points"], older["joining_rate_percent"] - young["joining_rate_percent"])
    assert len(simulation) == h1_results["n_permutations"] == 999
    assert np.isclose(simulation.mean(), analysis["shuffle_mean_gap_percentage_points"])
    tail = int(np.count_nonzero(simulation <= analysis["observed_gap_percentage_points"]))
    assert tail == analysis["simulated_gaps_less_than_or_equal_to_observed"] == 97
    assert (1 + tail) / (1 + len(simulation)) == analysis["lower_tail_one_sided_p_value"] == 0.098
    assert h1_results["shuffle_groups"] == ["from_club_id", "transfer_season"]
    assert set(h1_results["sample_and_exclusion_counts"]["eligible_records_by_season"]) == {f"{i:02d}/{i+1:02d}" for i in range(12, 25)}
    assert set(clubs) == {int(r["club_id"]) for r in layout}
    assert all(clubs[i]["color"] == groups[clubs[i]["community_id"]]["color"] for i in clubs)
    assert all(np.isclose(float(r["node_size"]), 2 + .72 * math.sqrt(
        int(clubs[int(r["club_id"])]["in_strength"]) + int(clubs[int(r["club_id"])]["out_strength"]))) for r in layout)
    font_manager.findfont("Arial", fallback_to_default=False)
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(WIDTH, HEIGHT))
        network = fig.add_axes((0.0, 0.015, 0.51, 0.80))
        handles, arrow_count = draw_backbone(network, routes, layout, clubs, groups)
        panel = fig.add_axes((0.025, 0.10, 0.49, 0.80), frameon=False)
        panel.set_axis_off()
        community_legend(panel, handles)
        draw_h1(fig.add_axes((0.595, 0.25, 0.385, 0.63)), analysis)
        fig.text(0.025, 0.925, "(a) Backbone disparity filter (α = 0.20)", fontsize=10)
        fig.text(0.595, 0.925, "(b) Premier League entry by age", fontsize=10)
        fig.canvas.draw()
        combined_network_inches = list(network.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).bounds)
        active_positions = [(float(r["x"]), float(r["y"])) for r in layout if int(r["club_id"]) in active]
        visible_positions = network.transData.transform(active_positions) / fig.dpi
        combined_node_center_bounds_inches = [*visible_positions.min(axis=0), *visible_positions.max(axis=0)]
        export(fig, "combined")
        print(DESTINATION / "combined.pdf", flush=True)
        fig = plt.figure(figsize=(8.6 / 2.54, HEIGHT))
        network = fig.add_axes((0.005, 0.015, 0.99, 0.84))
        handles, _ = draw_backbone(network, routes, layout, clubs, groups)
        panel = fig.add_axes((0.025, 0.08, 0.95, 0.90), frameon=False)
        panel.set_axis_off()
        community_legend(panel, handles)
        fig.canvas.draw()
        standalone_network_inches = list(network.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).bounds)
        export(fig, "transfer_backbone_alpha_020")
        fig = plt.figure(figsize=(8.6 / 2.54, HEIGHT))
        draw_h1(fig.add_axes((0.17, 0.25, 0.8, 0.71)), analysis)
        export(fig, "h1_all_eligible_transfers")
    assert arrow_count == len(selected)
    exports = {stem: inspect_export(stem) for stem in (
        "combined", "transfer_backbone_alpha_020", "h1_all_eligible_transfers")}
    assert "(a)" in exports["combined"]["text"] and "(b)" in exports["combined"]["text"]
    assert "Backbone disparity filter (α = 0.20)" in exports["combined"]["text"]
    for stem in ("combined", "h1_all_eligible_transfers"):
        assert all(label in exports[stem]["text"] for label in (
            "Shuffles (n = 999)", "Observed gap: -2.42", "Null mean: -1.31 ± 0.83"))
    for stem in ("transfer_backbone_alpha_020", "h1_all_eligible_transfers"):
        assert "(a)" not in exports[stem]["text"] and "(b)" not in exports[stem]["text"]
    after = {p.relative_to(REPORT).as_posix(): digest(p) for p in sources}
    assert before == after
    verification = {
        "presentation_only": True, "source_selectors": {"backbone_scope": "whole", "min_score_strictly_below": 0.2,
        "h1_key": "all_eligible_transfers", "frame_retained_endpoints_alpha": 0.3},
        "original_clubs": len(layout), "original_routes": len(routes), "eligible_records": 16636,
        "distinct_players": analysis["sample_counts"]["distinct_players"], "active_clubs": len(active),
        "retained_routes": len(selected), "retained_weighted_records": 5271,
        "volume_percent": 100 * 5271 / 16636, "structural_exceptions_whole": 0,
        "drawn_weighted_directional_arrows": arrow_count, "age_groups": analysis["age_groups"],
        "observed_gap_percentage_points": analysis["observed_gap_percentage_points"],
        "null_mean_percentage_points": float(simulation.mean()),
        "null_sample_sd_percentage_points_ddof1": float(simulation.std(ddof=1)),
        "n_saved_shuffles": len(simulation), "empirical_lower_tail_count_including_ties": tail,
        "empirical_one_sided_p": analysis["lower_tail_one_sided_p_value"],
        "source_sha256_before": before, "source_sha256_after": after,
        "sources_and_historical_exports_unchanged": before == after,
        "layout": {"community_legend": "upper right of backbone panel",
                   "node_marker_linear_scale_from_original": 1.5,
                   "node_marker_area_scale_from_original": 2.25,
                   "node_marker_area_factor_on_saved_node_size": 2.025,
                   "community_legend_marker_size_pt": 5.09,
                   "community_legend_labelspacing": 0.35,
                   "combined_network_axes_inches": combined_network_inches,
                   "combined_node_center_bounds_inches": combined_node_center_bounds_inches,
                   "combined_network_linear_scale_increase_percent": 100 * (combined_network_inches[3] / 2.28 - 1),
                   "standalone_network_axes_inches": standalone_network_inches,
                   "standalone_network_linear_scale_increase_percent": 100 * (standalone_network_inches[3] / 2.60 - 1),
                   "combined_h1_axes_figure_fraction": [0.595, 0.25, 0.385, 0.63]},
        "exports": exports, "visual_qa": "Inspect qa/*_color.png and qa/*_grayscale.png; see README for recorded review.",
        "producer_sha256": digest(Path(__file__)),
    }
    (DESTINATION / "verification.json").write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
