#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

origin = os.environ.get("SEEVU_ORIGIN", "http://localhost:8080").rstrip("/")
url = f"{origin}/api/search"
query = os.environ.get("SEEVU_SEARCH_QUERY", "Hello Seevu fixture")
top_k = int(os.environ.get("SEEVU_SEARCH_TOP_K", "5"))
payload = json.dumps({"query": query, "top_k": top_k}).encode("utf-8")
request = urllib.request.Request(
    url,
    data=payload,
    method="POST",
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(request, timeout=60) as response:
        status = response.status
        body = response.read()
except urllib.error.HTTPError as exc:
    raw = exc.read().decode("utf-8", errors="replace")
    print(f"check-search: {url} status {exc.code} body {raw!r}", file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as exc:
    print(f"check-search: {url} failed: {exc}", file=sys.stderr)
    sys.exit(1)

if status != 200:
    print(f"check-search: {url} status {status}", file=sys.stderr)
    sys.exit(1)

try:
    parsed = json.loads(body.decode("utf-8"))
except json.JSONDecodeError as exc:
    print(f"check-search: body is not JSON: {body!r} ({exc})", file=sys.stderr)
    sys.exit(1)

if not isinstance(parsed, dict):
    print(f"check-search: body is {parsed!r}", file=sys.stderr)
    sys.exit(1)
if parsed.get("query") != query:
    print(f"check-search: query is {parsed.get('query')!r}", file=sys.stderr)
    sys.exit(1)
results = parsed.get("results")
if not isinstance(results, list) or not results:
    print(f"check-search: expected at least one result, got {results!r}", file=sys.stderr)
    sys.exit(1)

scores: list[float] = []
saw_sample = False
for item in results:
    if not isinstance(item, dict):
        print("check-search: result is not an object", file=sys.stderr)
        sys.exit(1)
    score = item.get("score")
    if not isinstance(score, (int, float)):
        print(f"check-search: missing score in {item!r}", file=sys.stderr)
        sys.exit(1)
    scores.append(float(score))
    filename = item.get("filename")
    page = item.get("page")
    if not isinstance(filename, str) or not filename:
        print(f"check-search: missing filename in {item!r}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(page, int) or page < 1:
        print(f"check-search: missing page in {item!r}", file=sys.stderr)
        sys.exit(1)
    if filename == "sample.pdf":
        saw_sample = True
    for key in ("chunk_id", "document_id", "chunk_index", "text"):
        if key not in item:
            print(f"check-search: missing {key}", file=sys.stderr)
            sys.exit(1)

if scores != sorted(scores, reverse=True):
    print(f"check-search: scores are not descending: {scores!r}", file=sys.stderr)
    sys.exit(1)
if not saw_sample:
    print("check-search: no result named sample.pdf", file=sys.stderr)
    sys.exit(1)
blob = json.dumps(parsed)
if "openai_api_key" in blob.lower():
    print("check-search: response leaked a key field", file=sys.stderr)
    sys.exit(1)

sys.stdout.write(json.dumps(parsed, separators=(",", ":")))
sys.stdout.write("\n")
