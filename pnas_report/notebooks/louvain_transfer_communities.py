"""Instrument the directed branch of NetworkX 3.6.1 Louvain.

Adapted from networkx/algorithms/community/louvain.py.
https://github.com/networkx/networkx/blob/networkx-3.6.1/networkx/algorithms/community/louvain.py

Copyright (c) 2004-2025, NetworkX Developers
Aric Hagberg <hagberg@lanl.gov>
Dan Schult <dschult@colgate.edu>
Pieter Swart <swart@lanl.gov>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.
* Neither the name of the NetworkX Developers nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from collections import defaultdict
from pathlib import Path
from random import Random

import networkx as nx
from networkx.algorithms.community.louvain import _gen_graph, _neighbor_weights
import pandas as pd

from transfer_community_inputs import (
    REPORT, SHARED, TOL, TRANSFERS, WEIGHT, modularity, partition_key, prepare_shared_inputs,
    require, versions,
)
from transfer_community_outputs import analysis_cli, plot_saved, save_results

OUTPUT = REPORT / "output/louvain_transfer_communities_findings"
THRESHOLD = 1e-7


def optimize_louvain(original, seed):
    """Follow NetworkX's order, positive-gain rule and level stopping condition."""
    require(original.is_directed() and not original.is_multigraph() and original.size(weight=WEIGHT) > 0,
            "Expected a simple directed graph with positive transfer volume")
    graph = nx.DiGraph()
    graph.add_nodes_from(original)
    graph.add_weighted_edges_from(original.edges(data=WEIGHT))
    mass = graph.size(weight="weight")
    partition = [{club} for club in graph]
    q = previous_level_q = modularity(original, partition)
    rng = Random(seed)
    move = visit = level = candidate_count = completed_levels = 0
    max_gain_error = max_aggregation_error = 0.0
    progress, evaluations, mapping, sweeps = [], [], [], []

    def evaluate(kind, q_before, delta, candidate_q, *, level, sweep=0, node=None,
                 source=None, target=None, accepted=None):
        evaluations.append(dict(evaluation_id=len(evaluations)+1, evaluation_type=kind, level=level,
                                sweep=sweep, node_visit=visit, move=move, moved_node=node,
                                source_community=source, target_community=target, q_before=q_before,
                                delta_q=delta, q_candidate=candidate_q, accepted=accepted))

    progress.append(dict(move=0, level=0, sweep=0, moved_node=None, represented_clubs=0,
                         delta_q=0.0, q=q, community_count=len(partition)))
    evaluate("initial", q, 0.0, q, level=0)
    while True:
        level += 1
        node_to_community = {node: idx for idx, node in enumerate(graph)}
        inner = [{node} for node in graph]
        members = {node: graph.nodes[node].get("nodes", {node}) for node in graph}
        mapping.extend((level, node, node_to_community[node], club)
                       for node, clubs in members.items() for club in sorted(clubs))
        in_degree = dict(graph.in_degree(weight="weight"))
        out_degree = dict(graph.out_degree(weight="weight"))
        total_in, total_out = list(in_degree.values()), list(out_degree.values())
        neighbors = {}
        for node in graph:
            neighbors[node] = defaultdict(float)
            for _, other, weight in graph.out_edges(node, data="weight"):
                if other != node:
                    neighbors[node][other] += weight
            for other, _, weight in graph.in_edges(node, data="weight"):
                if other != node:
                    neighbors[node][other] += weight
        order = list(graph)
        rng.shuffle(order)
        level_start, sweep = move, 0
        while True:
            sweep += 1
            sweep_start = move
            for node in order:
                visit += 1
                source = best = node_to_community[node]
                best_gain = 0.0
                weights = _neighbor_weights(neighbors[node], node_to_community)
                incoming, outgoing = in_degree[node], out_degree[node]
                total_in[source] -= incoming
                total_out[source] -= outgoing
                remove_cost = (-weights[source] / mass
                               + (outgoing * total_in[source] + incoming * total_out[source]) / mass**2)
                candidates = []
                for target, weight in weights.items():
                    gain = (remove_cost + weight / mass
                            - (outgoing * total_in[target] + incoming * total_out[target]) / mass**2)
                    candidates.append((target, gain))
                    if gain > best_gain:
                        best_gain, best = gain, target
                candidate_count += len(candidates)
                for target, gain in candidates:
                    evaluate("candidate", q, gain, q + gain, level=level, sweep=sweep,
                             node=node, source=source, target=target, accepted=best == target != source)
                total_in[best] += incoming
                total_out[best] += outgoing
                if best == source:
                    continue
                partition[source].difference_update(members[node])
                inner[source].remove(node)
                partition[best].update(members[node])
                inner[best].add(node)
                node_to_community[node] = best
                move += 1
                active = [group for group in partition if group]
                verified = modularity(original, active)
                error = abs(q + best_gain - verified)
                require(error <= TOL and verified >= q - TOL, f"Louvain gain mismatch at move {move}")
                max_gain_error = max(max_gain_error, error)
                evaluate("accepted", q, best_gain, q + best_gain, level=level, sweep=sweep,
                         node=node, source=source, target=best, accepted=True)
                evaluate("verification", q, verified - q, verified, level=level, sweep=sweep,
                         node=node, source=source, target=best)
                progress.append(dict(move=move, level=level, sweep=sweep, moved_node=node,
                                     represented_clubs=len(members[node]), delta_q=verified-q,
                                     q=verified, community_count=len(active)))
                q = verified
            sweeps.append(dict(level=level, sweep=sweep, first_move_before_sweep=sweep_start,
                               last_move_after_sweep=move, accepted_moves=move-sweep_start,
                               node_visits=len(order), q=q))
            if move == sweep_start:
                break
        partition = list(filter(len, partition))
        inner = list(filter(len, inner))
        level_q = nx.community.modularity(graph, inner, weight="weight", resolution=1.0)
        require(abs(level_q - q) <= TOL, f"Coarse and original graph Q differ at level {level}")
        evaluate("boundary", previous_level_q, level_q-previous_level_q, level_q, level=level)
        # NetworkX yields the first level even if it found no move.
        if level > 1 and level_start == move:
            reason = "a higher level without accepted moves"
            break
        completed_levels += 1
        if level_q - previous_level_q <= THRESHOLD:
            reason = "level improvement at or below the NetworkX threshold"
            break
        previous_level_q = level_q
        graph = _gen_graph(graph, inner)
        q_aggregated = nx.community.modularity(graph, [{node} for node in graph], weight="weight")
        aggregation_error = abs(q_aggregated - level_q)
        require(graph.size(weight="weight") == mass and aggregation_error <= TOL,
                f"Aggregation changed total weight or Q at level {level}")
        max_aggregation_error = max(max_aggregation_error, aggregation_error)
        evaluate("aggregation_verification", level_q, q_aggregated-level_q, q_aggregated, level=level)

    final_q = modularity(original, partition)
    require(final_q == q, "Final Louvain Q differs from the last saved state")
    evaluate("final", q, 0.0, final_q, level=level)
    stats = dict(final_q=final_q, community_count=len(partition), accepted_moves=move,
                 candidate_evaluations=candidate_count, q_evaluations=len(evaluations),
                 accepted_move_verification_calls=move, node_visits=visit, sweeps=len(sweeps),
                 attempted_levels=level, completed_levels=completed_levels,
                 max_accepted_gain_error=max_gain_error, max_aggregation_error=max_aggregation_error,
                 stopping_reason=reason)
    return partition, progress, evaluations, mapping, sweeps, stats


