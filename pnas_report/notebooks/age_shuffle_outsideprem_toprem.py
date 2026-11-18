"""Age-label shuffle tests for recorded transfers from outside the Premier League."""

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
from matplotlib.ticker import MultipleLocator
import numpy as np


NON_CLUB_IDS = {515, 123, 2113}
PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TRANSFERS = Path(
    r"C:\Users\victo\Codex\Go_Nuts_repos\pnas_report\data\dataset_graph\outsideprem_toprem_eligible_transfers.csv.gz"
)
DEFAULT_LEAGUE_LOOKUP = PROJECT_DIR / "data/top_five_league_clubs.csv"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "output"
ALTERNATIVE = "joining_rate_30_plus < joining_rate_under_30"


def _read_csv(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _build_sample(transfers_path, league_lookup_path):
    membership = {
        (row["transfer_season"].strip(), int(row["club_id"]))
        for row in _read_csv(league_lookup_path)
        if row["competition_id"].strip() == "GB1"
    }
    rows = _read_csv(transfers_path)
    missing_seasons = {row["transfer_season"].strip() for row in rows} - {
        season for season, _ in membership
    }
    if missing_seasons:
        raise ValueError(f"Premier League lookup does not cover seasons: {sorted(missing_seasons)}")

    counts = {
        "input_transfer_records": len(rows),
        "excluded_premier_league_origin_records": 0,
        "excluded_non_club_origin_records": 0,
        "excluded_non_club_destination_records": 0,
        "excluded_missing_age_records": 0,
        "excluded_unusable_age_records": 0,
    }
    sample = []
    for row in rows:
        season = row["transfer_season"].strip()
        origin = int(row["from_club_id"])
        if (season, origin) in membership:
            counts["excluded_premier_league_origin_records"] += 1
            continue
        if origin in NON_CLUB_IDS:
            counts["excluded_non_club_origin_records"] += 1
            continue
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
             (season, destination) in membership)
        )
    counts["eligible_transfer_records"] = len(sample)
    counts["eligible_records_by_season"] = dict(sorted(Counter(r[2] for r in sample).items()))
    return sample, counts


def _lower_tail_p_value(simulated_gaps, observed_gap):
    lower_or_equal = int(np.count_nonzero(simulated_gaps <= observed_gap))
    return lower_or_equal, (1 + lower_or_equal) / (1 + len(simulated_gaps))


