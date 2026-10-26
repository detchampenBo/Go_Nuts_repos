"""Prepare the data for "Nominative Determinism" (Week 7, exercise 7.13).

Question: why does semantic (dense) search fail to find Spider-Man, and who does it find instead?

1. Every page is cut into 180-word chunks (all-MiniLM-L6-v2 reads at most 256 word pieces); the chunk vectors
   are averaged into one page vector, as in the course's corpus atlas.
2. 56 test descriptions in queries.tsv, written from memory before seeing results, never use the hero's name.
   Each is ranked against all 303 pages by keyword search (TF-IDF, sublinear tf, English stop words) and by
   meaning (cosine to the page vector). The rank of the right page is stored.
3. Name test: the hero's name as written (case-sensitive whole phrases: "Black Cat", "Spider-Man", and for
   "Ghost Rider (Johnny Blaze)" also "Johnny Blaze") is replaced by "X" on that hero's own page, so "cat burglar"
   or "radioactive spider" stay untouched. The masked corpus is embedded again. Re-ranking with only the target's
   page masked, or with every page masked except the target's, separates "my own name helped me" from
   "other heroes' names beat me".
4. Each bare name, and each word of the names shown in the results lists, is embedded on its own, so the page can
   mark the word the model "hears" (e.g. RED in Red Guardian for "russian spy trained in the red room").
5. For the in-browser rename tool: the page vectors (float32) and the full text of every hero in queries.tsv.

Input:  notebooks/data/marvel_pages.zip, showcases/week-07-cant-find-spider-man/queries.tsv
Output: names-data.js, pages.bin, rename-texts.json (next to this file)
Run from the repository root (first run downloads the model):
    python showcases/week-07-cant-find-spider-man/prepare_names.py
"""

from pathlib import Path
import json
import re
import urllib.parse
import zipfile

import numpy as np
from scipy.stats import spearmanr
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ZIP = ROOT / "notebooks" / "data" / "marvel_pages.zip"
QUERIES = HERE / "queries.tsv"
OUT = HERE / "names-data.js"

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_WORDS = 180
TOP = 8
# Parentheticals in titles that disambiguate rather than name: "(Marvel Comics)", "(character)", "(X-Men film series)".
GENERIC = {"the", "of", "and", "a", "marvel", "comics", "character", "characters", "new", "universe",
           "film", "series", "x-men", "ultimate"}
SUFFIX = re.compile(r"\s*\((Marvel Comics|character|characters|comics)\)$")


def display_name(node_id):
    return SUFFIX.sub("", node_id.replace("_", " "))


def name_phrases(node_id):
    """The ways a page names its hero: the title without its parenthetical, plus a parenthetical that is a name."""
    title = node_id.replace("_", " ")
    phrases = [re.sub(r"\s*\([^)]*\)", "", title).strip()]
    for inner in re.findall(r"\(([^)]*)\)", title):
        if not set(inner.lower().split()) <= GENERIC:
            phrases.append(inner)
    return sorted(set(p for p in phrases if p), key=len, reverse=True)


def rename(node_id, text, new="X"):
    for p in name_phrases(node_id):
        text = re.sub(r"(?<![\w-])" + re.escape(p) + r"(?![\w-])", new, text)
    return text


