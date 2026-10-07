"""Prepare the data for the "Her husband, his armor" Week 6 post.

Question: in the 303 Marvel Wikipedia pages, which words come right after "her"
and which come right after "his"? Is a Marvel woman written through her family
and her mind, and a Marvel man through his body, his gear and his plans?

Input:  notebooks/data/marvel_pages.zip   (one plain-text page per character)
Output: showcases/week-06-her-husband-his-armor/possessives-data.js

Run from the repository root:
    python showcases/week-06-her-husband-his-armor/prepare_possessives.py

Only the Python standard library is used.

Method (Week 6):
  context   the one word right after "her" / "his" (a context window of 1, as
            in exercise 6.6). Function words are dropped ("her from", "her to"),
            which removes most cases where "her" is an object, not a possessive.
  score     log2( P(w | her) / P(w | his) ), with add-one smoothing. This is
            PMI(her, w) - PMI(his, w): the same pointwise mutual information as
            exercise 6.6, used to compare two groups of text as Scattertext does.
  groups    the colour groups (partner & family, body, gear, mind, career) are our
            own labels, like topic labels in exercise 6.4. The model does not
            produce them.
  rate      the chart draws each word as uses per 1,000 words after "her" and per
            1,000 after "his", so the two sides are comparable.
"""

from collections import Counter, defaultdict
from pathlib import Path
import json
import math
import re
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "notebooks" / "data" / "marvel_pages.zip"
OUT = Path(__file__).with_name("possessives-data.js")

MIN_COUNT = 12  # a word must follow her/his at least this often to be ranked
EXAMPLES = 3     # sentences kept per word and side

STOP = set("""a about above after again against all also although am an and any are as
at away back be because been before being below between both but by can could did do
does down during each either even ever few for from further had has have having he her
here hers herself him himself his how however i if in into is it its itself just later
like may me might more most much must my no nor not now of off on once one only or other
our out over own same she should since so some such than that the their them then there
these they this those through thus to too two three under until up upon us very was we
well were what when where whether which while who whom whose why will with within without
would yet you""".split())

GROUPS = {
    "family": ("Partner & family", "husband wife boyfriend girlfriend fiancé fiancée lover partner children child son sons daughter daughters mother father parents brother brothers sister sisters cousin uncle aunt grandfather grandmother niece nephew family"),
    "body": ("Body & looks", "hair legs leg hands hand arms arm chest head face eyes body skin blood brain heart healing"),
    "gear": ("Gear", "armor armour mask suit costume shield weapon weapons sword hammer gun guns helmet ship"),
    "mind": ("Mind powers", "telepathic telepathy psychic telekinesis telekinetic mind spirit mental"),
    "career": ("Career & plans", "career work job plan plans decision successor criminal business company allies"),
}
WORD_GROUP = {w: g for g, (_, words) in GROUPS.items() for w in words.split()}

POSSESSIVE = re.compile(r"(?<![\w-])([Hh]er|[Hh]is)\s+([a-z][a-z-]*)\b(?!-)")


def load_pages():
    pages = {}
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if not name.endswith(".txt") or name.startswith("README"):
                continue
            title = urllib.parse.unquote(name[:-4]).replace("_", " ")
            pages[title] = z.read(info).decode("utf-8")
    return dict(sorted(pages.items()))


def snippet(text, start, end, width=80):
    left = re.sub(r"\s+", " ", text[max(0, start - width):start])
    right = re.sub(r"\s+", " ", text[end:end + width])
    return {"left": ("…" if start > width else "") + left.lstrip(), "match": text[start:end], "right": right.rstrip() + "…"}


def spread(examples, n):
    """One example per page first, so the panel shows several characters."""
    seen, first, rest = set(), [], []
    for ex in examples:
        (rest if ex["page"] in seen else first).append(ex)
        seen.add(ex["page"])
    return (first + rest)[:n]


