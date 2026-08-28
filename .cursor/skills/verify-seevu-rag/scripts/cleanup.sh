#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"
cd "$SEEVU_ROOT"

if [[ ! -f "$SEEVU_SESSION" ]]; then
  echo "cleanup: no session stamp, leaving compose running"
  exit 0
fi

kind="$(tr -d '[:space:]' < "$SEEVU_SESSION")"
rm -f "$SEEVU_SESSION"

if [[ "$kind" != "launched" ]]; then
  echo "cleanup: session was $kind, leaving compose running"
  exit 0
fi

docker compose down
echo "cleanup: stopped compose project started by launch.sh"
