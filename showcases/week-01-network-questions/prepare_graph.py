"""Convert versioned source-network data into the JSON used by the static site."""

import json
from math import cos, pi, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "source-network.json"
OUTPUT = ROOT / "data" / "graph-data.json"
COLORS = ["#c9ec45", "#5cdbeb", "#ff8c73", "#a69af4", "#f6ce6d", "#e384cf", "#6dc99e"]


def positioned_nodes(nodes):
    """Add stable positions and display colors for the current lightweight graph view."""
    count = len(nodes)
    for index, node in enumerate(nodes):
        angle = (2 * pi * index / count) - pi / 2
        node.update({
            "order": index + 1,
            "x": round(380 + 250 * cos(angle)),
            "y": round(245 + 170 * sin(angle)),
            "color": COLORS[index % len(COLORS)],
        })
    return nodes


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    output = {"nodes": positioned_nodes(source["nodes"]), "edges": source["edges"]}
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
