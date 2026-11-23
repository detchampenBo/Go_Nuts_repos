"""Save the approved H1 source-season subset and its reproducible provenance.

Run from the repository root:
python pnas_report/reruns/h1_2012_13-2024_25/reduce_h1_data.py
Only this rerun folder is written. No hypothesis or community analysis is run.
"""
from collections import Counter
import csv
from datetime import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]
SOURCE = REPORT / "data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz"
TARGET = RUN / "data/outsideprem_toprem_eligible_transfers.csv.gz"
PROVENANCE = RUN / "provenance"
SEASONS = [f"{year:02d}/{year + 1:02d}" for year in range(12, 25)]
EVENT_KEY = ["player_id", "transfer_date", "from_club_id", "to_club_id"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def read_gzip(path):
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def main():
    before = sha256(SOURCE)
    columns, original = read_gzip(SOURCE)
    selected = [row for row in original if row["transfer_season"] in SEASONS]
    assert len(original) == 19712 and len(selected) == 16636
    assert {row["transfer_season"] for row in selected} == set(SEASONS)
    assert len({tuple(row[key] for key in EVENT_KEY) for row in selected}) == len(selected)
    assert sum(int(row["age_when_transferred"]) >= 30 for row in selected) == 1063
    assert len({row["player_id"] for row in selected}) == 4602

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    # A fixed gzip timestamp and empty embedded filename make the saved bytes repeatable.
    with TARGET.open("wb") as binary:
        with gzip.GzipFile(filename="", mode="wb", fileobj=binary, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(selected)
    saved_columns, saved = read_gzip(TARGET)
    assert saved_columns == columns and saved == selected
    assert sha256(SOURCE) == before

    retained, excluded = [], []
    for number, row in enumerate(original, start=1):
        entry = {"source_data_row_1based": number, **{key: row[key] for key in EVENT_KEY},
                 "transfer_season": row["transfer_season"]}
        (retained if row["transfer_season"] in SEASONS else excluded).append(entry)
    row_columns = ["source_data_row_1based", *EVENT_KEY, "transfer_season"]
    write_csv(PROVENANCE / "retained_source_rows.csv", row_columns, retained)
    write_csv(PROVENANCE / "excluded_source_rows.csv", row_columns, excluded)

    lookup_path = REPORT / "data/top_five_league_clubs.csv"
    with lookup_path.open(encoding="utf-8-sig", newline="") as handle:
        pl = {(row["transfer_season"], row["club_id"]) for row in csv.DictReader(handle)
              if row["competition_id"] == "GB1"}
    counts = []
    for season in SEASONS:
        rows = [row for row in selected if row["transfer_season"] == season]
        assert all((season, row["from_club_id"]) not in pl for row in rows)
        assert all(row["from_club_id"] not in {"515", "123", "2113"} and
                   row["to_club_id"] not in {"515", "123", "2113"} for row in rows)
        counts.append({"transfer_season": season, "records": len(rows),
                       "under30": sum(int(row["age_when_transferred"]) < 30 for row in rows),
                       "age30plus": sum(int(row["age_when_transferred"]) >= 30 for row in rows),
                       "players": len({row["player_id"] for row in rows}),
                       "pl_arrivals": sum((season, row["to_club_id"]) in pl for row in rows),
                       "date_min": min(row["transfer_date"] for row in rows),
                       "date_max": max(row["transfer_date"] for row in rows)})
    write_csv(PROVENANCE / "sample_by_season.csv", list(counts[0]), counts)
    outputs = [TARGET, *(PROVENANCE / name for name in
                         ["retained_source_rows.csv", "excluded_source_rows.csv", "sample_by_season.csv"])]
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "decision": "User approved recorded transfer seasons 2012/13 through 2024/25 on 2026-11-20.",
        "selection_rule": "transfer_season in the explicit inclusive list; no transfer-date cutoff or other eligibility changes",
        "included_seasons": SEASONS,
        "source": {"path": SOURCE.relative_to(REPORT).as_posix(), "sha256": before, "rows": len(original)},
        "restricted": {"path": TARGET.relative_to(REPORT).as_posix(), "sha256": sha256(TARGET),
                       "rows": len(selected), "players": len({row["player_id"] for row in selected}),
                       "under30": 15573, "age30plus": 1063, "removed_rows": len(excluded),
                       "date_min": min(row["transfer_date"] for row in selected),
                       "date_max": max(row["transfer_date"] for row in selected),
                       "age_min": min(int(row["age_when_transferred"]) for row in selected),
                       "age_max": max(int(row["age_when_transferred"]) for row in selected),
                       "repeated_players": sum(n > 1 for n in Counter(row["player_id"] for row in selected).values()),
                       "clubs": len({row[key] for row in selected for key in ["from_club_id", "to_club_id"]}),
                       "directed_routes": len({(row["from_club_id"], row["to_club_id"]) for row in selected})},
        "columns": columns,
        "source_data_row_numbering": "One-based CSV data rows excluding the header, in original file order.",
        "checks": {"source_unchanged": True, "original_order_preserved": True,
                   "all_field_values_preserved": True, "saved_roundtrip_exact": True,
                   "event_keys_unique": True, "no_unapproved_eligibility_change": True,
                   "every_origin_outside_pl_in_recorded_season": True,
                   "no_nonclub_endpoints": True},
        "context_inputs_sha256": {path.relative_to(REPORT).as_posix(): sha256(path) for path in
                                  [lookup_path, REPORT / "data/exclusion_criteria.csv"]},
        "outputs_sha256": {path.relative_to(RUN).as_posix(): sha256(path) for path in outputs},
        "reduction_code_sha256": sha256(Path(__file__).resolve()),
        "python_version": sys.version,
        "limitations": ["Source-season labels are retained and are not identical to July-June date assignments.",
                        "Period restriction does not certify complete transfer histories or repair club-name exclusions.",
                        "No H1 permutation, structural analysis, or text analysis was rerun here."],
    }
    (PROVENANCE / "reduction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest["restricted"], indent=2))


if __name__ == "__main__":
    main()
