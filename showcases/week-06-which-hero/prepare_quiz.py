"""Prepare the data for the "Which Marvel hero do you sound like?" Week 6 quiz.

Each page becomes a TF-IDF vector (exercise 6.2). The reader's ten answers become a
tiny query vector, and the page with the highest cosine similarity is "you".

Input:  notebooks/data/marvel_pages.zip
Output: showcases/week-06-which-hero/quiz-data.js

Run from the repository root:
    python showcases/week-06-which-hero/prepare_quiz.py

Only the Python standard library is used.

  tokens   lower-case runs of letters, so "Spider-Man" becomes "spider" + "man"
  tf       1 + log(count), so a word said 40 times does not count 40 times as much
  idf      log(N / df); words on fewer than 2 pages are dropped
  page     each page vector is L2-normalised; the page keeps only the weights of the
           quiz words (enough to score any answer set) plus its own top TF-IDF words
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
OUT = Path(__file__).with_name("quiz-data.js")

# question, then (word scored, label shown)
QUESTIONS = [
    ("Your powers come from…", [("radiation", "radiation"), ("mutation", "a mutation"), ("magic", "magic"), ("technology", "technology")]),
    ("In a fight, you rely on your…", [("claws", "claws"), ("armor", "armor"), ("telepathy", "telepathy"), ("shield", "shield")]),
    ("Your story keeps returning to…", [("asgard", "Asgard"), ("wakanda", "Wakanda"), ("harlem", "Harlem"), ("space", "outer space")]),
    ("Your worst enemy is a…", [("vampire", "vampire"), ("demon", "demon"), ("alien", "alien"), ("gang", "street gang")]),
    ("You would join the…", [("avengers", "Avengers"), ("defenders", "Defenders"), ("guardians", "Guardians"), ("inhumans", "Inhumans")]),
    ("Your Wikipedia page keeps mentioning your…", [("husband", "husband"), ("wife", "wife"), ("daughter", "daughter"), ("father", "father")]),
    ("It all started with…", [("laboratory", "a lab"), ("experiment", "an experiment"), ("accident", "an accident"), ("curse", "a curse")]),
    ("Officially, you are a…", [("vigilante", "vigilante"), ("mercenary", "mercenary"), ("soldier", "soldier"), ("sorcerer", "sorcerer")]),
    ("What drives you is…", [("rage", "rage"), ("grief", "grief"), ("memory", "memory"), ("guilt", "guilt")]),
    ("Your adventures are mostly…", [("cosmic", "cosmic"), ("street", "on the street"), ("ancient", "ancient"), ("dimension", "in another dimension")]),
]
TOP_WORDS = 8
TOKEN = re.compile(r"[a-z]+")


def load_pages():
    pages = {}
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if name.endswith(".txt") and not name.startswith("README"):
                pages[urllib.parse.unquote(name[:-4]).replace("_", " ")] = z.read(info).decode("utf-8")
    return dict(sorted(pages.items()))


def sentence_with(text, word):
    """The first sentence on the page that contains the word, trimmed around it."""
    m = re.search(r"(?i)\b" + word + r"\b", text)
    if not m:
        return None
    start = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start())) + 1
    end_dot = text.find(".", m.end())
    end = len(text) if end_dot < 0 else end_dot + 1
    s, e = m.start() - start, m.end() - start
    sent = re.sub(r"\s+", " ", text[start:end]).strip()
    # re-find inside the cleaned sentence and keep at most ~90 characters each side
    m2 = re.search(r"(?i)\b" + word + r"\b", sent)
    s, e = m2.start(), m2.end()
    left, right = sent[max(0, s - 90):s], sent[e:e + 90]
    return [("…" if s > 90 else "") + left, sent[s:e], right + ("…" if e + 90 < len(sent) else "")]


def main():
    pages = load_pages()
    counts = {t: Counter(TOKEN.findall(x.lower())) for t, x in pages.items()}
    n = len(pages)
    df = Counter(w for c in counts.values() for w in c)
    idf = {w: math.log(n / d) for w, d in df.items() if d >= 2}
    quiz_words = [w for _, opts in QUESTIONS for w, _ in opts]
    missing = [w for w in quiz_words if w not in idf]
    assert not missing, f"quiz words missing from the corpus: {missing}"

    out_pages = []
    for title, c in counts.items():
        vec = {w: (1 + math.log(k)) * idf[w] for w, k in c.items() if w in idf}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1
        weights = {}
        for w in quiz_words:
            if w in vec:
                weights[w] = [round(vec[w] / norm, 5), sentence_with(pages[title], w)]
        top = sorted(vec.items(), key=lambda kv: -kv[1])[:TOP_WORDS]
        out_pages.append({"t": title, "words": len(TOKEN.findall(pages[title].lower())), "q": weights, "top": [w for w, _ in top]})

    data = {
        "pages": n,
        "questions": [{"q": q, "options": [{"w": w, "label": l} for w, l in opts]} for q, opts in QUESTIONS],
        "idf": {w: round(idf[w], 4) for w in quiz_words},
        "df": {w: df[w] for w in quiz_words},
        "heroes": out_pages,
    }
    OUT.write_text("// Generated by prepare_quiz.py. Do not edit by hand.\nwindow.QUIZ = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    def match(answer):
        u = {w: idf[w] for w in answer}
        un = math.sqrt(sum(v * v for v in u.values()))
        scores = [(sum(u[w] * p["q"].get(w, [0])[0] for w in u) / un, p["t"]) for p in out_pages]
        return sorted(scores, reverse=True)[:3]

    print(f"{n} pages, {len(quiz_words)} quiz words -> {OUT.relative_to(ROOT)}")
    for answer in (["mutation", "claws", "space", "alien", "avengers", "wife", "experiment", "soldier", "rage", "street"],
                   ["magic", "shield", "asgard", "demon", "avengers", "father", "curse", "sorcerer", "guilt", "ancient"]):
        print(answer[:3], [(round(s, 3), t) for s, t in match(answer)])
    print("top TF-IDF words, Storm:", next(p["top"] for p in out_pages if p["t"] == "Storm (Marvel Comics)"))


if __name__ == "__main__":
    main()
