Indexed FAISS data lives in `index/` (`faiss.index`, `chunks.json`, `documents.json`).

Compose bind-mounts `data/index` to `/data/index` in the backend container so the index survives `docker compose restart`. Do not commit the generated files.
