"""Create the compact network summary consumed by the Codex comparison page."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
NODES_FILE = ROOT / "notebooks" / "data" / "week1_nodes.tsv"
EDGES_FILE = ROOT / "notebooks" / "data" / "week1_edges.tsv"
OUTPUT_FILE = Path(__file__).resolve().parent / "heroes.json"


def rows(path):
    with path.open(encoding="utf-8") as file:
        yield from csv.DictReader((line for line in file if not line.startswith("#")), delimiter="\t")


nodes = list(rows(NODES_FILE))
with EDGES_FILE.open(encoding="utf-8") as file:
    edges = [
        {"source": source, "target": target}
        for source, target in csv.reader((line for line in file if not line.startswith("#")), delimiter="\t")
    ]
in_degree = Counter(edge["target"] for edge in edges)
out_degree = Counter(edge["source"] for edge in edges)

heroes = [
    {
        "id": node["node_id"],
        "name": node["name"],
        "url": node["url"],
        "inDegree": in_degree[node["node_id"]],
        "outDegree": out_degree[node["node_id"]],
    }
    for node in nodes
]

payload = {
    "summary": {"nodes": len(heroes), "edges": len(edges), "isolates": sum(hero["inDegree"] + hero["outDegree"] == 0 for hero in heroes)},
    "heroes": heroes,
    "edges": edges,
}
OUTPUT_FILE.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
