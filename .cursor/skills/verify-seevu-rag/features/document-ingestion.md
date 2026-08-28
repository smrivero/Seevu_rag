# Document ingestion

Document ingestion will turn files in `data/` into indexed chunks. It is not in the product yet.

## Sub-features

- `ingest-run` starts ingestion from a user control. Not shipped.
- `ingest-idempotent` retries the same batch and converges. Not shipped.

## How to get to it (user POV)

- No ingest button, job status, or `/api/ingest` route exists.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for ingest status copy. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a user-visible ingest control or `POST /api/ingest`.
- **When it ships.** Drive the control, then prove the same batch twice. The second run must not create a second corpus identity. Capture the status text both times.

## Gotchas

- `data/README.md` is documentation, not a running ingest job.
- A retried batch must converge to the same corpus state. Assert that when the feature is live, not before.
