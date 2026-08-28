---
name: verify-seevu-rag
description: Drive RAG Intelligence Platform through Docker Compose and Playwright. Proves GET /api/health, the page title RAG Intelligence Platform, and Backend: Connected. Use when verifying this app, after changing frontend, backend, nginx, or compose, or before claiming a feature works.
---

# Verify RAG Intelligence Platform

Read [features/README.md](features/README.md) before driving. Drive only features listed as live. Planned features are `verified-unreachable` until their file says otherwise.

Do not run `npm run dev`. The verified topology is Compose. The browser origin is `http://localhost:8080`. Axios uses `/api`. nginx rewrites `/api/health` to backend `GET /health`. Port 8000 is unpublished.

Exact strings to assert, unchanged:

- Health body `{"status":"ok"}`
- `RAG Intelligence Platform`
- `Backend: Connected`

## Launch

From the repo root (the directory that contains `docker-compose.yml`):

```bash
.cursor/skills/verify-seevu-rag/scripts/launch.sh
```

Ready when `scripts/doctor.sh` exits 0. That means `GET http://localhost:8080/api/health` returns exactly `{"status":"ok"}` and both Compose services are `healthy`.

Port 8080 is shared. Do not start a second stack on that port. If doctor already passes, launch reuses the instance and does not rebuild. If 8080 answers with a different body or a foreign process, launch exits non-zero and does not steal the port.

Do not run `npm run dev`. Do not publish backend 8000.

Teardown is [Cleanup](#cleanup).

## Doctor

```bash
.cursor/skills/verify-seevu-rag/scripts/doctor.sh
```

Read-only. Exits 0 only when all of these hold:

- `docker info` succeeds
- `docker compose ps` from the repo root shows `backend` and `frontend` as `healthy`
- `GET http://localhost:8080/api/health` status 200 and body exactly `{"status":"ok"}`

Run doctor before the first drive, after any failed drive, and before treating the instance as reusable.

## Drive

Harness is Playwright via `scripts/browser.mjs`. HTTP checks are `scripts/check-health.py`. Prefer role and accessible name over CSS.

```bash
.cursor/skills/verify-seevu-rag/scripts/verify.sh
```

That script is the lever. It launches or reuses, doctors, checks health, drives the live feature map entry, writes evidence, then cleans up what it started.

To drive one live feature after doctor already passed:

```bash
.cursor/skills/verify-seevu-rag/scripts/check-health.py
SEEVU_ORIGIN=http://localhost:8080 SEEVU_EVIDENCE=.cursor/skills/verify-seevu-rag/evidence \
  node .cursor/skills/verify-seevu-rag/scripts/browser.mjs
```

Selectors for the live page:

- Document title `RAG Intelligence Platform`
- `getByRole('heading', { name: 'RAG Intelligence Platform' })`
- `getByText('Backend: Connected', { exact: true })`

Wait until `Backend: Connected` appears. The first paint is `Backend: Checking`. A screenshot of Checking is not a pass.

For a new user-facing route, add a feature file under [features/](features/README.md), then add a check in `scripts/browser.mjs`. Do not invent UI. If the route is missing, record `verified-unreachable` with the path you tried.

## Evidence

Write under `.cursor/skills/verify-seevu-rag/evidence/`. Cleanup must not delete this directory.

Required artifacts for `health-status`:

- `health.json` the raw `/api/health` body
- `health-status.txt` the `main` inner text after Connected
- `health-status.png` full-page screenshot that shows the heading and `Backend: Connected`

Proof standards:

- Exercise the browser origin, not TestClient and not `localhost:8000`
- Capture the HTTP check and the UI state, not only the screenshot
- `Backend: Connected` is the side effect of the probe. The matching HTTP body must be in `health.json`
- No mocks. The backend process behind nginx is the system under test

## Cleanup

```bash
.cursor/skills/verify-seevu-rag/scripts/cleanup.sh
```

Kills only the Compose project this run started (stamp at `scripts/.session`). If launch reused an already-healthy stack, cleanup leaves it running. Never `pkill` nginx, node, or uvicorn by name. Evidence files stay.

After a failed iteration, run cleanup, then launch again. Do not pile stacks on 8080.

## Helpers

All paths relative to the repo root. Scripts are executable.

| Script | Invocation |
| --- | --- |
| Launch or reuse | `.cursor/skills/verify-seevu-rag/scripts/launch.sh` |
| Doctor | `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` |
| Health body | `.cursor/skills/verify-seevu-rag/scripts/check-health.py` |
| Playwright page | `SEEVU_ORIGIN=http://localhost:8080 SEEVU_EVIDENCE=.cursor/skills/verify-seevu-rag/evidence node .cursor/skills/verify-seevu-rag/scripts/browser.mjs` |
| Full run | `.cursor/skills/verify-seevu-rag/scripts/verify.sh` |
| Cleanup | `.cursor/skills/verify-seevu-rag/scripts/cleanup.sh` |

Install Playwright once per machine with `scripts/install-browser.sh`. `verify.sh` runs it if `node_modules/playwright` is missing. On hosts where bundled Chromium is unsupported, `browser.mjs` launches installed Google Chrome (`channel: "chrome"`).

Keep the feature map honest with `/maintain-verification-skill`.
