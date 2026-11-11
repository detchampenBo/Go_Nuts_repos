"""Age-label permutation tests conditional on origin club and transfer season."""

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
from pathlib import Path
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


NON_CLUB_IDS = {515, 123, 2113}
PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TRANSFERS = (
    PROJECT_DIR / "data/dataset_graph/reduced_cleaned_transfers_with_players.csv.gz"
)
DEFAULT_LEAGUE_LOOKUP = PROJECT_DIR / "data/top_five_league_clubs.csv"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "output"


def _read_csv(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _build_sample(transfers_path, league_lookup_path):
    membership = {
        (row["transfer_season"].strip(), int(row["club_id"]))
        for row in _read_csv(league_lookup_path)
    }
    rows = _read_csv(transfers_path)
    missing_seasons = {row["transfer_season"].strip() for row in rows} - {
        season for season, _ in membership
    }
    if missing_seasons:
        raise ValueError(f"League lookup does not cover seasons: {sorted(missing_seasons)}")

    counts = {
        "all_transfer_records": len(rows),
        "top_five_origin_records": 0,
        "excluded_non_club_destination_records": 0,
        "excluded_missing_age_records": 0,
        "excluded_unusable_age_records": 0,
    }
    sample = []
    for row in rows:
        season = row["transfer_season"].strip()
        origin = int(row["from_club_id"])
        if (season, origin) not in membership:
            continue
        counts["top_five_origin_records"] += 1
        destination = int(row["to_club_id"])
        if destination in NON_CLUB_IDS:
            counts["excluded_non_club_destination_records"] += 1
            continue
        raw_age = row["age_when_transferred"].strip()
        if not raw_age:
            counts["excluded_missing_age_records"] += 1
            continue
        try:
            age = float(raw_age)
        except ValueError:
            age = np.nan
        if not np.isfinite(age) or age < 0:
            counts["excluded_unusable_age_records"] += 1
            continue
        sample.append(
            (int(row["player_id"]), origin, season, age >= 30,
             (season, destination) not in membership)
        )
    counts["eligible_transfer_records"] = len(sample)
    counts["eligible_records_by_season"] = dict(sorted(Counter(r[2] for r in sample).items()))
    return sample, counts


def _run_test(sample, n_permutations, rng):
    older = np.array([row[3] for row in sample], dtype=bool)
    exits = np.array([row[4] for row in sample], dtype=bool)
    older_total = int(older.sum())
    younger_total = len(sample) - older_total
    if not older_total or not younger_total:
        raise ValueError("Both age groups must have eligible transfers.")

    grouped = defaultdict(list)
    for index, row in enumerate(sample):
        grouped[(row[1], row[2])].append(index)
    mixed_groups = [
        np.array(indices, dtype=int)
        for indices in grouped.values()
        if older[indices].any() and not older[indices].all()
    ]
    older_exits = int(np.count_nonzero(older & exits))
    total_exits = int(exits.sum())
    younger_exits = total_exits - older_exits

    def gap(older_exit_count):
        return 100 * (
            older_exit_count / older_total
            - (total_exits - older_exit_count) / younger_total
        )

    observed_gap = gap(older_exits)
    simulated_gaps = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = older.copy()
        for indices in mixed_groups:
            shuffled[indices] = rng.permutation(older[indices])
        simulated_gaps[permutation] = gap(int(np.count_nonzero(shuffled & exits)))

    player_counts = Counter(row[0] for row in sample)
    exceedances = int(np.count_nonzero(simulated_gaps >= observed_gap))
    return {
        "sample_counts": {
            "eligible_transfer_records": len(sample),
            "distinct_players": len(player_counts),
            "players_with_multiple_eligible_records": sum(n > 1 for n in player_counts.values()),
            "records_from_repeat_players": sum(n for n in player_counts.values() if n > 1),
            "origin_club_season_groups": len(grouped),
            "groups_with_both_age_labels": len(mixed_groups),
        },
        "age_groups": {
            "under_30": {
                "total_transfer_records": younger_total,
                "exit_records": younger_exits,
                "within_top_five_records": younger_total - younger_exits,
                "exit_rate": younger_exits / younger_total,
            },
            "age_30_plus": {
                "total_transfer_records": older_total,
                "exit_records": older_exits,
                "within_top_five_records": older_total - older_exits,
                "exit_rate": older_exits / older_total,
            },
        },
        "observed_gap_percentage_points": observed_gap,
        "shuffle_mean_gap_percentage_points": float(simulated_gaps.mean()),
        "simulated_gaps_at_least_observed": exceedances,
        "one_sided_p_value": (1 + exceedances) / (1 + n_permutations),
        "simulated_gaps_percentage_points": simulated_gaps.tolist(),
    }


def _verify_snapshot(counts, main):
    checks = {
        "all_transfer_records": (counts["all_transfer_records"], 23238),
        "top_five_origin_records": (counts["top_five_origin_records"], 14719),
        "excluded_non_club_destination_records": (counts["excluded_non_club_destination_records"], 391),
        "excluded_missing_age_records": (counts["excluded_missing_age_records"], 4),
        "excluded_unusable_age_records": (counts["excluded_unusable_age_records"], 0),
        "eligible_transfer_records": (counts["eligible_transfer_records"], 14324),
        "under_30_within_top_five": (main["age_groups"]["under_30"]["within_top_five_records"], 6614),
        "under_30_exits": (main["age_groups"]["under_30"]["exit_records"], 6480),
        "age_30_plus_within_top_five": (main["age_groups"]["age_30_plus"]["within_top_five_records"], 682),
        "age_30_plus_exits": (main["age_groups"]["age_30_plus"]["exit_records"], 548),
        "distinct_players": (main["sample_counts"]["distinct_players"], 4521),
        "groups_with_both_age_labels": (main["sample_counts"]["groups_with_both_age_labels"], 583),
        "records_from_repeat_players": (main["sample_counts"]["records_from_repeat_players"], 12918),
        "partial_26_27_eligible_records": (counts["eligible_records_by_season"].get("26/27", 0), 74),
    }
    discrepancies = {
        name: {"observed": observed, "expected": expected}
        for name, (observed, expected) in checks.items() if observed != expected
    }
    if discrepancies:
        warnings.warn(f"Input counts differ from the instruction snapshot: {discrepancies}")
    return {"all_reference_counts_match": not discrepancies, "discrepancies": discrepancies}


def _save_figure(main, sensitivity, path):
    analyses = [main, sensitivity]
    values = [
        value for analysis in analyses
        for value in analysis["simulated_gaps_percentage_points"]
        + [analysis["observed_gap_percentage_points"], analysis["shuffle_mean_gap_percentage_points"]]
    ]
    low, high = min(values), max(values)
    padding = max((high - low) * 0.08, 0.5)
    bins = np.linspace(low - padding, high + padding, 36)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharex=True, layout="constrained")
    for ax, analysis, title in zip(
        axes, analyses, ["All eligible transfers", "One transfer per player"]
    ):
        ax.hist(analysis["simulated_gaps_percentage_points"], bins=bins,
                color="#0072B2", label="Shuffled gaps", alpha=0.9)
        ax.axvline(analysis["observed_gap_percentage_points"], color="#D55E00",
                   linewidth=2.5, label="Observed gap")
        ax.axvline(analysis["shuffle_mean_gap_percentage_points"], color="#009E73",
                   linewidth=2.5, linestyle="--", label="Shuffle mean")
        ax.set_title(title, fontsize=14, pad=12)
        ax.set_xlim(bins[0], bins[-1])
        ax.set_ylabel("Number of shuffles", fontsize=11)
        ax.legend(loc="upper right", fontsize=10, frameon=False)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.3)
        ax.spines[["top", "right"]].set_visible(False)
    fig.supxlabel("Exit-rate gap (30+ minus under 30, percentage points)", fontsize=12)
    fig.savefig(path, dpi=300)
    plt.close(fig)


