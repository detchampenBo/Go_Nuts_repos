"""Build symposium-data.json for "The Symposium": 24 guests, seated by Louvain.

The party is the induced subgraph of 24 well-known philosophers in the week 4
network. Everything the page claims about seating is computed here, with the
same from-scratch Louvain, modularity and shuffle as prepare_data.py.
Run after prepare_data.py:  python3 prepare_symposium.py
"""
import itertools
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from prepare_data import load, louvain, modularity, nmi, shuffled

HERE = Path(__file__).resolve().parent
RUNS, NULL_RUNS = 50, 50
GUESTS = [  # (node id, place-card name)
    ("Socrates", "Socrates"), ("Plato", "Plato"), ("Aristotle", "Aristotle"), ("Epicurus", "Epicurus"),
    ("Cicero", "Cicero"), ("Seneca_the_Younger", "Seneca"), ("Augustine_of_Hippo", "Augustine"),
    ("Boethius", "Boethius"), ("Avicenna", "Avicenna"), ("Averroes", "Averroes"), ("Maimonides", "Maimonides"),
    ("Thomas_Aquinas", "Aquinas"), ("René_Descartes", "Descartes"), ("Thomas_Hobbes", "Hobbes"),
    ("Baruch_Spinoza", "Spinoza"), ("John_Locke", "Locke"), ("Gottfried_Wilhelm_Leibniz", "Leibniz"),
    ("David_Hume", "Hume"), ("Immanuel_Kant", "Kant"), ("Georg_Wilhelm_Friedrich_Hegel", "Hegel"),
    ("Arthur_Schopenhauer", "Schopenhauer"), ("Søren_Kierkegaard", "Kierkegaard"), ("Karl_Marx", "Marx"),
    ("Friedrich_Nietzsche", "Nietzsche"),
]


def wmodularity(weight, part):
    m = sum(weight.values())
    inside, total = Counter(), Counter()
    for (a, b), w in weight.items():
        total[part[a]] += w
        total[part[b]] += w
        if part[a] == part[b]:
            inside[part[a]] += w
    return sum(inside[c] / m - (total[c] / (2 * m)) ** 2 for c in total)


def clique_communities(adj, nodes, k):
    """Palla et al. 2005: k-cliques sharing k-1 nodes percolate into one community."""
    cliques = [set(c) for c in itertools.combinations(nodes, k) if all(b in adj[a] for a, b in itertools.combinations(c, 2))]
    root = list(range(len(cliques)))
    def find(i):
        while root[i] != i:
            i = root[i]
        return i
    for i, j in itertools.combinations(range(len(cliques)), 2):
        if len(cliques[i] & cliques[j]) == k - 1:
            root[find(i)] = find(j)
    groups = defaultdict(set)
    for i, c in enumerate(cliques):
        groups[find(i)] |= c
    return len(cliques), sorted((sorted(g, key=nodes.index) for g in groups.values()), key=lambda g: nodes.index(g[0]))


