# PDF upload

PDF upload will let a user choose a PDF and send it into the corpus. It is not in the product yet.

## Sub-features

- `pdf-upload-open` opens the upload control from the home page. Not shipped.
- `pdf-upload-accept` accepts a `.pdf` file. Not shipped.
- `pdf-upload-reject` rejects a non-PDF. Not shipped.

## How to get to it (user POV)

- No entry point exists. There is no upload heading, file input, or `/api/upload` route.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for a file input or a heading that names upload. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a user-visible upload control or `POST /api/upload`.
- **When it ships.** Add the locator and the request assertion to `scripts/browser.mjs`. Capture the chosen filename and the resulting status text. Keep a sample PDF under `data/` for the run, not in `evidence/`.

## Gotchas

- Do not treat `data/` being empty as a pass or a fail. Ingestion is not live.
- Do not invent an upload URL in `browser.mjs` before the route exists.
