"""Vendor pinned browser inference assets so gameplay needs no third-party requests."""
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parent / "dist"
FILES = {
    "vendor/transformers.min.js": "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js",
    "vendor/ort-wasm-simd.wasm": "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort-wasm-simd.wasm",
    "vendor/ort-wasm.wasm": "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort-wasm.wasm",
    "vendor/transformers-LICENSE.txt": "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/LICENSE",
    "vendor/onnxruntime-LICENSE.txt": "https://raw.githubusercontent.com/microsoft/onnxruntime/v1.14.0/LICENSE",
    "vendor/display-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/OFL.txt",
    "vendor/hand-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/OFL.txt",
}
REV = "751bff37182d3f1213fa05d7196b954e230abad9"
for name in ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "onnx/model_quantized.onnx"]:
    FILES["models/all-MiniLM-L6-v2/" + name] = "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/" + REV + "/" + name
FILES["models/LICENSE"] = "https://www.apache.org/licenses/LICENSE-2.0.txt"

for destination, url in FILES.items():
    path = ROOT / destination
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        continue
    print("Downloading", destination, flush=True)
    temporary = path.with_suffix(path.suffix + ".part")
    urlretrieve(url, temporary)
    temporary.replace(path)
    print(path.stat().st_size, "bytes", flush=True)

# Keep the typefaces local too. Google's CSS endpoint returns a Latin font file.
import re
from urllib.request import urlopen, Request
for filename, family in [("display.ttf", "Bricolage+Grotesque:wght@800"), ("hand.ttf", "Caveat:wght@700")]:
    path = ROOT / "vendor" / filename
    if not path.exists():
        request = Request("https://fonts.googleapis.com/css2?family=" + family + "&display=swap", headers={"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"})
        css = urlopen(request, timeout=30).read().decode()
        urlretrieve(re.findall(r"url\((https://[^)]+)\)", css)[-1], path)