def _run_test(sample, n_permutations, rng):
    older = np.array([row[3] for row in sample], dtype=bool)
    joins = np.array([row[4] for row in sample], dtype=bool)
    older_total = int(older.sum())
    younger_total = len(sample) - older_total
    if not older_total or not younger_total:
        raise ValueError("Both age groups must have eligible transfers.")

    grouped = defaultdict(list)
    for index, row in enumerate(sample):
        grouped[(row[1], row[2])].append(index)
    groups = [np.array(indices, dtype=int) for indices in grouped.values()]
    group_starts = np.cumsum([0] + [len(indices) for indices in groups[:-1]])
    grouped_indices = np.concatenate(groups)
    group_older_counts = np.add.reduceat(older[grouped_indices].astype(int), group_starts)
    mixed_groups = [
        indices for indices, count in zip(groups, group_older_counts)
        if 0 < count < len(indices)
    ]
    older_arrivals = int(np.count_nonzero(older & joins))
    total_arrivals = int(joins.sum())

    def gap(older_arrival_count):
        return 100 * (
            older_arrival_count / older_total
            - (total_arrivals - older_arrival_count) / younger_total
        )

    observed_gap = gap(older_arrivals)
    simulated_gaps = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = older.copy()
        for indices in mixed_groups:
            shuffled[indices] = rng.permutation(older[indices])
        # Verify every stratum, including fixed groups, on every draw.
        shuffled_counts = np.add.reduceat(shuffled[grouped_indices].astype(int), group_starts)
        if not np.array_equal(shuffled_counts, group_older_counts):
            raise AssertionError("Shuffle changed age-group counts within an origin/season.")
        simulated_gaps[permutation] = gap(int(np.count_nonzero(shuffled & joins)))

    player_counts = Counter(row[0] for row in sample)
    lower_or_equal, p_value = _lower_tail_p_value(simulated_gaps, observed_gap)
    age_groups = {}
    for name, total, arrivals in (
        ("under_30", younger_total, total_arrivals - older_arrivals),
        ("age_30_plus", older_total, older_arrivals),
    ):
        age_groups[name] = {
            "eligible_transfer_records": total,
            "premier_league_arrival_records": arrivals,
            "non_premier_league_destination_records": total - arrivals,
            "joining_rate_percent": 100 * arrivals / total,
        }
    return {
        "alternative": ALTERNATIVE,
        "sample_counts": {
            "eligible_transfer_records": len(sample),
            "distinct_players": len(player_counts),
            "players_with_multiple_eligible_records": sum(n > 1 for n in player_counts.values()),
            "records_from_repeat_players": sum(n for n in player_counts.values() if n > 1),
            "additional_records_beyond_one_per_player": len(sample) - len(player_counts),
            "origin_club_season_groups": len(groups),
            "groups_with_both_age_labels": len(mixed_groups),
            "eligible_records_by_season": dict(sorted(Counter(r[2] for r in sample).items())),
        },
        "age_groups": age_groups,
        "observed_gap_percentage_points": observed_gap,
        "shuffle_mean_gap_percentage_points": float(simulated_gaps.mean()),
        "simulated_gaps_less_than_or_equal_to_observed": lower_or_equal,
        "simulated_gaps_equal_to_observed": int(np.count_nonzero(simulated_gaps == observed_gap)),
        "lower_tail_one_sided_p_value": p_value,
        "within_group_age_counts_verified_for_all_shuffles": True,
        "simulated_gaps_percentage_points": simulated_gaps.tolist(),
    }


def _verify_snapshot(main):
    expected = {
        "under_30": {"premier_league_arrival_records": 2735, "eligible_transfer_records": 18398},
        "age_30_plus": {"premier_league_arrival_records": 147, "eligible_transfer_records": 1314},
    }
    discrepancies = {
        f"{group}.{field}": {"observed": main["age_groups"][group][field], "expected": value}
        for group, fields in expected.items() for field, value in fields.items()
        if main["age_groups"][group][field] != value
    }
    if discrepancies:
        warnings.warn(f"Input counts differ from the instruction snapshot: {discrepancies}")
    return {"all_reference_counts_match": not discrepancies, "discrepancies": discrepancies}


