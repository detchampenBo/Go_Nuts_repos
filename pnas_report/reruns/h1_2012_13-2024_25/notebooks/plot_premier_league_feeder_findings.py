"""Plot the saved feeder-route findings; do not rerun the shuffle or ownership audit.

Run from any directory: python -B <project>/notebooks/plot_premier_league_feeder_findings.py
Use the agreed IEEE two-column width; retain the historical output basename.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.text import OffsetFrom
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "output"
STEM = "premier_league_feeder_findings_three_panel"
WIDTH_IN = 7.16
PRIMARY_MIN_TRANSFERS = 7
ALTERNATE_MIN_TRANSFERS = 6
BAR_COLOR, BLUE, RED = "#DC831B", "#0072B2", "#C43C39"
CHARCOAL, REMAINING_COLOR, GRID = "#333333", "#372107", "#E4E4E4"
RED_MARKER_DIAMETER_PT = np.sqrt(18) * 1.2
KEYS = ["from_club_id", "to_club_id"]


def read_and_verify():
    results = json.loads((OUTPUT_DIR / "premier_league_feeder_results.json").read_text())
    ownership = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_results.json").read_text())
    evidence = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_evidence.json").read_text())
    manifest = json.loads((PROJECT_DIR / "provenance/reduction_manifest.json").read_text())
    routes = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_routes.csv")
    audit = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    events = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_events.csv")
    selected = routes.loc[routes.selected_route].copy()
    counts = results["sample_and_exclusion_counts"]
    coverage = pd.DataFrame(results["season_coverage"])
    assert coverage.pl_arrivals.sum() == routes.observed_count.sum() == counts["premier_league_arrival_records"]
    assert coverage.eligible_records.sum() == counts["eligible_transfer_records"] == manifest["restricted"]["rows"]
    observed = routes.loc[routes.observed_count.gt(0)]
    assert len(observed) == results["observed_routes"]
    assert observed.from_club_id.nunique() == counts["origin_clubs"]
    assert observed.to_club_id.nunique() == counts["destination_clubs"]
    assert len(routes) == results["testing_family_size"]
    assert np.isclose(routes.expected_count.sum(), counts["premier_league_arrival_records"])
    assert results["n_permutations"] == 999 and results["seed"] == 2026
    assert results["adjustment_method"] == "none"
    assert results["significance_threshold"] == 0.05
    assert results["minimum_route_transfers"] == 2
    assert np.array_equal(routes.significant, routes.p_value.lt(0.05))
    assert np.array_equal(routes.selected_route, routes.p_value.lt(0.05) & routes.observed_count.ge(2))
    assert np.allclose(routes.p_value, (1 + routes.permutations_greater_or_equal) / 1000)
    assert routes.significant.sum() == results["significant_route_count"]
    assert len(selected) == results["selected_route_count"] == len(audit)
    assert selected.observed_count.ge(2).all() and not audit.duplicated(KEYS).any()
    pd.testing.assert_frame_equal(selected.sort_values(KEYS).reset_index(drop=True),
                                  audit.sort_values(KEYS).reset_index(drop=True)[routes.columns])
    event_counts = events.groupby(KEYS).size().rename("observed_count")
    concurrent = events.groupby(KEYS).confirmed_shared_owner_on_record_date.sum()
    indexed = audit.set_index(KEYS).sort_index()
    assert indexed.observed_count.equals(event_counts.sort_index())
    assert np.array_equal(indexed.ownership_concurrent_records, concurrent.sort_index())
    assert np.array_equal(audit.has_ownership_concurrent_record, audit.ownership_concurrent_records.gt(0))
    assert audit.documented_shared_owner_during_model_interval.sum() == ownership["documented_shared_owner_pairs_during_model_interval"]
    assert events.ownership_boundary_uncertain.sum() == ownership["date_boundary_uncertain_records"]
    assert len(events) == audit.observed_count.sum() == results["selected_transfer_records"] == ownership["selected_transfer_records"]
    assert np.array_equal(audit.joint_ownership_group,
                          audit.has_ownership_concurrent_record | audit.manual_joint_ownership_inclusion)
    manual = audit.loc[audit.manual_joint_ownership_inclusion]
    assert set(zip(manual.from_club_id, manual.to_club_id)) == {
        (row["from_club_id"], row["to_club_id"]) for row in evidence["manual_joint_ownership_pairs"]}
    assert not manual.documented_shared_owner_during_model_interval.any()
    groups = [audit.loc[audit.joint_ownership_group.eq(flag)] for flag in [True, False]]
    assert len(groups[0]) == ownership["joint_ownership_group_pairs"]
    assert sum(len(group) for group in groups) == len(audit)
    assert all(group.observed_count.ge(2).all() for group in groups)
    assert groups[0].ownership_concurrent_records.sum() == ownership["ownership_concurrent_transfer_records"]
    ledger = pd.read_csv(PROJECT_DIR / "provenance/ownership_coverage_ledger.csv")
    assert set(ledger[KEYS].itertuples(index=False, name=None)) == set(audit[KEYS].itertuples(index=False, name=None))
    assert audit.ownership_status.eq("not_screened_new_selected_route").sum() == (
        ledger.coverage_status.eq("new_selected_route_not_screened").sum())
    assert ownership["screened_unique_pairs"] == len(audit) - audit.ownership_status.eq(
        "not_screened_new_selected_route").sum()
    display_routes = selected.loc[selected.observed_count.ge(ALTERNATE_MIN_TRANSFERS)].sort_values(
        ["observed_count", *KEYS], ascending=[False, True, True]
    ).merge(audit[KEYS + ["joint_ownership_group", "ownership_concurrent_records",
                        "manual_joint_ownership_inclusion"]], on=KEYS, validate="one_to_one")
    assert len(display_routes) == selected.observed_count.ge(ALTERNATE_MIN_TRANSFERS).sum()
    return results, coverage, display_routes, groups


def style_axis(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_linewidth(0.6)
    ax.tick_params(length=2.5, width=0.6, pad=2)


def plot_figure(top, groups, height_in=4.6, route_y_min=-.75):
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 9.5, "text.color": CHARCOAL,
        "axes.labelcolor": CHARCOAL, "axes.edgecolor": CHARCOAL,
        "xtick.color": CHARCOAL, "ytick.color": CHARCOAL,
        "axes.labelsize": 9.5, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(WIDTH_IN, height_in))
    ax_a = fig.add_axes([.045, .15, .44, .775])
    ax_b = fig.add_axes([.615, .15, .37, .775])
    for ax, title in [(ax_a, "(a) Frequent transfer routes"),
                      (ax_b, "(b) Transfer-count exceedance")]:
        style_axis(ax)
        ax.set_title(title, loc="left", fontsize=10, pad=10)

    aliases = {12321: "Girona", 667: "Strasbourg", 410: "Udinese", 399: "Leeds",
               543: "Wolves", 631: "Chelsea", 1010: "Watford", 148: "Tottenham"}
    positions = np.arange(len(top))[::-1] * 1.35
    for y, row in zip(positions, top.itertuples()):
        origin = aliases.get(row.from_club_id, row.from_club_name)
        destination = aliases.get(row.to_club_id, row.to_club_name)
        bar_y = y - .08
        ax_a.axhline(bar_y, color=GRID, linewidth=.45, zorder=0)
        origin_name = ax_a.text(0, y + .39, origin, va="center")
        arrow_origin = OffsetFrom(origin_name, (1, .5))
        ax_a.annotate("", xy=(16, 0), xycoords=arrow_origin,
                      xytext=(4, 0), textcoords=arrow_origin,
                      arrowprops={"arrowstyle": "simple,head_length=.4,head_width=.6,tail_width=.25",
                                  "mutation_scale": 9.5, "facecolor": CHARCOAL,
                                  "edgecolor": "none", "shrinkA": 0, "shrinkB": 0})
        route_name = ax_a.annotate(destination, xy=(20, 0), xycoords=arrow_origin,
                                   va="center")
        ax_a.barh(bar_y, row.observed_count, height=.25, color=BAR_COLOR, zorder=2)
        ax_a.scatter(row.expected_count, bar_y, marker="D", s=30,
                     facecolor=BLUE, edgecolor="white", linewidth=.5, zorder=4)
        ax_a.text(row.observed_count + .35, bar_y, str(row.observed_count),
                  va="center", fontweight="bold")
        ax_a.text(max(row.expected_count, 1.1), y - .44, f"{row.expected_count:.1f}",
                  color=BLUE, ha="center", va="center", fontsize=9)
        if row.ownership_concurrent_records or row.manual_joint_ownership_inclusion:
            annotation = (f"{row.ownership_concurrent_records}/{row.observed_count}"
                          if row.ownership_concurrent_records else str(row.observed_count))
            if row.manual_joint_ownership_inclusion and not row.ownership_concurrent_records:
                # Manual inclusion coverage, not a verified ownership-period count.
                annotation = f"{row.observed_count}/{row.observed_count}"
            dot_area = DrawingArea(RED_MARKER_DIAMETER_PT, RED_MARKER_DIAMETER_PT, 0, 0)
            dot_area.add_artist(Line2D([RED_MARKER_DIAMETER_PT / 2],
                                      [RED_MARKER_DIAMETER_PT / 2], marker="o",
                                      markersize=RED_MARKER_DIAMETER_PT, color=RED,
                                      markeredgewidth=0, linestyle="none"))
            ax_a.add_artist(AnnotationBbox(dot_area, (1, .5), xycoords=route_name,
                                          xybox=(6, 0), boxcoords="offset points",
                                          box_alignment=(0, .5), frameon=False, pad=0))
            ax_a.annotate(annotation, xy=(1, .5), xycoords=route_name,
                          xytext=(9 + RED_MARKER_DIAMETER_PT, 0), textcoords="offset points",
                          color=RED, va="center", fontsize=9)
    ax_a.set(xlim=(0, 20), ylim=(route_y_min, positions[0] + .82), yticks=[],
             xlabel="Recorded transfers per route")
    ax_a.xaxis.set_major_locator(MultipleLocator(5))
    ax_a.legend(handles=[Line2D([0], [0], color=BAR_COLOR, lw=5, label="Observed transfers"),
                         Line2D([0], [0], color=BLUE, marker="D", linestyle="none",
                                markersize=4.5, label="Expected transfers\n(null model)"),
                         Line2D([0], [0], color=RED, marker="o", linestyle="none",
                                markersize=RED_MARKER_DIAMETER_PT, markeredgewidth=0,
                                label="Joint ownership")],
                loc="lower right", ncol=1, frameon=True, fancybox=True,
                facecolor="white", edgecolor="#BBBBBB", framealpha=1,
                borderaxespad=.15, borderpad=.45, fontsize=8,
                labelspacing=.45, handlelength=1.3)

    thresholds = np.arange(0, max(group.observed_count.max() for group in groups) + 2)
    for group, color in zip(groups, [RED, REMAINING_COLOR]):
        counts = group.observed_count.to_numpy()
        exceedance = 100 * (counts[:, None] >= thresholds).mean(axis=0)
        # Inclusive P(count >= x); pre-steps preserve the integer threshold values.
        ax_b.step(thresholds, exceedance, where="pre", color=color,
                  linestyle="-", linewidth=1.5)
    ax_b.set(xlim=(thresholds[0], thresholds[-1]), ylim=(0, 105),
             xlabel="Recorded transfers per route",
             ylabel="Routes with at least x transfers (%)")
    ax_b.xaxis.set_major_locator(MultipleLocator(2))
    ax_b.yaxis.set_major_locator(MultipleLocator(20))
    ax_b.grid(True, axis="both", which="major", color="#B0B0B0", linewidth=.65)
    linked, remaining = groups
    ax_b.legend(handles=[
        Line2D([], [], color=RED, linestyle="-", linewidth=1.5,
               label=f"Joint ownership (n = {len(linked)})"),
        Line2D([], [], color=REMAINING_COLOR, linestyle="-", linewidth=1.5,
               label=f"Remaining routes (n = {len(remaining)})"),
    ], loc="upper right", ncol=1, frameon=True, fancybox=True,
       facecolor="white", edgecolor="#BBBBBB", framealpha=1,
       fontsize=8, borderaxespad=.6, borderpad=.6,
       handlelength=1.8, handletextpad=.6, labelspacing=.7)
    for ax in [ax_a, ax_b]:
        ax.get_legend().get_frame().set_linewidth(.6)
    return fig


def write_caption():
    caption = ("# Premier League feeder routes and ownership\n\n"
               "(a) Observed and seasonal-null expected transfer counts for selected routes "
               f"with at least {PRIMARY_MIN_TRANSFERS} recorded transfers. "
               "Red fractions count selected transfers during verified common-equity intervals. "
               "For Grasshoppers → Wolves and Vitesse → Chelsea, the fractions show the coverage of the "
               "existing manual inclusions, which use all selected records for those routes. "
               "(b) Percentage of routes with at least each transfer count. The joint-ownership group includes "
               "the verified transfer-date matches and the two manual inclusions, Grasshoppers → Wolves and "
               "Vitesse → Chelsea. For the remaining routes, the bounded source screen leaves common "
               "ownership unconfirmed or documents it outside the selected transfer dates.\n")
    (OUTPUT_DIR / f"{STEM}_caption.md").write_text(caption, encoding="utf-8")


def write_findings(results, coverage, top, groups):
    linked, remaining = groups
    counts = results["sample_and_exclusion_counts"]
    ownership = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_results.json").read_text())
    ledger = pd.read_csv(PROJECT_DIR / "provenance/ownership_coverage_ledger.csv")
    newly_screened = int(ledger.coverage_status.eq("new_selected_route_screened").sum())
    unscreened = int(ledger.coverage_status.eq("new_selected_route_not_screened").sum())
    manual = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    manual = manual.loc[manual.manual_joint_ownership_inclusion]
    section = f"""## Two-panel feeder findings

