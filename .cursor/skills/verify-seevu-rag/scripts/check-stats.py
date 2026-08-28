#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

origin = os.environ.get("SEEVU_ORIGIN", "http://localhost:8080").rstrip("/")
url = f"{origin}/api/stats"

try:
    with urllib.request.urlopen(url, timeout=15) as response:
        status = response.status
        body = response.read()
except urllib.error.URLError as exc:
    print(f"check-stats: {url} failed: {exc}", file=sys.stderr)
    sys.exit(1)

if status != 200:
    print(f"check-stats: {url} status {status}", file=sys.stderr)
    sys.exit(1)

try:
    parsed = json.loads(body.decode("utf-8"))
except json.JSONDecodeError as exc:
    print(f"check-stats: body is not JSON: {body!r} ({exc})", file=sys.stderr)
    sys.exit(1)

if not isinstance(parsed, dict):
    print(f"check-stats: body is {parsed!r}", file=sys.stderr)
    sys.exit(1)

store = parsed.get("vector_store")
corpus = parsed.get("corpus")
chunking = parsed.get("chunking")
embeddings = parsed.get("embeddings")
storage = parsed.get("storage")
if not isinstance(store, dict) or store.get("type") != "faiss":
    print(f"check-stats: vector_store is {store!r}", file=sys.stderr)
    sys.exit(1)
if store.get("index_type") != "IndexFlatIP":
    print(f"check-stats: index_type is {store.get('index_type')!r}", file=sys.stderr)
    sys.exit(1)
if not isinstance(corpus, dict):
    print(f"check-stats: corpus is {corpus!r}", file=sys.stderr)
    sys.exit(1)
if not isinstance(chunking, dict) or "min_chunk_tokens" not in chunking:
    print(f"check-stats: chunking is {chunking!r}", file=sys.stderr)
    sys.exit(1)
if not isinstance(embeddings, dict) or embeddings.get("provider") != "openai":
    print(f"check-stats: embeddings is {embeddings!r}", file=sys.stderr)
    sys.exit(1)
if not isinstance(storage, dict):
    print(f"check-stats: storage is {storage!r}", file=sys.stderr)
    sys.exit(1)

require_positive = os.environ.get("SEEVU_STATS_REQUIRE_VECTORS", "") == "1"
vectors = store.get("vectors")
if require_positive and (not isinstance(vectors, int) or vectors <= 0):
    print(f"check-stats: expected vectors > 0, got {vectors!r}", file=sys.stderr)
    sys.exit(1)

blob = json.dumps(parsed)
if "openai_api_key" in blob.lower() or "api_key" in blob.lower():
    print("check-stats: response leaked a key field", file=sys.stderr)
    sys.exit(1)

documents = parsed.get("documents")
if isinstance(documents, list):
    for item in documents:
        if isinstance(item, dict) and "text" in item:
            print("check-stats: document entry includes text", file=sys.stderr)
            sys.exit(1)

sys.stdout.write(json.dumps(parsed, separators=(",", ":")))
sys.stdout.write("\n")
