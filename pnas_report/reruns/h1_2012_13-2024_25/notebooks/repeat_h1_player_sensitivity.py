"""Reproduce the paper's fixed draw and run 999 new one-transfer-per-player draws."""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
from itertools import repeat
import json
import math
import os
from pathlib import Path
import sys

import numpy as np

RERUN = Path(__file__).resolve().parents[1]
REPORT = RERUN.parents[1]
sys.path.insert(0, str(REPORT / "notebooks"))
from age_shuffle_outsideprem_toprem import _build_sample, _run_test


DRAWS = 999
SHUFFLES = 999
MASTER_SEED = 20261126
PLAYERS = 4602
STEM = "repeat_h1_player_sensitivity"
GAP = "observed_gap_percentage_points"
SHUFFLED_MEAN = "shuffle_mean_gap_percentage_points"
P_VALUE = "lower_tail_one_sided_p_value"
LOWER_TAIL_COUNT = "simulated_gaps_less_than_or_equal_to_observed"
AGE_GROUPS = ("age_30_plus", "under_30")


def select_and_test(by_player, selection_seed, shuffle_seed):
    selection_rng = np.random.default_rng(selection_seed)
    selected = [rows[int(selection_rng.choice(len(rows)))] for rows in by_player.values()]
    if len(selected) != PLAYERS or {row[0] for row in selected} != by_player.keys():
        raise AssertionError("Expected exactly one transfer for each of the 4,602 players.")
    return _run_test(selected, SHUFFLES, np.random.default_rng(shuffle_seed))


def run_draw(draw, draw_seed, by_player):
    result = select_and_test(by_player, *draw_seed.spawn(2))
    row = {"draw": draw, "distinct_players": result["sample_counts"]["distinct_players"]}
    for group in AGE_GROUPS:
        stats = result["age_groups"][group]
        row[f"{group}_count"] = stats["eligible_transfer_records"]
        row[f"{group}_entries"] = stats["premier_league_arrival_records"]
        row[f"{group}_entry_rate_percent"] = stats["joining_rate_percent"]
    row.update({field: result[field] for field in (GAP, SHUFFLED_MEAN, LOWER_TAIL_COUNT, P_VALUE)})
    return row