The restricted recorded seasons are 2012/13–2024/25, with actual eligible-input dates 1 July 2012–15 July 2025. Coverage is not certified exhaustive. There are {counts['premier_league_arrival_records']:,} recorded PL arrivals from {counts['origin_clubs']} supplying clubs to {counts['destination_clubs']} receiving clubs ({counts['distinct_players']:,} distinct players). These are separate from the Guardian samples. Counts include repeat players, loans and returns. The source-season convention and original eligibility rules are retained.

Destinations are reassigned within each season, preserving seasonal origin and destination margins. Seed {results['seed']} and {results['n_permutations']} shuffles are unchanged. Expected counts sum origin-arrivals × destination-arrivals / all-arrivals over seasons. The upper-tail Monte Carlo p value includes ties and uses (1 + tail) / 1000. All {results['testing_family_size']:,} positive-expectation pairs are tested, including unobserved pairs. No multiplicity correction is applied. Of {results['significant_route_count']} pairs with unadjusted p<0.05, {results['selected_route_count']} have at least two recorded moves and contain {results['selected_transfer_records']} records.

Panel (a) displays all {len(top)} selected routes with observed count ≥{PRIMARY_MIN_TRANSFERS}, with ties retained and descending counts/club-ID ordering. Orange bars give observed counts and blue diamonds give expected counts, labelled to one decimal. Panel (b) uses the full selected sample.