def run_louvain_analysis(transfers_path, output_dir, *, seed=2026, shared_dir=None):
    """Run and verify Louvain on the observed and common shuffled networks."""
    output_dir = Path(output_dir)
    shared_dir = SHARED if shared_dir is None else Path(shared_dir)
    observed, shuffled, layout, info = prepare_shared_inputs(transfers_path, shared_dir, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    partitions, stats = {}, {}
    progress, evaluations, mapping, sweeps = [], [], [], []
    for run, graph in (("observed", observed), ("shuffled", shuffled)):
        groups, trace, q_evals, nodes, sweep_trace, stats[run] = optimize_louvain(graph, seed)
        public = nx.community.louvain_communities(graph, weight=WEIGHT, seed=seed, threshold=THRESHOLD)
        require(partition_key(groups) == partition_key(public), f"{run} Louvain differs from NetworkX")
        stats[run]["networkx_public_partition_matches"] = True
        partitions[run] = groups
        progress.extend(dict(run=run, **row) for row in trace)
        evaluations.extend(dict(run=run, **row) for row in q_evals)
        mapping.extend((run, *row) for row in nodes)
        sweeps.extend(dict(run=run, **row) for row in sweep_trace)
    for name, rows in (("progress", progress), ("q_evaluations", evaluations), ("sweeps", sweeps)):
        frame = pd.DataFrame(rows)
        for column in ("moved_node", "source_community", "target_community"):
            if column in frame:
                frame[column] = frame[column].astype("Int64")
        frame.to_csv(output_dir / f"louvain_{name}.csv", index=False)
    pd.DataFrame(mapping, columns=["run", "level", "node", "initial_community", "club_id"]).to_csv(
        output_dir / "louvain_supernode_mapping.csv", index=False)
    result = save_results(
        "louvain", output_dir, shared_dir, info, observed, layout, partitions, stats,
        {"initial_membership": "singleton", "minimum_move_gain": "strictly positive",
         "level_improvement_threshold": THRESHOLD, "level_cap": None,
         "stopping_rule": "level improvement <= threshold or no moves at the next level"},
        versions("networkx", "matplotlib", "numpy", "scipy", "pandas", "pyvis"),
    )
    plot_saved("louvain", output_dir, shared_dir)
    return result


if __name__ == "__main__":
    analysis_cli("louvain", TRANSFERS, OUTPUT, run_louvain_analysis)
