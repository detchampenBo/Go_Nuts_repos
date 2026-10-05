"""Prepare the data for the "Unmasked" Week 5 post.

Question: if you count gender words in the 303 Marvel Wikipedia pages with an
ordinary tokenizer, how many of those "men", "women", "girls" and "she"s are
really hero names such as X-Men, Spider-Woman or She-Hulk?

Input:  notebooks/data/marvel_pages.zip   (one plain-text page per character)
Output: showcases/week-05-unmasked/unmasked-data.js

Run from the repository root:
    python showcases/week-05-unmasked/prepare_unmasked.py

Only the Python standard library is used.

How a mention is classified (case-sensitive, on the raw text):
  real word  the word in lower case, not glued to a hyphen   ("a young man")
  name       glued to a hyphen ("X-Men", "Spider-Man's", "She-Hulk") or
             capitalised right after another capitalised word ("Iron Man")
  other caps any remaining capitalised use, e.g. at the start of a sentence
             or in a title ("Women of Marvel")
The tokenizer count is what a hyphen-splitting tokenizer such as
scikit-learn's CountVectorizer or spaCy sees: every case-insensitive match.
"""

from collections import Counter, defaultdict
from pathlib import Path
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "notebooks" / "data" / "marvel_pages.zip"
OUT = Path(__file__).with_name("unmasked-data.js")

NOUNS = ["man", "woman", "men", "women", "boy", "girl"]
DOT = 10  # one dot in the figure = 10 mentions
TOP_NAMES = 4  # name forms shown separately per word; the rest become "other names"


def load_pages():
    pages = {}
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if not name.endswith(".txt") or name.startswith("README"):
                continue
            title = name[:-4].replace("%3A", ":").replace("_", " ")
            pages[title] = z.read(info).decode("utf-8")
    return dict(sorted(pages.items()))


def snippet(text, start, end, width=70):
    left = re.sub(r"\s+", " ", text[max(0, start - width):start])
    right = re.sub(r"\s+", " ", text[end:end + width])
    return {"left": ("…" if start > width else "") + left.lstrip(), "match": text[start:end], "right": right.rstrip() + "…"}


def classify(word, pages):
    counts = Counter()
    forms = Counter()
    examples = defaultdict(list)
    pattern = re.compile(r"(?i)\b" + word + r"\b")
    for title, text in pages.items():
        for m in pattern.finditer(text):
            s, e = m.span()
            before = text[s - 1] if s else " "
            after = text[e] if e < len(text) else " "
            glued = before == "-" or after == "-"
            if m.group(0) == word and not glued:
                kind, form = "real", word
            elif glued:
                left = re.search(r"[A-Za-z][\w']*(?:-[A-Za-z][\w']*)*-$", text[max(0, s - 30):s])
                right = re.match(r"(?:-[A-Z][\w]*)+", text[e:e + 30])  # keep "-Thing", drop "-related"
                form = (left.group(0) if left and before == "-" else "") + m.group(0) + (right.group(0) if right and after == "-" else "")
                kind = "name"
            else:
                prev = re.search(r"([A-Z][\w]*) $", text[max(0, s - 30):s])
                if prev and m.group(0)[0].isupper():
                    kind, form = "name", prev.group(1) + " " + m.group(0)
                else:
                    kind, form = "other", m.group(0)
            if kind == "name":
                form = re.sub(r"'s$", "", form)
                forms[form] += 1
            counts[kind] += 1
            key = form if kind == "name" else kind
            if len(examples[key]) < 40:
                examples[key].append(dict(page=title, **snippet(text, s, e)))
    return counts, forms, examples


def pick(items, n):
    """Spread picks across the list so examples come from different pages."""
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


def dots(parts, total_dots):
    """Largest-remainder rounding so the dots add up to round(total / DOT)."""
    raw = [(label, count / DOT) for label, count in parts]
    base = [(label, int(v)) for label, v in raw]
    missing = total_dots - sum(n for _, n in base)
    order = sorted(range(len(raw)), key=lambda i: raw[i][1] - int(raw[i][1]), reverse=True)
    base = [list(b) for b in base]
    for i in order[:max(0, missing)]:
        base[i][1] += 1
    return [tuple(b) for b in base]


def main():
    pages = load_pages()
    words = {}
    for w in NOUNS:
        counts, forms, examples = classify(w, pages)
        total = sum(counts.values())
        top = forms.most_common(TOP_NAMES)
        other_names = counts["name"] - sum(c for _, c in top)
        parts = [("real", counts["real"])] + [(f, c) for f, c in top]
        if other_names:
            parts.append(("other names", other_names))
        if counts["other"]:
            parts.append(("other caps", counts["other"]))
        words[w] = {
            "total": total,
            "real": counts["real"],
            "name": counts["name"],
            "other": counts["other"],
            "parts": [{"label": l, "count": c} for l, c in parts],
            "dots": [{"label": l, "n": n} for l, n in dots(parts, round(total / DOT))],
            "examples": {k: pick(v, 4) for k, v in examples.items() if k in dict(parts) or k == "real"},
        }

    # "she": a hyphen-splitting tokenizer turns She-Hulk into the pronoun "she".
    cv = re.compile(r"(?u)\b\w\w+\b")  # scikit-learn CountVectorizer's default token pattern
    after_she = Counter()
    she_total = 0
    for text in pages.values():
        toks = cv.findall(text.lower())
        for a, b in zip(toks, toks[1:]):
            if a == "she":
                after_she[b] += 1
        she_total += sum(1 for t in toks if t == "she")
    she_glued = Counter()
    for text in pages.values():
        for m in re.finditer(r"(?i)\bshe\b", text):
            s, e = m.span()
            if (s and text[s - 1] == "-") or (e < len(text) and text[e] == "-"):
                she_glued[re.match(r"[\w-]+", text[s:]).group(0)] += 1
    she = {
        "tokenizer_total": she_total,
        "glued": sum(she_glued.values()),
        "glued_forms": she_glued.most_common(5),
        "next": after_she.most_common(8),
    }

    he_total = sum(len(re.findall(r"(?i)\bhe\b", t)) for t in pages.values())
    tokens = sum(len(cv.findall(t.lower())) for t in pages.values())
    data = {
        "pages": len(pages),
        "tokens": tokens,
        "dot": DOT,
        "words": words,
        "she": she,
        "he_total": he_total,
    }
    OUT.write_text("// Generated by prepare_unmasked.py. Do not edit by hand.\nwindow.UNMASKED = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    for w in NOUNS:
        d = words[w]
        print(f"{w:6s} total {d['total']:5d}  real {d['real']:4d}  name {d['name']:5d}  other {d['other']:3d}  dots {sum(x['n'] for x in d['dots'])}  {[(p['label'], p['count']) for p in d['parts']]}")
    print("she", she)
    print("pages", len(pages), "tokens", tokens, "->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
