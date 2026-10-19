"""Prepare the data for "The Marvel Type Indicator" (Week 6).

Four axes, each built from two word groups we chose (exercise 6.9.6 / suggested question 7:
"build two axes with your own word groupings ... validate characters at axis ends"):

  C / S   Cosmic   vs Street
  T / A   Tech     vs Arcane
  B / F   Born     vs Forged   (born different vs made by an accident, experiment, serum)
  E / L   Ensemble vs Lone

For each page and axis: raw = (A - B) / (A + B + K), where A and B are the TF-IDF weights of each
group's words on the page, sum of count x idf (exercise 6.2): a word on few pages ("galactus") counts
more than a word on many ("city"). K = 3 x the mean idf of the axis words keeps a page with one stray
word near the middle. Pages are then ranked on every axis and
split at the median, so each axis is close to 50/50, and each page gets a 4-letter type. Tied pages
share their average rank. A page where neither word group appears on an axis has no evidence there;
the page shows that letter as a guess.

Input:  notebooks/data/marvel_pages.zip
Output: showcases/week-06-marvel-words/types-data.js
Run from the repository root:
    python showcases/week-06-marvel-words/prepare_types.py
Only the Python standard library is used.
"""

from collections import Counter
from pathlib import Path
import json
import math
import re
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "notebooks" / "data" / "marvel_pages.zip"
OUT = Path(__file__).with_name("types-data.js")

AXES = [
    {"pos": "C", "neg": "S", "posName": "Cosmic", "negName": "Street",
     "posWords": "space cosmic galaxy planet planets alien aliens stars kree skrull galactus celestial celestials interstellar orbit",  # not "universe": 944 of 1,435 uses are franchise names such as "Marvel Cinematic Universe"
     "negWords": "street streets city gang gangs crime crimes criminal criminals police neighborhood harlem mob drug drugs detective cop cops"},
    {"pos": "T", "neg": "A", "posName": "Tech", "negName": "Arcane",
     "posWords": "science scientist technology laboratory lab armor robot robotic suit engineer engineering computer cybernetic cyborg invention invented",
     "negWords": "magic magical sorcerer sorceress mystic mystical spell spells demon demons curse cursed supernatural sorcery occult witch vampire vampires"},
    {"pos": "B", "neg": "F", "posName": "Born", "negName": "Forged",
     "posWords": "mutant mutants mutation inherited genetic gene genes heritage bloodline descendant lineage inhuman inhumans",
     "negWords": "accident serum exposed injected experiment experiments experimented chemical chemicals radiation radioactive transformed procedure enhanced augmented implanted"},
    {"pos": "E", "neg": "L", "posName": "Ensemble", "negName": "Lone",
     "posWords": "team teams teammates teammate avengers members member joined squad defenders alliance guardians",
     "negWords": "alone solo vigilante vigilantes loner independent lone isolated outcast rogue mercenary freelance"},
]
EXTREMES = 6
TOKEN = re.compile(r"[a-z]+")


def load_pages():
    pages = {}
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if name.endswith(".txt") and not name.startswith("README"):
                pages[urllib.parse.unquote(name[:-4]).replace("_", " ")] = z.read(info).decode("utf-8")
    return dict(sorted(pages.items()))


def best_sentence(text, words, idf):
    """The most informative sentence for one side of an axis.

    Candidates are sentences of 50 to 210 characters that contain at least one of the side's words.
    Score = sum of the idf of the distinct side words in the sentence, so a sentence with a rare word
    ("galactus") beats one with a common word ("city"). Shorter wins ties.
    """
    wordset = {w.lower() for w in words}
    best, best_score = None, 0.0
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        sent = re.sub(r"\s+", " ", sent).strip()
        if not 50 <= len(sent) <= 210 or sent.count("(") > 1 or re.search(r"https?:|#\d{2,}", sent):
            continue
        found = {m.group(0).lower() for m in re.finditer(r"[A-Za-z]+", sent) if m.group(0).lower() in wordset}
        if not found:
            continue
        score = sum(idf.get(w, 0) for w in found) - len(sent) / 400
        if score > best_score:
            best, best_score = sent, score
    if not best:
        return None
    hits = [m for m in re.finditer(r"[A-Za-z]+", best) if m.group(0).lower() in wordset]
    m = max(hits, key=lambda m: idf.get(m.group(0).lower(), 0))
    return [best[:m.start()], best[m.start():m.end()], best[m.end():]]


