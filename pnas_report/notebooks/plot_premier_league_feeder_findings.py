"""Plot the saved feeder-route findings; do not rerun the shuffle or ownership audit.

Run from any directory: python -B <project>/notebooks/plot_premier_league_feeder_findings.py
The bundled paper/pnas-new.cls sets textwidth=512pt; its captions use sans-serif.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "output"
STEM = "premier_league_feeder_findings_three_panel"
WIDTH_IN = 512 / 72.27  # TeX points, rather than PDF's 72 points/inch.
ORANGE, BLUE, RED = "#E69F00", "#0072B2", "#C43C39"
CHARCOAL, GRID = "#333333", "#D9D9D9"
KEYS = ["from_club_id", "to_club_id"]


def read_and_verify():
    results = json.loads((OUTPUT_DIR / "premier_league_feeder_results.json").read_text())
    routes = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_routes.csv")
    audit = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    events = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_events.csv")
    selected = routes.loc[routes.p_value.le(results["significance_threshold"])].copy()
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
    assert np.array_equal(routes.significant, routes.p_value.le(0.05))
    assert np.allclose(routes.p_value, (1 + routes.permutations_greater_or_equal) / 1000)
    assert len(selected) == results["significant_route_count"] == len(audit) == 334
    assert selected.observed_count.ge(2).sum() == 241
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
    assert len(events) == audit.observed_count.sum() == 821
    groups = [audit.loc[audit.has_ownership_concurrent_record.eq(flag)]
              for flag in [True, False]]
    assert [len(g) for g in groups] == [15, 319]
    assert [g.observed_count.sum() for g in groups] == [79, 742]
    assert [g.observed_count.median() for g in groups] == [4, 2]
    assert [round(g.observed_count.mean(), 2) for g in groups] == [5.27, 2.33]
    assert [g.observed_count.eq(1).sum() for g in groups] == [0, 93]
    assert groups[0].ownership_concurrent_records.sum() == 73
    top = selected.loc[selected.observed_count.ge(8)].sort_values(
        ["observed_count", *KEYS], ascending=[False, True, True]
    ).merge(audit[KEYS + ["ownership_status", "ownership_concurrent_records"]],
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


def plot_figure(results, coverage, top, groups):
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 7, "text.color": CHARCOAL,
        "axes.labelcolor": CHARCOAL, "axes.edgecolor": CHARCOAL,
        "xtick.color": CHARCOAL, "ytick.color": CHARCOAL,
        "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.facecolor": "white", "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(WIDTH_IN, 5.8))
    ax_a = fig.add_axes([.075, .245, .205, .51])
    ax_b = fig.add_axes([.385, .245, .325, .51])
    ax_c = fig.add_axes([.805, .245, .185, .51])
    fig.suptitle("Recorded transfers, unusual routes and shared ownership",
                 x=.5, y=.974, fontsize=11, fontweight="bold")
    for ax, letter, title in [(ax_a, "A", "Recorded arrivals"),
                              (ax_b, "B", "Unusually frequent routes"),
                              (ax_c, "C", "Ownership and volume")]:
        style_axis(ax)
        fig.text(ax.get_position().x0, .906, letter, fontsize=11, fontweight="bold")
        fig.text(ax.get_position().x0, .869, title, fontsize=8, fontweight="bold")

    counts = results["sample_and_exclusion_counts"]
    fig.text(.075, .812,
             f"{counts['premier_league_arrival_records']:,} arrivals · {counts['origin_clubs']} origins\n"
             f"{counts['destination_clubs']} destinations · {results['observed_routes']:,} routes",
             fontsize=7, linespacing=1.5)
    years = coverage.transfer_season.str[:2].astype(int).to_numpy() + 2000
    all_years = np.arange(years.min(), years.max() + 1)
    arrivals = pd.Series(coverage.pl_arrivals.to_numpy(), index=years).reindex(all_years)
    # Reindex to NaN, not zero: an absent season must break the line.
    ax_a.plot(all_years, arrivals, color=ORANGE, marker="o", markersize=2.3, linewidth=1.1)
    ax_a.set(xlim=(1999.4, 2026.6), ylim=(0, 350), xlabel="Transfer season",
             ylabel="Recorded Premier League arrivals")
    ticks = [2000, 2006, 2012, 2018, 2026]
    ax_a.set_xticks(ticks, [f"{y % 100:02d}/{(y + 1) % 100:02d}" for y in ticks],
                    rotation=45, ha="right")
    ax_a.yaxis.set_major_locator(MultipleLocator(100))
    ax_a.annotate("Sparse early\ncoverage", xy=(2004, arrivals.loc[2004]), xytext=(2000, 125),
                  fontsize=7, arrowprops={"arrowstyle": "-", "color": CHARCOAL, "lw": .6})
    ax_a.annotate("26/27: partial", xy=(2026, arrivals.loc[2026]), xytext=(2014, 70),
                  fontsize=7, arrowprops={"arrowstyle": "-", "color": CHARCOAL, "lw": .6})
    ax_a.text(.04, .96, "Recorded sample coverage;\nnot a population trend", transform=ax_a.transAxes,
              va="top", fontsize=7)

    fig.text(.385, .812, f"{len(top)} routes with ≥ 8 recorded transfers\n"
             "All ties at the cutoff included", fontsize=7, linespacing=1.5)
    aliases = {12321: "Girona", 667: "Strasbourg", 410: "Udinese", 399: "Leeds",
               543: "Wolves", 631: "Chelsea", 1010: "Watford", 148: "Tottenham"}
    positions = np.arange(len(top))[::-1] * 1.5
    for y, row in zip(positions, top.itertuples()):
        origin = aliases.get(row.from_club_id, row.from_club_name)
        destination = aliases.get(row.to_club_id, row.to_club_name)
        ax_b.axhline(y - .18, color=GRID, linewidth=.5, zorder=0)
        ax_b.text(0, y + .54, f"{origin} → {destination}", fontsize=7.2, va="center")
        if row.ownership_concurrent_records:
            status = f"{row.ownership_concurrent_records}/{row.observed_count} during shared ownership"
            marker, color, fill = "o", RED, RED
        elif row.ownership_status == "family_connected_common_equity_unverified":
            status = "Family link; common equity unverified"
            marker, color, fill = "D", CHARCOAL, "white"
        elif row.ownership_status == "unresolved_indirect_ownership_or_control":
            status = "Indirect equity/control unresolved"
            marker, color, fill = "D", CHARCOAL, "white"
        else:
            status = "No documented common equity found"
            marker, color, fill = "s", CHARCOAL, "white"
        ax_b.scatter(.25, y + .20, marker=marker, s=10, facecolor=fill,
                     edgecolor=color, linewidth=.7, zorder=4)
        ax_b.text(.85, y + .20, status, color=color, va="center", fontsize=6.5)
        ax_b.barh(y - .18, row.observed_count, height=.23, color=ORANGE, zorder=2)
        ax_b.scatter(row.expected_count, y - .18, marker="D", s=20,
                     facecolor=BLUE, edgecolor="white", linewidth=.45, zorder=4)
        ax_b.text(row.observed_count + .35, y - .18, str(row.observed_count),
                  va="center", fontsize=7, fontweight="bold")
        ax_b.text(max(row.expected_count, 1.05), y - .55, f"{row.expected_count:.3f}",
                  color=BLUE, ha="center", va="center", fontsize=6.5)
    ax_b.set(xlim=(0, 20), ylim=(-.95, positions[0] + .95), yticks=[],
             xlabel="Recorded transfers per route", ylabel="Origin → Premier League destination")
    ax_b.xaxis.set_major_locator(MultipleLocator(5))
    ax_b.legend(handles=[Line2D([0], [0], color=ORANGE, lw=4, label="Observed"),
                         Line2D([0], [0], color=BLUE, marker="D", linestyle="none",
                                markersize=4, label="Seasonal-null expectation")],
                loc="upper left", bbox_to_anchor=(-.02, -.16), frameon=False,
                borderaxespad=0, fontsize=6.5, labelspacing=.6, handlelength=1.2)

    fig.text(.805, .812, "Descriptive comparison\nPooled counts; dots = routes",
             fontsize=7, linespacing=1.5)
    for center, half_width, group, color, marker in zip(
            [0, 1.3], [.28, .55], groups, [RED, ORANGE], ["o", "s"]):
        # A deterministic dot matrix within each integer row reveals every route.
        # Vertical displacement stays below half a count; it is not measurement noise.
        for count, subset in group.groupby("observed_count", sort=True):
            n = len(subset)
            columns = min(n, 21 if center else 5)
            rows = int(np.ceil(n / columns))
            for i in range(n):
                row_index, column = divmod(i, columns)
                row_size = min(columns, n - row_index * columns)
                x = center + (column - (row_size - 1) / 2) * 2 * half_width / max(columns - 1, 1)
                y = count + (row_index - (rows - 1) / 2) * .14
                ax_c.scatter(x, y, s=1.6 if center else 10, marker=marker,
                             facecolor=color, edgecolor=CHARCOAL, linewidth=.12, zorder=3)
        median = group.observed_count.median()
        ax_c.hlines(median, center - half_width - .05, center + half_width + .05,
                    color=CHARCOAL, linewidth=1.1, linestyle="-" if center == 0 else "--", zorder=2)
    ax_c.set(xlim=(-.5, 1.95), ylim=(0, 18), ylabel="Recorded transfers per route (pooled)",
             xlabel="Ownership classification")
    ax_c.yaxis.set_major_locator(MultipleLocator(2))
    ax_c.set_xticks([0, 1.3], [f"Verified\nownership\noverlap\n(n = {len(groups[0])})",
                              f"Remaining\nselected\nroutes\n(n = {len(groups[1])})"])
    ax_c.tick_params(axis="x", labelsize=6.5)
    ax_c.legend(handles=[Line2D([0], [0], color=CHARCOAL, lw=1.1,
                                label=f"Median {groups[0].observed_count.median():g} (verified)"),
                         Line2D([0], [0], color=CHARCOAL, lw=1.1, linestyle="--",
                                label=f"Median {groups[1].observed_count.median():g} (remaining)")],
                loc="upper left", bbox_to_anchor=(-.03, -.29), frameon=False,
                borderaxespad=0, fontsize=6.5, handlelength=1.4, handletextpad=.4)
    fig.text(.075, .055,
             f"{results['significant_route_count']} selected routes · {results['n_permutations']} seasonal shuffles · "
             f"unadjusted upper-tail p ≤ {results['significance_threshold']} · "
             f"{counts['eligible_transfer_records']:,} eligible records", fontsize=7)
    fig.text(.075, .026,
             "Remaining routes include unresolved cases and two historical-only ownership pairs; "
             "ownership effects were not tested.", fontsize=7)
    return fig


def write_caption(results, groups):
    counts = results["sample_and_exclusion_counts"]
    linked, remaining = groups
    caption = f"""# Recorded transfers, unusual routes and shared ownership

