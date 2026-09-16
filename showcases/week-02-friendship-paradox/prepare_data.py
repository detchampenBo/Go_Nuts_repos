"""Build paradox-data.json for the Week 2 friendship-paradox explorable.

Reads the frozen Week 1 Marvel snapshot and emits, for three networks
(real Marvel, a scale-free Barabasi-Albert model, a random G(n, m) model),
every node's degree and its neighbours' mean degree, plus the aggregate
numbers the page shows: <k>, <k^2>/<k>, the variance, and sigma^2 / <k>.

Standard library only. Run from this folder:

    python prepare_data.py
"""

import hashlib
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data" / "week1"
NODES_TSV = DATA / "week1_nodes.tsv"
EDGES_TSV = DATA / "week1_edges.tsv"
OUT = HERE / "paradox-data.json"

# Seeds are fixed so the checked-in JSON is reproducible.
BA_SEED = 20802
ER_SEED = 20803
LAYOUT_SEEDS = {"marvel": 20811, "scalefree": 20812, "random": 20813}


def read_rows(path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            yield line.rstrip("\n").split("\t")


def load_marvel():
    rows = read_rows(NODES_TSV)
    header = next(rows)
    idx = {name: i for i, name in enumerate(header)}
    names, urls, order = {}, {}, []
    for row in rows:
        node_id = row[idx["node_id"]]
        order.append(node_id)
        names[node_id] = row[idx["name"]]
        urls[node_id] = row[idx["url"]] if idx.get("url", -1) < len(row) else ""
    adjacency = {node_id: set() for node_id in order}
    for source, target in read_rows(EDGES_TSV):
        if source in adjacency and target in adjacency and source != target:
            adjacency[source].add(target)
            adjacency[target].add(source)
    return order, names, urls, adjacency


def barabasi_albert(n, m, seed):
    """Growth + preferential attachment, mirroring networkx's algorithm."""
    rng = random.Random(seed)
    targets = list(range(m))
    repeated = []
    adjacency = {i: set() for i in range(n)}
    for new_node in range(m, n):
        for target in targets:
            adjacency[new_node].add(target)
            adjacency[target].add(new_node)
        repeated.extend(targets)
        repeated.extend([new_node] * m)
        chosen = set()
        while len(chosen) < m:
            chosen.add(rng.choice(repeated))
        targets = list(chosen)
    return adjacency


def gnm(n, m, seed):
    """Uniform random simple graph with exactly m edges."""
    rng = random.Random(seed)
    edges = set()
    while len(edges) < m:
        a = rng.randrange(n)
        b = rng.randrange(n)
        if a == b:
            continue
        edges.add((min(a, b), max(a, b)))
    adjacency = {i: set() for i in range(n)}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    return adjacency


def force_layout(order, adjacency, seed, iterations=520):
    """Deterministic Fruchterman-Reingold layout, normalised into a unit box.

    Only connected nodes take part in the simulation — pure repulsion would fling
    isolates to infinity. Isolates are parked in a tidy row along the bottom so
    they stay visible without distorting the rest of the picture.
    """
    rng = random.Random(seed)
    live = [node for node in order if adjacency[node]]
    n = len(live)
    positions = {}
    if n:
        index = {node: i for i, node in enumerate(live)}
        xs, ys = [], []
        for i in range(n):
            angle = 2 * math.pi * i / n
            radius = 0.35 + rng.random() * 0.08
            xs.append(0.5 + math.cos(angle) * radius)
            ys.append(0.5 + math.sin(angle) * radius)

        edges = []
        for node in live:
            a = index[node]
            for other in adjacency[node]:
                b = index.get(other)
                if b is not None and a < b:
                    edges.append((a, b))

        k = math.sqrt(1.0 / n)
        temperature = 0.12
        for _ in range(iterations):
            dx = [0.0] * n
            dy = [0.0] * n
            for i in range(n - 1):
                xi, yi = xs[i], ys[i]
                acc_x = acc_y = 0.0
                for j in range(i + 1, n):
                    ddx = xi - xs[j]
                    ddy = yi - ys[j]
                    d2 = ddx * ddx + ddy * ddy
                    if d2 < 1e-9:
                        ddx = (rng.random() - 0.5) * 1e-3
                        ddy = (rng.random() - 0.5) * 1e-3
                        d2 = ddx * ddx + ddy * ddy + 1e-12
                    force = k * k / d2
                    fx = ddx * force
                    fy = ddy * force
                    acc_x += fx
                    acc_y += fy
                    dx[j] -= fx
                    dy[j] -= fy
                dx[i] += acc_x
                dy[i] += acc_y

            for a, b in edges:
                ddx = xs[a] - xs[b]
                ddy = ys[a] - ys[b]
                d = math.sqrt(ddx * ddx + ddy * ddy) or 1e-9
                fx = ddx * d / k
                fy = ddy * d / k
                dx[a] -= fx
                dy[a] -= fy
                dx[b] += fx
                dy[b] += fy

            for i in range(n):
                d = math.sqrt(dx[i] * dx[i] + dy[i] * dy[i])
                if d > 1e-12:
                    step = min(d, temperature)
                    xs[i] += dx[i] / d * step
                    ys[i] += dy[i] / d * step
            temperature = max(temperature * 0.987, 0.0004)

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span = max(max_x - min_x, max_y - min_y) or 1.0
        # Keep the aspect ratio square, and leave the bottom strip for isolates.
        off_x = (span - (max_x - min_x)) / 2
        off_y = (span - (max_y - min_y)) / 2
        for node in live:
            i = index[node]
            x = (xs[i] - min_x + off_x) / span
            y = (ys[i] - min_y + off_y) / span
            positions[node] = [round(0.04 + x * 0.92, 4), round(0.03 + y * 0.87, 4)]

    isolates = [node for node in order if not adjacency[node]]
    for i, node in enumerate(isolates):
        x = 0.06 + (0.88 * (i + 0.5) / max(len(isolates), 1))
        positions[node] = [round(x, 4), 0.965]
    return positions


def summarise(order, adjacency, names, urls, layout_seed):
    degree = {node: len(adjacency[node]) for node in order}
    k_values = [degree[node] for node in order]
    n = len(order)
    edge_count = sum(k_values) // 2
    isolates = sum(1 for k in k_values if k == 0)
    mean_k = sum(k_values) / n
    mean_k2 = sum(k * k for k in k_values) / n
    variance = mean_k2 - mean_k * mean_k
    friend_mean = mean_k2 / mean_k  # degree of a node reached along a random edge
    excess = variance / mean_k

    positions = force_layout(order, adjacency, layout_seed)

    heroes = {}
    paradox_holds = 0
    connected = 0
    top_of_circle = []
    neighbour_mean_total = 0.0
    for node in order:
        neighbours = sorted(adjacency[node], key=lambda x: -degree[x])
        k = degree[node]
        if k:
            neighbour_mean = sum(degree[m] for m in neighbours) / k
            neighbour_mean_total += neighbour_mean
            connected += 1
            is_paradox = neighbour_mean > k
            paradox_holds += int(is_paradox)
            # A hero is "top of their circle" only when NO single friend outranks
            # them. That is stricter than their friends' mean being lower.
            bigger_friends = sum(1 for m in neighbours if degree[m] > k)
            is_top = bigger_friends == 0
            if is_top:
                top_of_circle.append(node)
        else:
            neighbour_mean = 0.0
            is_paradox = False
            bigger_friends = 0
            is_top = False
        heroes[node] = {
            "name": names.get(node, str(node)),
            "url": urls.get(node, ""),
            "degree": k,
            "neighborMean": round(neighbour_mean, 3),
            "neighbors": neighbours,
            "paradox": is_paradox,
            "biggerFriends": bigger_friends,
            "topOfCircle": is_top,
            "pos": positions[node],
        }

    # A friendly starting node: connected, low degree, paradox clearly true.
    suggested = min(
        (node for node in order if degree[node] >= 2),
        key=lambda node: (heroes[node]["degree"], -heroes[node]["neighborMean"]),
    )

    return {
        "nodes": n,
        "edges": edge_count,
        "isolates": isolates,
        "meanDegree": round(mean_k, 3),
        "meanSquareDegree": round(mean_k2, 3),
        "variance": round(variance, 3),
        # Expected degree at the end of a uniformly chosen connection.
        "friendMeanDegree": round(friend_mean, 3),
        # Average over connected nodes of that node's own friends' mean degree.
        # This is what the scatter's vertical axis averages, and it is NOT the
        # same quantity as friendMeanDegree above.
        "neighborMeanAverage": round(neighbour_mean_total / connected, 3) if connected else 0.0,
        "excessTerm": round(excess, 3),
        "paradoxFraction": round(paradox_holds / connected, 4),
        "paradoxCount": paradox_holds,
        "connectedCount": connected,
        "maxDegree": max(k_values),
        "topOfCircle": [
            {"id": node, "name": names.get(node, str(node)), "degree": degree[node]}
            for node in sorted(top_of_circle, key=lambda x: -degree[x])
        ],
        "suggested": suggested,
        "heroes": heroes,
    }


def synthetic_network(adjacency, layout_seed):
    order = list(adjacency.keys())
    names = {str(node): f"Node {node + 1}" for node in order}
    urls = {str(node): "" for node in order}
    adjacency = {str(k): {str(v) for v in vs} for k, vs in adjacency.items()}
    return summarise([str(node) for node in order], adjacency, names, urls, layout_seed)


def main():
    order, names, urls, adjacency = load_marvel()
    print("laying out marvel…", flush=True)
    marvel = summarise(order, adjacency, names, urls, LAYOUT_SEEDS["marvel"])
    n = marvel["nodes"]
    m_edges = marvel["edges"]

    # m for BA chosen so <k> ~ 2m matches Marvel's density at the same node count.
    ba_m = max(1, round(m_edges / n))
    print("laying out scale-free…", flush=True)
    scale_free = synthetic_network(barabasi_albert(n, ba_m, BA_SEED), LAYOUT_SEEDS["scalefree"])
    print("laying out random…", flush=True)
    random_graph = synthetic_network(gnm(n, m_edges, ER_SEED), LAYOUT_SEEDS["random"])

    digest = hashlib.sha256()
    for path in (NODES_TSV, EDGES_TSV):
        digest.update(path.read_bytes())

    payload = {
        "version": 1,
        "sourceSha256": digest.hexdigest(),
        "source": "Wikipedia Category:Marvel Comics superheroes, frozen Week 1 snapshot",
        "baParameter": ba_m,
        "seeds": {"barabasiAlbert": BA_SEED, "randomGnm": ER_SEED},
        "networks": {
            "marvel": {"label": "Marvel Wikipedia links", **marvel},
            "scalefree": {
                "label": f"Scale-free model (Barabasi-Albert, m={ba_m})",
                **scale_free,
            },
            "random": {"label": "Random model (Erdos-Renyi, same n and m)", **random_graph},
        },
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    for key, net in payload["networks"].items():
        print(
            f"{key:10s} n={net['nodes']} m={net['edges']:5d} "
            f"<k>={net['meanDegree']:.2f} friend={net['friendMeanDegree']:.2f} "
            f"paradox={net['paradoxFraction'] * 100:.1f}% top-of-circle={len(net['topOfCircle'])}"
        )
    print(f"wrote {OUT.relative_to(HERE.parent.parent)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