def run_age_shuffle_null_model(
    transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026
):
    """Save and return pooled transfer and one-transfer-per-player shuffle tests.

    Exit rates are proportions; gap fields are percentage points. P-values test
    whether older players have higher exit rates, conditional on exchangeable
    age labels within origin club and season. Repeated players can violate this
    assumption; the sensitivity sample selects one record uniformly per player.
    """
    if not isinstance(n_permutations, (int, np.integer)) or n_permutations < 1:
        raise ValueError("n_permutations must be a positive integer.")
    n_permutations = int(n_permutations)
    main_stream, selection_stream, sensitivity_stream = np.random.SeedSequence(seed).spawn(3)
    sample, counts = _build_sample(transfers_path, league_lookup_path)
    main = _run_test(sample, n_permutations, np.random.default_rng(main_stream))

    by_player = defaultdict(list)
    for index, row in enumerate(sample):
        by_player[row[0]].append(index)
    selection_rng = np.random.default_rng(selection_stream)
    selected = [sample[int(selection_rng.choice(indices))] for indices in by_player.values()]
    sensitivity = _run_test(selected, n_permutations, np.random.default_rng(sensitivity_stream))
    results = {
        "seed": int(seed),
        "n_permutations": n_permutations,
        "alternative": "exit_rate_age_30_plus > exit_rate_under_30",
        "shuffle_groups": ["from_club_id", "transfer_season"],
        "random_streams": {
            "method": "NumPy SeedSequence.spawn",
            "child_0": "main_shuffle",
            "child_1": "one_transfer_per_player_selection",
            "child_2": "sensitivity_shuffle",
        },
        "interpretation": (
            "The main analysis describes transfer records and its p-value is conditional "
            "on exchangeable age labels within origin club and season. Repeated players "
            "can undermine this assumption. The sensitivity analysis uses one uniformly "
            "selected eligible transfer per player."
        ),
        "sample_and_exclusion_counts": counts,
        "snapshot_verification": _verify_snapshot(counts, main),
        "all_eligible_transfers": main,
        "one_transfer_per_player": sensitivity,
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _save_figure(main, sensitivity, output_dir / "age_shuffle_null_model.png")
    with (output_dir / "age_shuffle_results.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return results


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfers-path", type=Path, default=DEFAULT_TRANSFERS)
    parser.add_argument("--league-lookup-path", type=Path, default=DEFAULT_LEAGUE_LOOKUP)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--n-permutations", type=int, default=999)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    results = run_age_shuffle_null_model(**vars(args))
    print(json.dumps({
        name: {key: value for key, value in analysis.items()
               if key != "simulated_gaps_percentage_points"}
        for name, analysis in results.items()
        if name in ("all_eligible_transfers", "one_transfer_per_player")
    }, indent=2))
    print(f"Saved outputs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    _main()
