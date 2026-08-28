# Document ingestion

Document ingestion accepts a PDF at `POST /api/documents`, chunks each page, embeds with OpenAI, and stores vectors in FAISS. `GET /api/documents` lists what is indexed. There is no ingest button in the UI.

## Sub-features

- `ingest-upload` posts the fixture PDF through nginx and returns `document_id`, `pages` > 0, `chunks` > 0, and `status: indexed`.
- `ingest-list` returns that `document_id` from `GET /api/documents`.
- `ingest-persist` keeps the document after `docker compose restart backend`. Files `data/index/faiss.index`, `chunks.json`, and `documents.json` exist on the host.

## How to get to it (user POV)

- With Compose healthy, `POST http://localhost:8080/api/documents` as multipart field `file`.
- `GET http://localhost:8080/api/documents` lists indexed documents.
- The home page still only shows health. Do not look for an upload control.

## Driving it with Playwright

Preconditions:

- `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` exits 0.
- `.env` contains a usable `OPENAI_API_KEY`.
- Fixture PDF at `.cursor/skills/verify-seevu-rag/fixtures/sample.pdf`.

- **Upload.** Run `python3 .cursor/skills/verify-seevu-rag/scripts/check-ingest.py upload`. Exit 0. Stdout includes `document_id`, `pages` > 0, `chunks` > 0. Write the body to `evidence/ingest.json`.
- **List.** The same script already calls `GET /api/documents` and fails if the new `document_id` is missing.
- **Disk.** `data/index/faiss.index`, `data/index/chunks.json`, and `data/index/documents.json` exist.
- **Restart.** `docker compose restart backend`, then doctor until healthy. Run `python3 .cursor/skills/verify-seevu-rag/scripts/check-ingest.py listed`. Write `evidence/ingest-persist.json`.
- **Browser.** Do not add Playwright steps for ingest. After the HTTP checks, `scripts/browser.mjs` still proves `Backend: Connected`.

## Gotchas

- The public path is `/api/documents`. Backend routes have no `/api` prefix. Calling `localhost:8000` is the wrong surface.
- Duplicate bytes return the same `document_id` without a second embedding call. That is success, not a miss.
- A 503 with "Embeddings are not configured" means `OPENAI_API_KEY` is missing in the backend container.
- Playwright has no file input to drive. Recording `verified-unreachable` for an upload heading is expected until a UI ships.
