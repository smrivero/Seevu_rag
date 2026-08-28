#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"
SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$SEEVU_EVIDENCE"

"$SCRIPTS/launch.sh"
"$SCRIPTS/doctor.sh"

"$SCRIPTS/check-health.py" | tee "$SEEVU_EVIDENCE/health.json" >/dev/null
python3 - <<'PY'
import json, os, pathlib
path = pathlib.Path(os.environ["SEEVU_EVIDENCE"]) / "health.json"
raw = path.read_text().strip()
parsed = json.loads(raw)
if parsed != {"status": "ok"}:
    raise SystemExit(f"health.json is {parsed!r}")
path.write_text(json.dumps(parsed, separators=(",", ":")) + "\n")
PY

"$SCRIPTS/install-browser.sh"
SEEVU_ORIGIN="$SEEVU_ORIGIN" SEEVU_EVIDENCE="$SEEVU_EVIDENCE" \
  node "$SCRIPTS/browser.mjs"

echo "verify: health-status passed. evidence in $SEEVU_EVIDENCE"
"$SCRIPTS/cleanup.sh"