def main():
    pages = load_pages()
    titles = list(pages)
    counts = {"her": Counter(), "his": Counter()}
    on_pages = {"her": defaultdict(set), "his": defaultdict(set)}
    examples = {"her": defaultdict(list), "his": defaultdict(list)}
    mentions = {"her": [], "his": []}  # every kept "her ___" / "his ___", in page order
    for pi, (title, text) in enumerate(pages.items()):
        for m in POSSESSIVE.finditer(text):
            p, w = m.group(1).lower(), m.group(2)
            if w in STOP:
                continue
            counts[p][w] += 1
            on_pages[p][w].add(title)
            ex = dict(page=title, **snippet(text, *m.span()))
            examples[p][w].append(ex)
            mentions[p].append((w, pi, ex))

    n_her, n_his = sum(counts["her"].values()), sum(counts["his"].values())
    ranked = []
    for w in set(counts["her"]) | set(counts["his"]):
        a, b = counts["her"][w], counts["his"][w]
        if a + b < MIN_COUNT:
            continue
        lr = math.log2(((a + 1) / (n_her + 1)) / ((b + 1) / (n_his + 1)))
        ranked.append((lr, w))
    ranked.sort(reverse=True)
    words = [{
        "w": w, "lr": round(lr, 2), "group": WORD_GROUP.get(w, "other"),
        "her": counts["her"][w], "his": counts["his"][w],
        "her_pages": len(on_pages["her"][w]), "his_pages": len(on_pages["his"][w]),
        "ex_her": spread(examples["her"][w], EXAMPLES), "ex_his": spread(examples["his"][w], EXAMPLES),
    } for lr, w in ranked]

    # groups: share of all her/his words, and how concentrated each group is on a few pages
    groups = {}
    for g, (label, _) in GROUPS.items():
        d = {"label": label}
        for side, n in (("her", n_her), ("his", n_his)):
            by_page = Counter(titles[pi] for w, pi, _ in mentions[side] if WORD_GROUP.get(w) == g)
            total = sum(by_page.values())
            top = by_page.most_common(5)
            d[side] = total
            d[side + "_share"] = round(total / n, 4)
            d[side + "_pages"] = len(by_page)
            d[side + "_top5"] = [[t, c] for t, c in top]
            d[side + "_top5_share"] = round(sum(c for _, c in top) / total, 3) if total else 0
            d[side + "_words"] = [[w, c] for w, c in counts[side].most_common() if WORD_GROUP.get(w) == g][:4]
        groups[g] = d

    # one profile per hero page for the "hero exam": the pronoun the page uses most, its top words and theme counts
    per_page = {side: defaultdict(Counter) for side in ("her", "his")}
    for side in ("her", "his"):
        for w, pi, _ in mentions[side]:
            per_page[side][pi][w] += 1
    heroes = []
    for pi, title in enumerate(titles):
        her_c, his_c = per_page["her"][pi], per_page["his"][pi]
        pron, c = ("her", her_c) if sum(her_c.values()) > sum(his_c.values()) else ("his", his_c)
        g = Counter(WORD_GROUP.get(w, "other") for w in c.elements())
        heroes.append({"t": title, "p": pron, "n": sum(c.values()), "top": c.most_common(8), "g": {k: g[k] for k in GROUPS}})

    # the opening "textscape": every kept phrase in page order, as flat [word, page] index pairs
    vocab = sorted(set(counts["her"]) | set(counts["his"]))
    vi = {w: i for i, w in enumerate(vocab)}
    wall = {side: [x for w, pi, _ in mentions[side] for x in (vi[w], pi)] for side in ("her", "his")}

    data = {
        "pages": len(pages),
        "her_total": n_her,
        "his_total": n_his,
        "min_count": MIN_COUNT,
        "ranked_total": len(ranked),
        "words": words,
        "groups": groups,
        "heroes": heroes,
        "titles": titles,
        "vocab": vocab,
        "wall": wall,
    }
    OUT.write_text("// Generated by prepare_possessives.py. Do not edit by hand.\nwindow.POSSESSIVES = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    print(f"pages {len(pages)}  her {n_her}  his {n_his}  ranked {len(ranked)}")
    print("most her:", ", ".join(f"{d['w']} {d['her']}/{d['his']}" for d in words[:12]))
    print("most his:", ", ".join(f"{d['w']} {d['her']}/{d['his']}" for d in words[-12:]))
    for g, d in groups.items():
        print(f"{d['label']:18s} her {d['her_share']:6.1%} on {d['her_pages']:3d} pages, top-5 {d['her_top5_share']:4.0%}  |  his {d['his_share']:6.1%} on {d['his_pages']:3d} pages, top-5 {d['his_top5_share']:4.0%}")
    print("her mind top-5 pages:", groups["mind"]["her_top5"])
    print("->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
