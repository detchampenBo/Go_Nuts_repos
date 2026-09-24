"""Build school-data.json for the Week 4 "Which School?" explorable.

Reads the frozen philosopher snapshot (../../data/week4), keeps the giant
component of the undirected network, and runs Louvain (unweighted, as on the
course page) with 50 seeds. Every run is aligned to one reference partition
(the medoid: highest mean NMI to all other runs), so each philosopher gets a
ballot: how many of the 50 runs put them in each school.

Also records a degree-preserving null (10 double-edge-swap shuffles), per-run
modularity and NMI, and birth years from Wikidata for the time axis.

Standard library only. Run from this folder:

    python3 prepare_data.py
"""

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data" / "week4"
NODES_TSV = DATA / "week4_philosophers_nodes.tsv"
EDGES_TSV = DATA / "week4_philosophers_edges.tsv"
YEARS_TSV = DATA / "week4_birth_years.tsv"
OUT = HERE / "school-data.json"

RUNS = 50
NULL_RUNS = 10
NULL_SEED = 40400
SPLINTER = 20
ERA_FALLBACK = {  # used only for the 50 philosophers Wikidata has no birth year for
    "centuries BC": -400, "1st through 10th centuries": 500, "11th through 14th centuries": 1250,
    "15th and 16th centuries": 1500, "17th century": 1650, "18th century": 1750, "19th century": 1850,
}


def read_rows(path):
    with path.open(encoding="utf-8") as handle:
        rows = (line.rstrip("\n").split("\t") for line in handle if line.strip() and not line.startswith("#"))
        header = next(rows)
        for row in rows:
            yield dict(zip(header, row + [""] * (len(header) - len(row))))


def load():
    nodes = {r["node_id"]: r for r in read_rows(NODES_TSV)}
    years = {r["wikidata_id"]: int(r["birth_year"]) for r in read_rows(YEARS_TSV)}
    weight = defaultdict(int)  # undirected: sum both directions
    for r in read_rows(EDGES_TSV):
        s, t = r["source"], r["target"]
        if s != t and s in nodes and t in nodes:
            weight[tuple(sorted((s, t)))] += int(r["weight"])
    adj = defaultdict(set)
    for s, t in weight:
        adj[s].add(t)
        adj[t].add(s)
    # giant component
    seen, best = set(), set()
    for start in adj:
        if start in seen:
            continue
        comp, stack = {start}, [start]
        while stack:
            for nb in adj[stack.pop()]:
                if nb not in comp:
                    comp.add(nb)
                    stack.append(nb)
        seen |= comp
        best = max(best, comp, key=len)
    adj = {n: adj[n] for n in best}
    weight = {e: w for e, w in weight.items() if e[0] in best}
    return nodes, years, adj, weight


# ---------------------------------------------------------------- Louvain

def louvain(adj, rng):
    """Blondel et al. 2008 on an unweighted graph. Returns {node: community index}."""
    # Sorted everywhere: set order depends on PYTHONHASHSEED, and tie-breaks must not.
    graph = {n: {nb: 1.0 for nb in sorted(adj[n])} for n in sorted(adj)}
    strength = {n: float(len(nbs)) for n, nbs in adj.items()}
    member = {n: n for n in adj}  # original node -> current super-node
    while True:
        com = one_level(graph, strength, rng)
        if len(set(com.values())) == len(graph):
            break
        member = {n: com[s] for n, s in member.items()}
        graph, strength = aggregate(graph, strength, com)
    labels = {c: i for i, c in enumerate(sorted(set(member.values()), key=str))}
    return {n: labels[c] for n, c in member.items()}


