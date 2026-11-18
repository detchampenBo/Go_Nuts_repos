"""Refresh the age-shuffle figures from saved results without rerunning permutations."""

import json
from pathlib import Path

from age_shuffle_outsideprem_toprem import _save_figures


def main():
    output_dir = Path(__file__).resolve().parents[1] / "output"
    results_path = output_dir / "age_shuffle_outsideprem_toprem_results.json"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    _save_figures(results["all_eligible_transfers"], results["one_transfer_per_player"], output_dir)
    print(f"Refreshed figures in {output_dir / 'age_shuffle_outsideprem_toprem_findings'}")


if __name__ == "__main__":
    main()
