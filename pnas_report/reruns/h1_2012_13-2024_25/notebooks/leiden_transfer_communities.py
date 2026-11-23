"""Trace directed weighted Leiden modularity at complete iteration boundaries."""

from collections import defaultdict
from pathlib import Path

import igraph as ig
import leidenalg as la
import pandas as pd

from transfer_community_inputs import (
    REPORT, SHARED, TOL, TRANSFERS, WEIGHT, modularity, prepare_shared_inputs, require, versions,
)
from transfer_community_outputs import analysis_cli, plot_saved, save_results

OUTPUT = REPORT / "output/leiden_transfer_communities_findings"


def to_igraph(graph):
    club_ids = list(graph)
    indices = {club: idx for idx, club in enumerate(club_ids)}
    edges = list(graph.edges(data=WEIGHT))
    converted = ig.Graph(n=len(club_ids), edges=[(indices[a], indices[b]) for a, b, _ in edges],
                         directed=True)
    converted.vs["club_id"] = club_ids
    converted.es[WEIGHT] = [weight for _, _, weight in edges]
    round_trip = [(club_ids[edge.source], club_ids[edge.target], edge[WEIGHT])
                  for edge in converted.es]
    require(converted.is_directed() and converted.vcount() == len(graph)
            and converted.ecount() == graph.number_of_edges() and round_trip == edges
            and len(indices) == len(club_ids), "igraph conversion changed vertices or directed routes")
    for mode, degree in (("in", graph.in_degree), ("out", graph.out_degree)):
        require(converted.strength(mode=mode, weights=WEIGHT) ==
                [degree(club, weight=WEIGHT) for club in club_ids], f"igraph changed {mode}-strength")
    return converted, club_ids


def groups_from_membership(club_ids, membership):
    require(len(membership) == len(club_ids), "Incomplete Leiden membership")
    groups = defaultdict(set)
    for club, community in zip(club_ids, membership):
        groups[community].add(club)
    return [groups[key] for key in sorted(groups)]


def optimize_leiden(graph, seed):
    converted, club_ids = to_igraph(graph)
    partition = la.ModularityVertexPartition(
        converted, weights=WEIGHT, initial_membership=list(range(len(club_ids))),
    )
    optimizer = la.Optimiser()
    optimizer.set_rng_seed(seed)
    settings = {name: getattr(optimizer, name) for name in (
        "consider_comms", "consider_empty_community", "max_comm_size", "optimise_routine",
        "refine_consider_comms", "refine_partition", "refine_routine",
    )}
    constants = {name: getattr(la, name) for name in (
        "ALL_COMMS", "ALL_NEIGH_COMMS", "RAND_COMM", "RAND_NEIGH_COMM", "MOVE_NODES", "MERGE_NODES",
    )}
    settings.update({
        "consider_comms": next(name for name in list(constants)[:4]
                               if constants[name] == settings["consider_comms"]),
        "refine_consider_comms": next(name for name in list(constants)[:4]
                                      if constants[name] == settings["refine_consider_comms"]),
        "optimise_routine": next(name for name in ("MOVE_NODES", "MERGE_NODES")
                                 if constants[name] == settings["optimise_routine"]),
        "refine_routine": next(name for name in ("MOVE_NODES", "MERGE_NODES")
                               if constants[name] == settings["refine_routine"]),
    })
    progress, memberships = [], []
    improvement, previous = 0.0, None
    while True:
        membership = partition.membership
        groups = groups_from_membership(club_ids, membership)
        q, verified_q = partition.quality(), modularity(graph, groups)
        delta = 0.0 if previous is None else verified_q - previous
        require(abs(q - verified_q) <= TOL and delta >= -TOL and improvement >= -TOL
                and abs(improvement - delta) <= TOL, "Leiden Q or returned improvement failed verification")
        progress.append(dict(iteration=len(progress), returned_improvement=improvement,
                             delta_q=delta, leiden_q=q, networkx_q=verified_q,
                             verification_error=q - verified_q, community_count=len(groups)))
        memberships.append(membership)
        if previous is not None and improvement <= 0:
            break
        previous = verified_q
        improvement = optimizer.optimise_partition(partition, n_iterations=1)
    stats = dict(final_q=verified_q, community_count=len(groups),
                 completed_iterations=len(progress)-1, quality_verification_calls=len(progress),
                 max_absolute_verification_error=max(abs(row["verification_error"]) for row in progress),
                 stopping_reason="first iteration without positive returned improvement")
    return groups, progress, memberships, stats, settings


def run_leiden_analysis(transfers_path, output_dir, *, seed=2026, shared_dir=None):
    """Run and verify Leiden on the observed and common shuffled networks."""
    output_dir = Path(output_dir)
    shared_dir = SHARED if shared_dir is None else Path(shared_dir)
    observed, shuffled, layout, info = prepare_shared_inputs(transfers_path, shared_dir, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    progress, membership_trace, partitions, stats = [], [], {}, {}
    for run, graph in (("observed", observed), ("shuffled", shuffled)):
        groups, trace, memberships, stats[run], settings = optimize_leiden(graph, seed)
        partitions[run] = groups
        progress.extend(dict(run=run, **row) for row in trace)
        membership_trace.extend((run, iteration, club, community)
                                for iteration, membership in enumerate(memberships)
                                for club, community in zip(graph, membership))
    pd.DataFrame(progress).to_csv(output_dir / "leiden_progress.csv", index=False)
    pd.DataFrame(membership_trace, columns=["run", "iteration", "club_id", "community_id"]).to_csv(
        output_dir / "leiden_membership_trace.csv", index=False)
    pd.DataFrame({"club_id": list(observed), "vertex_index": range(len(observed))}).to_csv(
        output_dir / "club_vertex_mapping.csv", index=False)
    result = save_results(
        "leiden", output_dir, shared_dir, info, observed, layout, partitions, stats,
        {"partition_type": "ModularityVertexPartition", "optimizer": settings,
         "initial_membership": "singleton", "stopping_rule": "returned improvement <= 0"},
        versions("networkx", "leidenalg", "igraph", "matplotlib", "numpy", "scipy", "pandas", "pyvis"),
    )
    plot_saved("leiden", output_dir, shared_dir)
    return result


if __name__ == "__main__":
    analysis_cli("leiden", TRANSFERS, OUTPUT, run_leiden_analysis)
