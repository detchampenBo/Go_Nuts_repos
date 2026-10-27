"""Corpus-wide evidence for the Squeeze game. Run with the repo's .venv/bin/python after prepare_data.py.

The game asks a player to squeeze a passage into 30, then 10, then 3 words and watches whether keyword
(TF-IDF) and semantic (MiniLM, best 60-word passage) search still find the source article. This script runs the
same squeeze automatically on every article, so a player's single round can be compared with the corpus.

For each of the 303 articles:
  source sentence = the first sentence with 18-45 words from the story sections (biography, powers), skipping
                    publication boilerplate ("Created by ... first appeared in ..."); the article's title (and each
                    capitalised title word) replaced by "someone", as in the game's prompts.
  squeeze rules   = first:  keep the first N words, in order
                    rarest: keep the N words with the highest TF-IDF query weight, in original order
                    taboo:  ban the 5 highest-weight words first, then keep the rarest N of the rest
  budgets         = 30, 20, 10, 5, 3, 2, 1 words.
The rank of the source article among all 303 is recorded for both searches. A query with no indexed word in
common with the source gets the worst rank (303): keyword search cannot tell the articles apart. Reads only the
files in dist/data, so the evidence uses exactly the vectors, vocabulary and IDF the browser uses (dense vectors
are the stored signed-byte vectors, renormalized). Queries are embedded with the original Sentence Transformers
model; the browser uses its quantized ONNX copy, so live ranks can differ by a few places.

Two dataset checks explain the result:
  fingerprints = vocabulary terms that occur on exactly one page; how many pages have them, and how many are names
                 (capitalised in at least 80% of their occurrences on that page).
  magnets      = which pages the wrong first results land on (first-N rule): their length against the corpus, and
                 for meaning search the passage that wins most often, so the page can show the actual text.
  order        = word order: each squeeze (first 10 / 30 words) is shuffled with a fixed seed; we record the cosine
                 between a sentence and its shuffled version (against two different heroes' sentences), and the
                 meaning-search rank before and after. Plus a few hand-written "who did what" swaps.
  neighbours   = the headline question, "when the message gets lost, where does it end up?": the drift test below,
                 repeated after a first-character capitalisation filter, then truncation to the word budget.
                 This heuristic can leave names preceded by punctuation and drops ordinary sentence-initial words.
                 Every filtered case where meaning search's wrong guess is a hyperlink neighbour is listed.
  merge        = hybrid search: keyword and meaning rankings merged by reciprocal rank fusion,
                 w / (60 + keyword rank) + (1 - w) / (60 + meaning rank), for w = 0.5 (the usual equal-weight default),
                 0.7 and 0.9, on three query sets: 10 words with names, 5 words without names, and the 56 hand-written
                 descriptions in descriptions.tsv. Top-5 shares, plus the heroes each merge gains and loses against
                 keyword search alone.
  checks       = the same question at 5 words, pushed further: how many link hops separate the right hero from
                 the wrong guess (against all page pairs), whether they share a Louvain community (seed 42), how the
                 answer changes with the retrieval unit (60-word, 180-word, whole page), and how removing detected
                 spaCy entities instead changes it. This also removes non-name entities and spaces punctuation.
  drift        = when a squeeze puts the wrong article first, is that article a hyperlink neighbour of the source
                 (week 1 network, undirected)? Compared with the share of all page pairs that are linked.
"""
import json
import random
import re
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
import spacy
from networkx.algorithms.community import louvain_communities
from scipy.sparse import csr_matrix
from sentence_transformers import SentenceTransformer

HERE = Path(__file__).resolve().parent
DATA = HERE / "dist" / "data"
EDGES = HERE.parents[1] / "notebooks" / "data" / "week1_edges.tsv"
HEROES = ["Spider-Man", "Hulk", "Wolverine", "Storm", "Deadpool", "Black Panther"]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BUDGETS = [30, 20, 10, 5, 3, 2, 1]
BANNED = 5
TINY = 3  # passages this short are splitter leftovers ("traveler.")
BOILERPLATE = re.compile(r"\b(created by|first appeared|first appearance|published by|appearing in american comic books)\b", re.I)
STORY_SECTIONS = {"fictional character biography", "fictional biography", "character biography", "biography",
                  "powers and abilities", "powers", "abilities", "powers, skills, and equipment", "personality", "origin", "origins"}
