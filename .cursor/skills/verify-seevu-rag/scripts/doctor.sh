#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"
cd "$SEEVU_ROOT"

if ! docker info >/dev/null 2>&1; then
  echo "doctor: docker daemon is not running" >&2
  exit 1
fi

ps_out="$(docker compose ps --format json 2>/dev/null || true)"
if [[ -z "$ps_out" ]]; then
  echo "doctor: no compose services from $SEEVU_ROOT" >&2
  exit 1
fi

python3 - "$ps_out" <<'PY'
import json, sys
raw = sys.argv[1]
items = []
for line in raw.splitlines():
    line = line.strip()
    if not line:
        continue
    items.append(json.loads(line))
# compose v2 may emit a JSON array or NDJSON
if len(items) == 1 and isinstance(items[0], list):
    items = items[0]
healthy = {}
for item in items:
    name = item.get("Service") or item.get("Name") or ""
    if "backend" in name:
        healthy["backend"] = item.get("Health", "").lower() == "healthy"
    if "frontend" in name:
        healthy["frontend"] = item.get("Health", "").lower() == "healthy"
if not healthy.get("backend"):
    sys.exit("doctor: backend is not healthy")
if not healthy.get("frontend"):
    sys.exit("doctor: frontend is not healthy")
PY

exec python3 "$SEEVU_SKILL/scripts/check-health.py"