| Route | Observed | Expected | Ownership annotation |
| --- | ---: | ---: | --- |
"""
    for row in top.itertuples():
        note = (f"{row.ownership_concurrent_records}/{row.observed_count} verified interval overlap" if row.ownership_concurrent_records else
                f"{row.observed_count}/{row.observed_count} manual inclusion coverage; interval unverified" if row.manual_joint_ownership_inclusion else
                "No documented shared-equity annotation; absence is not proven independence")
        section += f"| {row.from_club_name} → {row.to_club_name} | {row.observed_count} | {row.expected_count:.1f} | {note} |\n"
    section += f"""

Shared ownership means a documented common direct or indirect club-equity investor, including minority holdings. Source intervals are start-inclusive and exit-exclusive. Red dots mark the existing joint-ownership group. Verified fractions count event-date overlaps; manual fractions indicate inclusion coverage and are not verified ownership-period counts. The two authorised manual pairs remain:

"""
    for row in manual.itertuples():
        section += f"- {row.from_club_name} → {row.to_club_name}: {row.observed_count} pooled records; equity interval remains unverified.\n"
    section += f"""

The bounded source screen covers {len(ledger) - unscreened} of {len(ledger)} selected routes, including {newly_screened} additional routes reviewed for this rerun. The coverage ledger records the status of each route. The scoped evidence omits the historical Hearts/Liverpool interval because it predates the restricted period. Historical minority and beneficial-owner disclosures remain incomplete, so documented counts are a confirmed minimum. [Coverage ledger](../provenance/ownership_coverage_ledger.csv) · [Additional route screen](../provenance/ownership_screen_28_routes.md)

