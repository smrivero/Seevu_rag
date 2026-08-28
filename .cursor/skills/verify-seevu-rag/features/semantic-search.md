# Semantic search

Semantic search embeds a query and returns the top chunks from the FAISS index at `POST /api/search`. It does not generate an LLM answer. There is no search box in the UI.

## Sub-features

- `search-http` posts `{"query":"...","top_k":5}` through nginx and returns ranked chunks.
- `search-metadata` includes `score`, `filename`, `page`, `chunk_id`, and `text` on each hit.
- `search-sample` returns at least one hit from the fixture `sample.pdf` for the query `Hello Seevu fixture`.

## How to get to it (user POV)

- With Compose healthy and a PDF ingested, `POST http://localhost:8080/api/search` with JSON `query` and `top_k`.
- The home page still only shows health. Do not look for a search field.

## Driving it with Playwright

Preconditions:

- `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` exits 0.
- Ingest already ran (`check-ingest.py upload`).

- **Search.** Run `python3 .cursor/skills/verify-seevu-rag/scripts/check-search.py`. Exit 0. At least one result. A result named `sample.pdf` has `page` and `score`. Write the body to `evidence/search.json`.
- **Browser.** Do not add Playwright steps. `scripts/browser.mjs` still proves `Backend: Connected`.

## Gotchas

- The public path is `/api/search`. Backend route is `/search`.
- This is retrieval, not an answer. `rag-query.md` stays planned until generation ships.
- An empty index returns `results: []`, status 200.
- Scores are cosine similarity from normalized `IndexFlatIP`. Highest first.
