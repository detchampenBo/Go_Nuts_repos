"""Rebuild the real 303-article retrieval corpus. Run with the repo's .venv/bin/python.

No model training or invented rankings. Dense vectors use MiniLM, normalized per
passage; document vectors average the 180-word passage vectors and renormalize.
Passages respect both word budgets and the encoder's token limit. Signed-byte
storage is renormalized by the client; it is a small quantization approximation.
"""
import json
import re
import urllib.parse
import zipfile
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

HERE = Path(__file__).resolve().parent
OUT = HERE / "dist" / "data"
ROOT = HERE.parents[1]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MIN_WORDS = 8  # shorter passages are splitter leftovers; see split()

# Exact source excerpts. Names are masked only in the drawing prompt.
SEEDS = [
    ("Spider-Man", "He sews a spider-web patterned spandex costume", "Peter", "someone"),
    ("Storm_(Marvel_Comics)", "She is able to control the weather", None, None),
    ("Hulk", "Following his accidental exposure to gamma rays", "Banner|Hulk|Rick Jones", "someone"),
    ("Doctor_Strange", "The character starts as an intelligent", None, None),
    ("Wolverine_(character)", "He possesses a range of superpowers", None, None),
    ("Black_Bolt", None, None, None),
    ("Rocket_Raccoon", None, None, None),
    ("Hank_Pym", None, None, None),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    archive = zipfile.ZipFile(ROOT / "notebooks/data/marvel_pages.zip")
    files = {urllib.parse.unquote(Path(n).stem): n for n in archive.namelist()
             if n.endswith(".txt") and "README" not in n}
    ids = sorted(files)
    texts = [archive.read(files[i]).decode("utf-8", "replace") for i in ids]
    print(f"Loaded {len(ids)} articles", flush=True)
    model = SentenceTransformer(MODEL, local_files_only=True, device="cpu")
    model.tokenizer.model_max_length = 1000000
    max_tokens = model.max_seq_length - 2

    def split(text, budget):
        chunks, current = [], []
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            words = sentence.split()
            for start in range(0, len(words), budget):
                part = words[start:start + budget]
                while part:
                    candidate = current + part
                    if len(candidate) <= budget and len(model.tokenizer.encode(" ".join(candidate), add_special_tokens=False)) <= max_tokens:
                        current = candidate
                        break
                    if current:
                        chunks.append(" ".join(current)); current = []
                    else:
                        count = len(part)
                        while len(model.tokenizer.encode(" ".join(part[:count]), add_special_tokens=False)) > max_tokens:
                            count //= 2
                            if count == 0:
                                raise ValueError("One word exceeds encoder limit")
                        chunks.append(" ".join(part[:count])); part = part[count:]
        if current:
            chunks.append(" ".join(current))
        # A sentence longer than the budget is cut at the budget, which can leave a one-word remainder
        # ("traveler.") as its own passage. Merge any passage under MIN_WORDS into the previous one, or
        # re-split the pair into two balanced halves when together they exceed the limits.
        def fits(words):
            return len(words) <= budget and len(model.tokenizer.encode(" ".join(words), add_special_tokens=False)) <= max_tokens
        merged = []
        for chunk in chunks:
            words = chunk.split()
            if merged and len(words) < MIN_WORDS:
                both = merged[-1].split() + words
                if fits(both):
                    merged[-1] = " ".join(both); continue
                half = (len(both) + 1) // 2
                if fits(both[:half]) and fits(both[half:]):
                    merged[-1] = " ".join(both[:half]); merged.append(" ".join(both[half:])); continue
            merged.append(chunk)
        return merged

    docs = [{"id": i, "title": re.sub(r"\s*\((?:character|Marvel Comics|comics)\)$", "", i.replace("_", " ")),
             "text": t, "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(i)} for i, t in zip(ids, texts)]
    tf = TfidfVectorizer(stop_words="english", sublinear_tf=True, token_pattern=r"(?u)\b[a-zA-Z0-9_]{2,}\b")
    matrix = tf.fit_transform(texts)
    lexical = {"vocab": tf.get_feature_names_out().tolist(), "idf": tf.idf_.round(7).tolist(),
               "stop": sorted(ENGLISH_STOP_WORDS), "rows": []}
    for i in range(len(ids)):
        row = matrix.getrow(i)
        lexical["rows"].append([row.indices.tolist(), row.data.round(7).tolist()])
    (OUT / "lexical.json").write_text(json.dumps(lexical, separators=(",", ":")))
    catalog = {}
    for budget in [180, 60]:
        passages = [{"doc": i, "text": passage} for i, text in enumerate(texts) for passage in split(text, budget)]
        print(f"Embedding {len(passages)} passages (max {budget} words)", flush=True)
        vectors = model.encode([p["text"] for p in passages], batch_size=64,
                               normalize_embeddings=True, show_progress_bar=True)
        np.rint(vectors * 127).clip(-127, 127).astype("i1").tofile(OUT / f"vectors-{budget}.bin")
        (OUT / f"passages-{budget}.json").write_text(json.dumps(passages, ensure_ascii=False, separators=(",", ":")))
        catalog[str(budget)] = len(passages)
        if budget == 180:
            owners = np.array([p["doc"] for p in passages])
            means = np.stack([vectors[owners == i].mean(axis=0) for i in range(len(ids))])
            means /= np.linalg.norm(means, axis=1, keepdims=True)
            np.rint(means * 127).clip(-127, 127).astype("i1").tofile(OUT / "vectors-page.bin")
    prompts = []
    for hero, start, pattern, replacement in SEEDS[:5]:
        doc = ids.index(hero)
        sentences = re.split(r"(?<=[.!?])\s+", texts[doc])
        original = next(s for s in sentences if s.startswith(start))
        masked = re.sub(pattern, replacement, original) if pattern else original
        prompts.append({"doc": doc, "original": original, "prompt": masked})
    (OUT / "corpus.json").write_text(json.dumps({"documents": docs, "prompts": prompts,
        "model": MODEL, "dimensions": 384, "passageCounts": catalog,
        "source": "02805 frozen Wikipedia snapshot, 2026-08-26"}, ensure_ascii=False, separators=(",", ":")))
    print("Wrote corpus, lexical index, passage texts, and normalized dense vectors.", flush=True)


if __name__ == "__main__":
    main()