**A — Recorded arrivals.** The sample contains {counts['premier_league_arrival_records']:,} recorded Premier League arrivals involving {counts['distinct_players']:,} distinct players, from {counts['origin_clubs']} supplying clubs into {counts['destination_clubs']} receiving clubs across {results['observed_routes']:,} observed directed routes, selected from {counts['eligible_transfer_records']:,} eligible transfer records. Premier League membership is evaluated in the transfer season. Orange points and connecting lines show the season-specific recorded arrivals, not a measured population trend. All recorded seasons are retained, including sparse early coverage and partial 26/27 coverage. The absent 01/02 season is a gap, not an imputed zero. Date ranges do not establish complete coverage. Recorded movements include loans and returns and need not represent permanent sales.

**B — Unusually frequent routes.** All six selected routes with at least eight recorded transfers are displayed, including ties at the cutoff, ranked by observed count. Orange bars start at zero; blue diamonds and three-decimal labels show expected pooled counts under the seasonal null. Within each season, Premier League destinations are reassigned among arrival records while preserving each origin's PL-bound total and each destination's recruitment total; origins, players and seasons stay fixed. Expectations are the exact sum of seasonal origin-total × destination-total / seasonal-arrival-total terms, and may be fractional. Selection uses {results['n_permutations']} seasonal shuffles (seed {results['seed']}) and unadjusted upper-tail Monte Carlo p ≤ {results['significance_threshold']}, including ties and a plus-one correction (minimum p = {results['permutation_p_value_resolution']}). The testing family contains {results['testing_family_size']:,} positive-expectation pairs, including unobserved pairs. There are {results['significant_route_count']} selected routes, of which 241 contain at least two recorded transfers and 93 contain one. Exceeding the null mean alone is not the selection criterion. Filled red circles identify verified shared ownership with transfer overlap; hollow charcoal diamonds identify family-connected or unresolved evidence, and the hollow square indicates no documented common equity found. Timing annotations give records during verified overlap / pooled route records: Girona–Manchester City 12/17, Strasbourg–Chelsea 11/11 and Udinese–Watford 9/9. Five Girona records predate acquisition. Pooled expectations do not specifically estimate the ownership period.

