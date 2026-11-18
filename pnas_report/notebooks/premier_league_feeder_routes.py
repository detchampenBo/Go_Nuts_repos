"""Season-stratified permutation analysis of recorded Premier League feeder routes."""

import argparse
import json
from pathlib import Path
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import networkx as nx
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
NON_CLUB_IDS = {515, 123, 2113}  # Without Club, Retired, Career break.
PREFIX = "premier_league_feeder"
DISPLAY_RULE = "Top 20 origins by PL-bound transfer count, ties by club ID; all connected destinations."
GREY, ORANGE = "#9AA5B1", "#D55E00"


def _club_names(transfers, lookup):
    names = pd.concat([
        transfers[["from_club_id", "from_club_name"]].rename(
            columns={"from_club_id": "club_id", "from_club_name": "club_name"}),
        transfers[["to_club_id", "to_club_name"]].rename(
            columns={"to_club_id": "club_id", "to_club_name": "club_name"}),
    ]).dropna()
    canonical = lookup[["club_id", "club_name"]].dropna()

    def most_common(frame):
        frame = frame.loc[frame.club_name.str.strip().ne("")]
        counts = frame.groupby(["club_id", "club_name"]).size().reset_index(name="n")
        return counts.sort_values(["n", "club_name"], ascending=[False, True]).drop_duplicates(
            "club_id").set_index("club_id")["club_name"].to_dict()

    labels = most_common(names)
    labels.update(most_common(canonical))
    return labels


def _build_sample(transfers_path, league_lookup_path):
    transfers = pd.read_csv(transfers_path)
    lookup = pd.read_csv(league_lookup_path)
    required = ["from_club_id", "to_club_id", "transfer_season", "player_id"]
    if transfers[required].isna().any().any():
        raise ValueError("Transfer IDs and seasons must not be missing.")
    for column in ("from_club_id", "to_club_id", "player_id"):
        values = pd.to_numeric(transfers[column], errors="raise")
        if ((values <= 0) | (values != np.floor(values))).any():
            raise ValueError(f"Invalid positive integer IDs in {column}.")
        transfers[column] = values.astype(np.int64)
    for column in ("from_club_name", "to_club_name", "transfer_date"):
        if column not in transfers:
            transfers[column] = ""
    transfers["transfer_season"] = transfers.transfer_season.str.strip()
    pl = lookup.loc[lookup.competition_id.str.strip().eq("GB1")].copy()
    pl["transfer_season"] = pl.transfer_season.str.strip()
    membership = set(pl[["transfer_season", "club_id"]].itertuples(index=False, name=None))
    missing = sorted(set(transfers.transfer_season) - set(pl.transfer_season))
    if missing:
        raise ValueError(f"Premier League lookup does not cover seasons: {missing}")
    origin_pl = np.array([(s, c) in membership for s, c in
                          transfers[["transfer_season", "from_club_id"]].itertuples(index=False, name=None)])
    destination_pl = np.array([(s, c) in membership for s, c in
                               transfers[["transfer_season", "to_club_id"]].itertuples(index=False, name=None)])
    eligible = np.ones(len(transfers), dtype=bool)
    counts = {"input_transfer_records": len(transfers)}
    for name, invalid in (
        ("non_club_origin", transfers.from_club_id.isin(NON_CLUB_IDS).to_numpy()),
        ("non_club_destination", transfers.to_club_id.isin(NON_CLUB_IDS).to_numpy()),
        ("premier_league_origin", origin_pl),
    ):
        counts[f"excluded_{name}_records"] = int(np.count_nonzero(eligible & invalid))
        eligible &= ~invalid
    counts["eligible_transfer_records"] = int(eligible.sum())
    counts["excluded_non_premier_league_destination_records"] = int(
        np.count_nonzero(eligible & ~destination_pl))
    sample = transfers.loc[eligible & destination_pl].sort_values(
        ["transfer_season", "from_club_id", "to_club_id", "player_id", "transfer_date"],
        kind="stable").reset_index(drop=True)
    if sample.empty:
        raise ValueError("No eligible Premier League arrivals.")
    counts.update({
        "premier_league_arrival_records": len(sample),
        "distinct_players": int(sample.player_id.nunique()),
        "origin_clubs": int(sample.from_club_id.nunique()),
        "destination_clubs": int(sample.to_club_id.nunique()),
        "identical_arrival_records": int(sample.duplicated().sum()),
        "additional_arrival_records_beyond_one_per_player": len(sample) - int(sample.player_id.nunique()),
    })
    coverage = []
    for season, records in transfers.groupby("transfer_season", sort=True):
        arrivals = sample.loc[sample.transfer_season.eq(season)]
        dates = records.transfer_date.dropna()
        arrival_dates = arrivals.transfer_date.dropna()
        coverage.append({
            "transfer_season": season,
            "input_records": len(records),
            "eligible_records": int(eligible[records.index].sum()),
            "pl_arrivals": len(arrivals),
            "pl_membership_clubs": len({c for s, c in membership if s == season}),
            "input_date_min": str(dates.min()) if len(dates) else None,
            "input_date_max": str(dates.max()) if len(dates) else None,
            "arrival_date_min": str(arrival_dates.min()) if len(arrival_dates) else None,
            "arrival_date_max": str(arrival_dates.max()) if len(arrival_dates) else None,
        })
    snapshot = {"input_transfer_records": 19712, "premier_league_arrival_records": 2882}
    discrepancies = {key: {"expected": value, "observed": counts[key]}
                     for key, value in snapshot.items() if counts[key] != value}
    if discrepancies:
        warnings.warn(f"Snapshot count discrepancies; inspect exclusions and season coverage: {discrepancies}")
    return sample, _club_names(transfers, lookup), counts, coverage, discrepancies


