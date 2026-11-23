"""Keep the feeder plot construction; use cross-file checks and current prose."""
import difflib
from pathlib import Path

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]
source = REPORT / "notebooks/plot_premier_league_feeder_findings.py"
before = source.read_text(encoding="utf-8")
text = before
start = text.index("def read_and_verify():")
end = text.index("\ndef style_axis", start)
text = text[:start] + '''def read_and_verify():
    results = json.loads((OUTPUT_DIR / "premier_league_feeder_results.json").read_text())
    ownership = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_results.json").read_text())
    evidence = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_evidence.json").read_text())
    manifest = json.loads((PROJECT_DIR / "provenance/reduction_manifest.json").read_text())
    routes = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_routes.csv")
    audit = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    events = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_events.csv")
    selected = routes.loc[routes.selected_route].copy()
    counts = results["sample_and_exclusion_counts"]
    coverage = pd.DataFrame(results["season_coverage"])
    assert coverage.pl_arrivals.sum() == routes.observed_count.sum() == counts["premier_league_arrival_records"]
    assert coverage.eligible_records.sum() == counts["eligible_transfer_records"] == manifest["restricted"]["rows"]
    observed = routes.loc[routes.observed_count.gt(0)]
    assert len(observed) == results["observed_routes"]
    assert observed.from_club_id.nunique() == counts["origin_clubs"]
    assert observed.to_club_id.nunique() == counts["destination_clubs"]
    assert len(routes) == results["testing_family_size"]
    assert np.isclose(routes.expected_count.sum(), counts["premier_league_arrival_records"])
    assert results["n_permutations"] == 999 and results["seed"] == 2026
    assert results["adjustment_method"] == "none"
    assert results["significance_threshold"] == 0.05
    assert results["minimum_route_transfers"] == 2
    assert np.array_equal(routes.significant, routes.p_value.lt(0.05))
    assert np.array_equal(routes.selected_route, routes.p_value.lt(0.05) & routes.observed_count.ge(2))
    assert np.allclose(routes.p_value, (1 + routes.permutations_greater_or_equal) / 1000)
    assert routes.significant.sum() == results["significant_route_count"]
    assert len(selected) == results["selected_route_count"] == len(audit)
    assert selected.observed_count.ge(2).all() and not audit.duplicated(KEYS).any()
    pd.testing.assert_frame_equal(selected.sort_values(KEYS).reset_index(drop=True),
                                  audit.sort_values(KEYS).reset_index(drop=True)[routes.columns])
    event_counts = events.groupby(KEYS).size().rename("observed_count")
    concurrent = events.groupby(KEYS).confirmed_shared_owner_on_record_date.sum()
    indexed = audit.set_index(KEYS).sort_index()
    assert indexed.observed_count.equals(event_counts.sort_index())
    assert np.array_equal(indexed.ownership_concurrent_records, concurrent.sort_index())
    assert np.array_equal(audit.has_ownership_concurrent_record, audit.ownership_concurrent_records.gt(0))
    assert audit.documented_shared_owner_during_model_interval.sum() == ownership["documented_shared_owner_pairs_during_model_interval"]
    assert events.ownership_boundary_uncertain.sum() == ownership["date_boundary_uncertain_records"]
    assert len(events) == audit.observed_count.sum() == results["selected_transfer_records"] == ownership["selected_transfer_records"]
    assert np.array_equal(audit.joint_ownership_group,
                          audit.has_ownership_concurrent_record | audit.manual_joint_ownership_inclusion)
    manual = audit.loc[audit.manual_joint_ownership_inclusion]
    assert set(zip(manual.from_club_id, manual.to_club_id)) == {
        (row["from_club_id"], row["to_club_id"]) for row in evidence["manual_joint_ownership_pairs"]}
    assert not manual.documented_shared_owner_during_model_interval.any()
    groups = [audit.loc[audit.joint_ownership_group.eq(flag)] for flag in [True, False]]
    assert len(groups[0]) == ownership["joint_ownership_group_pairs"]
    assert sum(len(group) for group in groups) == len(audit)
    assert all(group.observed_count.ge(2).all() for group in groups)
    assert groups[0].ownership_concurrent_records.sum() == ownership["ownership_concurrent_transfer_records"]
    ledger = pd.read_csv(PROJECT_DIR / "provenance/ownership_coverage_ledger.csv")
    assert set(ledger[KEYS].itertuples(index=False, name=None)) == set(audit[KEYS].itertuples(index=False, name=None))
    assert audit.ownership_status.eq("not_screened_new_selected_route").sum() == (~ledger.previously_screened_route).sum()
    top = selected.loc[selected.observed_count.ge(8)].sort_values(
        ["observed_count", *KEYS], ascending=[False, True, True]
    ).merge(audit[KEYS + ["joint_ownership_group", "ownership_concurrent_records",
                        "manual_joint_ownership_inclusion"]], on=KEYS, validate="one_to_one")
    assert len(top) == selected.observed_count.ge(8).sum()
    return results, coverage, top, groups

''' + text[end:]
start = text.index("def write_findings(")
end = text.index("\ndef save_figure", start)
text = text[:start] + '''def write_findings(results, coverage, top, groups):
    linked, remaining = groups
    counts = results["sample_and_exclusion_counts"]
    ownership = json.loads((OUTPUT_DIR / "premier_league_feeder_ownership_results.json").read_text())
    ledger = pd.read_csv(PROJECT_DIR / "provenance/ownership_coverage_ledger.csv")
    unscreened = int((~ledger.previously_screened_route).sum())
    manual = pd.read_csv(OUTPUT_DIR / "premier_league_feeder_ownership_audit.csv")
    manual = manual.loc[manual.manual_joint_ownership_inclusion]
    section = f"""## Two-panel feeder findings

The restricted recorded seasons are 2012/13–2024/25, with actual eligible-input dates 1 July 2012–15 July 2025. Coverage is not certified exhaustive. There are {counts['premier_league_arrival_records']:,} recorded PL arrivals from {counts['origin_clubs']} supplying clubs to {counts['destination_clubs']} receiving clubs ({counts['distinct_players']:,} distinct players). These are separate from the Guardian samples. Counts include repeat players, loans and returns. The source-season convention and original eligibility rules are retained.

Destinations are reassigned within each season, preserving seasonal origin and destination margins. Seed {results['seed']} and {results['n_permutations']} shuffles are unchanged. Expected counts sum origin-arrivals × destination-arrivals / all-arrivals over seasons. The upper-tail Monte Carlo p value includes ties and uses (1 + tail) / 1000. All {results['testing_family_size']:,} positive-expectation pairs are tested, including unobserved pairs. No multiplicity correction is applied. Of {results['significant_route_count']} pairs with unadjusted p<0.05, {results['selected_route_count']} have at least two recorded moves and contain {results['selected_transfer_records']} records.

Panel (a) displays all {len(top)} selected routes with observed count ≥8, with ties retained and descending counts/club-ID ordering. Orange bars give observed counts and blue diamonds give expected counts, labelled to one decimal. The display threshold does not change the sample used in panel (b).

| Route | Observed | Expected | Ownership annotation |
| --- | ---: | ---: | --- |
"""
    for row in top.itertuples():
        note = (f"{row.ownership_concurrent_records}/{row.observed_count} verified interval overlap" if row.ownership_concurrent_records else
                f"{row.observed_count}/{row.observed_count} manual inclusion coverage; interval unverified" if row.manual_joint_ownership_inclusion else
                "No documented shared-equity annotation; absence is not proven independence")
        section += f"| {row.from_club_name} → {row.to_club_name} | {row.observed_count} | {row.expected_count:.1f} | {note} |\\n"
    section += f"""

Shared ownership means a documented common direct or indirect club-equity investor, including minority holdings. Source intervals are start-inclusive and exit-exclusive. Red dots mark the existing joint-ownership group. Verified fractions count event-date overlaps; manual fractions indicate inclusion coverage and are not verified ownership-period counts. The two authorised manual pairs remain:

"""
    for row in manual.itertuples():
        section += f"- {row.from_club_name} → {row.to_club_name}: {row.observed_count} pooled records; equity interval remains unverified.\\n"
    section += f"""

The existing bounded source screen covers {int(ledger.previously_screened_route.sum())} of {len(ledger)} selected routes. **{unscreened} newly selected routes have not been screened** and are explicitly labelled in the [coverage ledger](../provenance/ownership_coverage_ledger.csv) and route audit. The scoped evidence omits Hearts/Liverpool's historical interval because it does not overlap the restricted model dates. No new ownership research is claimed. The remaining group includes unscreened and unresolved cases and is not a verified independently owned control group.

Panel (b) gives 100 × the fraction of each entire group with at least each integer transfer count, using inclusive pre-step curves. There is no binning, smoothing, jitter or fitted distribution. The red group contains {len(linked)} routes and the dark-brown remaining group {len(remaining)}. Curves use all {len(linked)+len(remaining)} selected observations and end at zero one count above the observed maximum. Means and medians describe pooled route counts, not ownership-period transfer counts.

| Group | Routes | Pooled records | Mean | Median |
| --- | ---: | ---: | ---: | ---: |
| Joint ownership | {len(linked)} | {int(linked.observed_count.sum())} | {linked.observed_count.mean():.6f} | {linked.observed_count.median():g} |
| Remaining routes | {len(remaining)} | {int(remaining.observed_count.sum())} | {remaining.observed_count.mean():.6f} | {remaining.observed_count.median():g} |

Of {int(linked.observed_count.sum())} pooled records in the joint group, {ownership['ownership_concurrent_transfer_records']} have verified event-date ownership overlap. The comparison is descriptive and does not establish causation, an ownership effect, financial mechanism or network-wide overrepresentation. The unscreened routes are an unresolved evidence gap.

[Ownership evidence](premier_league_feeder_ownership_evidence.json), [route audit](premier_league_feeder_ownership_audit.csv), [event flags](premier_league_feeder_ownership_events.csv), [ownership results](premier_league_feeder_ownership_results.json).

![Restricted feeder findings](premier_league_feeder_findings_three_panel.png)

[PDF](premier_league_feeder_findings_three_panel.pdf), [SVG](premier_league_feeder_findings_three_panel.svg), [caption](premier_league_feeder_findings_three_panel_caption.md), [combined and standalone exports](premier_league_feeder_findings/README.md).

"""
    path = OUTPUT_DIR / "premier_league_feeder_summary.md"
    summary = path.read_text(encoding="utf-8")
    start = summary.find("## Two-panel feeder findings\\n")
    end = summary.index("## Figures\\n")
    if start == -1:
        start = end
    path.write_text(summary[:start] + section + summary[end:], encoding="utf-8")

''' + text[end:]
text = text.replace('"239 selected recurring routes, with groups of 17 and 222. "',
                    'f"{results[\'selected_route_count\']} selected recurring routes, with groups of {len(groups[0])} and {len(groups[1])}. "\n'
                    '        "There are 28 newly selected routes without prior source screening; remaining routes are not a verified independently owned control group. "')
start = text.index('    print("Verified: six unchanged routes;')
end = text.index('    print(f"Saved 7.16-inch', start)
text = text[:start] + '    print(f"Verified {len(top)} displayed routes; {sum(len(g) for g in groups)} selected routes in groups {[len(g) for g in groups]}.")\n' + text[end:]
text = text.replace('python -B pnas_report/notebooks/plot_premier_league_feeder_findings.py',
                    'conda run -n machine-learning python pnas_report/reruns/h1_2012_13-2024_25/notebooks/plot_premier_league_feeder_findings.py')
(RUN / "notebooks" / source.name).write_text(text, encoding="utf-8")
(RUN / "provenance/feeder_plot_source_adaptations.diff").write_text("\n".join(difflib.unified_diff(
    before.splitlines(), text.splitlines(), fromfile="original/" + source.name,
    tofile="rerun/" + source.name)) + "\n", encoding="utf-8")
