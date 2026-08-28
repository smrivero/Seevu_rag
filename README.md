# RAG Intelligence Platform

How to run the health demo and how to add the next route.

## Start the stack

From the repo root, run:

```bash
docker compose up --build
```

Open `http://localhost:8080`. The tab title is `RAG Intelligence Platform`. After the probe succeeds, the page shows `Backend: Connected`.

The browser origin is port 8080. Axios uses `baseURL` `/api`. nginx rewrites `/api/health` to backend `/health`. Port 8000 is not published. There is no `VITE_API_URL` and no CORS middleware.

## Run backend tests

From `backend/`:

```bash
uv sync --group dev
uv run pytest
```

Tests call `GET /health` on `TestClient(create_app())`. They do not use Docker, nginx, or the `/api` prefix.

## Add a second API route

1. Add a FastAPI router next to `backend/app/health.py`.
2. Include it from `create_app()` with no prefix, the same way health is included.
3. Call it from the existing axios instance as `client.get("/your-path")`. nginx already forwards `/api/` to the backend root.

When that second endpoint lands, add `openapi-typescript` against `create_app().openapi()` and a check that fails on drift. Do not add `dump_openapi.py` until then.

## Later owners

Do not create these files until the capability exists.

| Capability | Owner when it exists |
| --- | --- |
| OpenAI and any LLM | `backend/app/generate.py` |
| FAISS and Pinecone | `backend/app/index.py`, which hides the vendor |
| Document ingestion | `backend/app/ingest.py`, which reads `data/` |
| Rerank, language, guardrails | Policy inside the future answer module until each owns its own invariants |
| Citations | Fields on a future answer type |
| Query UI | `frontend/src/useQuery.ts` plus a view. Move `useBackendProbe.ts` into `src/hooks/` in the same change as the second hook |
| Auth | Out of scope for this product increment |

A retried ingest batch must converge to the same corpus state.

## UI kit for the next view

The next interactive view uses MUI with `sx`. Do not install MUI until that view exists. This page is native HTML. Do not add Tailwind, CSS Modules, or styled-components.

## Environment

`.env.example` lists future secrets as comments. The running process does not load them. Do not add `settings.py` until something parses environment.