OTHER_SECTIONS = {"publication history", "creation", "concept and creation", "development", "creation and development",
                  "reception", "critical reception", "critical response", "accolades", "legacy", "in other media",
                  "other media", "collected editions", "bibliography", "other versions", "alternate versions"}
STOP_SECTIONS = {"references", "external links", "see also", "notes", "further reading"}
TOKEN = re.compile(r"\b[a-z0-9_]{2,}\b")  # same token rule as retrieval.js queryVector


def source_sentence(doc):
    """First 18-45-word sentence from the story sections (biography, powers), like the game's prompts.
    Publication boilerplate ("Created by Stan Lee and Jack Kirby, the character first appeared in ...") is
    skipped: it describes the comic, not the hero, and many pages share it word for word."""
    title = doc["title"]
    masked = doc["text"].replace(title, "someone")
    for word in re.findall(r"[A-Z][\w-]{2,}", title):
        masked = re.sub(rf"\b{re.escape(word)}\b", "someone", masked)
    story, fallback = None, None
    mode = False
    for line in masked.split("\n"):
        head = line.strip().lower()
        if 0 < len(head.split()) <= 6 and not head.endswith((".", ":")):
            if head in STOP_SECTIONS:
                break
            if head in STORY_SECTIONS or head in OTHER_SECTIONS:
                mode = head in STORY_SECTIONS
            continue
        for s in re.split(r"(?<=[.!?])\s+", line):
            if 18 <= len(s.split()) <= 45 and not BOILERPLATE.search(s):
                if mode and story is None:
                    story = s
                if fallback is None:
                    fallback = s
    return story or fallback


