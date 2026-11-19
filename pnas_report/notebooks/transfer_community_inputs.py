"""Prepare and validate the common directed transfer networks and layout."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from importlib.metadata import version
import json
import math
from pathlib import Path
from random import Random

import networkx as nx
import pandas as pd

REPORT = Path(__file__).resolve().parents[1]
TRANSFERS = REPORT / "data/dataset_graph/outsideprem_toprem_eligible_transfers.csv.gz"
SHARED = REPORT / "output/transfer_community_comparison"
WEIGHT = "transfer_count"
ROUTE_COLUMNS = ["from_club_id", "to_club_id", WEIGHT]
TOL = 1e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checksum(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def routes(graph):
    return sorted(graph.edges(data=WEIGHT))


def load_source(transfers_path):
    columns = [*ROUTE_COLUMNS[:2], "from_club_name", "to_club_name", "player_id"]
    transfers = pd.read_csv(transfers_path, usecols=columns, dtype={
        "from_club_id": "int64", "to_club_id": "int64",
    })
    counts = transfers.groupby(ROUTE_COLUMNS[:2], sort=True).size()
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(
        ((int(a), int(b), int(w)) for (a, b), w in counts.items()), weight=WEIGHT
    )
    # Match exploration_v3: last source name, overridden by last destination name.
    names, variants = {}, defaultdict(set)
    for side in ("from", "to"):
        for club, name in zip(transfers[f"{side}_club_id"], transfers[f"{side}_club_name"]):
            if pd.notna(name):
                names[club] = name
                variants[club].add(name)
    require(set(names) == set(graph), "Missing club labels in the eligible input")
    nx.set_node_attributes(graph, names, "label")
    totals = {
        "records": len(transfers), "distinct_players": transfers.player_id.nunique(),
        "nodes": len(graph), "edges": graph.number_of_edges(),
        "self_loops": nx.number_of_selfloops(graph), "total_transfer_count": int(graph.size(weight=WEIGHT)),
    }
    require(totals["self_loops"] == 0 and totals["records"] == totals["total_transfer_count"],
            f"Unexpected loop or transfer total: {totals}")
    if Path(transfers_path).name == TRANSFERS.name:
        saved = json.loads((REPORT / "output/age_shuffle_outsideprem_toprem_results.json").read_text(
            encoding="utf-8"
        ))
        sample = saved["all_eligible_transfers"]["sample_counts"]
        require(totals["records"] == sample["eligible_transfer_records"] == 19712
                and totals["distinct_players"] == sample["distinct_players"] == 5213
                and (totals["nodes"], totals["edges"]) == (1254, 12794),
                f"Eligible transfer snapshot differs from the saved analysis: {totals}")
    conflicts = {str(club): {"chosen": names[club], "variants": sorted(options)}
                 for club, options in sorted(variants.items()) if len(options) > 1}
    return graph, totals, conflicts


def try_three_edge_swap(graph, a, b, c, d):
    """Apply the directed path swap only if the complete proposal is valid."""
    removed = ((a, b), (b, c), (c, d))
    added = ((a, c), (c, b), (b, d))
    if any(u == v or graph.has_edge(u, v) for u, v in added):
        return False
    graph.remove_edges_from(removed)
    graph.add_edges_from(added)
    return True


def verify_shuffle(observed, shuffled):
    require(set(observed) == set(shuffled) and observed.number_of_edges() == shuffled.number_of_edges()
            and not shuffled.is_multigraph() and shuffled.is_directed()
            and nx.number_of_selfloops(shuffled) == 0, "Shuffled topology has invalid nodes or routes")
    for attribute in ("in_degree", "out_degree"):
        require(dict(getattr(observed, attribute)()) == dict(getattr(shuffled, attribute)()),
                f"Shuffle changed {attribute}")
    require(Counter(w for _, _, w in routes(observed)) == Counter(w for _, _, w in routes(shuffled)),
            "Shuffle changed the weight multiset")
    return len(set(observed.edges) & set(shuffled.edges)) / observed.number_of_edges()


def shuffle_routes(observed, swap_seed, weight_seed, *, target=None):
    # The proposal follows NetworkX directed_edge_swap, with explicit loop rejection.
    graph = nx.DiGraph()
    graph.add_nodes_from(observed)
    graph.add_edges_from(observed.edges)
    nodes, degrees = zip(*graph.degree())
    cdf = nx.utils.cumulative_distribution(degrees)
    rand = Random(swap_seed)
    target = 10 * graph.number_of_edges() if target is None else target
    successes = 0
    for attempts in range(1, 100 * target + 1):
        a = nodes[nx.utils.discrete_sequence(1, cdistribution=cdf, seed=rand)[0]]
        path = [a]
        for _ in range(3):
            successors = graph.succ[path[-1]]
            if not successors:
                break
            path.append(rand.choice(tuple(successors)))
        if len(path) == 4 and try_three_edge_swap(graph, *path):
            successes += 1
            if successes == target:
                break
    else:
        raise ValueError(f"Shuffle achieved {successes}/{target} swaps in {100 * target} proposals")

    weights = [w for _, _, w in routes(observed)]
    Random(weight_seed).shuffle(weights)
    # Insert again in deterministic endpoint order, independent of swap history.
    shuffled = nx.DiGraph()
    shuffled.add_nodes_from(observed)
    shuffled.add_weighted_edges_from(
        ((a, b, w) for (a, b), w in zip(sorted(graph.edges), weights)), weight=WEIGHT
    )
    retained = verify_shuffle(observed, shuffled)
    return shuffled, {"target": target, "max_attempts": 100 * target, "successes": successes,
                      "attempts": attempts, "fraction_original_routes_retained": retained}


def load_graph(path, node_ids):
    rows = list(pd.read_csv(path).itertuples(index=False, name=None))
    graph = nx.DiGraph()
    graph.add_nodes_from(node_ids)
    graph.add_weighted_edges_from(rows, weight=WEIGHT)
    require(list(graph) == node_ids and routes(graph) == rows
            and all(isinstance(w, int) and w > 0 for _, _, w in rows),
            f"Invalid or noncanonical saved routes in {path}")
    return graph


def prepare_shared_inputs(transfers_path=TRANSFERS, shared_dir=SHARED, *, seed=2026):
    transfers_path, shared_dir = Path(transfers_path), Path(shared_dir)
    source, totals, conflicts = load_source(transfers_path)
    seeds = dict(optimizer=seed, swap=seed+1, weight_permutation=seed+2, layout=seed+3)
    expected = {
        "input_sha256": checksum(transfers_path), "counts": totals, "seeds": seeds,
        "directed": True, "weight": WEIGHT, "resolution": 1.0, "node_order": list(source),
        "edge_order": "sorted directed endpoint pairs",
        "club_name_conflicts": conflicts, "swap_target_multiplier": 10, "attempt_multiplier": 100,
        "layout": {"algorithm": "NetworkX spring_layout", "method": "force", "iterations": 100,
                   "node_size": "scatter area in pt^2: 3 + 1.4 * sqrt(unweighted total degree)"},
    }
    files = ("observed_routes.csv", "shuffled_routes.csv", "layout.csv")
    metadata = shared_dir / "shared_inputs.json"
    if not metadata.exists():
        require(not any((shared_dir / name).exists() for name in files),
                f"Incomplete shared inputs in {shared_dir}; investigate before regenerating")
        shuffled, diagnostics = shuffle_routes(source, seeds["swap"], seeds["weight_permutation"])
        require(diagnostics["fraction_original_routes_retained"] < 1, "Shuffle did not change routes")
        xy = nx.spring_layout(source, seed=seeds["layout"], weight=WEIGHT,
                              method="force", iterations=100)
        shared_dir.mkdir(parents=True, exist_ok=True)
        for graph, name in zip((source, shuffled), files):
            pd.DataFrame(routes(graph), columns=ROUTE_COLUMNS).to_csv(shared_dir / name, index=False)
        pd.DataFrame([(club, *xy[club], 3 + 1.4 * math.sqrt(source.degree(club))) for club in source],
                     columns=["club_id", "x", "y", "node_size"]).to_csv(shared_dir / files[2], index=False)
        write_json(metadata, {**expected, "shuffle": diagnostics,
                              "versions": versions("networkx", "numpy", "scipy", "pandas"),
                              "files_sha256": {name: checksum(shared_dir / name) for name in files}})
    info = json.loads(metadata.read_text(encoding="utf-8"))
    require(all(info[key] == value for key, value in expected.items()),
            f"Shared inputs do not match source data or settings in {shared_dir}")
    require(info["files_sha256"] == {name: checksum(shared_dir / name) for name in files},
            f"Shared input checksum mismatch in {shared_dir}")
    observed, shuffled = (load_graph(shared_dir / name, info["node_order"]) for name in files[:2])
    require(routes(observed) == routes(source), "Saved observed routes differ from the source")
    nx.set_node_attributes(observed, nx.get_node_attributes(source, "label"), "label")
    diagnostics = info["shuffle"]
    require(verify_shuffle(observed, shuffled) == diagnostics["fraction_original_routes_retained"] < 1
            and diagnostics["target"] == diagnostics["successes"] == 10 * observed.number_of_edges()
            and diagnostics["successes"] <= diagnostics["attempts"] <= diagnostics["max_attempts"]
            == 100 * diagnostics["target"], "Saved shuffle diagnostics are inconsistent")
    layout = pd.read_csv(shared_dir / files[2], float_precision="round_trip").set_index("club_id")
    require(list(layout.index) == list(observed)
            and all(math.isfinite(v) for row in layout.to_numpy() for v in row)
            and all(row.node_size == 3 + 1.4 * math.sqrt(observed.degree(club))
                    for club, row in layout.iterrows()), "Invalid saved layout")
    return observed, shuffled, layout, info


def versions(*packages):
    return {package: version(package) for package in packages}


def partition_key(groups):
    return tuple(sorted(tuple(sorted(group)) for group in groups))


def modularity(graph, groups):
    return nx.community.modularity(graph, groups, weight=WEIGHT, resolution=1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfers-path", type=Path, default=TRANSFERS)
    parser.add_argument("--shared-dir", type=Path, default=SHARED)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    _, _, _, info = prepare_shared_inputs(args.transfers_path, args.shared_dir, seed=args.seed)
    print(info["counts"], info["shuffle"])
