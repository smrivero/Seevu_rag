# Language detection

Language detection will identify the language of a question or document and keep that choice visible. It is not in the product yet.

## Sub-features

- `language-detect` shows the detected language on a query or ingest item. Not shipped.

## How to get to it (user POV)

- No language badge or control exists.

## Driving it with Playwright

Preconditions:

- None. Do not drive this feature.

- **Reach.** Open `http://localhost:8080` and look for visible language copy. None is present.
- **Report.** Record `verified-unreachable`. Attempted origin `http://localhost:8080`. Unmet precondition is a language indicator tied to a query or document.
- **When it ships.** Submit a known-language sample and assert the shown language code or name. Capture the input and the indicator.

## Gotchas

- Browser `lang="en"` on `index.html` is the page locale, not detection.
- Do not treat a missing badge as a pass.