def one_level(graph, strength, rng):
    """Phase 1: move single nodes to the neighbouring community with the best gain."""
    m2 = sum(strength.values())
    com = {n: n for n in graph}
    tot = dict(strength)
    order = sorted(graph, key=str)
    moved = True
    while moved:
        moved = False
        rng.shuffle(order)
        for n in order:
            k, home = strength[n], com[n]
            links = defaultdict(float)
            for nb, w in graph[n].items():
                if nb != n:
                    links[com[nb]] += w
            tot[home] -= k
            best, best_gain = home, links.get(home, 0.0) - tot[home] * k / m2
            for c, w in links.items():
                gain = w - tot[c] * k / m2
                if gain > best_gain + 1e-12:
                    best, best_gain = c, gain
            tot[best] += k
            if best != home:
                com[n] = best
                moved = True
    return com


def aggregate(graph, strength, com):
    """Phase 2: collapse each community into one weighted super-node."""
    new_graph = defaultdict(lambda: defaultdict(float))
    new_strength = defaultdict(float)
    for n, nbs in graph.items():
        new_strength[com[n]] += strength[n]
        for nb, w in nbs.items():
            new_graph[com[n]][com[nb]] += w
    return {c: dict(v) for c, v in new_graph.items()}, dict(new_strength)


def modularity(adj, part):
    m = sum(len(v) for v in adj.values()) / 2
    inside, degree = Counter(), Counter()
    for n, nbs in adj.items():
        degree[part[n]] += len(nbs)
        inside[part[n]] += sum(part[nb] == part[n] for nb in nbs) / 2
    return sum(inside[c] / m - (degree[c] / (2 * m)) ** 2 for c in degree)


def nmi(a, b, keys):
    """Normalized mutual information, arithmetic mean normalization (sklearn default)."""
    n = len(keys)
    ca, cb = Counter(a[k] for k in keys), Counter(b[k] for k in keys)
    joint = Counter((a[k], b[k]) for k in keys)
    mi = sum(v / n * math.log(v * n / (ca[x] * cb[y])) for (x, y), v in joint.items())
    h = lambda c: -sum(v / n * math.log(v / n) for v in c.values())
    denom = (h(ca) + h(cb)) / 2
    return mi / denom if denom else 1.0


def shuffled(adj, rng):
    """Degree-preserving null: 10·m double-edge swaps, no self-loops or multi-edges."""
    edges = sorted({tuple(sorted((a, b))) for a, nbs in adj.items() for b in nbs})
    present = set(edges)
    for _ in range(10 * len(edges)):
        i, j = rng.randrange(len(edges)), rng.randrange(len(edges))
        (a, b), (c, d) = edges[i], edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        e1, e2 = tuple(sorted((a, d))), tuple(sorted((c, b)))
        if len({a, b, c, d}) < 4 or e1 in present or e2 in present:
            continue
        present -= {edges[i], edges[j]}
        present |= {e1, e2}
        edges[i], edges[j] = e1, e2
    out = {}
    for a, b in edges:
        out.setdefault(a, set()); out.setdefault(b, set())
    for a, b in edges:
        out[a].add(b)
        out[b].add(a)
    return out


# ---------------------------------------------------------------- build

