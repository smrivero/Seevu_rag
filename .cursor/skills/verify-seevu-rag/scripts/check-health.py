#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

origin = os.environ.get("SEEVU_ORIGIN", "http://localhost:8080").rstrip("/")
url = f"{origin}/api/health"
expected = {"status": "ok"}

try:
    with urllib.request.urlopen(url, timeout=5) as response:
        status = response.status
        body = response.read()
except urllib.error.URLError as exc:
    print(f"check-health: {url} failed: {exc}", file=sys.stderr)
    sys.exit(1)

if status != 200:
    print(f"check-health: {url} status {status}", file=sys.stderr)
    sys.exit(1)

try:
    parsed = json.loads(body.decode("utf-8"))
except json.JSONDecodeError as exc:
    print(f"check-health: body is not JSON: {body!r} ({exc})", file=sys.stderr)
    sys.exit(1)

if parsed != expected:
    print(f"check-health: expected {expected!r} got {parsed!r}", file=sys.stderr)
    sys.exit(1)

sys.stdout.write(json.dumps(parsed, separators=(",", ":")))
sys.stdout.write("\n")
