# Agent log

## Completed

- Health-only scaffold. FastAPI `GET /health` returns `{"status":"ok"}` from `HealthStatus` with `Literal["ok"]`.
- Frontend probe is a `ProbeState` state machine (`checking` | `live` | `down`). Success copy is `Backend: Connected`. Document title is `RAG Intelligence Platform`.
- Compose publishes frontend on 8080. nginx rewrites `/api/` to the backend. Backend port 8000 is not published.
- pytest covers status, JSON body, empty environment, and OpenAPI literal pin for `status`.
- nginx resolves `backend` at request time via Docker DNS `127.0.0.11`.
- Verification skill at `.cursor/skills/verify-seevu-rag/`.
- Milestone 2. `POST /documents` and `GET /documents`. pypdf page text, `TokenChunker` (600/100), `OpenAIEmbeddingProvider`, `FAISSVectorStore` (cosine via L2-normalized `IndexFlatIP`). Index files under `data/index/` on a Compose volume. Duplicate SHA-256 uploads are idempotent. Tests mock OpenAI.
- Backend pytest: 29 passed. Compose images built. Live `GET /api/health` and Playwright still show `Backend: Connected`. Live `POST /api/documents` returned 503 because `.env` on disk has no `OPENAI_API_KEY`. Re-run `.cursor/skills/verify-seevu-rag/scripts/verify.sh` after the key is set.

## Follow-ups

- PDF upload UI. Install MUI and use `sx`. Move `useBackendProbe.ts` into `src/hooks/` in the same change as the second hook.
- When a frontend consumer needs generated types, add `openapi-typescript` against `create_app().openapi()` and a drift check.
- `PineconeVectorStore` behind `open_vector_store()` without changing `IngestService`.
- RAG answer generation, chat, reranking, guardrails, language detection, auth. Not this increment.

## Next steps

- Put `OPENAI_API_KEY` in `.env` (see `.env.example`) and re-run `.cursor/skills/verify-seevu-rag/scripts/verify.sh` to prove ingest and FAISS persistence on Compose.
- Keep health free of OpenAI. Missing `OPENAI_API_KEY` is a 503 on ingest, not a failed `/health`.
- First interactive view is upload. Install MUI and use `sx`.
- When a new user-facing route ships, fill its file under `.cursor/skills/verify-seevu-rag/features/` and run `/maintain-verification-skill`.