def _route_statistics(sample, n_permutations, seed):
    origins = np.sort(sample.from_club_id.unique())
    destinations = np.sort(sample.to_club_id.unique())
    origin_index = np.searchsorted(origins, sample.from_club_id)
    destination_index = np.searchsorted(destinations, sample.to_club_id)
    shape = (len(origins), len(destinations))
    size = len(origins) * len(destinations)
    observed = np.bincount(origin_index * len(destinations) + destination_index, minlength=size)
    expected = np.zeros(shape)
    strata = []
    for indices in sample.groupby("transfer_season", sort=True).indices.values():
        oc = np.bincount(origin_index[indices], minlength=len(origins))
        dc = np.bincount(destination_index[indices], minlength=len(destinations))
        expected += np.outer(oc, dc) / len(indices)
        strata.append((indices, oc, dc))
    expected = expected.ravel()
    # Define the family using only seasonal margins, before comparing route strength.
    family = expected > 0
    if np.any(observed[~family]) or not np.isclose(expected.sum(), len(sample)):
        raise AssertionError("Expected counts do not cover the observed network.")
    greater_or_equal = np.zeros(size, dtype=np.int64)
    equal = np.zeros(size, dtype=np.int64)
    rng = np.random.default_rng(seed)
    shuffled = np.empty_like(destination_index)
    for _ in range(n_permutations):
        for indices, oc, dc in strata:
            shuffled[indices] = rng.permutation(destination_index[indices])
            # Check every season on every draw, including fixed/single-record strata.
            if not (np.array_equal(np.bincount(origin_index[indices], minlength=len(origins)), oc)
                    and np.array_equal(np.bincount(shuffled[indices], minlength=len(destinations)), dc)):
                raise AssertionError("Permutation changed season-specific margins.")
        simulated = np.bincount(origin_index * len(destinations) + shuffled, minlength=size)
        greater_or_equal += simulated >= observed
        equal += simulated == observed
    p_values = (1 + greater_or_equal[family]) / (1 + n_permutations)
    oi, di = np.nonzero(family.reshape(shape))
    table = pd.DataFrame({
        "from_club_id": origins[oi], "to_club_id": destinations[di],
        "observed_count": observed[family], "expected_count": expected[family],
        "observed_expected_ratio": observed[family] / expected[family],
        "origin_pl_bound_total": np.bincount(origin_index)[oi],
        "destination_arrival_total": np.bincount(destination_index)[di],
        "distinct_players": 0,
        "permutations_greater_or_equal": greater_or_equal[family],
        "permutations_equal": equal[family],
        "p_value": p_values,
        "significant": p_values <= 0.05,
    })
    players = sample.groupby(["from_club_id", "to_club_id"]).player_id.nunique()
    table["distinct_players"] = [int(players.get((a, b), 0)) for a, b in
                                 zip(table.from_club_id, table.to_club_id)]
    table["destination_share"] = table.observed_count / table.origin_pl_bound_total
    table["repeat_player_extra_records"] = table.observed_count - table.distinct_players
    table["repeated_player_flag"] = table.repeat_player_extra_records > 0
    table["recurring_route"] = table.observed_count >= 2
    if not table.loc[table.observed_count.eq(0), "p_value"].eq(1).all():
        raise AssertionError("Unobserved routes must have p-value 1 (ties included).")
    verification = {
        "all_permutations_preserved_origin_and_destination_totals_within_every_season": True,
        "season_margin_checks_per_run": n_permutations * len(strata),
        "positive_expected_pairs_equal_testing_family_size": len(table) == int(family.sum()),
        "unobserved_routes_included_with_p_value_one": True,
        "upper_tail_includes_ties": bool(np.array_equal(
            table.p_value.to_numpy(), (1 + table.permutations_greater_or_equal) / (1 + n_permutations))),
        "p_values_cover_entire_testing_family": len(p_values) == len(table),
        "significance_uses_unadjusted_p_values": bool(np.array_equal(table.significant, table.p_value <= 0.05)),
        "expected_counts_sum_to_arrivals": bool(np.isclose(expected.sum(), len(sample))),
    }
    return table, verification


