"""Verify the restricted H1 outputs and write data-derived publication recaps."""
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]
sys.path.insert(0, str(REPORT / "notebooks"))
import age_shuffle_outsideprem_toprem as h1


def main():
    output = RUN / "output"
    results = json.loads((output / "age_shuffle_outsideprem_toprem_results.json").read_text())
    manifest = json.loads((RUN / "provenance/reduction_manifest.json").read_text())
    transfers = RUN / "data/outsideprem_toprem_eligible_transfers.csv.gz"
    assert hashlib.sha256(transfers.read_bytes()).hexdigest() == manifest["restricted"]["sha256"]
    sample, counts = h1._build_sample(transfers, REPORT / "data/top_five_league_clubs.csv")
    assert counts == results["sample_and_exclusion_counts"]
    assert len(sample) == manifest["restricted"]["rows"]
    main_stream, selection_stream, sensitivity_stream = np.random.SeedSequence(2026).spawn(3)
    by_player = defaultdict(list)
    for index, row in enumerate(sample):
        by_player[row[0]].append(index)
    rng = np.random.default_rng(selection_stream)
    indices = [int(rng.choice(pool)) for pool in by_player.values()]
    selected = [sample[index] for index in indices]
    assert len(selected) == len({row[0] for row in selected}) == 4602
    for name, rows, stream in [("all_eligible_transfers", sample, main_stream),
                               ("one_transfer_per_player", selected, sensitivity_stream)]:
        computed = h1._run_test(rows, 999, np.random.default_rng(stream))
        assert computed == results[name], name
        tail = sum(value <= computed["observed_gap_percentage_points"]
                   for value in computed["simulated_gaps_percentage_points"])
        assert computed["lower_tail_one_sided_p_value"] == (1 + tail) / 1000
    with (RUN / "provenance/h1_sensitivity_selected_rows.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["restricted_data_row_1based", "player_id", "from_club_id", "transfer_season",
                         "age_30_plus", "joins_premier_league"])
        writer.writerows((index + 1, *sample[index]) for index in indices)
    table = ["| Analysis | Under-30 arrivals / transfers (%) | 30+ arrivals / transfers (%) | Observed gap (pp) | Null mean (pp) | One-sided p |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    captions = []
    for key, title in [("all_eligible_transfers", "All eligible transfers"),
                       ("one_transfer_per_player", "One transfer per player")]:
        result = results[key]
        younger, older = (result["age_groups"][name] for name in ("under_30", "age_30_plus"))
        def cell(group):
            return f"{group['premier_league_arrival_records']:,} / {group['eligible_transfer_records']:,} ({group['joining_rate_percent']:.2f})"
        table.append(f"| {title} | {cell(younger)} | {cell(older)} | {result['observed_gap_percentage_points']:.2f} | {result['shuffle_mean_gap_percentage_points']:.2f} | {result['lower_tail_one_sided_p_value']:.3f} |")
        sd = np.std(result["simulated_gaps_percentage_points"], ddof=1)
        captions.append(f"**{title}.** Brown bars show 999 age-label permutations within origin club and recorded season. The orange line marks the observed gap ({result['observed_gap_percentage_points']:.2f} percentage points); the blue line marks the null mean ({result['shuffle_mean_gap_percentage_points']:.2f} ± {sd:.2f}, one sample standard deviation). The brown normal fit is illustrative; inference uses the empirical permutations.")
    summary = """# Age and Premier League entry: restricted-period permutation analysis

Recorded source seasons 2012/13–2024/25 include 16,636 eligible transfers involving 4,602 players, dated 1 July 2012–15 July 2025. This is a source-season restriction, not an exact July–June date cutoff. Other eligibility rules are unchanged. Both endpoints use season-specific Premier League membership (GB1).

Joining rates divide Premier League arrivals by all eligible transfers within each age group. The statistic is 100 × (rate_30_plus − rate_under_30), in percentage points. Seed 2026 supplies the same three SeedSequence child streams for main shuffles, player selection and sensitivity shuffles. The 999 within-origin-club/season age-label permutations hold destinations and stratum age counts fixed. The lower-tail p value includes ties and uses (1 + tail count) / 1000.

The sensitivity sample is a new uniform draw of one eligible transfer for each of the 4,602 players in the restricted input. This draw remains fixed across permutations; membership is saved in ../provenance/h1_sensitivity_selected_rows.csv.

""" + "\n".join(table) + """

Both observed gaps are negative. The one-sided permutation p values are 0.098 and 0.074; neither falls below 0.05. The null expectation need not be zero because age groups differ in origin club–season composition. Repeated players can undermine exchangeability in the main analysis. The sensitivity is conditional on one fixed draw, not an independent replication. These results describe recorded transfers and do not establish a causal age effect or exhaustive transfer histories.

![Main age-label shuffle distribution](age_shuffle_outsideprem_toprem_all_eligible_transfers.png)

[Publication exports and captions](age_shuffle_outsideprem_toprem_findings/README.md). [Saved results](age_shuffle_outsideprem_toprem_results.json). The JSON snapshot_verification compares with historical broad-period counts and is expected to differ; it is not restricted-sample validation. Restricted validation is saved in ../provenance/h1_verification.json.
"""
    (output / "age_shuffle_outsideprem_toprem_summary.md").write_text(summary, encoding="utf-8")
    readme = "# Age-label permutation figures: restricted period\n\n"
    readme += "Recorded seasons 2012/13–2024/25. Same plotting functions, sizes, bins, fonts, colors and normal-fit conventions as the original producer. Standalone views are 3.58 × 3.4 inches; comparison is 7.16 × 3.4 inches; PNGs use 600 dpi.\n\n"
    for stem in ["all_eligible_transfers", "one_transfer_per_player", "comparison"]:
        name = "age_shuffle_outsideprem_toprem_" + stem
        readme += f"{stem.replace('_', ' ')}: [PDF]({name}.pdf), [PNG]({name}.png), [SVG]({name}.svg).\n\n"
    readme += "\n\n".join(captions)
    readme += "\n\n**Combined comparison.** Panels (a) and (b) show all transfers and one fixed uniformly drawn transfer per player. Negative gaps mean lower older-group joining rates. Each panel retains its own 30-bin range. Legends reserve space above the data.\n\n[Full numerical recap and limitations](../age_shuffle_outsideprem_toprem_summary.md).\n"
    (output / "age_shuffle_outsideprem_toprem_findings/README.md").write_text(readme, encoding="utf-8")
    baseline = json.loads((RUN / "provenance/baseline_outputs_manifest.json").read_text())["files"]
    assert all(hashlib.sha256((REPORT / item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in baseline)
    expected = [item for item in baseline if item["issue"] == "01"]
    assert all((RUN / item["path"]).exists() for item in expected)
    verification = {"fresh_agent": "/root/restricted_h1_reruns", "restricted_sha256": manifest["restricted"]["sha256"],
                    "independent_recomputation_matches_all_results_and_permutations": True,
                    "sensitivity_draw_rebuilt_from_restricted_sample": True,
                    "sensitivity_one_record_per_player": True, "all_original_124_hashes_unchanged": True,
                    "h1_artifacts_present": len(expected),
                    "historical_snapshot_warning_expected": True,
                    "outputs_sha256": {item["path"]: hashlib.sha256((RUN / item["path"]).read_bytes()).hexdigest() for item in expected}}
    (RUN / "provenance/h1_verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
