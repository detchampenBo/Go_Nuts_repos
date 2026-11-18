"""Join the manually sourced ownership evidence to the exact feeder-route sample.

This reproduces a bounded source audit, not a complete beneficial-owner registry.
Edit the cited evidence JSON when research establishes another ownership interval.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from premier_league_feeder_routes import _build_sample


PROJECT_DIR = Path(__file__).resolve().parents[1]
KEYS = ["from_club_id", "to_club_id"]
PREFIX = "premier_league_feeder_ownership"


def run_ownership_audit():
    output = PROJECT_DIR / "output"
    paths = {
        "routes": output / "premier_league_feeder_routes.csv",
        "selected_routes": output / "premier_league_feeder_significant_routes.csv",
        "shuffle_results": output / "premier_league_feeder_results.json",
        "transfers": PROJECT_DIR / "data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz",
        "membership": PROJECT_DIR / "data/top_five_league_clubs.csv",
        "ownership_evidence": output / f"{PREFIX}_evidence.json",
    }
    evidence = json.loads(paths["ownership_evidence"].read_text(encoding="utf-8"))
    shuffle = json.loads(paths["shuffle_results"].read_text(encoding="utf-8"))
    if shuffle["n_permutations"] != 999 or shuffle["adjustment_method"] != "none":
        raise ValueError("Ownership research was screened against the 999-shuffle, unadjusted analysis.")
    full = pd.read_csv(paths["routes"])
    routes = full.loc[full.p_value.le(0.05)].sort_values(
        ["p_value", "observed_count", *KEYS], ascending=[True, False, True, True]).reset_index(drop=True)
    # The filtered CSV has been serialized once more than the complete table.
    pd.testing.assert_frame_equal(routes, pd.read_csv(paths["selected_routes"]),
                                  check_exact=False, rtol=1e-12, atol=1e-15)
    if len(routes) != 334 or routes.duplicated(KEYS).any():
        raise ValueError("The research denominator must remain the 334 unique screened routes.")

    sample, _, _, _, _ = _build_sample(paths["transfers"], paths["membership"])
    events = sample.merge(routes[KEYS], on=KEYS, validate="many_to_one")
    counts = events.groupby(KEYS).size().sort_index()
    np.testing.assert_array_equal(counts.index.to_numpy(), routes.set_index(KEYS).sort_index().index.to_numpy())
    np.testing.assert_array_equal(counts, routes.set_index(KEYS).sort_index().observed_count)
    model_start = min(row["input_date_min"] for row in shuffle["season_coverage"])
    model_end = max(row["input_date_max"] for row in shuffle["season_coverage"])
    as_of = pd.Timestamp(evidence["research_as_of"])
    cutoff = as_of + pd.Timedelta(days=1)
    events = events[[*KEYS, "transfer_season", "transfer_date", "player_id", "player_name"]].copy()
    events["confirmed_shared_owner_on_record_date"] = False
    events["ownership_boundary_uncertain"] = False
    events["in_trust_control_window"] = False
    events["common_owner"] = ""
    audit = routes.copy()
    audit["ownership_status"] = "no_documented_common_equity_found"
    audit["documented_shared_owner_during_model_interval"] = False
    audit["screening_note"] = np.where(
        audit.to_club_id.eq(281), "../notes/premier_league_feeder_ownership_audit.md#city-group-screen",
        np.where(audit.to_club_id.isin([631, 873, 1237, 1010, 703, 1003, 1148, 11, 180, 543]),
                 "../notes/feeder_ownership_candidate_sources.md",
                 "../notes/feeder_ownership_other_destinations.md"))
    for column in ("common_owner", "start_date_min", "start_date_max", "end_date_min", "end_date_max",
                   "date_precision", "ownership_sources", "ownership_note"):
        audit[column] = ""
    known_pairs = set()
    for row in evidence["confirmed_pair_intervals"]:
        pair = (row["from_club_id"], row["to_club_id"])
        if pair in known_pairs:
            raise ValueError(f"Duplicate evidence pair: {pair}")
        known_pairs.add(pair)
        route_mask = audit.from_club_id.eq(pair[0]) & audit.to_club_id.eq(pair[1])
        if route_mask.sum() != 1 or not row["sources"]:
            raise ValueError(f"Evidence pair lacks a selected route or citations: {pair}")
        start_min, start_max = pd.Timestamp(row["start_date_min"]), pd.Timestamp(row["start_date_max"])
        end_min = pd.Timestamp(row["end_date_min"]) if row["end_date_min"] else cutoff
        end_max = pd.Timestamp(row["end_date_max"]) if row["end_date_max"] else cutoff
        if not (start_min <= start_max < end_min <= end_max):
            raise ValueError(f"Invalid ownership interval bounds: {pair}")
        if not (start_max <= pd.Timestamp(model_end) and end_min > pd.Timestamp(model_start)):
            raise ValueError(f"Ownership evidence does not overlap the modelling interval: {pair}")
        for column in ("common_owner", "start_date_min", "start_date_max", "end_date_min",
                       "end_date_max", "date_precision"):
            audit.loc[route_mask, column] = row[column] or ""
        audit.loc[route_mask, "ownership_sources"] = " | ".join(row["sources"])
        audit.loc[route_mask, "ownership_note"] = row["note"]
        audit.loc[route_mask, "documented_shared_owner_during_model_interval"] = True
        event_mask = events.from_club_id.eq(pair[0]) & events.to_club_id.eq(pair[1])
        dates = pd.to_datetime(events.loc[event_mask, "transfer_date"])
        verified = dates.ge(start_max) & dates.lt(end_min) & dates.le(as_of)
        possible = dates.ge(start_min) & dates.lt(end_max) & dates.le(as_of)
        events.loc[event_mask, "confirmed_shared_owner_on_record_date"] = verified.to_numpy()
        events.loc[event_mask, "ownership_boundary_uncertain"] = (possible & ~verified).to_numpy()
        events.loc[event_mask, "common_owner"] = row["common_owner"]

    # Conservatively check the influence/control restrictions separately from equity.
    # No selected event on a verified common-owner route falls in these windows.
    for destination, origins, windows in (
        (281, [12321], [("2024-07-01", "2025-07-01")]),
        (703, [683, 2425], [("2025-04-29", "2025-06-06"), ("2026-04-17", "2026-06-10")]),
    ):
        for start, end in windows:
            mask = (events.to_club_id.eq(destination) & events.from_club_id.isin(origins)
                    & events.transfer_date.ge(start) & events.transfer_date.lt(end))
            events.loc[mask, "in_trust_control_window"] = True
    grouped = events.groupby(KEYS)
    for name, source in (
        ("ownership_concurrent_records", "confirmed_shared_owner_on_record_date"),
        ("ownership_boundary_uncertain_records", "ownership_boundary_uncertain"),
    ):
        audit = audit.merge(grouped[source].sum().rename(name), on=KEYS, validate="one_to_one")
    audit["has_ownership_concurrent_record"] = audit.ownership_concurrent_records.gt(0)
    known = audit.documented_shared_owner_during_model_interval
    audit.loc[known & audit.has_ownership_concurrent_record, "ownership_status"] = "confirmed_shared_equity_with_transfer_overlap"
    audit.loc[known & ~audit.has_ownership_concurrent_record, "ownership_status"] = "confirmed_shared_equity_outside_selected_transfer_dates"
    for origin, destination, status, note in (
        (499, 631, "unresolved_indirect_ownership_or_control", "Vitesse/Chelsea: KNVB findings and financing/control allegations do not establish a verified equity interval; see research note."),
        (504, 543, "family_connected_common_equity_unverified", "Grasshoppers/Wolves: family-connected disclosed owners; identical equity investor not verified."),
        (409, 399, "branded_network_common_equity_unverified", "Salzburg/Leeds: selected moves predate Red Bull Leeds investment; Salzburg association equity ownership differs from sponsorship."),
        (132, 281, "partnership_common_equity_unverified", "NAC/City: documented development/loan partnership does not itself establish common club equity."),
        (1096, 985, "partnership_common_equity_unverified", "Antwerp/United: loan cooperation does not establish equity ownership."),
    ):
        mask = audit.from_club_id.eq(origin) & audit.to_club_id.eq(destination)
        if audit.loc[mask, "documented_shared_owner_during_model_interval"].any():
            raise ValueError("A flagged unconfirmed case conflicts with confirmed evidence.")
        audit.loc[mask, "ownership_status"] = status
        audit.loc[mask, "ownership_note"] = note
    by_destination = audit.groupby(["to_club_id", "to_club_name"]).agg(
        screened_pairs=("from_club_id", "size"),
        documented_pairs=("documented_shared_owner_during_model_interval", "sum"),
        transfer_concurrent_pairs=("has_ownership_concurrent_record", "sum"),
    )
    results = {
        "research_as_of": evidence["research_as_of"], "definition": evidence["definition"],
        "model_seasons": [row["transfer_season"] for row in shuffle["season_coverage"]],
        "model_input_date_min": model_start, "model_input_date_max": model_end,
        "selected_route_event_date_min": events.transfer_date.min(),
        "selected_route_event_date_max": events.transfer_date.max(),
        "shuffle_permutations": shuffle["n_permutations"], "shuffle_seed": shuffle["seed"],
        "selection_threshold": "unadjusted upper-tail Monte Carlo p <= 0.05",
        "screened_unique_pairs": len(audit),
        "unique_unordered_pairs": len({tuple(sorted(pair)) for pair in audit[KEYS].itertuples(index=False, name=None)}),
        "origin_clubs": int(audit.from_club_id.nunique()), "destination_clubs": len(by_destination),
        "selected_transfer_records": len(events),
        "documented_shared_owner_pairs_during_model_interval": int(known.sum()),
        "documented_pair_percent": float(100 * known.mean()),
        "pairs_with_ownership_concurrent_transfer": int(audit.has_ownership_concurrent_record.sum()),
        "transfer_concurrent_pair_percent": float(100 * audit.has_ownership_concurrent_record.mean()),
        "selected_records_on_ever_shared_owner_pairs": int(audit.loc[known, "observed_count"].sum()),
        "ownership_concurrent_transfer_records": int(events.confirmed_shared_owner_on_record_date.sum()),
        "date_boundary_uncertain_records": int(events.ownership_boundary_uncertain.sum()),
        "selected_events_after_research_date": int(events.transfer_date.gt(evidence["research_as_of"]).sum()),
        "verified_route_events_in_trust_control_windows": int(events.in_trust_control_window.sum()),
        "unconfirmed_pairs": int((~known).sum()),
        "status_counts": {k: int(v) for k, v in audit.ownership_status.value_counts().items()},
        "verification": {
            "filtered_routes_equal_current_analysis_within_csv_roundtrip_precision": True,
            "every_route_event_count_equals_original_observed_count": True,
            "evidence_keys_are_unique_selected_pairs_with_citations": True,
            "date_bounds_valid_and_overlapping_model": True,
            "unconfirmed_is_not_proven_independent_ownership": True,
        },
        "inputs": {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                   for key, path in paths.items()},
        "source_screen_limit": "Confirmed minimum; incomplete historical minority/beneficial-owner disclosures prevent proving no common investor for all unconfirmed pairs.",
    }
    audit.to_csv(output / f"{PREFIX}_audit.csv", index=False)
    events.to_csv(output / f"{PREFIX}_events.csv", index=False)
    by_destination.to_csv(output / f"{PREFIX}_destinations.csv")
    (output / f"{PREFIX}_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    results = run_ownership_audit()
    print(json.dumps({key: value for key, value in results.items() if key not in {"inputs", "model_seasons"}}, indent=2))
