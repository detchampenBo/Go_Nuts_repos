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
BAR_COLOR, BLUE, RED = "#DC831B", "#0072B2", "#C43C39"
CHARCOAL, REMAINING_COLOR, GRID = "#333333", "#372107", "#E4E4E4"
RED_MARKER_DIAMETER_PT = np.sqrt(18) * 1.2
KEYS = ["from_club_id", "to_club_id"]


def read_and_verify():
    results = json.loads((OUTPUT_DIR / "premier_league_feeder_results.json").read_text())
    routes = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_routes.csv")
    audit = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    events = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_events.csv")
    selected = routes.loc[routes.selected_route].copy()
    counts = results["sample_and_exclusion_counts"]
    coverage = pd.DataFrame(results["season_coverage"])
    assert [counts[k] for k in ["premier_league_arrival_records", "origin_clubs",
                               "destination_clubs", "eligible_transfer_records",
                               "distinct_players"]] == [2882, 500, 42, 19712, 1445]
    assert coverage.pl_arrivals.sum() == routes.observed_count.sum() == 2882
    assert coverage.eligible_records.sum() == 19712
    observed = routes.loc[routes.observed_count.gt(0)]
    assert len(observed) == results["observed_routes"] == 1988
    assert observed.from_club_id.nunique() == 500
    assert observed.to_club_id.nunique() == 42
    assert len(routes) == results["testing_family_size"] == 12742
    assert np.isclose(routes.expected_count.sum(), 2882)
    assert results["n_permutations"] == 999 and results["seed"] == 2026
    assert results["adjustment_method"] == "none"
    assert results["significance_threshold"] == 0.05
    assert results["minimum_route_transfers"] == 2
    assert np.array_equal(routes.significant, routes.p_value.lt(0.05))
    assert np.array_equal(routes.selected_route, routes.p_value.lt(0.05) & routes.observed_count.ge(2))
    assert np.allclose(routes.p_value, (1 + routes.permutations_greater_or_equal) / 1000)
    assert routes.significant.sum() == results["significant_route_count"] == 328
    assert len(selected) == results["selected_route_count"] == len(audit) == 239
    assert selected.observed_count.ge(2).all()
    assert not audit.duplicated(KEYS).any()
    pd.testing.assert_frame_equal(
        selected.sort_values(KEYS).reset_index(drop=True),
        audit.sort_values(KEYS).reset_index(drop=True)[routes.columns],
    )
    event_counts = events.groupby(KEYS).size().rename("observed_count")
    concurrent = events.groupby(KEYS).confirmed_shared_owner_on_record_date.sum()
    indexed = audit.set_index(KEYS).sort_index()
    assert indexed.observed_count.equals(event_counts.sort_index())
    assert np.array_equal(indexed.ownership_concurrent_records, concurrent.sort_index())
    assert np.array_equal(audit.has_ownership_concurrent_record,
                          audit.ownership_concurrent_records.gt(0))
    assert audit.documented_shared_owner_during_model_interval.sum() == 17
    assert events.ownership_boundary_uncertain.sum() == 0
    assert len(events) == audit.observed_count.sum() == results["selected_transfer_records"] == 721
    assert np.array_equal(audit.joint_ownership_group,
                          audit.has_ownership_concurrent_record | audit.manual_joint_ownership_inclusion)
    manual = audit.loc[audit.manual_joint_ownership_inclusion]
    assert set(zip(manual.from_club_id, manual.to_club_id)) == {(499, 631), (504, 543)}
    assert manual.set_index(KEYS).observed_count.to_dict() == {(499, 631): 8, (504, 543): 10}
    assert not manual.documented_shared_owner_during_model_interval.any()
    groups = [audit.loc[audit.joint_ownership_group.eq(flag)]
              for flag in [True, False]]
    assert [len(g) for g in groups] == [17, 222]
    assert [g.observed_count.sum() for g in groups] == [97, 624]
    assert [g.observed_count.median() for g in groups] == [4, 2]
    assert [round(g.observed_count.mean(), 2) for g in groups] == [5.71, 2.81]
    assert [g.observed_count.eq(1).sum() for g in groups] == [0, 0]
    assert groups[0].ownership_concurrent_records.sum() == 73
    top = selected.loc[selected.observed_count.ge(8)].sort_values(
        ["observed_count", *KEYS], ascending=[False, True, True]
    ).merge(audit[KEYS + ["joint_ownership_group", "ownership_concurrent_records",
                        "manual_joint_ownership_inclusion"]],
            on=KEYS, validate="one_to_one")
    assert list(zip(top.from_club_id, top.to_club_id)) == [
        (12321, 281), (667, 631), (504, 543), (410, 1010), (399, 148), (499, 631)
    ]
    assert top.observed_count.tolist() == [17, 11, 10, 9, 8, 8]
    assert np.allclose(top.expected_count.round(3), [1.910, 1.636, .953, .846, 1.771, 1.361])
    assert top.ownership_concurrent_records.tolist() == [12, 11, 0, 9, 0, 0]
    return results, coverage, top, groups


