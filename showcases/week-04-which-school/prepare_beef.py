"""Reproduce the original Louvain partitions for exact pair co-membership.

The existing school-data lanes use many-to-one alignment and cannot establish
whether two people actually share a community. Keep this result separate.
Run: python3 showcases/week-04-which-school/prepare_beef.py
"""
import json
import random
from pathlib import Path
from prepare_data import load, louvain, modularity

HERE = Path(__file__).resolve().parent
PAIRS = [
    ("hegel", "Georg_Wilhelm_Friedrich_Hegel", "Arthur_Schopenhauer"),
    ("hobbes", "Thomas_Hobbes", "Jean-Jacques_Rousseau"),
    ("plato", "Plato", "Aristotle"),
]


def main():
    data = json.loads((HERE / "school-data.json").read_text())
    _, _, adj, _ = load()
    runs = [louvain(adj, random.Random(seed)) for seed in data["meta"]["seeds"]]
    for run, stored in zip(runs, data["runs"]):
        assert abs(modularity(adj, run) - stored["q"]) < 0.00006
        assert len(set(run.values())) == stored["k"]
    pairs = {}
    for key, a, b in PAIRS:
        together = [run[a] == run[b] for run in runs]
        pairs[key] = {"ids": [a, b], "together": together}
        print(f"{key}: same community in {sum(together)}/{len(runs)} runs")
    result = {"inputSha256": data["meta"]["inputSha256"], "pairs": pairs}
    (HERE / "beef-data.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
