# RAG Intelligence Platform

How to run the health page and how PDF ingest is wired.

## Start the stack

Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. From the repo root:

```bash
docker compose up --build
```

Open `http://localhost:8080`. The tab title is `RAG Intelligence Platform`. After the probe succeeds, the page shows `Backend: Connected`.

The browser origin is port 8080. Axios uses `baseURL` `/api`. nginx rewrites `/api/health` to backend `/health` and `/api/documents` to backend `/documents`. Port 8000 is not published. There is no `VITE_API_URL` and no CORS middleware.

## Ingest a PDF

There is no upload UI yet. From the same origin:

```bash
curl -sS -F "file=@your.pdf;type=application/pdf" http://localhost:8080/api/documents
curl -sS http://localhost:8080/api/documents
```

`document_id` is the SHA-256 of the file bytes. The same bytes return the existing record. Chunks stay inside page boundaries. Vectors live in `data/index/` (`faiss.index`, `chunks.json`, `documents.json`) on a Compose bind mount.

## Run backend tests

From `backend/`:

```bash
uv sync --group dev
uv run pytest
```

Tests mock OpenAI. They do not call the network. They do not use Docker, nginx, or the `/api` prefix.

## Add another API route

1. Add a FastAPI router next to `backend/app/health.py` or `backend/app/documents.py`.
2. Include it from `create_app()` with no prefix.
3. Call it from the existing axios instance as `client.get("/your-path")`. nginx already forwards `/api/` to the backend root.

When a frontend consumer needs generated types, add `openapi-typescript` against `create_app().openapi()` and a check that fails on drift.

## Later owners

Do not create these files until the capability exists.

| Capability | Owner when it exists |
| --- | --- |
| OpenAI completions | `backend/app/generate.py` |
| Pinecone | A `PineconeVectorStore` next to `FAISSVectorStore`. Wire it in `vector_stores.py`. Leave `IngestService` on the `VectorStore` protocol. |
| Rerank, language, guardrails | Policy inside the future answer module until each owns its own invariants |
| Citations | Fields on a future answer type |
| Query UI | `frontend/src/useQuery.ts` plus a view. Move `useBackendProbe.ts` into `src/hooks/` in the same change as the second hook |
| PDF upload UI | MUI with `sx`. Do not add Tailwind, CSS Modules, or styled-components |
| Auth | Out of scope for this product increment |

A retried ingest of the same bytes must return the same `document_id`.

## Environment

`.env.example` lists `OPENAI_API_KEY`, `EMBEDDING_MODEL`, `VECTOR_STORE`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_UPLOAD_BYTES`, and `INDEX_DIR`. Compose sets `INDEX_DIR=/data/index` and bind-mounts `./data/index`. Do not put the API key in the image.
