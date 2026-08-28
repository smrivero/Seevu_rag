#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"
cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ ! -d node_modules/playwright ]]; then
  npm install
fi

if npx playwright install chromium >/tmp/seevu-playwright-install.log 2>&1; then
  exit 0
fi

if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  echo "install-browser: bundled Chromium is unavailable. browser.mjs uses Google Chrome."
  exit 0
fi

cat /tmp/seevu-playwright-install.log >&2
exit 1
