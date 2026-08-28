# PDF upload

PDF upload will let a user choose a PDF in the browser and send it into the corpus. The HTTP ingest route exists. The page control does not.

## Sub-features

- `pdf-upload-open` opens the upload control from the home page. Not shipped.
- `pdf-upload-accept` accepts a `.pdf` file from that control. Not shipped.
- `pdf-upload-reject` rejects a non-PDF from that control. Not shipped.

## How to get to it (user POV)

- No entry point exists on the home page. There is no upload heading or file input.
- HTTP ingest is documented in [document-ingestion.md](./document-ingestion.md), not here.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature in the browser.

- **Reach.** Open `http://localhost:8080` and look for a file input or a heading that names upload. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a user-visible upload control.
- **When it ships.** Add the locator and the request assertion to `scripts/browser.mjs`. Capture the chosen filename and the resulting status text. Keep a sample PDF under `fixtures/` for the run, not in `evidence/`.

## Gotchas

- `POST /api/documents` succeeding is not a pass for this feature. That proof belongs to document ingestion.
- Do not invent an upload URL in `browser.mjs` before the control exists.