def _save_figures(main, sensitivity, output_dir):
    analyses = [main, sensitivity]
    for analysis, suffix in zip(
        analyses,
        ["all_eligible_transfers", "one_transfer_per_player"],
    ):
        values = analysis["simulated_gaps_percentage_points"] + [
            analysis["observed_gap_percentage_points"], analysis["shuffle_mean_gap_percentage_points"]
        ]
        low, high = min(values), max(values)
        padding = 0.3 if suffix == "all_eligible_transfers" else max((high - low) * 0.08, 0.3)
        bins = np.linspace(low - padding, high + padding, 31)
        fig, ax = plt.subplots(figsize=(9, 6))
        fig.subplots_adjust(
            left=0.1, right=0.97, bottom=0.2,
            top=0.83 if suffix == "one_transfer_per_player" else 0.88,
        )
        fig.suptitle(
            (
                "Age-label permutation null model\non a fixed network with one eligible transfer\n"
                "sampled uniformly at random per player"
                if suffix == "one_transfer_per_player"
                else "Age-label permutation null model\non the fixed observed transfer network"
            ),
            fontsize=15, y=0.98,
        )
        ax.hist(analysis["simulated_gaps_percentage_points"], bins=bins,
                color="#0072B2",
                label=f"Shuffles (n = {len(analysis['simulated_gaps_percentage_points']):,})",
                alpha=0.9, rwidth=0.9)
        ax.axvline(analysis["observed_gap_percentage_points"], color="#D55E00",
                   linewidth=2.5,
                   label=f"Observed gap: {analysis['observed_gap_percentage_points']:.2f}")
        null_mean = analysis["shuffle_mean_gap_percentage_points"]
        null_sd = np.std(analysis["simulated_gaps_percentage_points"], ddof=1)
        if null_sd > 0:
            x = np.linspace(bins[0], bins[-1], 500)
            density = np.exp(-0.5 * ((x - null_mean) / null_sd) ** 2) / (
                null_sd * np.sqrt(2 * np.pi)
            )
            expected_counts = density * len(analysis["simulated_gaps_percentage_points"]) * (bins[1] - bins[0])
            ax.plot(x, expected_counts, color="#333333", linewidth=2, label="Normal fit")
        ax.axvline(null_mean, color="#CC0000", linewidth=2.5, linestyle="--",
                   label=f"Null mean: {null_mean:.2f} ± {null_sd:.2f}")
        ax.set_xlim(bins[0], bins[-1])
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.set_ylabel("Number of shuffles", fontsize=11)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.7)
        ax.legend(loc="upper right", fontsize=10, frameon=True, fancybox=True,
                  facecolor="white", edgecolor="#D0D5DD", framealpha=1,
                  borderpad=0.9, labelspacing=0.6)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.35)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel(
            "Premier League joining-rate gap\n(30+ minus under 30, percentage points)",
            fontsize=12, labelpad=12,
        )
        fig.savefig(Path(output_dir) / f"age_shuffle_outsideprem_toprem_{suffix}.png", dpi=300)
        plt.close(fig)


def run_age_shuffle_outsideprem_toprem(
    transfers_path, league_lookup_path, output_dir, *, n_permutations=999, seed=2026
):
    """Save and return transfer-level and one-transfer-per-player permutation tests.

    Joining rates use all eligible transfers as denominators. Rates are percentages
    and gaps are percentage points. The lower-tail test assumes age labels are
    exchangeable within origin club and season; repeat players can undermine this.
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
    if len(selected) != len(by_player) or len({row[0] for row in selected}) != len(by_player):
        raise AssertionError("Sensitivity sample must contain exactly one transfer per eligible player.")
    sensitivity = _run_test(selected, n_permutations, np.random.default_rng(sensitivity_stream))
    results = {
        "seed": int(seed),
        "n_permutations": n_permutations,
        "alternative": ALTERNATIVE,
        "shuffle_groups": ["from_club_id", "transfer_season"],
        "input_paths": {
            "transfers": str(Path(transfers_path).resolve()),
            "league_lookup": str(Path(league_lookup_path).resolve()),
        },
        "random_streams": {
            "method": "NumPy SeedSequence.spawn",
            "child_0": "main_shuffle",
            "child_1": "one_transfer_per_player_selection",
            "child_2": "sensitivity_shuffle",
        },
        "interpretation": (
            "The main analysis describes recorded transfers. Its p-value is conditional on "
            "exchangeable age labels within origin club and season. Repeated players can "
            "undermine this assumption. The sensitivity check describes one fixed sample "
            "of uniformly selected eligible transfers, one per player, and is not a "
            "population-wide or causal comparison. Negative gaps mean lower older-group joining rates."
        ),
        "sample_and_exclusion_counts": counts,
        "snapshot_verification": _verify_snapshot(main),
        "sensitivity_selection_verified_one_record_per_eligible_player": True,
        "all_eligible_transfers": main,
        "one_transfer_per_player": sensitivity,
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _save_figures(main, sensitivity, output_dir)
    with (output_dir / "age_shuffle_outsideprem_toprem_results.json").open("w", encoding="utf-8") as handle:
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
    results = run_age_shuffle_outsideprem_toprem(**vars(args))
    print(json.dumps({
        name: {key: value for key, value in results[name].items()
               if key != "simulated_gaps_percentage_points"}
        for name in ("all_eligible_transfers", "one_transfer_per_player")
    }, indent=2))
    print(f"Saved outputs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    _main()
