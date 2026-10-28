import urllib.request, os

ROOT = os.path.dirname(os.path.abspath(__file__))
urls = {
    "public/lib/vue.global.prod.js": "https://unpkg.com/vue@3/dist/vue.global.prod.js",
    "public/lib/face-api.min.js": "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js",
    "public/models/tiny_face_detector_model-weights_manifest.json": "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-weights_manifest.json",
    "public/models/tiny_face_detector_model-shard1": "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-shard1",
    "public/models/face_expression_model-weights_manifest.json": "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/face_expression_model-weights_manifest.json",
    "public/models/face_expression_model-shard1": "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/face_expression_model-shard1",
}

for path, url in urls.items():
    full = os.path.join(ROOT, path)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=90).read()
        with open(full, "wb") as f:
            f.write(data)
        print(f"OK {path} {len(data)} bytes")
    except Exception as e:
        print(f"FAIL {path}: {e}")
