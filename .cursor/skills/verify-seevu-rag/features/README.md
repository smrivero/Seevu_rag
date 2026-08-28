# RAG Intelligence Platform verification map

This directory is the maintained source for verifying user-facing behavior. Read this index before driving the app. Use the matching feature file as the recipe.

## Baseline preconditions

- Drive `http://localhost:8080` served by Docker Compose from the repo root.
- Run `.cursor/skills/verify-seevu-rag/scripts/doctor.sh` and require exit 0.
- Do not run `npm run dev`.
- Do not call `localhost:8000`. The backend port is unpublished.
- Reuse a healthy instance on 8080. Do not start a second Compose stack on that port.

## Driving conventions

- Start from the baseline unless a feature file lists extra preconditions.
- Prefer ARIA roles and accessible names.
- Treat quoted UI copy as literal.
- Run HTTP proof with `scripts/check-health.py`, `scripts/check-ingest.py`, `scripts/check-stats.py`, and `scripts/check-search.py`.
- Run browser proof with `scripts/browser.mjs`.
- Planned features are `verified-unreachable` until the product ships the named route or heading.

## Proof and skip reporting

- Capture the user action and the resulting state, not only the final screen.
- UI proof includes `main` text and a screenshot with the product title visible.
- HTTP proof includes status code and the exact JSON body.
- Record the feature ID with every artifact under `evidence/`.
- Report an unreachable path with the attempted URL or heading and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 and one paragraph. It then uses exactly four H2 sections in this order.

1. `Sub-features`
2. `How to get to it (user POV)`
3. `Driving it with Playwright`
4. `Gotchas`

When a later capability ships, fill its file with real entry points and commands. Add the matching wait and assertion to `scripts/browser.mjs`. Leave product code out of this map.

## Live

- [Health status](./health-status.md) covers `GET /api/health`, the home heading, and `Backend: Connected`.
- [Document ingestion](./document-ingestion.md) covers `POST /api/documents`, `GET /api/documents`, and FAISS files under `data/index/`.
- [Runtime stats](./runtime-stats.md) covers `GET /api/stats`.
- [Semantic search](./semantic-search.md) covers `POST /api/search`.

## Planned

These files exist so the next feature lands in the map instead of a one-off script. They are not live. Do not drive them.

- [PDF upload](./pdf-upload.md)
- [RAG query](./rag-query.md)
- [Citations](./citations.md)
- [Language detection](./language-detection.md)
- [Reranking](./reranking.md)
- [Guardrails](./guardrails.md)