Panel (b) gives 100 × the fraction of each entire group with at least each integer transfer count, using inclusive pre-step curves. There is no binning, smoothing, jitter or fitted distribution. The red group contains {len(linked)} routes and the dark-brown remaining group {len(remaining)}. Curves use all {len(linked)+len(remaining)} selected observations and end at zero one count above the observed maximum. Means and medians describe pooled route counts, not ownership-period transfer counts.

| Group | Routes | Pooled records | Mean | Median |
| --- | ---: | ---: | ---: | ---: |
| Joint ownership | {len(linked)} | {int(linked.observed_count.sum())} | {linked.observed_count.mean():.6f} | {linked.observed_count.median():g} |
| Remaining routes | {len(remaining)} | {int(remaining.observed_count.sum())} | {remaining.observed_count.mean():.6f} | {remaining.observed_count.median():g} |

Of {int(linked.observed_count.sum())} pooled records in the joint group, {ownership['ownership_concurrent_transfer_records']} have verified event-date ownership overlap. This descriptive comparison concerns the selected recurring routes. Estimating an ownership effect or network-wide overrepresentation would require further evidence.

[Ownership evidence](premier_league_feeder_ownership_evidence.json), [route audit](premier_league_feeder_ownership_audit.csv), [event flags](premier_league_feeder_ownership_events.csv), [ownership results](premier_league_feeder_ownership_results.json).