**C — Ownership and pooled route volume.** Each dot represents one of all {len(linked) + len(remaining)} selected routes, classified by whether at least one selected record occurred during verified common direct or indirect equity ownership, including minority interests. Red circles show {len(linked)} verified-overlap routes ({100 * len(linked) / (len(linked) + len(remaining)):.2f}%); orange squares show the {len(remaining)} remaining routes. Points are placed in deterministic matrices within integer count rows, with vertical displacement of at most 0.35 records to reveal coincident observations; underlying counts are integers. Solid and dashed charcoal horizontal segments mark group medians of {linked.observed_count.median():g} and {remaining.observed_count.median():g}, respectively; means are {linked.observed_count.mean():.2f} and {remaining.observed_count.mean():.2f}. The verified group contains {linked.observed_count.sum()} pooled records, of which {linked.ownership_concurrent_records.sum()} occurred during ownership overlap; five Girona records and one Lorient record predate ownership completion. The remaining group includes unresolved evidence and two historical-only ownership pairs (Granada–Watford and Hearts–Liverpool), and is not a verified independently owned control group. Seventeen pairs had ownership overlap somewhere in the modelling interval, but only 15 had a selected transfer during that overlap. This comparison is descriptive: no ownership-effect test, inferential significance stars, or error bars are implied, and the association does not establish causation or a financial mechanism.

