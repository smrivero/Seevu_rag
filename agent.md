# Agent log

## Completed

- Health-only scaffold. FastAPI `GET /health` returns `{"status":"ok"}` from `HealthStatus` with `Literal["ok"]`.
- Frontend probe is a `ProbeState` state machine (`checking` | `live` | `down`). Success copy is `Backend: Connected`. Document title is `RAG Intelligence Platform`.
- Compose publishes frontend on 8080. nginx rewrites `/api/` to backend `/health`. Backend port 8000 is not published.
- pytest covers status, JSON body, empty environment, and OpenAPI literal pin for `status`.
- Compose verified on a live daemon. `GET http://localhost:8080/api/health` returns `{"status":"ok"}`. The browser shows `Backend: Connected`. Port 8000 is unpublished.
- nginx resolves `backend` at request time via Docker DNS `127.0.0.11`, so a missing upstream is a 502 instead of a failed container start.

## Follow-ups

- Second FastAPI router. Include it from `create_app()` with no prefix. Call it as `client.get("/your-path")` on the existing axios instance.
- When that second endpoint lands, add `openapi-typescript` against `create_app().openapi()` and a drift check. Add `dump_openapi.py` in the same change.
- First interactive view. Install MUI and use `sx`. Do not add Tailwind, CSS Modules, or styled-components.
- Move `useBackendProbe.ts` into `src/hooks/` in the same change as the second frontend hook.

## Next steps

- Keep health free of environment and of RAG, OpenAI, Pinecone, FAISS, and auth.
- When ingestion exists, `ingest.py` reads `data/`. A retried batch must converge to the same corpus state.
- First interactive view. Install MUI and use `sx`.
