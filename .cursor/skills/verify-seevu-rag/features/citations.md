# Citations

Citations will show the source spans that support an answer. They are not in the product yet.

## Sub-features

- `citations-list` lists sources on a successful answer. Not shipped.
- `citations-open` opens a cited span. Not shipped.

## How to get to it (user POV)

- No citations list exists. There is no answered query to hang them on.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for a list named `Citations`. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a completed RAG answer that renders citations.
- **When it ships.** Drive [RAG query](./rag-query.md) first. Then assert at least one citation is visible and that opening it shows source text. Capture the answer and the citation list together.

## Gotchas

- Do not mark citations verified because a query returned text. The citation list is a separate observable.
- An answer with no citations, once the product requires them, is a fail.