def main():
    nodes, years, full_adj, full_weight = load()
    ids = [g for g, _ in GUESTS]
    idx = {g: i for i, g in enumerate(ids)}
    adj = {g: {n for n in full_adj[g] if n in idx} for g in ids}
    weight = {e: w for e, w in full_weight.items() if e[0] in idx and e[1] in idx}
    edges = sorted([idx[a], idx[b], w] for (a, b), w in weight.items())

    def evening(seed, weighted):
        trace, last = [], {g: g for g in ids}
        def record(part):
            nonlocal last
            trace.append([[idx[g], idx[part[g]]] for g in ids if part[g] != last[g]])
            last = dict(part)
        part = louvain(adj, random.Random(seed), weight if weighted else None, None if weighted else record)
        return part, trace

    unweighted, weighted = [], []
    for seed in range(1, RUNS + 1):
        part, trace = evening(seed, False)
        unweighted.append({"part": [part[g] for g in ids], "q": round(modularity(adj, part), 4), "trace": trace})
        part, _ = evening(seed, True)
        weighted.append({"part": [part[g] for g in ids], "q": round(wmodularity(weight, part), 4),
                         "qCount": round(modularity(adj, part), 4)})

    null_rng = random.Random(40400)
    null = []
    for _ in range(NULL_RUNS):
        g = shuffled(adj, null_rng)
        part = louvain(g, null_rng)
        null.append({"q": round(modularity(g, part), 4),
                     "edges": sorted([idx[a], idx[b]] for a in g for b in g[a] if idx[a] < idx[b]),
                     "part": [part[x] for x in ids]})

    # The full hall: where each guest sits in the reference run of the 1,374-node network.
    school = json.loads((HERE / "school-data.json").read_text())
    ref = school["meta"]["referenceRun"]
    by_id = {p["id"]: p for p in school["philosophers"]}
    era_plan = [{"centuries BC": 0, "1st through 10th centuries": 1, "11th through 14th centuries": 1}.get(nodes[g]["era"], 2 if nodes[g]["era"] in ("15th and 16th centuries", "17th century") else 3) for g in ids]

    data = {
        "meta": {"inputSha256": school["meta"]["inputSha256"], "seeds": list(range(1, RUNS + 1)), "nullSeed": 40400},
        "guests": [{"id": g, "name": nodes[g]["name"], "card": card, "era": nodes[g]["era"],
                    "year": years.get(nodes[g]["wikidata_id"]), "url": nodes[g]["url"],
                    "fullDegree": len(full_adj[g]), "hall": by_id[g]["runs"][ref]} for g, card in GUESTS],
        "edges": edges,
        "eraPlan": era_plan,
        "unweighted": unweighted,
        "weighted": weighted,
        "null": null,
        "cliques": {k: dict(zip(("cliques", "communities"), (n, [[idx[g] for g in c] for c in cs])))
                    for k in (3, 4, 5, 6) for n, cs in [clique_communities(adj, ids, k)]},
        "hall": [{"lane": i, "top": lane["top"][:3], "size": lane["size"]} for i, lane in enumerate(school["lanes"])],
    }
    (HERE / "symposium-data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    # self-checks for what the page says
    qs = [r["q"] for r in unweighted]
    nq = [r["q"] for r in null]
    mu = sum(nq) / len(nq)
    sd = (sum((q - mu) ** 2 for q in nq) / (len(nq) - 1)) ** 0.5
    assert all(0 < q for q in qs) and min(qs) > mu + 3 * sd
    assert all(len(r["trace"]) > 0 for r in unweighted)
    tables = Counter(len(set(r["part"])) for r in unweighted)
    wtables = Counter(len(set(r["part"])) for r in weighted)
    same = Counter(tuple(sorted(Counter(r["part"]).values())) for r in unweighted)
    plato_aristotle = sum(r["part"][1] == r["part"][2] for r in unweighted), sum(r["part"][1] == r["part"][2] for r in weighted)
    print(f"{len(ids)} guests, {len(edges)} conversations; count Q {min(qs):.3f}-{max(qs):.3f}, null {mu:.3f}±{sd:.3f}, z {(sum(qs)/len(qs)-mu)/sd:.1f}")
    print(f"tables (count) {dict(tables)}, (volume) {dict(wtables)}, volume Q {min(r['q'] for r in weighted):.3f}-{max(r['q'] for r in weighted):.3f}")
    print(f"Plato & Aristotle together: count {plato_aristotle[0]}/50, volume {plato_aristotle[1]}/50")
    print(f"NMI era plan vs evening 1: {nmi(dict(enumerate(era_plan)), dict(enumerate(unweighted[0]['part'])), list(range(len(ids)))):.2f}")
    for k, c in data["cliques"].items():
        print(f"k={k}: {c['cliques']} cliques, communities {[[GUESTS[i][1] for i in g] for g in c['communities']]}")


if __name__ == "__main__":
    main()
