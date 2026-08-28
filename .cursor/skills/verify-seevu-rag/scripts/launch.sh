#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"
cd "$SEEVU_ROOT"

mkdir -p "$SEEVU_EVIDENCE"

reused=0
if "$(dirname "${BASH_SOURCE[0]}")/doctor.sh" >/dev/null 2>&1; then
  reused=1
elif curl -sS -m 2 -o /dev/null -w "%{http_code}" "$SEEVU_ORIGIN/api/health" 2>/dev/null | grep -qE '^[23]'; then
  echo "launch: $SEEVU_ORIGIN answers but doctor failed. Refusing to steal port 8080." >&2
  "$(dirname "${BASH_SOURCE[0]}")/doctor.sh" || true
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "launch: docker daemon is not running" >&2
  exit 1
fi

docker compose up --build -d

if [[ "$reused" -eq 1 ]]; then
  echo "reused" > "$SEEVU_SESSION"
else
  echo "launched" > "$SEEVU_SESSION"
fi

for _ in $(seq 1 60); do
  if "$(dirname "${BASH_SOURCE[0]}")/doctor.sh" >/dev/null 2>&1; then
    if [[ "$reused" -eq 1 ]]; then
      echo "launch: rebuilt healthy stack at $SEEVU_ORIGIN"
    else
      echo "launch: stack ready at $SEEVU_ORIGIN"
    fi
    exit 0
  fi
  sleep 2
done

echo "launch: timed out waiting for doctor" >&2
"$(dirname "${BASH_SOURCE[0]}")/doctor.sh" || true
exit 1
