"""Compare the saved Leiden and Louvain partitions on common transfer inputs."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from transfer_community_inputs import (
    REPORT, SHARED, TOL, TRANSFERS, checksum, modularity, partition_key, prepare_shared_inputs, require,
)
from transfer_community_outputs import (
    REFERENCES, configure_plotting, draw_network_panel, export, network_legend_height, read_community_view,
)

STEM = "louvain_leiden_community_comparison"
LEIDEN = REPORT / "output/leiden_transfer_communities_findings"
LOUVAIN = REPORT / "output/louvain_transfer_communities_findings"


def comparison_row(method, folder, shared, info, observed, shuffled, clubs, summary):
    result = json.loads((folder / f"{method}_results.json").read_text(encoding="utf-8"))
    final = pd.read_csv(folder / "final_partitions.csv")
    require(result["shared_inputs_sha256"] == checksum(shared / "shared_inputs.json")
            and result["input_sha256"] == info["input_sha256"]
            and result["shared_files_sha256"] == info["files_sha256"]
            and checksum(folder / "shuffled_routes.csv") == info["files_sha256"]["shuffled_routes.csv"]
            and result["seeds"] == info["seeds"] and result["resolution"] == 1
            and result["directed"] and result["weight"] == "transfer_count"
            and result["settings"]["initial_membership"] == "singleton",
            f"{method} results use different inputs or objectives")
    require(set(final.run) == {"observed", "shuffled"}, f"Incomplete {method} runs")
    row = dict(method=method.capitalize(), resolution=result["resolution"],
               optimizer_seed=info["seeds"]["optimizer"], settings=json.dumps(result["settings"]),
               versions=json.dumps(result["versions"]))
    for run, graph in (("observed", observed), ("shuffled", shuffled)):
        membership = final.loc[final.run == run]
        require(membership.club_id.is_unique and set(membership.club_id) == set(graph),
                f"{method} {run} partition does not cover every club exactly once")
        groups = [set(group.club_id) for _, group in membership.groupby("community_id")]
        q = modularity(graph, groups)
        stats = result["runs"][run]
        require(abs(q - stats["final_q"]) <= TOL and abs(q - result[f"q_{run}"]) <= TOL
                and len(groups) == stats["community_count"], f"{method} {run} results disagree with saved clubs")
        row[f"q_{run}"] = q
        row[f"{run}_community_count"] = len(groups)
        row[f"{run}_convergence"] = stats["stopping_reason"]
        if run == "observed":
            view_groups = [set(group.index) for _, group in clubs.groupby("community_id")]
            require(partition_key(groups) == partition_key(view_groups)
                    and sorted(summary.community_size) == sorted(map(len, groups)),
                    f"{method} figures and final observed membership disagree")
    row["observed_community_sizes"] = json.dumps(summary.community_size.tolist())
    row["delta_q"] = row["q_observed"] - row["q_shuffled"]
    require(abs(row["delta_q"] - result["delta_q"]) <= TOL, f"{method} delta Q mismatch")
    return row


def overlap_and_connectivity(observed, views):
    louvain, leiden = (views[method][1].community_id for method in ("louvain", "leiden"))
    pairs = Counter(zip(louvain, leiden))
    left_sizes, right_sizes = Counter(louvain), Counter(leiden)
    rows, row_totals, column_totals = [], Counter(), Counter()
    for (left, right), count in sorted(pairs.items()):
        a, b = left_sizes[left], right_sizes[right]
        rows.append(dict(louvain_id=left, leiden_id=right, louvain_size=a, leiden_size=b,
                         intersection_size=count, jaccard=count / (a+b-count)))
        row_totals[left] += count
        column_totals[right] += count
    require(row_totals == left_sizes and column_totals == right_sizes
            and sum(pairs.values()) == len(observed), "Invalid overlap coverage")
    components = []
    for method, (_, clubs, _) in views.items():
        for community, members in clubs.groupby("community_id"):
            induced = observed.subgraph(members.index)
            components.append(dict(
                method=method.capitalize(), community_id=community,
                community_name=members.community_name.iloc[0], community_size=len(members),
                weak_components=nx.number_weakly_connected_components(induced),
                strong_components=nx.number_strongly_connected_components(induced),
            ))
    return pd.DataFrame(rows), pd.DataFrame(components)


def run_comparison(transfers_path, shared_dir, leiden_dir, louvain_dir, *, seed=2026):
    shared = Path(shared_dir)
    folders = {"leiden": Path(leiden_dir), "louvain": Path(louvain_dir)}
    require((shared / "shared_inputs.json").exists()
            and all((folder / f"{method}_results.json").exists() for method, folder in folders.items()),
            "Run both analyses on the shared inputs before generating the comparison")
    observed, shuffled, _, info = prepare_shared_inputs(transfers_path, shared, seed=seed)
    views = {method: read_community_view(folder, shared) for method, folder in folders.items()}
    rows = {method: comparison_row(method, folders[method], shared, info, observed, shuffled, *views[method][1:])
            for method in ("leiden", "louvain")}
    overlap, connectivity = overlap_and_connectivity(observed, views)
    pd.DataFrame(rows.values()).to_csv(shared / "method_comparison.csv", index=False)
    overlap.to_csv(shared / "community_overlap.csv", index=False)
    connectivity.to_csv(shared / "community_connectivity.csv", index=False)

    configure_plotting()
    height = max(3.4, 2.75 + max(network_legend_height(view[2]) for view in views.values()))
    fig = plt.figure(figsize=(7.16, height))
    legend_height = max(network_legend_height(view[2]) for view in views.values())
    for index, method in enumerate(("louvain", "leiden")):
        draw_network_panel(fig, (.009 + .5*index, .02, .48, .91), views[method],
                           f"({'ab'[index]}) {method.capitalize()}", legend_height=legend_height)
    export(fig, shared, STEM)
    write_comparison(shared, folders, info, rows, overlap, connectivity)
    return rows


def write_comparison(shared, folders, info, rows, overlap, connectivity):
    links = {method: Path(os.path.relpath(folder / "README.md", shared)).as_posix()
             for method, folder in folders.items()}
    summary_rows = []
    for row in rows.values():
        summary_rows.append(f"| {row['method']} | {row['q_observed']:.9f} | {row['q_shuffled']:.9f} | "
                            f"{row['delta_q']:.9f} | {row['observed_community_count']} | "
                            f"{row['shuffled_community_count']} |")
    differences = {run: rows["leiden"][f"q_{run}"] - rows["louvain"][f"q_{run}"]
                   for run in ("observed", "shuffled")}
    component_rows = []
    for method, part in connectivity.groupby("method"):
        weak = (part.weak_components == 1).sum()
        strong = (part.strong_components == 1).sum()
        component_rows.append(f"| {method} | {weak}/{len(part)} | {strong}/{len(part)} |")
    file_checksums = "\n".join(f"- [{file}]({file}) `{sha}`" for file, sha in info["files_sha256"].items())
    counts = info["counts"]
    (shared / "method_comparison.md").write_text(
        "# Leiden and Louvain transfer communities\n\n"
        f"Both methods started from the same singleton partition of {counts['nodes']:,} clubs. "
        f"The common directed graph represents {counts['records']:,} eligible transfers across "
        f"{counts['edges']:,} routes, with transfer counts as weights. Both methods optimized "
        "directed weighted modularity at gamma = 1 using the same observed graph and the same "
        "degree-preserving shuffled graph. NetworkX independently scored all four final partitions. "
        f"Each run used optimizer seed {info['seeds']['optimizer']}, with reproducibility defined within each implementation.\n\n"
        "| Method | Observed Q | Shuffled Q | Observed − shuffled | Observed communities | Shuffled communities |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: |\n" + "\n".join(summary_rows) + "\n\n"
        f"Leiden minus Louvain Q was {differences['observed']:+.9f} on the observed graph and "
        f"{differences['shuffled']:+.9f} on the shared null. Each progress view uses its own run's "
        "optimized null Q. The level threshold governs Louvain and the first iteration without "
        "positive returned improvement governs Leiden. Accepted moves and completed "
        "iterations measure different operations. The different instrumentation scopes preclude a "
        "runtime ranking.\n\n"
        f"The overlap table contains {len(overlap)} nonempty intersections spanning all {counts['nodes']:,} "
        "observed clubs. It uses shared membership and Jaccard overlap. Community IDs, names and "
        "colour swatches apply within each method. Both panels reuse the same node coordinates and "
        "sizes. Numbers identify the highest-degree representatives and key to their full names.\n\n"
        "| Method | Weakly connected communities | Strongly connected communities |\n"
        "| --- | ---: | ---: |\n" + "\n".join(component_rows) + "\n\n"
        "The connectivity counts describe the induced directed subgraphs. Leiden's refinement phase "
        "motivated its selection. Strong connectivity is assessed directly on these transfer routes. "
        f"{REFERENCES['leiden']}. {REFERENCES['louvain']}.\n\n"
        "The null preserves every club's topological in/out degrees and the global weight multiset. "
        "It can change club-specific strengths, seasons, eligibility by season, geography, ownership, "
        "reciprocal routes and player trajectories. One seed and one randomized realization support a "
        "descriptive modularity comparison. Both methods are heuristic.\n\n"
        f"- [Leiden findings and figures]({links['leiden']})\n"
        f"- [Louvain findings and figures]({links['louvain']})\n"
        "- [Comparison values, sizes and settings](method_comparison.csv)\n"
        "- [Community overlap](community_overlap.csv)\n"
        "- [Community connectivity](community_connectivity.csv)\n"
        f"- Paired network · [PDF]({STEM}.pdf) · [PNG]({STEM}.png) · [SVG]({STEM}.svg)\n"
        f"- [Shared metadata](shared_inputs.json) `{checksum(shared / 'shared_inputs.json')}`\n"
        f"- Eligible transfer input SHA-256 `{info['input_sha256']}`\n"
        f"{file_checksums}\n\n"
        "Run from the repository root in the machine-learning environment.\n\n"
        "```powershell\npython -B pnas_report/notebooks/transfer_community_inputs.py\n"
        "python -B pnas_report/notebooks/leiden_transfer_communities.py\n"
        "python -B pnas_report/notebooks/louvain_transfer_communities.py\n"
        "python -B pnas_report/notebooks/compare_transfer_communities.py\n```\n",
        encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfers-path", type=Path, default=TRANSFERS)
    parser.add_argument("--shared-dir", type=Path, default=SHARED)
    parser.add_argument("--leiden-dir", type=Path, default=LEIDEN)
    parser.add_argument("--louvain-dir", type=Path, default=LOUVAIN)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    run_comparison(args.transfers_path, args.shared_dir, args.leiden_dir, args.louvain_dir, seed=args.seed)
