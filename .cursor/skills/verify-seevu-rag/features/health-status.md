# Health status

Health status is the home page of RAG Intelligence Platform. The browser loads `http://localhost:8080`, the page probes `GET /api/health`, and a successful probe shows `Backend: Connected`.

## Sub-features

- `health-http` returns `{"status":"ok"}` from `GET /api/health` on the browser origin.
- `health-title` sets the document title and the `h1` to `RAG Intelligence Platform`.
- `health-connected` replaces `Backend: Checking` with `Backend: Connected` after a live probe.

## How to get to it (user POV)

- Open `http://localhost:8080` in a browser after Compose is up.
- Call `GET http://localhost:8080/api/health` from the same origin the page uses.

## Driving it with Playwright

Preconditions:

- `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` exits 0.
- Compose frontend is published on 8080.

- **HTTP health.** Request the public health URL. Run `.cursor/skills/verify-seevu-rag/scripts/check-health.py`. Exit 0. Stdout is `{"status":"ok"}`. Write the body to `evidence/health.json`.
- **Open home.** Open the origin. Run `SEEVU_ORIGIN=http://localhost:8080 SEEVU_EVIDENCE=.cursor/skills/verify-seevu-rag/evidence node .cursor/skills/verify-seevu-rag/scripts/browser.mjs`. The document title is `RAG Intelligence Platform`.
- **Heading.** Assert the level-1 heading. Playwright locator `getByRole('heading', { name: 'RAG Intelligence Platform' })` is visible.
- **Connected.** Wait until the exact paragraph `Backend: Connected` is visible. Locator `getByText('Backend: Connected', { exact: true })`. `Backend: Checking` or `Backend: Unavailable` is a failure.
- **Proof.** `evidence/health-status.txt` contains both strings. `evidence/health-status.png` shows the heading and `Backend: Connected`. `evidence/health.json` is `{"status":"ok"}`.

## Gotchas

- The first paint is `Backend: Checking`. Do not screenshot until `Backend: Connected` appears. Timeout 15s.
- `GET http://localhost:8000/health` is the wrong surface. The backend port is unpublished. A connection refused there is expected and is not a pass for this feature.
- FastAPI TestClient `GET /health` is a unit test. It does not prove nginx or the browser path.
- `npm run dev` is not the verified topology.
- A 200 with a body other than `{"status":"ok"}` is a fail even if the page still says Connected.
- Bundled Playwright Chromium is unsupported on macOS 13. `browser.mjs` launches Google Chrome instead.