def style_axis(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_linewidth(0.6)
    ax.tick_params(length=2.5, width=0.6, pad=2)


def plot_figure(top, groups):
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 9.5, "text.color": CHARCOAL,
        "axes.labelcolor": CHARCOAL, "axes.edgecolor": CHARCOAL,
        "xtick.color": CHARCOAL, "ytick.color": CHARCOAL,
        "axes.labelsize": 9.5, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(WIDTH_IN, 4.6))
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
    ax_a.set(xlim=(0, 20), ylim=(-.75, positions[0] + .82), yticks=[],
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
               "(a) Observed and seasonal-null expected transfer counts for the displayed routes. "
               "(b) Percentage of routes with at least each transfer count, by ownership group.\n")
    (OUTPUT_DIR / f"{STEM}_caption.md").write_text(caption, encoding="utf-8")


def write_findings(results, coverage, top, groups):
    """Keep the figure's methods and results in the existing feeder recap."""
    linked, remaining = groups
    counts = results["sample_and_exclusion_counts"]
    final = coverage.iloc[-1]
    section = f"""## Two-panel feeder findings

The publication figure has two panels: **(a) Frequent transfer routes** and **(b) Transfer-count exceedance**. It is {WIDTH_IN:.2f} inches wide with Arial main labels at 9-10 pt and legends at 8 pt, using the agreed IEEE two-column width because the repository contains a PNAS template rather than an IEEE template. Lowercase parenthesised labels follow the requested subfigure convention. The historical output basename is retained for existing references.

### Sample coverage and selection

The underlying sample comprises **{counts['premier_league_arrival_records']:,} recorded Premier League arrivals**, **{counts['distinct_players']:,} distinct players**, **{counts['origin_clubs']} supplying clubs**, **{counts['destination_clubs']} receiving clubs**, and **{results['observed_routes']:,} observed directed routes**, within **{counts['eligible_transfer_records']:,} eligible records originating outside the Premier League. Premier League membership is evaluated in the transfer season. Roles remain separate when a club supplies in one season and receives in another.

The removed arrivals panel described coverage, not a population trend. Early coverage is sparse: 00/01 and 02/03 have no recorded PL arrivals, and 03/04 and 04/05 have two each. Season 01/02 is absent, not an imputed zero. The final recorded season, **{final.transfer_season}**, is partial, with **{int(final.pl_arrivals)} PL arrivals** among **{int(final.input_records)} input records**; dates extend to **{final.input_date_max}**, including future-dated or scheduled movements and possible loan returns. Recorded arrivals and their changes across seasons do not establish a population trend or complete season coverage. The full season table below preserves the removed panel's coverage context.

Selected routes require **at least {results['minimum_route_transfers']} recorded transfers per directed club pair** and **unadjusted upper-tail shuffle p < {results['significance_threshold']}**. The statistical threshold identifies unusually concentrated movement; the minimum count is a design choice to focus on recurring movement. The shuffle uses the full arrival sample before either route-level filter is applied. Of **{results['significant_route_count']}** routes passing the p-value criterion, **{results['selected_route_count']}** meet both criteria and contain **{results['selected_transfer_records']} recorded transfers**. Counts include repeated players, loans and returns, not necessarily distinct players or permanent sales.

### Seasonal null and panel (a)

Within each season, destinations are reassigned among arrival records, preserving every origin's number of PL-bound records and every destination's recruitment total. Origins, players and seasons remain fixed. There are **{results['n_permutations']} shuffles**, with seed **{results['seed']}**. Each pooled expected count is the sum across seasons of `origin_PL_arrivals * destination_arrivals / total_PL_arrivals`. The Monte Carlo p-value is `(1 + number of shuffles with count >= observed count) / (1 + permutations)`, with ties included and minimum/grid spacing {results['permutation_p_value_resolution']}. Tests cover all **{results['testing_family_size']:,}** positive-expectation pairs, including unobserved pairs. P-values are unadjusted; no multiple-comparison correction is applied.

Panel (a) displays **all {len(top)} selected routes with at least eight recorded transfers**, in descending observed-count order with club-ID tie breaks. Both eight-transfer routes are retained, so every tie at the cutoff is included. This is a readability subset, not the sample used to calculate ownership-group statistics. Orange bars (#DC831B) and end labels give observed totals; blue diamonds give seasonal-null expected counts. Expected labels are rounded to exactly one decimal place for display; all calculations retain full precision. These expectations refer to pooled route counts, not specifically the ownership period.

| Route | Observed | Expected (display) | Ownership annotation |
| --- | ---: | ---: | --- |
"""
    for row in top.itertuples():
        annotation = (f"{row.ownership_concurrent_records}/{row.observed_count}"
                      if row.ownership_concurrent_records else
                      f"{row.observed_count} (pooled route total; manual inclusion)" if row.manual_joint_ownership_inclusion else
                      "None: shared ownership not documented")
        if row.manual_joint_ownership_inclusion and not row.ownership_concurrent_records:
            annotation = f"{row.observed_count}/{row.observed_count} (manual inclusion coverage; ownership-period count unverified)"
        section += (f"| {row.from_club_name} \u2192 {row.to_club_name} | {row.observed_count} "
                    f"| {row.expected_count:.1f} | {annotation} |\n")
    section += f"""
A red dot beside the destination club's name denotes **Joint ownership**. Where ownership-period overlap is documented, the adjacent **x/n** reports the number of selected records within a documented common-ownership interval (**x**) divided by the route's full pooled record count (**n**). Numerators are checked against the event-level `confirmed_shared_owner_on_record_date` flags. Thus Girona-Manchester City is **12/17**, Strasbourg-Chelsea **11/11**, and Udinese-Watford **9/9**. Five Girona records precede the acquisition. Vitesse-Chelsea's **8/8** and Grasshoppers-Wolves' **10/10** are exceptions: they report all pooled route records included by manual classification, not verified ownership-period fractions. No manual-inclusion labels are displayed in the figure. Leeds-Tottenham has no red dot or fraction because shared ownership was not documented; missing documentation is not proof that the true overlap count is zero.

### Ownership definition and manual additions

The source audit defines shared ownership as a documented common direct or indirect club-equity investor, including minority holdings; accounting common-control disclosures require club-ownership corroboration. Owner names, sources and inclusive-start/exclusive-exit date brackets are retained in [the evidence input](premier_league_feeder_ownership_evidence.json), [route audit](premier_league_feeder_ownership_audit.csv), and [event flags](premier_league_feeder_ownership_events.csv). The [source-linked ownership note](../notes/premier_league_feeder_ownership_audit.md) records the evidence and its limitations. A sponsor, lender, loan partnership or family relationship alone does not establish a common equity investor.

The joint-ownership analysis group comprises **15 routes with verified transfer-period overlap plus two manual additions**, **Vitesse-Chelsea** and **Grasshoppers-Wolves**, included by user decision. These additions contribute **8** and **10** pooled records, respectively. Their common-equity intervals and event-level ownership overlap have not been verified. They appear with a red dot and **8/8 for Vitesse-Chelsea (manual inclusion coverage)** and **10/10 for Grasshoppers-Wolves (manual inclusion coverage)**, rather than daggers. Neither annotation establishes how many moves occurred during shared ownership. The zero verified-event flags for these manual additions encode a lack of confirmation, not a measured absence of overlap. Their source-evidence classifications remain unchanged.

### Panel (b): exceedance distributions and group statistics

Panel (b) replaces the individual dot matrix with **empirical exceedance curves** using all **{len(linked) + len(remaining)}** selected routes. At each integer threshold **x**, a curve gives **100 times the number of routes with at least x recorded transfers divided by that group's total number of routes**. The comparison is normalised separately within the **{len(linked)} joint-ownership routes** and **{len(remaining)} remaining routes**, so their unequal sample sizes do not determine curve heights. Equality is included: a route with four transfers contributes at x = 4, but not x = 5. All 239 source observations contribute to the curves, although individual route markers are no longer drawn. There is no jitter, binning, density smoothing or fitted distribution.

The joint-ownership curve is solid red (#C43C39); the remaining-route curve is solid dark brown (#372107). Red retains the ownership meaning from panel (a); the dark-brown curve has a darker luminance for grayscale reproduction. The x-axis is recorded transfers per route; the y-axis is the percentage of routes with at least that many transfers. Pre-step lines represent the inclusive exceedance probabilities between integer thresholds. Both curves remain at 100% from zero through the selection minimum of two transfers and reach zero at 18, one above the observed maximum of 17.

| Group | Routes | Pooled records | Arithmetic mean | Median |
| --- | ---: | ---: | ---: | ---: |
| Joint ownership | {len(linked)} | {int(linked.observed_count.sum())} | {linked.observed_count.mean():.6f} | {linked.observed_count.median():g} |
| Remaining routes | {len(remaining)} | {int(remaining.observed_count.sum())} | {remaining.observed_count.mean():.6f} | {remaining.observed_count.median():g} |

Both arithmetic means and medians are calculated across the **entire respective group**, not the six routes shown in panel (a). The upper-right legend has two vertically stacked entries, Joint ownership and Remaining routes, with their sample sizes and matching line colours. Means and medians are retained in the table above; neither statistical labels nor reference lines are drawn in the figure.

| At least this many transfers | Joint ownership | Remaining routes |
| --- | ---: | ---: |


"""
    for threshold in [4, 8]:
        section += (f"| {threshold} | {100 * linked.observed_count.ge(threshold).mean():.1f}% "
                    f"| {100 * remaining.observed_count.ge(threshold).mean():.1f}% |\n")
    section += f"""

These threshold examples are read from the full curves; all integer thresholds from 0 through 18 are displayed. Starting the axis at zero does not add routes with zero or one transfer to the selected sample.

This is a **descriptive comparison of pooled route counts within the selected sample**. The joint group contains {int(linked.observed_count.sum())} pooled records, of which {int(linked.ownership_concurrent_records.sum())} have verified ownership-period overlap; five Girona records and one Lorient record precede ownership completion, while the 18 records on the manual additions have unverified timing. The remaining group includes unresolved evidence and two historical-only common-equity pairs (Granada-Watford and Hearts-Liverpool); it is not a verified independently owned control group. The comparison does not establish an ownership effect, causation, financial mechanism, or overrepresentation across the whole transfer network.

![Recurring transfer routes and ownership](premier_league_feeder_findings_three_panel.png)

[Vector PDF](premier_league_feeder_findings_three_panel.pdf) \u00b7 [High-resolution PNG](premier_league_feeder_findings_three_panel.png) \u00b7 [Editable SVG](premier_league_feeder_findings_three_panel.svg) \u00b7 [Brief caption](premier_league_feeder_findings_three_panel_caption.md)

The [figure export folder](premier_league_feeder_findings/README.md) contains the combined figure and separate plots of [frequent transfer routes](premier_league_feeder_findings/frequent_transfer_routes.pdf) and [transfer-count exceedance](premier_league_feeder_findings/transfer_count_exceedance.pdf), each as PDF, PNG and SVG. Standalone plots use a 3.58-inch page width and omit titles and subfigure letters; the combined figure retains its 7.16-inch width and panel labels.

Reproduce the figure and this recap section with `python -B pnas_report/notebooks/plot_premier_league_feeder_findings.py`. The plotting script verifies the saved analysis; it does not rerun the shuffle or change ownership classifications.

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
    results, coverage, top, groups = read_and_verify()
    figure_dir = OUTPUT_DIR / "premier_league_feeder_findings"
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig = plot_figure(top, groups)
    save_figure(fig, OUTPUT_DIR / STEM)
    save_figure(fig, figure_dir / "combined")
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
        "The combined figure is 7.16 inches wide. Standalone plots are 3.58 inches wide "
        "with the same Arial typography and colours, and omit titles and subfigure letters. "
        "PDFs are vector exports with embedded fonts.\n\n"
        "Data, selection and ownership classifications are shared by all three views: "
        "239 selected recurring routes, with groups of 17 and 222. "
        "See the [findings recap](../premier_league_feeder_summary.md) for methods and interpretation.\n\n"
        "Reproduce with `python -B pnas_report/notebooks/plot_premier_league_feeder_findings.py`.\n",
        encoding="utf-8")
    write_caption()
    write_findings(results, coverage, top, groups)
    print("Verified: six unchanged routes; exceedance curves use all 239 routes in groups 17/222.")
    print("Ownership annotations: 12/17, 11/11, 9/9; Grasshoppers 10/10 and Vitesse 8/8 (inclusion coverage).")
    print("Group means: 5.705882/2.810811; medians: 4/2 (all group observations).")
    print(f"Saved 7.16-inch PDF, PNG (600 dpi), SVG and brief caption: {OUTPUT_DIR / STEM}")
    print(f"Saved combined and standalone plots (PDF, PNG, SVG): {figure_dir}")
    print("Updated findings recap: premier_league_feeder_summary.md")


if __name__ == "__main__":
    main()
