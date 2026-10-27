"""Who is the centre of the Marvel universe: by the hyperlinks, and by the text? Run from the repo root with
.venv/bin/python (about 5 minutes on a laptop CPU).

Text:      each of the 303 pages, up to its references, is cut into ~120-word chunks; MiniLM (all-MiniLM-L6-v2) embeds
           every chunk; a page vector is the normalized mean of its chunk vectors.
Links:     week-1 hyperlinks, undirected; a page's degree is its number of linked pages.
Picked:    every page picks the K=10 pages whose vectors are most similar (cosine). A page's k-occurrence is how many
           pages picked it. In a space without hubs that would be about 10 for everyone.
Controls:  the same count on 303 random unit vectors of the same dimension (seed 0), and after centring (the mean page
           vector subtracted from every vector before cosine), the usual fix for hubness.
Checks:    k = 5 and 20, and the text with every capitalised word removed and she/he/... replaced by "they".
Retrieval: every chunk is used as a query against the other 302 page vectors; how often each page lands in the top 5,
           raw and centred, and how often a chunk still finds its own page in the top 5.
Map:       t-SNE (cosine, perplexity 30, seed 0) places the pages; random vectors get their own t-SNE map.
Per page:  its "most average passage" (the chunk closest to the mean page vector) and how many of the other 302 titles
           its text names, so the page can show why a page sits near the middle.
"""
import json
import re
import urllib.parse
import warnings
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import orthogonal_procrustes
from scipy.stats import spearmanr
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE

warnings.filterwarnings("ignore", category=RuntimeWarning)  # spurious matmul overflow warnings from numpy 2 + Accelerate

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "notebooks" / "data"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK, K = 120, 10
STOP_HEADINGS = {"references", "external links", "see also", "notes", "further reading", "bibliography"}
PRONOUNS = re.compile(r"\b(she|he|her|hers|his|him|herself|himself)\b", re.I)


def load():
    archive = zipfile.ZipFile(DATA / "marvel_pages.zip")
    files = {urllib.parse.unquote(Path(n).stem): n for n in archive.namelist() if n.endswith(".txt") and "README" not in n}
    nodes = [l.split("\t") for l in (DATA / "week1_nodes.tsv").read_text().splitlines() if l and not l.startswith("#")][1:]
    ids = [r[0] for r in nodes]
    titles = [re.sub(r" \((Marvel Comics|character|comics)\)$", "", r[1]) for r in nodes]
    texts = []
    for i in ids:
        lines = []
        for line in archive.read(files[i]).decode("utf-8", "replace").splitlines():
            if line.strip().lower() in STOP_HEADINGS:
                break
            lines.append(line)
        texts.append("\n".join(lines))
    index = {i: k for k, i in enumerate(ids)}
    links = set()
    for l in (DATA / "week1_edges.tsv").read_text().splitlines():
        if l.startswith("#") or not l.strip():
            continue
        a, b = l.split("\t")[:2]
        if a in index and b in index and a != b:
            links.add(tuple(sorted((index[a], index[b]))))
    return ids, titles, texts, sorted(links)


def chunks(text):
    """Sentences packed into chunks of at most CHUNK words (a longer sentence is its own chunk; MiniLM truncates)."""
    out, cur = [], []
    for s in re.split(r"(?<=[.!?])\s+|\n+", text):
        w = s.split()
        if cur and len(cur) + len(w) > CHUNK:
            out.append(" ".join(cur)); cur = []
        cur += w
    if cur:
        out.append(" ".join(cur))
    return [c for c in out if len(c.split()) >= 8] or [text[:600]]


def unit(V):
    return V / np.linalg.norm(V, axis=1, keepdims=True)


def picks(V, k=K):
    """Each row's k most similar other rows, and how often each row is picked."""
    S = V @ V.T; np.fill_diagonal(S, -np.inf)
    nn = np.argsort(-S, axis=1)[:, :k]
    return nn, np.bincount(nn.ravel(), minlength=len(V))


