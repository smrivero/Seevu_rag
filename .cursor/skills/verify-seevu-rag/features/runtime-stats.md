# Runtime stats

Runtime stats expose FAISS, corpus, chunking, embedding, and storage numbers at `GET /api/stats`. There is no stats page in the UI.

## Sub-features

- `stats-http` returns `vector_store`, `corpus`, `documents`, `chunking`, `embeddings`, and `storage` from `GET /api/stats`.
- `stats-index` reads `ntotal`, dimension, index type, and `is_trained` from the persisted FAISS index after ingest.
- `stats-safe` omits API keys and chunk text.

## How to get to it (user POV)

- With Compose healthy, `GET http://localhost:8080/api/stats`.
- The home page still only shows health.

## Driving it with Playwright

Preconditions:

- `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` exits 0.
- Ingest already ran (`check-ingest.py upload`).

- **Stats.** Run `SEEVU_STATS_REQUIRE_VECTORS=1 python3 .cursor/skills/verify-seevu-rag/scripts/check-stats.py`. Exit 0. `vector_store.vectors` > 0. Write the body to `evidence/stats.json`.
- **Browser.** Do not add Playwright steps. `scripts/browser.mjs` still proves `Backend: Connected`.

## Gotchas

- The public path is `/api/stats`. Backend route is `/stats`.
- Empty index is valid: vectors 0, token stats 0. The full verify run asserts vectors > 0 after ingest.
- `provider: openai` in the JSON is the vendor name, not a secret.