Source files: `premier_league_feeder_results.json`, `premier_league_feeder_routes.csv`, `premier_league_feeder_ownership_audit.csv` and `premier_league_feeder_ownership_events.csv`, all in this directory; source-linked ownership evidence is documented in `../notes/premier_league_feeder_ownership_audit.md`.

Figure size: 512 TeX points ({WIDTH_IN:.4f} inches) wide × 5.8 inches high, matching the full text width in the bundled PNAS template. PNG: 600 dpi; PDF: embedded TrueType fonts; SVG: editable text (Arial). Reproduce from any working directory with `python -B <project>/notebooks/plot_premier_league_feeder_findings.py`. The script verifies saved numeric checkpoints before plotting and does not modify the shuffle analysis or ownership classifications.
"""
    (OUTPUT_DIR / f"{STEM}_caption.md").write_text(caption, encoding="utf-8")


def main():
    results, coverage, top, groups = read_and_verify()
    fig = plot_figure(results, coverage, top, groups)
    for extension in ["png", "pdf", "svg"]:
        # Avoid bbox_inches='tight': preserve the template's exact physical width.
        fig.savefig(OUTPUT_DIR / f"{STEM}.{extension}", dpi=600)
    write_caption(results, groups)
    plt.close(fig)
    print("Verified: 2,882 arrivals; 1,988 observed routes; 334 selected (241 recurring).")
    print("Verified: six largest routes; ownership 15/319; medians 4/2; means 5.27/2.33.")
    print("Verified: 79 pooled ownership-linked records, 73 during overlap; 821 selected records.")
    print(f"Saved PNG (600 dpi), PDF, SVG and caption: {OUTPUT_DIR / STEM}")


if __name__ == "__main__":
    main()
