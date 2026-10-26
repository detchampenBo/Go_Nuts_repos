"""Prepare a real CLIP image-to-article retriever. Run with the repo's .venv/bin/python.

Only the image encoder and precomputed text embeddings ship to the browser. No
target label, passage, or human description is sent to the image encoder.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
MODEL = DIST / "models" / "clip-vit-base-patch32"
CACHE = Path("/tmp/pass-it-on-clip-analysis")
REVISION = "d15189d7028b43f1d3e65039190477f6af591c2a"
BASE = "https://huggingface.co/Xenova/clip-vit-base-patch32/resolve/" + REVISION + "/"
MODEL.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(exist_ok=True)


def download(name, destination):
    if destination.exists() and destination.stat().st_size > 0:
        return
    print("Downloading", name, flush=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    urlretrieve(BASE + name, temporary)
    temporary.replace(destination)


for name in ["config.json", "preprocessor_config.json"]:
    download(name, MODEL / name)
    download(name, CACHE / name)
for name in ["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "merges.txt", "vocab.json"]:
    download(name, CACHE / name)
download("onnx/text_model_quantized.onnx", CACHE / "text_model_quantized.onnx")
download("onnx/vision_model_quantized.onnx", CACHE / "vision_model_quantized.onnx")
license_path = MODEL / "LICENSE"
if not license_path.exists():
    urlretrieve("https://raw.githubusercontent.com/openai/CLIP/main/LICENSE", license_path)

# Split the immutable image model into deployment-sized static assets. The
# browser reassembles exactly these bytes before creating the ONNX session.
parts = []
with (CACHE / "vision_model_quantized.onnx").open("rb") as stream:
    index = 0
    while True:
        data = stream.read(20 * 1024 * 1024)
        if not data:
            break
        name = f"vision-{index:02d}.bin"
        (MODEL / name).write_bytes(data)
        parts.append({"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        index += 1

corpus = json.loads((DIST / "data/corpus.json").read_text())
candidates = []
visual = re.compile(r"\b(?:powers?|abilit\w*|wears|costume|armor|claws|wings|weather|superhuman|strength|green|flies|flying|shrink\w*|grow\w*|weapon|sword|lightning|fire|invisib\w*|telepath\w*|healing|transform\w*)\b", re.I)
for doc, article in enumerate(corpus["documents"]):
    # Freeze three prototypes per article before any player drawing is seen.
    intro = " ".join(article["text"].split()[:800])
    sentences = re.split(r"(?<=[.!?])\s+", intro)
    choices = [s for s in sentences if visual.search(s) and len(s.split()) >= 8]
    base = "A drawing of " + article["title"] + "."
    for slot in range(3):
        sentence = "" if slot == 0 else choices[(slot - 1) % len(choices)] if choices else sentences[0]
        candidates.append({"doc": doc, "title": article["title"], "prompt": base + (" " + sentence if sentence else ""),
                           "source": sentence, "kind": "article name" if slot == 0 else "early visual-description sentence"})

tokenizer = AutoTokenizer.from_pretrained(CACHE, local_files_only=True)
options = ort.SessionOptions()
options.intra_op_num_threads = 4
session = ort.InferenceSession(str(CACHE / "text_model_quantized.onnx"), sess_options=options,
                               providers=["CPUExecutionProvider"])
print("Text model inputs:", [i.name for i in session.get_inputs()], flush=True)
print("Text model outputs:", [i.name for i in session.get_outputs()], flush=True)
vectors = []
for start in range(0, len(candidates), 16):
    batch = candidates[start:start + 16]
    encoded = tokenizer([c["prompt"] for c in batch], padding="max_length", truncation=True,
                        max_length=77, return_tensors="np")
    inputs = {i.name: encoded[i.name].astype(np.int64) for i in session.get_inputs()}
    embedded = session.run(["text_embeds"], inputs)[0]
    assert embedded.shape == (len(batch), 512), embedded.shape
    embedded /= np.linalg.norm(embedded, axis=1, keepdims=True)
    vectors.append(embedded)
    print(f"Encoded {min(start + 16, len(candidates))}/{len(candidates)} candidate descriptions", flush=True)
np.concatenate(vectors).astype("<f4").tofile(DIST / "data/vision-text-vectors.bin")
metadata = {"model": "Xenova/clip-vit-base-patch32", "revision": REVISION, "dimensions": 512,
            "textTokenLimit": 77, "imageSize": 224, "patchSize": 32,
            "prototypesPerArticle": 3, "candidates": candidates, "parts": parts,
            "visionBytes": sum(p["bytes"] for p in parts)}
(DIST / "data/vision.json").write_text(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))
print("Ready: drawing pixels → 512D CLIP image vector → 303 ranked articles.", flush=True)