def main():
    nodes, years, adj, weight = load()
    keys = sorted(adj)
    runs = [louvain(adj, random.Random(seed)) for seed in range(1, RUNS + 1)]
    qs = [modularity(adj, p) for p in runs]
    pair = [[1.0 if i == j else None for j in range(RUNS)] for i in range(RUNS)]
    for i in range(RUNS):
        for j in range(i + 1, RUNS):
            pair[i][j] = pair[j][i] = nmi(runs[i], runs[j], keys)
    ref_i = max(range(RUNS), key=lambda i: sum(pair[i]))
    ref = runs[ref_i]

    # Align every run to the reference: each run-community maps to the reference
    # community it overlaps most. Two run-communities may land in the same lane.
    aligned = []
    for p in runs:
        overlap = defaultdict(Counter)
        for n in keys:
            overlap[p[n]][ref[n]] += 1
        to_ref = {c: cnt.most_common(1)[0][0] for c, cnt in overlap.items()}
        aligned.append({n: to_ref[p[n]] for n in keys})

    # Lanes ordered by median birth year so the picture reads as a river through time.
    def year(n):
        return years.get(nodes[n]["wikidata_id"], ERA_FALLBACK.get(nodes[n]["era"], 1000))

    size = Counter(ref.values())
    lanes = sorted(set(ref.values()), key=lambda c: sorted(year(n) for n in keys if ref[n] == c)[size[c] // 2])
    # Communities under SPLINTER members share one grey lane: eight hues is the categorical limit.
    big = [c for c in lanes if size[c] >= SPLINTER]
    lane_of = {c: big.index(c) if c in big else len(big) for c in lanes}
    lanes = big + ([None] if len(big) < len(lanes) else [])

    idx = {n: i for i, n in enumerate(keys)}
    philosophers = []
    for n in keys:
        votes = [0] * len(lanes)
        for a in aligned:
            votes[lane_of[a[n]]] += 1
        r = nodes[n]
        philosophers.append({
            "id": n,
            "name": r["name"],
            "year": year(n),
            "yearKnown": r["wikidata_id"] in years,
            "era": r["era"],
            "subfields": [s.strip() for s in r["subfields"].split(",") if s.strip()],
            "desc": r["description"][:260],
            "url": r["url"],
            "degree": len(adj[n]),
            "votes": votes,
            "runs": [lane_of[a[n]] for a in aligned],
        })

    edges = [[idx[a], idx[b], w] for (a, b), w in weight.items()]

    lane_info = []
    for i, c in enumerate(lanes):
        members = sorted((p for p in philosophers if lane_of[ref[p["id"]]] == i), key=lambda p: -p["degree"])
        lane_info.append({
            "splinter": c is None,
            "size": len(members),
            "top": [p["name"] for p in members[:6]],
            "medianYear": sorted(p["year"] for p in members)[len(members) // 2],
            "eras": Counter(p["era"] for p in members).most_common(),
        })

    null_rng = random.Random(NULL_SEED)
    null_q = [modularity(g, louvain(g, null_rng)) for g in (shuffled(adj, null_rng) for _ in range(NULL_RUNS))]
    null_mean = sum(null_q) / NULL_RUNS
    null_sd = (sum((q - null_mean) ** 2 for q in null_q) / (NULL_RUNS - 1)) ** 0.5

    digest = hashlib.sha256()
    for path in (NODES_TSV, EDGES_TSV, YEARS_TSV):
        digest.update(path.read_bytes())

    data = {
        "meta": {
            "inputSha256": digest.hexdigest(),
            "seeds": list(range(1, RUNS + 1)),
            "referenceRun": ref_i,
            "nodes": len(keys),
            "links": len(edges),
            "nullSeed": NULL_SEED,
        },
        "runs": [{"q": round(qs[i], 4), "k": len(set(runs[i].values())), "nmi": round(pair[i][ref_i], 3)} for i in range(RUNS)],
        "nullQ": {"mean": round(null_mean, 4), "sd": round(null_sd, 4), "values": [round(q, 4) for q in null_q]},
        "lanes": lane_info,
        "philosophers": philosophers,
        "edges": edges,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # self-check: sanity of what the page will claim
    assert all(sum(p["votes"]) == RUNS for p in philosophers)
    assert abs(modularity(adj, {n: 0 for n in keys})) < 1e-9, "single community must score Q = 0"
    assert min(qs) > null_mean + 5 * null_sd, "real partitions should beat the shuffled null"
    loyal = sum(max(p["votes"]) == RUNS for p in philosophers)
    print(f"{len(keys)} nodes, {len(edges)} links, ref run {ref_i}, Q {min(qs):.3f}–{max(qs):.3f}, "
          f"k {min(r['k'] for r in data['runs'])}–{max(r['k'] for r in data['runs'])}, "
          f"NMI {min(x for row in pair for x in row):.2f}–{max(x for i, row in enumerate(pair) for j, x in enumerate(row) if i != j):.2f}, "
          f"null {null_mean:.3f}±{null_sd:.3f}, always-same-school {loyal}/{len(keys)}")
    for i, lane in enumerate(lane_info):
        print(i, lane["size"], lane["medianYear"], lane["top"][:4])


if __name__ == "__main__":
    main()
