# Reranking

Reranking will reorder retrieved evidence before the answer is written. It is not a user-facing screen of its own today, and it is not in the product yet.

## Sub-features

- `rerank-visible` shows that evidence order changed, or exposes a rank score, if the product chooses to surface it. Not shipped.

## How to get to it (user POV)

- No evidence list or rank display exists.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for an evidence or rank list. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a user-visible evidence list after a query.
- **When it ships.** Drive [RAG query](./rag-query.md). If rerank stays internal, keep this file as `verified-unreachable` for UI and prove order only if the product exposes evidence. Do not invent a rank panel.

## Gotchas

- Internal rerank with no UI is not a Playwright pass. Record that the capability is internal and stop.
- Do not scrape network payloads as a substitute for a user-visible list unless this file is updated to name that contract.
