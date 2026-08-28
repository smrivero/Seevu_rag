import json
import logging
import sys

_LOGGER = logging.getLogger("seevu")
_PREVIEW_CHARS = 120


def configure_logging(level: str) -> None:
    resolved = getattr(logging, level.upper(), logging.INFO)
    _LOGGER.setLevel(resolved)
    if not _LOGGER.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        _LOGGER.addHandler(handler)
    _LOGGER.propagate = False


def emit(event: str, **fields: object) -> None:
    _LOGGER.info(json.dumps({"event": event, **fields}, ensure_ascii=False))


def emit_debug(event: str, **fields: object) -> None:
    if _LOGGER.isEnabledFor(logging.DEBUG):
        _LOGGER.debug(json.dumps({"event": event, **fields}, ensure_ascii=False))


def text_preview(text: str) -> str:
    if len(text) <= _PREVIEW_CHARS:
        return text
    return text[:_PREVIEW_CHARS]
