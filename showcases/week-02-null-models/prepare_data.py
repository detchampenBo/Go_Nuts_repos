"""Build the puzzle's frozen data from the shared Week 1 snapshot (stdlib only)."""

import csv
import hashlib
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "data" / "week1"


def load_graph():
    rows = csv.DictReader(
        (line for line in (SOURCE / "week1_nodes.tsv").read_text(encoding="utf-8").splitlines()
         if not line.startswith("#")), delimiter="\t"
    )
    nodes = {row["node_id"]: row for row in rows}
    graph = {node: set() for node in nodes}
    directed = set()
    for line in (SOURCE / "week1_edges.tsv").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        a, b = line.split("\t")
        if a != b:
            graph[a].add(b)
            graph[b].add(a)
            directed.add((a, b))
    return nodes, graph, len(directed)


def neighborhood(graph, node):
    neighbors = sorted(graph[node])
    links = [[i, j] for i, a in enumerate(neighbors)
             for j, b in enumerate(neighbors) if i < j and b in graph[a]]
    k = len(neighbors)
    return {"degree": k, "links": links,
            "clustering": 2 * len(links) / (k * (k - 1)) if k > 1 else 0}


def average_clustering(graph):
    total = 0
    for neighbors in graph.values():
        k = len(neighbors)
        if k > 1:
            total += sum(len(neighbors & graph[v]) for v in neighbors) / (k * (k - 1))
    return total / len(graph)


def random_graph(original, rng):
    """Uniform G(n,m): keep node and edge counts, but not individual degrees."""
    nodes = sorted(original)
    pairs = [(a, b) for i, a in enumerate(nodes) for b in nodes[i + 1:]]
    graph = {node: set() for node in nodes}
    for a, b in rng.sample(pairs, sum(map(len, original.values())) // 2):
        graph[a].add(b)
        graph[b].add(a)
    return graph


def shuffle_graph(original, rng, swaps=None):
    """Simple undirected double-edge swaps: no loops or duplicate edges."""
    graph = {node: set(neighbors) for node, neighbors in original.items()}
    edges = [(a, b) for a in sorted(graph) for b in sorted(graph[a]) if a < b]
    target = swaps if swaps is not None else 10 * len(edges)
    completed = 0
    for _ in range(max(target * 100, 1)):
        if completed == target:
            return graph
        i, j = rng.sample(range(len(edges)), 2)
        a, b = edges[i]
        c, d = edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if len({a, b, c, d}) != 4 or d in graph[a] or b in graph[c]:
            continue
        for u, v in ((a, b), (c, d)):
            graph[u].remove(v)
            graph[v].remove(u)
        for u, v in ((a, d), (c, b)):
            graph[u].add(v)
            graph[v].add(u)
        edges[i], edges[j] = (a, d), (c, b)
        completed += 1
    raise RuntimeError("Could not complete the requested edge swaps")


PUZZLES = [
    {"id": "01", "name": "Big names, small circles",
     "degree": ["Black_Cat_(Marvel_Comics)", "Hulk", "Spider-Man", "Ajak", "Doctor_Strange"],
     "clustering": ["Frog-Man", "Spider-Man_Noir", "Shuri_(character)", "Thena", "Hawkeye_(comics)"]},
    {"id": "02", "name": "An unexpected connection",
     "degree": ["Beta_Ray_Bill", "Doctor_Strange", "Spider-UK", "Hulk", "Peggy_Carter"],
     "clustering": ["Shatterstar", "Surge_(Marvel_Comics)", "Ajak", "Leech_(character)", "Ricochet_(comics)"]},
    {"id": "03", "name": "The company you keep",
     "degree": ["Ajak", "Hulk", "Shuri_(character)", "Spider-Man", "Beta_Ray_Bill"],
     "clustering": ["Doctor_Druid", "Mania_(character)", "Beta_Ray_Bill", "Oya_(comics)", "Gargoyle_(comics)"]},
]


def build():
    nodes, graph, directed_count = load_graph()
    rng = random.Random(2805)
    samples = []
    for _ in range(100):
        shuffled = shuffle_graph(graph, rng)
        assert all(len(graph[n]) == len(shuffled[n]) for n in graph)
        samples.append(average_clustering(shuffled))
    selected = {n for p in PUZZLES for metric in ("degree", "clustering") for n in p[metric]}
    heroes = {}
    for node in sorted(selected):
        row = nodes[node]
        heroes[node] = {
            "name": re.sub(r" \((?:character|comics|Marvel_Comics|Marvel Comics)\)$", "", row["name"]),
            "url": row["url"],
            **neighborhood(graph, node),
            "shuffled": neighborhood(shuffled, node),
        }
    for puzzle in PUZZLES:
        for metric in ("degree", "clustering"):
            values = [heroes[n][metric] for n in puzzle[metric]]
            assert len(set(values)) == len(values), (puzzle["id"], metric, values)
    observed = average_clustering(graph)
    random_rng = random.Random(2806)
    random_samples = [average_clustering(random_graph(graph, random_rng)) for _ in range(100)]
    digest = hashlib.sha256((SOURCE / "week1_nodes.tsv").read_bytes()
                            + (SOURCE / "week1_edges.tsv").read_bytes()).hexdigest()
    output = {
        "version": 1, "sourceSha256": digest,
        "source": "02805 Week 1 frozen Wikipedia snapshot · 2026-08-26",
        "nodes": len(graph), "directedEdges": directed_count,
        "edges": sum(map(len, graph.values())) // 2,
        "isolates": sum(not ns for ns in graph.values()),
        "clustering": observed, "shuffleSamples": samples,
        "shuffleMean": sum(samples) / len(samples),
        "randomSamples": random_samples,
        "randomMean": sum(random_samples) / len(random_samples),
        "empiricalP": (1 + sum(x >= observed for x in samples)) / (1 + len(samples)),
        "heroes": heroes, "puzzles": PUZZLES,
    }
    (HERE / "puzzle-data.json").write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Built {len(PUZZLES)} puzzles; C={observed:.4f}; shuffle mean={output['shuffleMean']:.4f}")


if __name__ == "__main__":
    build()
