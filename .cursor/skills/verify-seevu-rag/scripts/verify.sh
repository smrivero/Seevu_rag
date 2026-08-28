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

python3 "$SCRIPTS/check-ingest.py" upload | tee "$SEEVU_EVIDENCE/ingest.json" >/dev/null
python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ["SEEVU_ROOT"])
evidence = pathlib.Path(os.environ["SEEVU_EVIDENCE"])
record = json.loads((evidence / "ingest.json").read_text())
for key in ("document_id", "pages", "chunks"):
    if key not in record:
        raise SystemExit(f"ingest.json missing {key}")
if not isinstance(record["pages"], int) or record["pages"] <= 0:
    raise SystemExit(f"pages is {record['pages']!r}")
if not isinstance(record["chunks"], int) or record["chunks"] <= 0:
    raise SystemExit(f"chunks is {record['chunks']!r}")
index = root / "data" / "index"
for name in ("faiss.index", "chunks.json", "documents.json"):
    path = index / name
    if not path.is_file():
        raise SystemExit(f"missing {path}")
PY

docker compose restart backend
for _ in $(seq 1 30); do
  if "$SCRIPTS/doctor.sh" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
"$SCRIPTS/doctor.sh"
python3 "$SCRIPTS/check-ingest.py" listed | tee "$SEEVU_EVIDENCE/ingest-persist.json" >/dev/null

"$SCRIPTS/install-browser.sh"
SEEVU_ORIGIN="$SEEVU_ORIGIN" SEEVU_EVIDENCE="$SEEVU_EVIDENCE" \
  node "$SCRIPTS/browser.mjs"

echo "verify: health-status and document-ingestion passed. evidence in $SEEVU_EVIDENCE"
"$SCRIPTS/cleanup.sh"