def main():
    corpus = json.loads((DATA / "corpus.json").read_text())
    lex = json.loads((DATA / "lexical.json").read_text())
    docs = corpus["documents"]
    n = len(docs)
    vocab = {w: i for i, w in enumerate(lex["vocab"])}
    idf = np.array(lex["idf"])
    stop = set(lex["stop"])
    rows, cols, vals = [], [], []
    for d, (idx, w) in enumerate(lex["rows"]):
        rows += [d] * len(idx); cols += idx; vals += w
    M = csr_matrix((vals, (rows, cols)), shape=(n, len(vocab)))

    passages = json.loads((DATA / "passages-60.json").read_text())
    owners = np.array([p["doc"] for p in passages])
    texts_60 = [p["text"] for p in passages]
    V = np.fromfile(DATA / "vectors-60.bin", dtype="i1").astype("f4").reshape(len(passages), -1)
    V /= np.linalg.norm(V, axis=1, keepdims=True)

    def weights(text):
        """TF-IDF query weights per vocabulary index, exactly as queryVector() in retrieval.js."""
        counts = {}
        for t in TOKEN.findall(text.lower()):
            if t not in stop and t in vocab:
                counts[vocab[t]] = counts.get(vocab[t], 0) + 1
        return {i: (1 + np.log(c)) * idf[i] for i, c in counts.items()}

    def sparse_rank(text, target):
        w = weights(text)
        if not w:
            return n
        q = np.zeros(len(vocab)); q[list(w)] = list(w.values())
        s = M @ (q / np.linalg.norm(q))
        return n if s[target] <= 0 else int((s > s[target]).sum()) + 1

    def squeeze(sentence, rule, budget):
        words = sentence.split()
        if rule == "first":
            return " ".join(words[:budget])
        # Weight of each word = weight of its first indexed token; unindexed words never survive.
        w = weights(sentence)
        def score(word):
            toks = [t for t in TOKEN.findall(word.lower()) if t in vocab and t not in stop]
            return w[vocab[toks[0]]] if toks else 0.0
        order = sorted(range(len(words)), key=lambda k: -score(words[k]))
        order = [k for k in order if score(words[k]) > 0]
        if rule == "taboo":
            banned = {TOKEN.findall(words[k].lower())[0] for k in order[:BANNED]}
            order = [k for k in order if not set(TOKEN.findall(words[k].lower())) & banned]
        keep = sorted(order[:budget])
        return " ".join(words[k] for k in keep)

    model = SentenceTransformer(MODEL, local_files_only=True, device="cpu")
    picked = [(d, source_sentence(doc)) for d, doc in enumerate(docs)]
    picked = [(d, s) for d, s in picked if s]
    queries = [(d, rule, b, squeeze(s, rule, b)) for d, s in picked for rule in ("first", "rarest", "taboo") for b in BUDGETS]
    texts = [q[3] for q in queries]
    E = model.encode([t or "." for t in texts], batch_size=128, normalize_embeddings=True, show_progress_bar=True)

    index = {doc["id"]: k for k, doc in enumerate(docs)}
    links = set()
    for line in EDGES.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        a, b = line.split("\t")[:2]
        if a in index and b in index and a != b:
            links.add(frozenset((index[a], index[b])))

    def keyword_top(text):
        w = weights(text)
        if not w:
            return None
        q = np.zeros(len(vocab)); q[list(w)] = list(w.values())
        s = M @ q
        return int(np.argmax(s)) if s.max() > 0 else None

    ranks, drift, magnets = {}, {}, {}
    for (d, rule, b, text), e in zip(queries, E):
        best = None
        if not text:
            kr = dr = n
        else:
            kr = sparse_rank(text, d)
            best = np.full(n, -np.inf); np.maximum.at(best, owners, V @ e)
            dr = int((best > best[d]).sum()) + 1
        ranks.setdefault(rule, {}).setdefault(b, {"keyword": [], "semantic": []})
        ranks[rule][b]["keyword"].append(kr); ranks[rule][b]["semantic"].append(dr)
        if text:
            for method, top in (("keyword", keyword_top(text)), ("semantic", int(np.argmax(best)))):
                if top is not None and top != d and rule == "first":
                    cell = magnets.setdefault(b, {"keyword": [Counter(), Counter()], "semantic": [Counter(), Counter()]})[method]
                    cell[0][top] += 1
                    if method == "semantic":
                        cell[1][int(np.argmax(V @ e))] += 1
                if top is not None and top != d:
                    cell = drift.setdefault(rule, {}).setdefault(b, {"keyword": [0, 0], "semantic": [0, 0]})[method]
                    cell[0] += 1; cell[1] += frozenset((d, top)) in links

    def rank_dense(e, d):
        best = np.full(n, -np.inf); np.maximum.at(best, owners, V @ e)
        return int((best > best[d]).sum()) + 1
    rng = random.Random(7)
    order = {"swaps": []}
    for b in (10, 30):
        kept = [(d, " ".join(s.split()[:b])) for d, s in picked]
        shuffled = []
        for _, q in kept:
            w = q.split(); rng.shuffle(w); shuffled.append(" ".join(w))
        A = model.encode([q for _, q in kept], batch_size=128, normalize_embeddings=True)
        Bv = model.encode(shuffled, batch_size=128, normalize_embeddings=True)
        cos = (A * Bv).sum(1); other = (A * np.roll(A, 1, axis=0)).sum(1)
        before = np.array([rank_dense(a, d) for a, (d, _) in zip(A, kept)])
        after = np.array([rank_dense(x, d) for x, (d, _) in zip(Bv, kept)])
        order[b] = {"medianCos": round(float(np.median(cos)), 3), "above08": round(float((cos > 0.8).mean()), 3),
                    "otherHeroes": round(float(np.median(other)), 3),
                    "top5Before": round(float((before <= 5).mean()), 3), "top5After": round(float((after <= 5).mean()), 3),
                    "sameRank": round(float((before == after).mean()), 3),
                    "example": {"title": docs[kept[0][0]]["title"], "text": kept[0][1], "shuffled": shuffled[0]}}
    for a_, b_ in [("Peter Parker was bitten by a spider", "A spider was bitten by Peter Parker"),
                   ("Wolverine killed his father", "His father killed Wolverine"),
                   ("Banner turns into the Hulk", "The Hulk turns into Banner"),
                   ("Fury recruited Captain America", "Captain America recruited Fury")]:
        e = model.encode([a_, b_], normalize_embeddings=True)
        order["swaps"].append({"a": a_, "b": b_, "cos": round(float(e[0] @ e[1]), 3)})

    def no_names(s):
        return " ".join(w for w in s.split() if not (w[:1].isupper() or w.lower().startswith("someone")))
    neighbours = {"budgets": [10, 5, 3], "withNames": {}, "noNames": {}, "cases": []}
    for label, transform in (("withNames", lambda s: s), ("noNames", no_names)):
        for b in neighbours["budgets"]:
            kept = [(d, " ".join(transform(s).split()[:b])) for d, s in picked]
            kept = [(d, q) for d, q in kept if q]
            Ek = model.encode([q for _, q in kept], batch_size=256, normalize_embeddings=True)
            cells = {"keyword": [0, 0], "semantic": [0, 0]}
            for (d, q), e in zip(kept, Ek):
                best = np.full(n, -np.inf); np.maximum.at(best, owners, V @ e)
                for method, top in (("keyword", keyword_top(q)), ("semantic", int(np.argmax(best)))):
                    if top is None or top == d:
                        continue
                    linked = frozenset((d, top)) in links
                    cells[method][0] += 1; cells[method][1] += linked
                    if label == "noNames" and method == "semantic" and b == 5 and linked:
                        neighbours["cases"].append({"hero": docs[d]["title"], "words": q, "guess": docs[top]["title"]})
            neighbours[label][b] = cells

    def ranks_of(s):
        o = np.argsort(-s, kind="stable"); r = np.empty(n, int); r[o] = np.arange(1, n + 1); return r
    def keyword_scores(q):
        w = weights(q)
        v = np.zeros(len(vocab)); v[list(w)] = list(w.values())
        return M @ v
    titles = [doc["title"] for doc in docs]
    described = [line.split("\t") for line in (HERE / "descriptions.tsv").read_text().splitlines()
                 if line and not line.startswith("#")]
    merge = {"weights": [0.5, 0.7, 0.9], "sets": []}
    for label, kept in (("10 words from the hero's story, names kept", [(d, " ".join(s.split()[:10])) for d, s in picked]),
                        ("5 words, every name removed", [(d, " ".join(no_names(s).split()[:5])) for d, s in picked if no_names(s)]),
                        (f"{len(described)} descriptions written by us", [(titles.index(h), q) for h, q in described])):
        Ek = model.encode([q for _, q in kept], batch_size=256, normalize_embeddings=True)
        hit = {"keyword": [], "meaning": [], **{str(w): [] for w in merge["weights"]}}
        for (d, q), e in zip(kept, Ek):
            ks = keyword_scores(q); best = np.full(n, -np.inf); np.maximum.at(best, owners, V @ e)
            rk = ranks_of(ks) if ks.max() > 0 else np.full(n, n); rm = ranks_of(best)
            hit["keyword"].append(bool(rk[d] <= 5 and ks[d] > 0)); hit["meaning"].append(bool(rm[d] <= 5))
            for w in merge["weights"]:
                hit[str(w)].append(bool(ranks_of(w / (60 + rk) + (1 - w) / (60 + rm))[d] <= 5))
        kw = np.array(hit["keyword"])
        merge["sets"].append({"label": label, "n": len(kept),
            "top5": {k: round(float(np.mean(v)), 3) for k, v in hit.items()},
            "vsKeyword": {str(w): {"gains": int((np.array(hit[str(w)]) & ~kw).sum()), "losses": int((~np.array(hit[str(w)]) & kw).sum())} for w in merge["weights"]}})

    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(tuple(e) for e in links)
    hops = dict(nx.all_pairs_shortest_path_length(G))
    community = {v: i for i, c in enumerate(louvain_communities(G, seed=42)) for v in c}
    hop = lambda a, b: min(hops[a].get(b, 4), 4)  # 4 means "4 or more" (or unreachable)
    all_pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    base_hops = Counter(hop(a, b) for a, b in all_pairs)
    checks = {"randomHops": [round(base_hops[h] / len(all_pairs), 3) for h in (1, 2, 3, 4)],
              "randomCommunity": round(float(np.mean([community[a] == community[b] for a, b in all_pairs])), 3),
              "communities": len(set(community.values())), "budget": 5, "runs": {}}
    nlp = spacy.load("en_core_web_sm")
    def ner_strip(s):
        doc = nlp(s); ent = {tok.i for e in doc.ents for tok in e}
        return " ".join(tok.text for tok in doc if tok.i not in ent and tok.text.lower() != "someone")
    def unit_vectors(unit):
        if unit == "page":
            X = np.fromfile(DATA / "vectors-page.bin", dtype="i1").astype("f4").reshape(n, -1); own = np.arange(n)
        else:
            ps = json.loads((DATA / f"passages-{unit}.json").read_text()); own = np.array([q["doc"] for q in ps])
            X = np.fromfile(DATA / f"vectors-{unit}.bin", dtype="i1").astype("f4").reshape(len(ps), -1)
        return X / np.linalg.norm(X, axis=1, keepdims=True), own
    for key, unit, strip in (("60", "60", no_names), ("180", "180", no_names), ("page", "page", no_names), ("60-ner", "60", ner_strip)):
        X, own = unit_vectors(unit)
        kept = [(d, " ".join(strip(s).split()[:5])) for d, s in picked]
        kept = [(d, q) for d, q in kept if q]
        Ek = model.encode([q for _, q in kept], batch_size=256, normalize_embeddings=True)
        h, same = Counter(), 0
        for (d, q), e in zip(kept, Ek):
            best = np.full(n, -np.inf); np.maximum.at(best, own, X @ e); top = int(np.argmax(best))
            if top != d:
                h[hop(d, top)] += 1; same += community[d] == community[top]
        misses = sum(h.values())
        checks["runs"][key] = {"misses": misses, "hops": [round(h[k] / misses, 3) for k in (1, 2, 3, 4)],
                               "sameCommunity": round(same / misses, 3)}

    df = Counter(i for idx, _ in lex["rows"] for i in idx)
    per_page = [[i for i in idx if df[i] == 1] for idx, _ in lex["rows"]]
    names = total = 0
    for d, unique in enumerate(per_page):
        for i in unique:
            occ = re.findall(rf"\b{re.escape(lex['vocab'][i])}\b", docs[d]["text"], flags=re.I)
            if occ:
                total += 1; names += sum(o[0].isupper() for o in occ) / len(occ) >= 0.8
    def examples(title):
        d = next(k for k, doc in enumerate(docs) if doc["title"] == title)
        weight = dict(zip(*lex["rows"][d]))
        return {"title": title, "count": len(per_page[d]),
                "words": [lex["vocab"][i] for i in sorted(per_page[d], key=lambda i: -weight[i])[:8]]}
    length = np.array([len(doc["text"].split()) for doc in docs])
    short, long_ = np.percentile(length, 10), np.percentile(length, 90)
    def magnet(b, method):
        pages, passages = magnets[b][method]
        total = sum(pages.values())
        guessed = np.array([length[k] for k in pages.elements()])
        top = pages.most_common(5)
        out = {"misses": total, "medianWords": float(np.median(guessed)),
               "shortest10": round(sum(v for k, v in pages.items() if length[k] <= short) / total, 3),
               "longest10": round(sum(v for k, v in pages.items() if length[k] >= long_) / total, 3),
               "top": [{"title": docs[k]["title"], "count": v, "words": int(length[k])} for k, v in top]}
        if passages:
            out["tinyWins"] = round(sum(v for pi, v in passages.items() if len(texts_60[pi].split()) <= TINY) / total, 3)
            pi, wins = passages.most_common(1)[0]
            out["passage"] = {"title": docs[owners[pi]]["title"], "wins": wins, "text": texts_60[pi]}
        else:
            k = top[0][0]
            out["passage"] = {"title": docs[k]["title"], "wins": top[0][1], "text": " ".join(docs[k]["text"].split()[:70]) + " …"}
        return out
    magnet_out = {"tiny": [{"title": docs[owners[i]]["title"], "text": s} for i, s in enumerate(texts_60) if len(s.split()) <= TINY],
                  "passages": len(texts_60), "corpusMedianWords": float(np.median(length)), "shortestCut": float(short), "longestCut": float(long_),
                  "budgets": {b: {m: magnet(b, m) for m in ("keyword", "semantic")} for b in (10, 3, 1)}}
    fingerprints = {"vocabulary": len(vocab), "unique": sum(1 for v in df.values() if v == 1),
                    "pages": int(sum(1 for u in per_page if u)), "median": float(np.median([len(u) for u in per_page])),
                    "nameShare": round(names / total, 3), "examples": [examples(h) for h in HEROES]}

    def summary(values):
        v = np.array(values)
        return {"median": float(np.median(v)), "q1": float(np.percentile(v, 25)), "q3": float(np.percentile(v, 75)),
                "top5": round(float((v <= 5).mean()), 3)}

    out = {"articles": len(picked), "documents": n, "budgets": BUDGETS, "banned": BANNED, "unit": "60",
           "rules": {rule: {method: [summary(ranks[rule][b][method]) for b in BUDGETS] for method in ("keyword", "semantic")}
                     for rule in ranks},
           "neighbours": neighbours,
           "checks": checks,
           "merge": merge,
           "order": order,
           "fingerprints": fingerprints,
           "magnets": magnet_out,
           "drift": {"density": round(2 * len(links) / (n * (n - 1)), 4),
                     "rules": {rule: {method: [drift[rule][b][method] for b in BUDGETS] for method in ("keyword", "semantic")}
                               for rule in drift}},
           "example": {"title": docs[picked[0][0]]["title"], "sentence": picked[0][1],
                       "squeezed": {rule: {b: squeeze(picked[0][1], rule, b) for b in (10, 3)} for rule in ("first", "rarest", "taboo")}}}
    (DATA / "squeeze-evidence.json").write_text(json.dumps(out, separators=(",", ":")))
    for rule in ("first", "rarest", "taboo"):
        print(rule, {m: [round(s["median"]) for s in out["rules"][rule][m]] for m in ("keyword", "semantic")})
        print("   top5", {m: [s["top5"] for s in out["rules"][rule][m]] for m in ("keyword", "semantic")})
    for b in (10, 3, 1):
        for m in ("keyword", "semantic"):
            g = magnet_out["budgets"][b][m]
            print("magnets", b, m, g.get("tinyWins"), g["misses"], g["medianWords"], g["shortest10"], g["longest10"], [(x["title"], x["count"]) for x in g["top"][:3]], "| passage:", g["passage"]["title"], g["passage"]["wins"], g["passage"]["text"][:160])
    print("merge", json.dumps(merge))
    print("checks", checks)
    print("neighbours", {k: neighbours[k] for k in ("withNames", "noNames")}, "cases", len(neighbours["cases"]))
    print("order", {b: {k: v for k, v in order[b].items() if k != "example"} for b in (10, 30)}, [(s["b"], s["cos"]) for s in order["swaps"]])
    print("fingerprints", {k: v for k, v in fingerprints.items() if k != "examples"})
    print("drift first-rule (misses, linked)", out["drift"]["rules"]["first"], "density", out["drift"]["density"])
    print(f"{len(picked)} articles; wrote dist/data/squeeze-evidence.json")


if __name__ == "__main__":
    main()
