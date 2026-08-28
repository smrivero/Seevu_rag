#!/usr/bin/env bash
set -euo pipefail

# .cursor/skills/verify-seevu-rag/scripts -> repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SKILL="$ROOT/.cursor/skills/verify-seevu-rag"
export SEEVU_ROOT="$ROOT"
export SEEVU_SKILL="$SKILL"
export SEEVU_EVIDENCE="$SKILL/evidence"
export SEEVU_ORIGIN="${SEEVU_ORIGIN:-http://localhost:8080}"
export SEEVU_SESSION="$SKILL/scripts/.session"