![Restricted feeder findings](premier_league_feeder_findings_three_panel.png)

[PDF](premier_league_feeder_findings_three_panel.pdf), [SVG](premier_league_feeder_findings_three_panel.svg), [caption](premier_league_feeder_findings_three_panel_caption.md), [combined and standalone exports](premier_league_feeder_findings/README.md).

"""
    path = OUTPUT_DIR / "premier_league_feeder_summary.md"
    summary = path.read_text(encoding="utf-8")
    start = summary.find("## Two-panel feeder findings\n")
    end = summary.index("## Figures\n")
    if start == -1:
        start = end
    path.write_text(summary[:start] + section + summary[end:], encoding="utf-8")


def save_figure(fig, stem):
    for extension in ["png", "pdf", "svg"]:
        # Preserve the requested physical width rather than cropping the canvas.
        fig.savefig(stem.with_suffix(f".{extension}"), dpi=600)


def main():
    results, coverage, display_routes, groups = read_and_verify()
    top = display_routes.loc[display_routes.observed_count.ge(PRIMARY_MIN_TRANSFERS)]
    figure_dir = OUTPUT_DIR / "premier_league_feeder_findings"
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig = plot_figure(top, groups)
    save_figure(fig, OUTPUT_DIR / STEM)
    save_figure(fig, figure_dir / "combined")
    plt.close(fig)
    # Leave space for the legend below the lowest route name.
    fig = plot_figure(display_routes, groups, height_in=7.4, route_y_min=-2.3)
    fig.savefig(figure_dir / f"combined_min_{ALTERNATE_MIN_TRANSFERS}.pdf", dpi=600)
    plt.close(fig)
    for panel_index, stem, position in [
        (0, "frequent_transfer_routes", [.09, .15, .88, .775]),
        (1, "transfer_count_exceedance", [.19, .15, .78, .775]),
    ]:
        fig = plot_figure(top, groups)
        ax = fig.axes[panel_index]
        fig.delaxes(fig.axes[1 - panel_index])
        fig.set_size_inches(WIDTH_IN / 2, 4.6)
        ax.set_position(position)
        ax.set_title("", loc="left")
        save_figure(fig, figure_dir / stem)
        plt.close(fig)
    (figure_dir / "README.md").write_text(
        "# Premier League feeder findings\n\n"
        "| Plot | PDF | PNG (600 dpi) | SVG |\n"
        "| --- | --- | --- | --- |\n"
        "| Combined | [PDF](combined.pdf) | [PNG](combined.png) | [SVG](combined.svg) |\n"
        "| Frequent transfer routes (section A) | [PDF](frequent_transfer_routes.pdf) | "
        "[PNG](frequent_transfer_routes.png) | [SVG](frequent_transfer_routes.svg) |\n"
        "| Transfer-count exceedance (section B) | [PDF](transfer_count_exceedance.pdf) | "
        "[PNG](transfer_count_exceedance.png) | [SVG](transfer_count_exceedance.svg) |\n\n"
        f"The primary combined figure displays {len(top)} routes with at least {PRIMARY_MIN_TRANSFERS} recorded transfers. "
        f"The [alternate PDF](combined_min_{ALTERNATE_MIN_TRANSFERS}.pdf) displays all {len(display_routes)} routes "
        f"with at least {ALTERNATE_MIN_TRANSFERS} recorded transfers.\n\n"
        "The combined figure is 7.16 inches wide. Standalone plots are 3.58 inches wide "
        "with the same Arial typography and colours, and omit titles and subfigure letters. "
        "PDFs are vector exports with embedded fonts.\n\n"
        "Data, selection and ownership classifications are shared across the plots: "
        f"{results['selected_route_count']} selected recurring routes, with groups of {len(groups[0])} and {len(groups[1])}. "
        "The bounded ownership screen and the two manual inclusions are described in the caption and findings recap. "
        "See the [findings recap](../premier_league_feeder_summary.md) for methods and interpretation.\n\n"
        "Reproduce with `conda run -n machine-learning --no-capture-output python -B "
        "pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_premier_league_feeder_findings.py`.\n",
        encoding="utf-8")
    write_caption()
    write_findings(results, coverage, top, groups)
    print(f"Verified {len(top)} primary and {len(display_routes)} alternate displayed routes. "
          f"Panel (b) uses {sum(len(g) for g in groups)} selected routes in groups {[len(g) for g in groups]}.")
    print(f"Saved 7.16-inch PDF, PNG (600 dpi), SVG and brief caption: {OUTPUT_DIR / STEM}")
    print(f"Saved combined and standalone plots (PDF, PNG, SVG): {figure_dir}")
    print("Updated findings recap: premier_league_feeder_summary.md")


if __name__ == "__main__":
    main()
