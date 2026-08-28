# Guardrails

Guardrails will refuse a query or an answer that violates policy and show that refusal to the user. They are not in the product yet.

## Sub-features

- `guardrail-refuse` shows a refused outcome instead of an answer. Not shipped.

## How to get to it (user POV)

- No refusal copy or blocked-query state exists.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for refusal copy. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a query UI plus a documented refused prompt.
- **When it ships.** Submit the documented refused prompt. Assert the refusal text is visible and that no answer body is shown. Capture the prompt and the refusal.

## Gotchas

- `Backend: Unavailable` is a probe failure, not a guardrail.
- Do not use a live harmful prompt that is not listed in this file.
