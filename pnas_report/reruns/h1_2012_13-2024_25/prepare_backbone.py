"""Redirect the backbone producer and replace historical snapshot checks with current inputs."""
import difflib
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
REPORT = RUN.parents[1]
source = REPORT / "notebooks/louvain_transfer_backbone.py"
before = source.read_text(encoding="utf-8")
text = before
start = text.index("OBSERVED_Q = ")
end = text.index("\n\n\n@dataclass", start)
text = text[:start] + '''OBSERVED_Q = json.loads((LOUVAIN / "louvain_results.json").read_text())["q_observed"]
COMMUNITY_SUMMARY = {row["community_id"]: row for row in csv.DictReader(
    (LOUVAIN / "community_summary.csv").open(encoding="utf-8"))}
''' + text[end:]
text = text.replace('require(set(groups) == CHECKPOINTS.keys(), "Unexpected display community IDs")',
                    'require(set(groups) == COMMUNITY_SUMMARY.keys(), "Display communities differ from saved summary")')
text = text.replace('groups = {key: groups[key] for key in CHECKPOINTS}',
                    'groups = {key: groups[key] for key in COMMUNITY_SUMMARY}')
text = text.replace('(1254, 12794, 19712)',
                    '(shared["counts"]["nodes"], shared["counts"]["edges"], shared["counts"]["records"])')
text = text.replace('for group, checkpoint in CHECKPOINTS.items():', 'for group, checkpoint in COMMUNITY_SUMMARY.items():')
text = text.replace('require(actual == checkpoint, f"Community {group} checkpoint differs: {actual}")',
                    'require(actual[0] == checkpoint["community_name"] and actual[1] == int(checkpoint["community_size"]),\n'
                    '                f"Community {group} checkpoint differs: {actual}")')
text = text.replace('require((internal_routes, internal_weight) == (7583, 13003), "Internal checkpoint differs")\n'
                    '    require((len(edges) - internal_routes, sum(edges.values()) - internal_weight) == (5211, 6709),\n'
                    '            "Between-community checkpoint differs")',
                    'require(internal_routes == sum(clubs[u].community == clubs[v].community for u, v in edges),\n'
                    '            "Internal route totals disagree")\n'
                    '    require(internal_weight == sum(w for (u, v), w in edges.items() if clubs[u].community == clubs[v].community),\n'
                    '            "Internal transfer totals disagree")\n'
                    '    require(abs(nx.community.modularity(graph, list(display_groups.values()), weight="weight") - OBSERVED_Q) <= 1e-10,\n'
                    '            "Observed partition Q differs from new saved optimizer result")')
text = text.replace('subprocess.run(["Rscript",',
                    'subprocess.run(["conda", "run", "-n", "network_analysis", "--no-capture-output", "Rscript",')
start = text.index('            require(reference == statistical,')
end = text.index('            diagnostics.append({', start)
text = text[:start] + '''            retained = {r.pair: r.transfer_count for r in scope.retained(alpha)}
            statistical_match = reference == statistical
            paper_match = retained == (reference | exceptions)
''' + text[end:]
text = text.replace('"structural_exceptions": len(exceptions), "paper_routes": len(retained),',
                    '"structural_exceptions": len(exceptions), "paper_routes": len(retained),\n'
                    '                "statistical_match": statistical_match, "paper_rule_match": paper_match,\n'
                    '                "r_only": sorted(reference.items() - statistical.items()),\n'
                    '                "python_only": sorted(statistical.items() - reference.items()),')
text = text.replace('print(f"Verified {len(parity)} directed R parity comparisons.", flush=True)',
                    'print(f"Completed {len(parity)} directed R parity comparisons; "\n'
                    '          f"{sum(not row[\'paper_rule_match\'] for row in parity)} paper-rule mismatches. "\n'
                    '          "Failures remain explicit; scoring and strict cutoffs are unchanged.", flush=True)')
text = text.replace('"parity": parity,',
                    '"parity": parity,\n'
                    '        "r_parity_passed": all(row["statistical_match"] and row["paper_rule_match"] for row in parity),')
text = text.replace('    save_docs(destination, scopes, clubs, groups, retention)',
                    '    save_docs(destination, scopes, clubs, groups, retention)\n'
                    '    failed = [row for row in parity if not row["statistical_match"] or not row["paper_rule_match"]]\n'
                    '    for document in ("README.md", "backbone_summary.md"):\n'
                    '        with (destination / document).open("a", encoding="utf-8") as handle:\n'
                    '            handle.write(f"\\n\\nR reference status: {len(parity)} actual scope/cutoff comparisons completed; {len(failed)} differ. "\n'
                    '                         "Parity is NOT verified. Python retains the original integer-numerator precision and strict cutoff. "\n'
                    '                         "See backbone_results.json parity diagnostics and ../../../provenance/backbone_boundary_diagnosis.json.\\n")')
text = text.replace('    markers = dict(zip(groups, ("o", "s", "^", "D", "P"), strict=True))',
                    '    from itertools import cycle\n    markers = dict(zip(groups, cycle(("o", "s", "^", "D", "P"))))')
text = text.replace('ncol=5, fontsize=8', 'ncol=min(5, len(groups)), fontsize=8')
text = text.replace('saved five-community Louvain partition', 'saved {len(groups)}-community Louvain partition')
text = text.replace('    wolves = lookup["5", 0.10]\n', '')
text = text.replace('        f"Wolves has {wolves[\'weak_components\']} active weak components across {wolves[\'active_clubs\']} active clubs "\n'
                    '        "at that cutoff. Its backbone is empty at α = 0.01.",',
                    '        "The per-community retention table records the full slider grid without historical community assumptions.",')
text = text.replace('f"of transfer volume, with all {whole[\'active_clubs\']:,} active clubs in one weak component covering "\n'
                    '        f"{whole[\'largest_weak_component_fraction\']:.1%} of observed clubs. "',
                    'f"of transfer volume, with {whole[\'active_clubs\']:,} active clubs in {whole[\'weak_components\']} weak components; "\n'
                    '        f"the largest covers {whole[\'largest_weak_component_fraction\']:.1%} of observed clubs. "')
text = text.replace('"Panels use fixed positions and node sizes, with colours and symbols identifying the five saved Louvain "',
                    'f"Panels use fixed positions and node sizes, with colours and symbols identifying the {len(groups)} saved Louvain "')
text = text.replace('"The analysis runs R package parity on all six views at five cutoffs before exporting. The retention table "',
                    'f"The analysis runs R package parity on all {len(scopes)} views at five cutoffs before exporting. The retention table "')
text = text.replace('../../paper/transfer_backbone', '../../../../paper/transfer_backbone')
text = text.replace('python pnas_report/notebooks/louvain_transfer_backbone.py',
                    'conda run -n machine-learning python pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_backbone.py')
(RUN / "notebooks" / source.name).write_text(text, encoding="utf-8")
for name in ["disparityfilter_reference.R", "louvain_transfer_backbone_template.html"]:
    shutil.copyfile(REPORT / "notebooks" / name, RUN / "notebooks" / name)
(RUN / "provenance/backbone_source_adaptations.diff").write_text("\n".join(difflib.unified_diff(
    before.splitlines(), text.splitlines(), fromfile="original/" + source.name,
    tofile="rerun/" + source.name)) + "\n", encoding="utf-8")
