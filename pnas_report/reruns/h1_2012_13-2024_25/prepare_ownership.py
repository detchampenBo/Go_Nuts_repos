"""Scope the existing cited screen to new routes, without inventing new research."""
from copy import deepcopy
import difflib
import hashlib
import json
from pathlib import Path
import shutil

import pandas as pd

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]
KEYS = ["from_club_id", "to_club_id"]


def main():
    output = RUN / "output"
    evidence_path = REPORT / "output/premier_league_feeder_ownership_evidence.json"
    original = json.loads(evidence_path.read_text())
    shutil.copyfile(evidence_path, RUN / "provenance/original_ownership_evidence.json")
    old = pd.read_csv(REPORT / "output/premier_league_feeder_ownership_audit.csv")
    new = pd.read_csv(output / "premier_league_feeder_selected_routes.csv")
    old_pairs = set(old[KEYS].itertuples(index=False, name=None))
    new_pairs = set(new[KEYS].itertuples(index=False, name=None))
    evidence = deepcopy(original)
    feeder = json.loads((output / "premier_league_feeder_results.json").read_text())
    model_start = min(row["input_date_min"] for row in feeder["season_coverage"])
    model_end = max(row["input_date_max"] for row in feeder["season_coverage"])
    omitted = []
    for field in ["confirmed_pair_intervals", "manual_joint_ownership_pairs"]:
        kept = []
        for row in evidence[field]:
            pair = row["from_club_id"], row["to_club_id"]
            if pair not in new_pairs:
                omitted.append({"field": field, "pair": pair, "reason": "not selected in restricted analysis"})
                continue
            if field == "confirmed_pair_intervals" and not (
                row["start_date_max"] <= model_end and
                (row["end_date_min"] or original["research_as_of"]) > model_start
            ):
                omitted.append({"field": field, "pair": pair, "reason": "documented interval does not overlap restricted model dates"})
                continue
            row["note"] = "Historical broad-period research note: " + row["note"]
            count = int(new.set_index(KEYS).loc[pair, "observed_count"])
            if field == "manual_joint_ownership_pairs":
                row["note"] += f" Restricted-run application retains the authorised manual inclusion of all {count} selected pooled records; no verified equity interval is asserted."
            kept.append(row)
        evidence[field] = kept
    (output / evidence_path.name).write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = new[KEYS + ["from_club_name", "to_club_name", "observed_count"]].copy()
    ledger["previously_screened_route"] = [pair in old_pairs for pair in new[KEYS].itertuples(index=False, name=None)]
    ledger["coverage_status"] = ledger.previously_screened_route.map({True: "existing_bounded_screen_reused", False: "new_selected_route_not_screened"})
    ledger.to_csv(RUN / "provenance/ownership_coverage_ledger.csv", index=False)
    scoping = {"original_evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
               "selected_routes": len(new), "previously_screened_routes": int(ledger.previously_screened_route.sum()),
               "new_unscreened_routes": int((~ledger.previously_screened_route).sum()),
               "omitted_evidence": omitted, "new_research_performed": False}
    (RUN / "provenance/ownership_scoping.json").write_text(json.dumps(scoping, indent=2) + "\n")
    # Copy the route module only as an unchanged library for its existing sample builder.
    shutil.copyfile(REPORT / "notebooks/premier_league_feeder_routes.py", RUN / "notebooks/premier_league_feeder_routes.py")
    source = REPORT / "notebooks/premier_league_feeder_ownership_audit.py"
    before = source.read_text(encoding="utf-8")
    text = before.replace('PROJECT_DIR / "data/dataset_graph/', 'PROJECT_DIR / "data/')
    text = text.replace('PROJECT_DIR / "data/top_five_league_clubs.csv"',
                        'PROJECT_DIR.parents[1] / "data/top_five_league_clubs.csv"')
    text = text.replace('../notes/', '../../../notes/')
    text = text.replace('    known_pairs = set()',
        '    coverage = pd.read_csv(PROJECT_DIR / "provenance/ownership_coverage_ledger.csv")\n'
        '    screened_pairs = set(coverage.loc[coverage.previously_screened_route, KEYS].itertuples(index=False, name=None))\n'
        '    screened_mask = np.array([pair in screened_pairs for pair in audit[KEYS].itertuples(index=False, name=None)])\n'
        '    audit.loc[~screened_mask, "ownership_status"] = "not_screened_new_selected_route"\n'
        '    audit.loc[~screened_mask, "screening_note"] = "../provenance/ownership_coverage_ledger.csv: new route, no source screen performed"\n'
        '    known_pairs = set()')
    text = text.replace('    results = {',
        '    by_destination["screened_pairs"] = audit.assign(screened=screened_mask).groupby(["to_club_id", "to_club_name"]).screened.sum()\n'
        '    results = {')
    text = text.replace('"screened_unique_pairs": len(audit)', '"screened_unique_pairs": int(screened_mask.sum())')
    text = text.replace('"source_screen_limit": "Confirmed minimum;',
        '"source_screen_limit": f"Restricted screen reuses {int(screened_mask.sum())} previously screened routes; {int((~screened_mask).sum())} newly selected routes remain unscreened. Confirmed minimum;')
    target = RUN / "notebooks" / source.name
    target.write_text(text, encoding="utf-8")
    (RUN / "provenance/ownership_source_adaptations.diff").write_text("\n".join(difflib.unified_diff(
        before.splitlines(), text.splitlines(), fromfile="original/" + source.name,
        tofile="rerun/" + source.name)) + "\n", encoding="utf-8")
    print(json.dumps(scoping, indent=2))


if __name__ == "__main__":
    main()
