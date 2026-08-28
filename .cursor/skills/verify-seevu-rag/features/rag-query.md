# RAG query

RAG query will let a user ask a question against the ingested corpus and read an answer. It is not in the product yet.

## Sub-features

- `query-submit` sends a question from the page. Not shipped.
- `query-answer` shows an answer after retrieval. Not shipped.

## How to get to it (user POV)

- No question field, submit control, or `/api/query` route exists.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for a textbox named for a question. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a question textbox or `POST /api/query`.
- **When it ships.** Fill the question, submit, wait for the answer region, and capture that region plus the request. Do not assert on a mocked LLM.

## Gotchas

- Health `Backend: Connected` is not a query result.
- Wait for the answer region, not a fixed sleep.
