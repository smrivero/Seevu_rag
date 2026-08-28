# Agent log

## Completed

- Health-only scaffold. FastAPI `GET /health` returns `{"status":"ok"}`.
- Frontend probe `ProbeState` (`checking` | `live` | `down`). Title `RAG Intelligence Platform`. Copy `Backend: Connected`.
- Milestone 2. PDF ingest, OpenAI embeddings, FAISS cosine index under `data/index/`.
- Observability. `GET /stats` and JSON ingest logs.
- Milestone 3. `POST /search` embeds the query through `EmbeddingProvider`, searches `VectorStore`, returns scored chunks. No LLM answer. Logs `search.start`, `search.embedding.done`, `search.faiss.done`, `search.result`.
- Backend pytest: 46 passed. Compose verification passed health, ingest, stats, `POST /api/search` (`Hello Seevu fixture` → `sample.pdf` page 1, score ~0.89), and Playwright `Backend: Connected`.

## Follow-ups

- PDF upload UI. Install MUI and use `sx`.
- RAG answer generation on top of `/search`. Chat, reranking, guardrails, language detection, auth. Not this increment.
- `PineconeVectorStore` behind `open_vector_store()`.

## Next steps

- Keep health free of OpenAI. Missing key is 503 on ingest and search, not on `/health` or `/stats`.
- First interactive view can be search or upload. Install MUI and use `sx`.
- When a new user-facing route ships, fill its file under `.cursor/skills/verify-seevu-rag/features/`.