def _network(table):
    graph = nx.Graph()
    for row in table.loc[table.observed_count.gt(0)].itertuples():
        origin, destination = ("origin", row.from_club_id), ("destination", row.to_club_id)
        graph.add_node(origin, bipartite=0)
        graph.add_node(destination, bipartite=1)
        graph.add_edge(origin, destination, weight=row.observed_count)
    return graph


def _display_selection(table):
    totals = table.groupby("from_club_id").origin_pl_bound_total.first()
    origins = sorted(totals.index, key=lambda club: (-totals[club], club))[:20]
    displayed = table.loc[table.from_club_id.isin(origins) & table.observed_count.gt(0)]
    destination_totals = displayed.groupby("to_club_id").observed_count.sum()
    destinations = sorted(destination_totals.index, key=lambda club: (-destination_totals[club], club))
    return origins, destinations, displayed


def _save_figures(table, labels, output_dir, origins, destinations, displayed):
    def label(club):
        return f"{labels.get(club, str(club))} [{club}]"

    origin_y = dict(zip(origins, np.linspace(1, 0, len(origins))))
    destination_y = dict(zip(destinations, np.linspace(1, 0, len(destinations))))
    fig, ax = plt.subplots(figsize=(18, max(12, len(destinations) * 0.34)))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.13)
    for row in displayed.sort_values(["significant", "observed_count"]).itertuples():
        ax.plot([0, 1], [origin_y[row.from_club_id], destination_y[row.to_club_id]],
                linewidth=0.45 * row.observed_count,
                color=ORANGE if row.significant else GREY,
                alpha=0.9 if row.significant else 0.28, solid_capstyle="round")
    for clubs, positions, x, alignment, offset in (
        (origins, origin_y, 0, "right", -0.025),
        (destinations, destination_y, 1, "left", 0.025),
    ):
        ax.scatter([x] * len(clubs), list(positions.values()), s=25, color="#243746", zorder=3)
        for club in clubs:
            ax.text(x + offset, positions[club], label(club), ha=alignment, va="center", fontsize=10)
    ax.text(0, 1.045, "SUPPLYING ROLE · outside PL in transfer season", ha="center", fontsize=11)
    ax.text(1, 1.045, "RECEIVING ROLE · PL in transfer season", ha="center", fontsize=11)
    ax.set(xlim=(-0.57, 1.57), ylim=(-0.025, 1.075))
    ax.axis("off")
    fig.suptitle("Recorded routes into the Premier League", fontsize=21, y=0.975)
    handles = [Line2D([0], [0], color=GREY, lw=2, label="Unadjusted p > 0.05"),
               Line2D([0], [0], color=ORANGE, lw=2, label="Unadjusted p ≤ 0.05")]
    maximum = int(displayed.observed_count.max())
    for count in sorted({1, max(2, maximum // 2), maximum}):
        handles.append(Line2D([0], [0], color="#243746", lw=0.45 * count,
                              label=f"{count} recorded transfers"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.045),
               ncol=3, frameon=False, fontsize=10)
    outside = int((table.significant & ~table.from_club_id.isin(origins)).sum())
    fig.text(0.5, 0.025,
             f"Top 20 origins by PL-bound count (ties: club ID); all {len(destinations)} connected destinations. "
             f"Full-sample tests; {outside} significant routes outside this view.\n"
             "Line width is proportional to transfer count. Club IDs are in brackets; roles remain separate across seasons.",
             ha="center", fontsize=10)
    fig.savefig(output_dir / f"{PREFIX}_network.png", dpi=300)
    plt.close(fig)

    matrix = table.pivot(index="from_club_id", columns="to_club_id", values="observed_count").reindex(
        index=origins, columns=destinations).fillna(0).to_numpy(dtype=int)
    significant = table.pivot(index="from_club_id", columns="to_club_id", values="significant").reindex(
        index=origins, columns=destinations).eq(True).to_numpy(dtype=bool)
    fig, ax = plt.subplots(figsize=(max(18, len(destinations) * 0.40), 13))
    fig.subplots_adjust(left=0.19, right=0.93, top=0.89, bottom=0.29)
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=matrix.max(), aspect="auto")
    ax.set_xticks(range(len(destinations)), [label(c) for c in destinations], rotation=65, ha="right", fontsize=9)
    ax.set_yticks(range(len(origins)), [label(c) for c in origins], fontsize=10)
    for i, j in zip(*np.nonzero(matrix)):
        ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=8,
                color="white" if matrix[i, j] > matrix.max() * 0.55 else "#243746")
    for i, j in zip(*np.nonzero(significant)):
        ax.add_patch(Rectangle((j - 0.48, i - 0.48), 0.96, 0.96, fill=False,
                               edgecolor=ORANGE, linewidth=1.6))
    colorbar = fig.colorbar(im, ax=ax, fraction=0.024, pad=0.025)
    colorbar.set_label("Recorded transfers (blank cells = 0)", fontsize=10)
    ax.set_xlabel("Premier League destination (receiving role)", labelpad=10)
    ax.set_ylabel("Outside-PL origin (supplying role)")
    fig.suptitle("Destination patterns among the 20 largest supplying clubs", fontsize=20, y=0.97)
    fig.legend(handles=[Line2D([0], [0], color=ORANGE, lw=2, label="Orange cell border: unadjusted p ≤ 0.05")],
               loc="lower center", bbox_to_anchor=(0.5, 0.085), frameon=False, fontsize=10)
    fig.text(0.5, 0.04,
             f"Same origins and order as the network: top 20 by PL-bound count, ties by club ID; "
             f"all {len(destinations)} connected destinations.\n"
             f"Counts are pooled across all recorded seasons. Tests use the full sample; {outside} significant routes outside this view.",
             ha="center", fontsize=10)
    fig.savefig(output_dir / f"{PREFIX}_heatmap.png", dpi=300)
    plt.close(fig)


def _save_summary(table, results, output_dir):
    counts = results["sample_and_exclusion_counts"]
    significant = table.loc[table.significant]
    # Do not rank one-record 100% shares as prominent recurring routes.
    prominent = table.loc[table.recurring_route & table.observed_expected_ratio.gt(1)].sort_values(
        ["p_value", "observed_count", "from_club_id", "to_club_id"],
        ascending=[True, False, True, True]).head(10)
    lines = [
        "# Recorded feeder routes into the Premier League", "",
        f"The sample contains **{counts['premier_league_arrival_records']:,} Premier League arrivals** "
        f"from {counts['origin_clubs']:,} supplying clubs to {counts['destination_clubs']} receiving clubs, "
        f"selected from {counts['input_transfer_records']:,} input records. "
        "Both endpoints use Premier League membership (`GB1`) in the recorded transfer season. "
        "Non-club IDs 515 (Without Club), 123 (Retired), and 2113 (Career break) are excluded. "
        "Supplying and receiving roles are separate nodes even when a club occupies both across seasons.", "",
        f"Exclusions, applied sequentially: {counts['excluded_non_club_origin_records']} non-club origins; "
        f"{counts['excluded_non_club_destination_records']} non-club destinations; "
        f"{counts['excluded_premier_league_origin_records']} PL origins; "
        f"{counts['excluded_non_premier_league_destination_records']:,} non-PL destinations. "
        f"Snapshot discrepancies: {json.dumps(results['snapshot_discrepancies'], sort_keys=True)}.", "",
        "## Methods", "",
        "Route counts are pooled across seasons. Each expected count is the sum over seasons of "
        "`origin_PL_arrivals * destination_arrivals / total_PL_arrivals`. Destination share is the route count "
        "divided by the origin's PL-bound total: it describes destination choice conditional on entering the PL, "
        "rather than the origin's overall PL joining rate. Counts accompany shares because one transfer can yield 100%.", "",
        f"We shuffled destination IDs within each season {results['n_permutations']:,} times using NumPy "
        f"default_rng, seed {results['seed']}, after sorting by season, origin ID, destination ID, player ID, and date. "
        "Every draw preserves both origin and destination totals in every season. The upper-tail Monte Carlo "
        "p-value is `(1 + count(shuffled_count >= observed_count)) / (1 + permutations)`, including ties. "
        f"Its minimum and grid spacing are {results['permutation_p_value_resolution']:.4g}. "
        f"We tested **all {len(table):,} pairs with positive expected count**, "
        f"including {results['unobserved_tested_pairs']:,} unobserved routes (p = 1). "
        "The significance flag and highlighting use unadjusted p ≤ 0.05. No multiple-comparison correction "
        "is applied; this is a per-route threshold and does not control false discoveries across all tested routes. "
        "A minimum-grid p-value is not zero.", "",
        "## Results", "",
        (f"**{len(significant)} routes meet the unadjusted p ≤ 0.05 threshold.**" if len(significant)
         else "**No route meets the unadjusted p ≤ 0.05 threshold.**"), "",
        f"The smallest unadjusted p-value is {table.p_value.min():.4g}; "
        f"{int(table.p_value.eq(results['permutation_p_value_resolution']).sum())} routes reach the "
        "minimum Monte Carlo p-value. The finite resolution limits distinctions between routes "
        "with small tail probabilities.", "",
        "The table below lists recurring, over-expected routes ranked by unadjusted p, then count "
        "(ID tie breaks). The per-route significance threshold is unadjusted p ≤ 0.05.", "",
        "| Origin → destination (IDs) | Transfers | Expected | Obs./exp. | Origin PL total | Share | Distinct players | Repeat extras | Unadjusted p |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in prominent.itertuples():
        lines.append(f"| {row.from_club_name} [{row.from_club_id}] → {row.to_club_name} [{row.to_club_id}] "
                     f"| {row.observed_count} | {row.expected_count:.3f} | {row.observed_expected_ratio:.2f} "
                     f"| {row.origin_pl_bound_total} | {row.destination_share:.1%} | {row.distinct_players} "
                     f"| {row.repeat_player_extra_records} | {row.p_value:.4g} |")
    lines += [
        "", f"Among observed routes, {int(table.repeated_player_flag.sum())} have more transfers than distinct players; "
        f"there are {int(table.repeat_player_extra_records.sum())} extra route records beyond one per player per route. "
        f"The ten displayed candidates contain {int(prominent.repeated_player_flag.sum())} flagged routes. "
        "This flags repeated player involvement, not necessarily duplicate events, and is a descriptive check, "
        "not an independent significance test. The route table includes distinct players, repeat extras, "
        f"and a flag for every pair. There are {counts['identical_arrival_records']} completely identical arrival rows.", "",
        "## Figures", "",
        f"{DISPLAY_RULE} Both figures use the same origin order and connected destinations; all routes remain "
        f"in the analysis. {results['significant_routes_outside_display']} routes meeting the unadjusted threshold fall outside this view.", "",
        f"![Two-column weighted transfer network]({PREFIX}_network.png)", "",
        "*Line width is proportional to recorded transfer count. Grey routes have unadjusted p > 0.05; "
        "orange routes have unadjusted p ≤ 0.05. Club IDs appear in brackets. The top-20-origin display is a subset of the full analysis.*", "",
        f"![Origin-by-destination transfer heatmap]({PREFIX}_heatmap.png)", "",
        "*The heatmap shows counts for the same top 20 origins and all their connected destinations. "
        "Blank cells have zero transfers; orange borders identify routes with unadjusted p ≤ 0.05.*", "",
        f"[Complete route table]({PREFIX}_routes.csv) · [Results and verification]({PREFIX}_results.json)", "",
        "## Season coverage and limitations", "",
        "All recorded seasons are retained, including sparse and partial coverage. Dates below describe recorded "
        "events, not evidence of complete season observation. In particular, 2026/27 contains recorded future-dated "
        "transfers, which may include scheduled moves or loan returns. The analysis uses recorded season labels "
        "and does not infer completeness from the date span. Seasons with zero PL arrivals are retained in the "
        "coverage audit and contribute no permutation stratum.", "",
        "| Season | Input records | PL arrivals | PL lookup clubs | Input date range |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for season in results["season_coverage"]:
        lines.append(f"| {season['transfer_season']} | {season['input_records']:,} | {season['pl_arrivals']:,} "
                     f"| {season['pl_membership_clubs']} | {season['input_date_min']} to {season['input_date_max']} |")
    lines += [
        "", "The shuffle controls seasonal transfer volumes, but not geography, ownership, player characteristics, "
        "or dependence between repeated players. A feeder route means a recurring, disproportionately strong "
        "connection in this recorded sample; it does not establish a formal partnership, a feeder agreement, "
        "or its cause. This analysis asks which PL club receives a transfer; the separate age analysis asks "
        "whether a transfer enters the PL at all. The degree recap describes unequal connectivity in the broader eligible network.", "",
        "## Verification", "",
        "All input seasons have membership coverage; selected records have real-club endpoints under the project's "
        "non-club exclusion rule, non-PL origins, and PL destinations. Edge weights sum to the arrival count. "
        "Every permutation's seasonal margins were checked. The complete statistical analysis was repeated "
        "with the same seed and produced identical route tables, including unadjusted p-values and significance flags. "
        "Role-specific node sets are disjoint. Verification details are saved in the results JSON.", "",
        "Sources: [proposal](../notes/premier_league_feeder_clubs_proposal.md), "
        "[implementation](../notebooks/premier_league_feeder_routes.py), "
        "[age summary](age_shuffle_outsideprem_toprem_summary.md), "
        "[degree recap](degree_distribution_recap.md), "
        "[NetworkX bipartite documentation](https://networkx.org/documentation/stable/reference/algorithms/bipartite.html).", "",
    ]
    (output_dir / f"{PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def run_feeder_routes(transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026):
    """Save the full route analysis and verify same-seed statistical reproducibility.

    All records and seasons are retained after endpoint eligibility and PL arrival
    selection. Counts describe recorded events, including repeat player involvement.
    """
    if not isinstance(n_permutations, (int, np.integer)) or n_permutations < 1:
        raise ValueError("n_permutations must be a positive integer.")
    n_permutations = int(n_permutations)
    sample, labels, counts, coverage, discrepancies = _build_sample(transfers_path, league_lookup_path)
    table, verification = _route_statistics(sample, n_permutations, seed)
    repeated_table, repeated_verification = _route_statistics(sample, n_permutations, seed)
    pd.testing.assert_frame_equal(table, repeated_table, check_exact=True)
    if verification != repeated_verification:
        raise AssertionError("Same-seed verification results differ.")
    table.insert(1, "from_club_name", table.from_club_id.map(lambda c: labels.get(c, str(c))))
    table.insert(3, "to_club_name", table.to_club_id.map(lambda c: labels.get(c, str(c))))
    graph = _network(table)
    origin_nodes = {node for node, attributes in graph.nodes(data=True) if attributes["bipartite"] == 0}
    destination_nodes = set(graph) - origin_nodes
    if not (nx.is_bipartite(graph) and origin_nodes.isdisjoint(destination_nodes)
            and sum(nx.get_edge_attributes(graph, "weight").values()) == len(sample)):
        raise AssertionError("Weighted bipartite network verification failed.")
    origins, destinations, displayed = _display_selection(table)
    verification.update({
        "membership_covers_every_input_season": True,
        "selected_endpoints_pass_non_club_exclusions": True,
        "selected_origins_outside_pl_and_destinations_in_pl_by_season": True,
        "edge_weight_sum": sum(nx.get_edge_attributes(graph, "weight").values()),
        "edge_weights_sum_to_arrival_count": True,
        "bipartite_role_nodes_disjoint": True,
        "clubs_occupying_both_roles": len(set(sample.from_club_id) & set(sample.to_club_id)),
        "same_seed_statistical_rerun_identical": True,
        "statistical_runs": 2,
    })
    results = {
        "input_paths": {"transfers": str(Path(transfers_path).resolve()),
                        "league_lookup": str(Path(league_lookup_path).resolve())},
        "sample_and_exclusion_counts": counts, "snapshot_discrepancies": discrepancies,
        "season_coverage": coverage,
        "season_coverage_note": "All recorded seasons retained; date ranges do not establish complete coverage.",
        "record_order": ["transfer_season", "from_club_id", "to_club_id", "player_id", "transfer_date"],
        "seed": int(seed), "n_permutations": n_permutations,
        "random_generator": "numpy.random.default_rng (PCG64)",
        "testing_family": "All origin/destination pairs with positive seasonal-margin expected count, including unobserved routes.",
        "testing_family_size": len(table),
        "observed_routes": int(table.observed_count.gt(0).sum()),
        "unobserved_tested_pairs": int(table.observed_count.eq(0).sum()),
        "adjustment_method": "none",
        "significance_basis": "unadjusted upper-tail Monte Carlo p_value <= 0.05",
        "significance_threshold": 0.05,
        "permutation_p_value_resolution": 1 / (1 + n_permutations),
        "significant_route_count": int(table.significant.sum()),
        "display_selection_rule": DISPLAY_RULE,
        "display_origin_ids": [int(c) for c in origins],
        "display_destination_ids": [int(c) for c in destinations],
        "displayed_routes": len(displayed),
        "displayed_transfer_records": int(displayed.observed_count.sum()),
        "significant_routes_outside_display": int((table.significant & ~table.from_club_id.isin(origins)).sum()),
        "routes_with_repeated_players": int(table.repeated_player_flag.sum()),
        "route_repeat_player_extra_records": int(table.repeat_player_extra_records.sum()),
        "verification": verification,
        "deviations_from_proposal": [],
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_dir / f"{PREFIX}_routes.csv", index=False)
    _save_figures(table, labels, output_dir, origins, destinations, displayed)
    (output_dir / f"{PREFIX}_results.json").write_text(
        json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    _save_summary(table, results, output_dir)
    return results


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfers-path", type=Path,
                        default=PROJECT_DIR / "data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz")
    parser.add_argument("--league-lookup-path", type=Path, default=PROJECT_DIR / "data/top_five_league_clubs.csv")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--n-permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    results = run_feeder_routes(**vars(args))
    print(json.dumps({key: results[key] for key in (
        "sample_and_exclusion_counts", "testing_family_size", "significant_route_count", "verification")}, indent=2))
    print(f"Saved outputs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    _main()