def summarize(csv_path, original, original_seed):
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if [int(row["draw"]) for row in rows] != list(range(1, DRAWS + 1)):
        raise AssertionError(f"Expected {DRAWS} saved draws in order.")
    for row in rows:
        counts = [int(row[f"{group}_count"]) for group in AGE_GROUPS]
        entries = [int(row[f"{group}_entries"]) for group in AGE_GROUPS]
        rates = [float(row[f"{group}_entry_rate_percent"]) for group in AGE_GROUPS]
        tail_count = int(row[LOWER_TAIL_COUNT])
        if (
            int(row["distinct_players"]) != PLAYERS
            or sum(counts) != PLAYERS
            or not all(0 <= entry <= count and count > 0 for entry, count in zip(entries, counts))
            or rates != [100 * entry / count for entry, count in zip(entries, counts)]
            or not math.isclose(float(row[GAP]), rates[0] - rates[1], abs_tol=1e-12)
            or not math.isfinite(float(row[SHUFFLED_MEAN]))
            or not 0 <= tail_count <= SHUFFLES
            or float(row[P_VALUE]) != (1 + tail_count) / (1 + SHUFFLES)
        ):
            raise AssertionError(f"Invalid values in draw {row['draw']}.")

    gaps = np.array([float(row[GAP]) for row in rows])
    centered = gaps - np.array([float(row[SHUFFLED_MEAN]) for row in rows])
    p_values = np.array([float(row[P_VALUE]) for row in rows])
    original_centered = original[GAP] - original[SHUFFLED_MEAN]
    table = []
    for label, values, reference, precision in (
        ("Observed gap (pp)", gaps, original[GAP], 4),
        ("Observed gap minus its shuffle mean (pp)", centered, original_centered, 4),
        ("Conditional lower-tail p-value", p_values, original[P_VALUE], 3),
    ):
        low, median, high = np.percentile(values, [2.5, 50, 97.5])
        rank = np.count_nonzero(values <= reference)
        table.append(
            f"| {label} | {median:.{precision}f} | [{low:.{precision}f}, {high:.{precision}f}] "
            f"| {reference:.{precision}f} | {rank}/{DRAWS} ({rank / DRAWS:.2%}) |"
        )
    table_rows = "\n".join(table)
    older, younger = (original["age_groups"][group] for group in AGE_GROUPS)
    negative = np.count_nonzero(gaps < 0)
    below_mean = np.count_nonzero(centered < 0)

    return f"""# Repeated H1 one-transfer-per-player sensitivity check

The restricted 2012/13–2024/25 input and Premier League lookup matched the reduction
manifest hashes. The sample contained 16,636 eligible transfers from {PLAYERS:,} players.
The original selection (seed {original_seed}) reproduced the saved result exactly,
including all {SHUFFLES} ordered shuffle gaps. Premier League entry rates were
{older['joining_rate_percent']:.2f}% at age 30+ ({older['premier_league_arrival_records']}/{older['eligible_transfer_records']})
and {younger['joining_rate_percent']:.2f}% under 30 ({younger['premier_league_arrival_records']}/{younger['eligible_transfer_records']}).
The original shuffle mean was {original[SHUFFLED_MEAN]:.4f} percentage points.

| Statistic | Median | Central 95% | Original draw | Draws at or below original |
|---|---:|---:|---:|---:|
{table_rows}

The central 95% uses the empirical 2.5th and 97.5th percentiles with linear interpolation.
The observed gap was below zero in {negative}/{DRAWS} draws ({negative / DRAWS:.2%})
and below its own shuffle mean in {below_mean}/{DRAWS} draws ({below_mean / DRAWS:.2%}).
The spread measures sensitivity to which eligible transfer represents each player
in this fixed set of players. Each p-value is conditional on its selected transfers.

Each draw selected one transfer uniformly per player, with age classified at that
transfer. The selected transfers stayed fixed for {SHUFFLES} age-label permutations
within origin club and recorded season. Lower-tail p-values counted shuffled gaps
at or below the observed older-minus-younger gap, with a plus-one adjustment.
All draws contained {PLAYERS:,} distinct players and both age groups. The original
permutation routine checked the age-group counts in every stratum of every shuffle.

Run from the repository root with Python {sys.version.split()[0]} and NumPy {np.__version__}.
NumPy `SeedSequence({MASTER_SEED})` spawned {DRAWS} child seeds in draw order, and each child
spawned separate `default_rng` streams for transfer selection and shuffling.
The summary was generated by reading back the saved [per-draw CSV]({csv_path.name}).

```powershell
python -B pnas_report/reruns/h1_2012_13-2024_25/notebooks/{STEM}.py
```
"""


def main():
    transfers = RERUN / "data/outsideprem_toprem_eligible_transfers.csv.gz"
    lookup = REPORT / "data/top_five_league_clubs.csv"
    manifest = json.loads((RERUN / "provenance/reduction_manifest.json").read_text(encoding="utf-8"))
    for path, expected in (
        (transfers, manifest["outputs_sha256"][f"data/{transfers.name}"]),
        (lookup, manifest["context_inputs_sha256"][f"data/{lookup.name}"]),
    ):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise AssertionError(f"Input hash mismatch for {path}.")
    sample, counts = _build_sample(transfers, lookup)
    by_player = defaultdict(list)
    for row in sample:
        by_player[row[0]].append(row)
    if (len(sample), len(by_player)) != (16636, PLAYERS):
        raise AssertionError("Unexpected restricted sample size.")

    output = RERUN / "output"
    saved_path = output / "age_shuffle_outsideprem_toprem_results.json"
    saved = json.loads(saved_path.read_text(encoding="utf-8"))
    _, selection, shuffle = np.random.SeedSequence(saved["seed"]).spawn(3)
    original = select_and_test(by_player, selection, shuffle)
    if original != saved["one_transfer_per_player"] or counts != saved["sample_and_exclusion_counts"]:
        raise AssertionError("Failed to reproduce the original fixed draw exactly.")
    print(f"Reproduced the original draw. Starting {DRAWS} new draws.", flush=True)

    seeds = np.random.SeedSequence(MASTER_SEED).spawn(DRAWS)
    with ProcessPoolExecutor(max_workers=min(10, os.cpu_count() or 1)) as pool:
        draws = pool.map(run_draw, range(1, DRAWS + 1), seeds, repeat(by_player), chunksize=5)
        rows = []
        for row in draws:
            rows.append(row)
            if len(rows) % 100 == 0 or len(rows) == DRAWS:
                print(f"Completed {len(rows)} of {DRAWS} draws.", flush=True)

    csv_path = output / f"{STEM}_draws.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / f"{STEM}_summary.md").write_text(
        summarize(csv_path, original, saved["seed"]), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
