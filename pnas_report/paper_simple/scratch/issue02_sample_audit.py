"""Read-only sample audit; writes only adjacent Issue 02 audit artifacts.

Run from any directory: python <path to this file>.
Does not rerun sentiment, hypothesis tests, fetch articles, or change selections.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPORT = HERE.parents[1]
DATA = REPORT / "data"
KEY = ["player_id", "transfer_date", "from_club_id", "to_club_id"]


def read(path):
    return pd.read_csv(DATA / path)


def keys(frame):
    return pd.MultiIndex.from_frame(frame[KEY])


def describe(frame, age):
    counts = frame.player_id.value_counts()
    return dict(rows=len(frame), players=int(counts.size),
                repeated_players=int((counts > 1).sum()),
                max_records_per_player=int(counts.max()),
                under30=int((frame[age] < 30).sum()),
                age30plus=int((frame[age] >= 30).sum()),
                age_min=int(frame[age].min()), age_max=int(frame[age].max()),
                date_min=frame.transfer_date.min(), date_max=frame.transfer_date.max(),
                duplicate_event_keys=int(keys(frame).duplicated().sum()))


g = read("dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz")
c = read("dataset_graph/cleaned_transfers_with_players.csv.gz")
r = read("dataset_graph/reduced_cleaned_transfers_with_players.csv.gz")
t = read("transfermarkt-datasets/transfers.csv.gz")
s = read("dataset_nlp/data/signings.csv")
tone = read("dataset_nlp/results/signing_tone.csv")
ap = read("dataset_nlp/data/article_player_notext.csv.gz")
lookup = read("top_five_league_clubs.csv")
excluded = read("exclusion_criteria.csv")
pl = set(zip(lookup.loc[lookup.competition_id.eq("GB1"), "transfer_season"],
             lookup.loc[lookup.competition_id.eq("GB1"), "club_id"]))
top = set(zip(lookup.transfer_season, lookup.club_id))


def membership(frame, column, members=pl):
    return pd.Series([(season, club) in members for season, club in
                      zip(frame.transfer_season, frame[column])], index=frame.index)


# Independently reconstruct the graph selections from their saved parent tables.
expected_r = c[membership(c, "from_club_id", top) | membership(c, "to_club_id", top)]
expected_c = t[~t.from_club_id.isin(excluded.club_id) & ~t.to_club_id.isin(excluded.club_id)]
expected_g = r[~membership(r, "from_club_id") &
               ~r.from_club_id.isin([515, 123, 2113]) &
               ~r.to_club_id.isin([515, 123, 2113]) &
               r.age_when_transferred.ge(0) & r.age_when_transferred.notna()]
g["joins_pl"] = membership(g, "to_club_id")
g["date_season_year"] = pd.to_datetime(g.transfer_date).dt.year - (
    pd.to_datetime(g.transfer_date).dt.month < 7).astype(int)
g["label_season_year"] = g.transfer_season.str[:2].astype(int) + 2000
born = pd.to_datetime(g.date_of_birth)
on = pd.to_datetime(g.transfer_date)
age = on.dt.year - born.dt.year - (
    on.dt.month * 100 + on.dt.day < born.dt.month * 100 + born.dt.day).astype(int)

# Reuse select() with the local raw snapshot; intercept its save operation.
spec = importlib.util.spec_from_file_location(
    "issue02_pipeline", DATA / "dataset_nlp/pipeline/get_guardian_articles.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
pipeline.DATA = DATA / "transfermarkt-datasets"
pipeline.save_csv = lambda *args: True
log = io.StringIO()
with contextlib.redirect_stdout(log):
    selected = pipeline.select()
selected.transfer_date = selected.transfer_date.astype(str)
selected.date_of_birth = selected.date_of_birth.astype(str)
saved_indexed = s.set_index("signing_id").sort_index()
selected_indexed = selected.set_index("signing_id").sort_index()
column_disagreements = {}
for column in saved_indexed:
    left, right = saved_indexed[column], selected_indexed[column]
    column_disagreements[column] = int((~(left.eq(right) | (left.isna() & right.isna()))).sum())

history = t.copy()
history.transfer_date = pd.to_datetime(history.transfer_date)
history = history.reset_index().sort_values(["player_id", "transfer_date", "index"])
previous = history.groupby("player_id")[["from_club_id", "to_club_id", "transfer_date"]].shift()
history["reverse730"] = (previous.from_club_id.eq(history.to_club_id) &
                         previous.to_club_id.eq(history.from_club_id) &
                         (history.transfer_date - previous.transfer_date).dt.days.le(730))
history.transfer_date = history.transfer_date.astype(str)
loan_checks = {}
for label, frame in [("h1", g), ("text", s)]:
    joined = frame.merge(history[KEY + ["reverse730"]], on=KEY, validate="one_to_one")
    loan_checks[label] = {
        "reverse730": int(joined.reverse730.sum()),
        "reverse730_unpaid_or_missing_fee": int((joined.reverse730 & ~joined.transfer_fee.gt(0)).sum()),
        "missing_fee": int(frame.transfer_fee.isna().sum())}

# Exact event linkage: player, date, origin and destination; no fuzzy matches.
audit = s.copy()
for label, frame in [("raw", t), ("cleaned", c), ("reduced", r), ("h1", g)]:
    audit[f"in_{label}"] = keys(s).isin(keys(frame))
audit["recorded_transfer_season"] = keys(s).map(
    t.drop_duplicates(KEY).set_index(KEY).transfer_season)
audit["origin_pl_date_season"] = [
    (f"{year % 100:02d}/{(year + 1) % 100:02d}", club) in pl
    for year, club in zip(s.season, s.from_club_id)]
audit["origin_pl_recorded_season"] = [
    (season, club) in pl for season, club in
    zip(audit.recorded_transfer_season, s.from_club_id)]
audit["excluded_origin_id"] = s.from_club_id.isin(excluded.club_id)
audit["nonclub_origin"] = s.from_club_id.isin([515, 123, 2113])
audit["in_main_sample"] = s.signing_id.isin(tone.loc[tone.in_main_sample, "signing_id"])
audit["link_status"] = "unexplained"
for mask, reason in [
    (~audit.in_raw, "absent from local raw snapshot"),
    (audit.in_raw & ~audit.in_cleaned, "origin excluded by graph club-ID list"),
    (audit.in_cleaned & ~audit.in_reduced, "neither endpoint in top-five lookup for recorded season"),
    (audit.in_reduced & audit.origin_pl_recorded_season, "Premier League origin in recorded season"),
    (audit.in_reduced & audit.nonclub_origin, "non-club origin"),
    (audit.in_h1, "exact H1 event match"),
]:
    audit.loc[mask, "link_status"] = reason
assert audit.link_status.ne("unexplained").all()
assert audit.loc[~audit.in_cleaned, "excluded_origin_id"].all()
matched_ages = s.merge(g[KEY + ["age_when_transferred"]], on=KEY, validate="one_to_one")

counts = ap[ap.mentions.ge(1) & ap.period.isin(["before", "after"])].groupby(
    ["signing_id", "period"]).article_id.nunique().unstack().reindex(s.signing_id).fillna(0)
main = s[s.signing_id.isin(tone.loc[tone.in_main_sample, "signing_id"])]
ps = read("dataset_nlp/results/a1_roberta_per_signing.csv")
links_main = audit[audit.in_main_sample]
season_counts = pd.crosstab(g.transfer_season, g.age_when_transferred.ge(30))
season_counts.columns = ["under30", "age30plus"]
season_counts["pl_arrivals"] = g.groupby("transfer_season").joins_pl.sum()
text_seasons = pd.crosstab(s.season, s.age_at_transfer.ge(30))
text_seasons.columns = ["under30", "age30plus"]
summary = {
    "audit_date": "2026-11-20", "h1": describe(g, "age_when_transferred"),
    "text_selected": describe(s, "age_at_transfer"),
    "text_main": describe(main, "age_at_transfer"),
    "graph_parent_checks": {
        "cleaned_rows": len(c), "reduced_rows": len(r),
        "cleaned_matches_raw_club_filter": sorted(keys(c)) == sorted(keys(expected_c)),
        "reduced_matches_parent_selection": sorted(keys(r)) == sorted(keys(expected_r)),
        "h1_matches_parent_selection": sorted(keys(g)) == sorted(keys(expected_g)),
        "age_disagreements_with_completed_years": int(age.ne(g.age_when_transferred).sum()),
        "matched_text_age_disagreements": int(matched_ages.age_at_transfer.ne(matched_ages.age_when_transferred).sum()),
        "same_club_events": int(g.from_club_id.eq(g.to_club_id).sum()),
        "missing_transfer_market_value": int(g.market_value_in_eur_transfer.isna().sum()),
        "transfer_market_value_below_2m": int(g.market_value_in_eur_transfer.lt(2000000).sum())},
    "h1_period_checks": {
        "after_audit_date": int(g.transfer_date.gt("2026-11-20").sum()),
        "after_documented_membership_audit_date": int(g.transfer_date.gt("2026-11-04").sum()),
        "latest_nonfuture_date": g.loc[g.transfer_date.le("2026-11-20"), "transfer_date"].max(),
        "date_vs_recorded_season_disagreements": int(g.date_season_year.ne(g.label_season_year).sum()),
        "future_by_age_and_outcome": g[g.transfer_date.gt("2026-11-20")].groupby(
            [g.age_when_transferred.ge(30), "joins_pl"]).size().to_string()},
    "h1_arrivals": g.groupby(g.age_when_transferred.ge(30)).joins_pl.agg(["sum", "size"]).to_dict(),
    "local_select_reproduction": {
        "rows": len(selected), "same_event_keys": sorted(keys(s)) == sorted(keys(selected)),
        "saved_only": int((~keys(s).isin(keys(selected))).sum()),
        "local_only": int((~keys(selected).isin(keys(s))).sum()),
        "column_disagreements": column_disagreements, "selection_log": log.getvalue()},
    "loan_heuristic_checks": loan_checks,
    "link_status_selected": audit.link_status.value_counts().to_dict(),
    "link_status_main": links_main.link_status.value_counts().to_dict(),
    "matched_age_groups": audit[audit.in_h1].age_at_transfer.ge(30).value_counts().to_dict(),
    "main_matched_age_groups": links_main[links_main.in_h1].age_at_transfer.ge(30).value_counts().to_dict(),
    "text_date_vs_recorded_season_disagreements": int(
        audit.recorded_transfer_season.str[:2].astype(int).add(2000).ne(audit.season).sum()),
    "text_origin_membership_disagreements": int(
        audit.origin_pl_date_season.ne(audit.origin_pl_recorded_season).sum()),
    "text_coverage": {
        "article_signing_links": len(ap), "unique_articles": int(ap.article_id.nunique()),
        "linked_signings": int(ap.signing_id.nunique()),
        "date_min": ap.publication_date.min(), "date_max": ap.publication_date.max(),
        "days_min": int(ap.days_from_transfer.min()), "days_max": int(ap.days_from_transfer.max()),
        "duplicate_article_signing": int(ap.duplicated(["article_id", "signing_id"]).sum()),
        "duplicate_article_player": int(ap.duplicated(["article_id", "player_id"]).sum()),
        "counts_match_tone_before": bool((counts.before.to_numpy() == tone.articles_before.to_numpy()).all()),
        "counts_match_tone_after": bool((counts.after.to_numpy() == tone.articles_after.to_numpy()).all()),
        "main_keys_match_per_signing": set(main.signing_id) == set(ps.signing_id),
        "min_main_sentences_before": int(ps.n_sent_before.min()),
        "min_main_sentences_after": int(ps.n_sent_after.min()),
        "latest_requested_article_date": str((pd.to_datetime(s.transfer_date).max() + pd.Timedelta(days=365)).date()),
        "period_counts": ap.period.value_counts().to_dict()},
    "h1_seasons": season_counts.to_dict(orient="index"),
    "text_seasons": text_seasons.to_dict(orient="index"),
}
summary["proposed_h1_period_counts"] = {}
for label, mask in {
    "recorded_seasons_2012_to_2024": g.label_season_year.between(2012, 2024),
    "dates_2012_07_01_to_2025_06_30": g.transfer_date.between("2012-07-01", "2025-06-30"),
}.items():
    frame = g[mask]
    summary["proposed_h1_period_counts"][label] = {
        "events": len(frame), "under30": int(frame.age_when_transferred.lt(30).sum()),
        "age30plus": int(frame.age_when_transferred.ge(30).sum()),
        "players": int(frame.player_id.nunique())}
summary["input_sha256"] = {}
for path in ["transfermarkt-datasets/transfers.csv.gz", "transfermarkt-datasets/players.csv.gz",
             "transfermarkt-datasets/games.csv.gz", "top_five_league_clubs.csv", "exclusion_criteria.csv",
             "dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz", "dataset_nlp/data/signings.csv",
             "dataset_nlp/data/article_player_notext.csv.gz", "dataset_nlp/results/signing_tone.csv",
             "dataset_nlp/results/a1_h2b_controls.csv"]:
    summary["input_sha256"][path] = hashlib.sha256((DATA / path).read_bytes()).hexdigest()
audit.to_csv(HERE / "issue02_signing_linkage.csv", index=False)
(HERE / "issue02_sample_audit.json").write_text(
    json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k not in ["h1_seasons", "text_seasons"]},
                 indent=2, default=str))