def page_vectors(model, texts):
    chunks, owner = [], []
    for i, t in enumerate(texts):
        w = t.split()
        for s in range(0, len(w), CHUNK_WORDS):
            chunks.append(" ".join(w[s:s + CHUNK_WORDS]))
            owner.append(i)
    E = model.encode(chunks, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    owner = np.array(owner)
    X = np.stack([E[owner == i].mean(0) for i in range(len(texts))])
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def rank_of(scores, own):
    """1 + number of other pages scoring strictly higher than `own`."""
    return int((scores > own).sum()) + 1


def main():
    z = zipfile.ZipFile(ZIP)
    files = {urllib.parse.unquote(Path(n).stem): n for n in z.namelist() if n.endswith(".txt") and "README" not in n}
    ids = sorted(files)
    texts = [z.read(files[i]).decode("utf-8", "ignore") for i in ids]
    queries = [line.rstrip("\n").split("\t") for line in QUERIES.read_text(encoding="utf-8").splitlines()
               if line and not line.startswith(("#", "hero_id"))]
    missing = [h for h, _ in queries if h not in ids]
    assert not missing, f"unknown hero ids in queries.tsv: {missing}"

    model = SentenceTransformer(MODEL)
    P = page_vectors(model, texts)
    PM = page_vectors(model, [rename(i, t) for i, t in zip(ids, texts)])
    N = model.encode([display_name(i) for i in ids], normalize_embeddings=True, show_progress_bar=False)
    tfidf = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    T = tfidf.fit_transform(texts)

    word_cache = {}

    def heard(j, v):
        """Each word of page j's display name with its cosine to the query vector v."""
        words = [w for w in re.split(r"[\s\-]+", re.sub(r"[()]", "", display_name(ids[j]))) if w]
        for w in words:
            if w not in word_cache:
                word_cache[w] = model.encode(w, normalize_embeddings=True, show_progress_bar=False)
        return [[w, round(float(word_cache[w] @ v), 3)] for w in words]

    out, fit, effect, rhos = [], [], [], []
    for hero, q in queries:
        i = ids.index(hero)
        v = model.encode(q, normalize_embeddings=True)
        kw = (T @ tfidf.transform([q]).T).toarray().ravel()
        dense, masked, name_sim = P @ v, PM @ v, N @ v
        top_kw, top_dense = np.argsort(-kw)[:TOP], np.argsort(-dense)[:TOP]
        r = {
            "hero": i, "q": q,
            "kw": rank_of(kw, kw[i]),
            "dense": rank_of(dense, dense[i]),
            "ownHidden": rank_of(np.delete(dense, i), masked[i]),          # only the target's own name removed
            "rivalsHidden": rank_of(np.delete(masked, i), dense[i]),       # every other page's name removed
            "topKw": [int(j) for j in top_kw], "kwTopScores": [round(float(kw[j]), 4) for j in top_kw],
            "kwScore": round(float(kw[i]), 4),
            "topDense": [int(j) for j in top_dense], "denseTopScores": [round(float(dense[j]), 4) for j in top_dense],
            "denseScore": round(float(dense[i]), 4),
            "nameSim": round(float(name_sim[i]), 3), "winnerNameSim": round(float(name_sim[top_dense[0]]), 3),
            "words": {str(j): heard(j, v) for j in set(int(x) for x in top_dense) | {i}},
        }
        out.append(r)
        fit.append(name_sim[i])
        effect.append(np.log(r["ownHidden"]) - np.log(r["dense"]))
        rhos.append(spearmanr(name_sim, dense)[0])

    col = lambda k: np.array([r[k] for r in out])
    stats = {
        "pages": len(ids), "queries": len(out), "model": MODEL, "chunkWords": CHUNK_WORDS,
        "medianKw": float(np.median(col("kw"))), "medianDense": float(np.median(col("dense"))),
        "medianOwnHidden": float(np.median(col("ownHidden"))), "medianRivalsHidden": float(np.median(col("rivalsHidden"))),
        "top5Kw": int((col("kw") <= 5).sum()), "top5Dense": int((col("dense") <= 5).sum()),
        "rhoFitEffect": round(float(spearmanr(fit, effect)[0]), 2),
        "medianRhoNamePage": round(float(np.median(rhos)), 2),
    }
    heroes = sorted({i for i in (r["hero"] for r in out)})
    data = {"stats": stats, "names": [display_name(i) for i in ids], "queries": out,
            "phrases": {str(i): name_phrases(ids[i]) for i in heroes}}
    OUT.write_text("// Generated by prepare_names.py. Do not edit by hand.\nwindow.NAMES = "
                   + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    P.astype("<f4").tofile(HERE / "pages.bin")
    (HERE / "rename-texts.json").write_text(json.dumps({str(i): texts[i] for i in heroes}, ensure_ascii=False),
                                            encoding="utf-8")
    print(json.dumps(stats, indent=2))
    for f in (OUT, HERE / "pages.bin", HERE / "rename-texts.json"):
        print(f"wrote {f.relative_to(ROOT)} ({f.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