def main():
    pages = load_pages()
    counts = {t: Counter(TOKEN.findall(x.lower())) for t, x in pages.items()}
    titles = list(pages)
    n = len(titles)
    groups = [(a["posWords"].split(), a["negWords"].split()) for a in AXES]

    df = Counter(w for c in counts.values() for w in set(c))
    idf = {w: round(math.log(n / df[w]), 4) if df[w] else 0 for pos, neg in groups for w in pos + neg}
    kk = [3 * sum(idf[w] for w in pos + neg) / len(pos + neg) for pos, neg in groups]
    raw, hits = {}, {}
    for t, c in counts.items():
        raw[t], hits[t] = [], []
        for k, (pos, neg) in enumerate(groups):
            A, B = sum(c[w] * idf[w] for w in pos), sum(c[w] * idf[w] for w in neg)
            raw[t].append((A - B) / (A + B + kk[k]))
            hits[t].append([sum(c[w] for w in pos), sum(c[w] for w in neg)])

    # rank every axis and split at the median: pct 0-100 toward the first pole, >= 50 means first letter
    pct = {t: [0] * len(AXES) for t in titles}
    axes_out = []
    for k, a in enumerate(AXES):
        order = sorted(titles, key=lambda t: (raw[t][k], t))
        # tied pages share their average rank, so a tie is never broken by alphabetical order
        i = 0
        while i < n:
            j = i
            while j + 1 < n and raw[order[j + 1]][k] == raw[order[i]][k]:
                j += 1
            for t in order[i:j + 1]:
                pct[t][k] = round(100 * ((i + j) / 2) / (n - 1))
            i = j + 1
        axes_out.append({**{key: a[key] for key in ("pos", "neg", "posName", "negName")},
                         "posWords": groups[k][0], "negWords": groups[k][1],
                         "mostPos": order[-EXTREMES:][::-1], "mostNeg": order[:EXTREMES]})

    heroes = []
    for t in titles:
        code = "".join(AXES[k]["pos"] if pct[t][k] >= 50 else AXES[k]["neg"] for k in range(len(AXES)))
        evidence = []
        for k, (pos, neg) in enumerate(groups):
            side = pos if pct[t][k] >= 50 else neg
            evidence.append(best_sentence(pages[t], side, idf))
        # raw counts of every axis word on this page, so the browser can rebuild the axes live
        wc = {w: counts[t][w] for pos, neg in groups for w in pos + neg if counts[t][w]}
        heroes.append({"t": t, "pct": pct[t], "code": code, "hits": hits[t], "ev": evidence, "wc": wc, "uni": counts[t]["universe"]})

    # "universe" was dropped from the Cosmic words (mostly franchise names); kept here so the page can show its effect
    data = {"pages": n, "axes": axes_out, "heroes": heroes, "idf": idf, "df": {w: df[w] for w in idf}, "k": kk,
            "uniIdf": round(math.log(n / df["universe"]), 4)}
    OUT.write_text("// Generated by prepare_types.py. Do not edit by hand.\nwindow.TYPES = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    print(f"{n} pages -> {OUT.relative_to(ROOT)}")
    print("types:", sorted(Counter(h["code"] for h in heroes).items(), key=lambda kv: -kv[1]))
    for a in axes_out:
        print(f"{a['posName']:>8s}: {a['mostPos'][:4]}  |  {a['negName']}: {a['mostNeg'][:4]}")
    print("no evidence on an axis (both groups absent):", sum(1 for h in heroes for A, B in h["hits"] if A + B == 0), "of", n * len(AXES))


if __name__ == "__main__":
    main()