def main():
    ids, titles, texts, links = load()
    n = len(ids)
    deg = np.zeros(n, int)
    for a, b in links:
        deg[a] += 1; deg[b] += 1
    model = SentenceTransformer(MODEL, local_files_only=True, device="cpu")

    def embed(version):
        pc = [chunks(version(t)) for t in texts]
        flat = [c for cs in pc for c in cs]
        owner = np.array([k for k, cs in enumerate(pc) for _ in cs])
        C = model.encode(flat, batch_size=64, normalize_embeddings=True)
        X = np.zeros((n, C.shape[1])); np.add.at(X, owner, C)
        return unit(X), C, owner, flat

    X, C, owner, flat = embed(lambda t: t)
    mean = X.mean(0)
    Xc = unit(X - mean)
    noise = unit(np.random.default_rng(0).standard_normal(X.shape))
    nn, picked = picks(X)
    nnc, picked_c = picks(Xc)
    nnn, picked_n = picks(noise)
    print("picked: max", picked.max(), "| centred max", picked_c.max(), "| random max", picked_n.max(), flush=True)

    # Robustness: other k, and the text without names or gendered pronouns.
    Xb, *_ = embed(lambda t: PRONOUNS.sub("they", " ".join(w for w in t.split() if not w[:1].isupper())))
    _, picked_b = picks(Xb)
    top = lambda counts, m=5: [{"page": int(i), "picked": int(counts[i])} for i in np.argsort(-counts, kind="stable")[:m]]

    # Retrieval: each chunk queries the other pages (its own page excluded), raw and centred.
    def retrieval(Q, V):
        S = Q @ V.T
        own = S[np.arange(len(Q)), owner].copy()
        finds_own = float(np.mean((S > own[:, None]).sum(1) < 5))
        S[np.arange(len(Q)), owner] = -np.inf
        return np.bincount(np.argsort(-S, axis=1)[:, :5].ravel(), minlength=n), finds_own
    hits, own5 = retrieval(C, X)
    hits_c, own5_c = retrieval(unit(C - mean), Xc)

    cos_mean = X @ (mean / np.linalg.norm(mean))
    near_mean = C @ (mean / np.linalg.norm(mean))
    words = np.array([len(t.split()) for t in texts])
    short = [t.split(" (")[0] for t in titles]
    names = np.array([sum(1 for j, s in enumerate(short) if j != i and len(s) > 3 and s in texts[i]) for i in range(n)])
    linkset = set(links)

    def layout(V):
        Y = TSNE(2, perplexity=30, metric="cosine", init="pca", random_state=0).fit_transform(V)
        return Y - Y.mean(0)
    Y = layout(X); Y /= np.abs(Y).max()
    Yn = layout(noise); R, _ = orthogonal_procrustes(Yn, Y); Yn = Yn @ R; Yn /= np.abs(Yn).max()

    nodes = []
    for i in range(n):
        mine = np.flatnonzero(owner == i)
        best = mine[np.argmax(near_mean[mine])]
        nodes.append({"id": ids[i], "title": titles[i], "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(ids[i])}",
                      "deg": int(deg[i]), "words": int(words[i]), "names": int(names[i]),
                      "picked": int(picked[i]), "pickedCentred": int(picked_c[i]), "pickedRandom": int(picked_n[i]),
                      "retrieved": int(hits[i]), "retrievedCentred": int(hits_c[i]), "cosMean": round(float(cos_mean[i]), 3),
                      "nn": nn[i].tolist(), "nnCentred": nnc[i].tolist(), "nnRandom": nnn[i].tolist(),
                      "average": " ".join(flat[best].split()[:70]),
                      "xy": np.round(Y[i], 4).tolist(), "xyRandom": np.round(Yn[i], 4).tolist()})
    rho = lambda a, b: round(float(spearmanr(a, b)[0]), 2)
    hub = int(np.argmax(picked))
    summary = {
        "k": K, "chunks": len(flat), "links": len(links),
        "noOne": int((picked == 0).sum()), "noOneCentred": int((picked_c == 0).sum()), "noOneRandom": int((picked_n == 0).sum()),
        "noOneShorter": int(sum(words[i] < np.median(words) for i in np.flatnonzero(picked == 0))), "medianWords": int(np.median(words)),
        "rhoDegree": rho(picked, deg), "rhoDegreeCentred": rho(picked_c, deg), "rhoMean": rho(picked, cos_mean),
        "rhoWords": rho(picked, words), "rhoNames": rho(picked, names), "medianNames": int(np.median(names)),
        "topLinkedInTopPicked": len(set(np.argsort(-deg)[:10]) & set(np.argsort(-picked)[:10])),
        "hub": hub, "hubFansLinked": int(sum(tuple(sorted((i, hub))) in linkset for i in range(n) if hub in nn[i])),
        "top5": top(picked), "top5k5": top(picks(X, 5)[1]), "top5k20": top(picks(X, 20)[1]), "top5Bare": top(picked_b),
        "retrieval": {"queries": len(C), "medianPage": int(np.median(hits)), "max": int(hits.max()), "hub": int(hits[hub]),
                      "hubCentred": int(hits_c[hub]), "hubPages": int(len(set(owner[np.any(np.argsort(-(C @ X.T - np.eye(n)[owner] * 9), axis=1)[:, :5] == hub, axis=1)]))),
                      "findsOwn": round(own5, 3), "findsOwnCentred": round(own5_c, 3)},
    }
    print(json.dumps(summary, indent=1)[:1500], flush=True)
    out = {"model": MODEL, "chunkWords": CHUNK, "summary": summary, "nodes": nodes, "links": [list(e) for e in links]}
    (HERE / "centre-data.js").write_text("window.CENTRE = " + json.dumps(out, separators=(",", ":")) + ";\n")
    print("wrote centre-data.js", round((HERE / "centre-data.js").stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
