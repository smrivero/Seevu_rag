import json
import logging

from app.chunking import TokenChunker
from app.events import text_preview
from app.stats import summarize_tokens
from tests.pdf_fixtures import pdf_bytes


def _event_names(messages: list[str]) -> list[str]:
    names: list[str] = []
    for message in messages:
        payload = json.loads(message)
        names.append(str(payload["event"]))
    return names


def _forbidden_keys(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = key.lower()
            if lowered in {"api_key", "openai_api_key", "text"}:
                found.append(key)
            found.extend(_forbidden_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_forbidden_keys(item))
    return found


def test_token_summary_empty() -> None:
    summary = summarize_tokens([])
    assert summary.minimum == 0
    assert summary.maximum == 0
    assert summary.average == 0.0
    assert summary.median == 0.0


def test_token_summary_min_max_mean_median() -> None:
    summary = summarize_tokens([1, 2, 3, 4])
    assert summary.minimum == 1
    assert summary.maximum == 4
    assert summary.average == 2.5
    assert summary.median == 2.5


def test_text_preview_truncates_to_120_chars() -> None:
    text = "a" * 200
    preview = text_preview(text)
    assert len(preview) == 120
    assert preview == text[:120]


def test_stats_empty_index(client) -> None:
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["vector_store"]["type"] == "faiss"
    assert body["vector_store"]["index_type"] == "IndexFlatIP"
    assert body["vector_store"]["vectors"] == 0
    assert body["vector_store"]["dimension"] == 0
    assert body["vector_store"]["metric"] == "cosine_similarity"
    assert body["vector_store"]["trained"] is False
    assert body["corpus"] == {"documents": 0, "pages": 0, "chunks": 0}
    assert body["documents"] == []
    assert body["chunking"]["chunk_size"] == 600
    assert body["chunking"]["chunk_overlap"] == 100
    assert body["chunking"]["min_chunk_tokens"] == 0
    assert body["chunking"]["max_chunk_tokens"] == 0
    assert body["embeddings"]["provider"] == "openai"
    assert body["embeddings"]["model"] == "text-embedding-3-small"
    assert body["storage"]["faiss_index_bytes"] == 0
    assert _forbidden_keys(body) == []


def test_stats_after_ingest_reads_faiss_and_metadata(client) -> None:
    payload = pdf_bytes("Hello Seevu stats page one", "Hello Seevu stats page two")
    uploaded = client.post(
        "/documents",
        files={"file": ("sample.pdf", payload, "application/pdf")},
    )
    assert uploaded.status_code == 200
    ingest_body = uploaded.json()

    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    snapshot = body["vector_store"]
    assert snapshot["type"] == "faiss"
    assert snapshot["index_type"] == "IndexFlatIP"
    assert snapshot["vectors"] == ingest_body["chunks"]
    assert snapshot["dimension"] > 0
    assert snapshot["metric"] == "cosine_similarity"
    assert snapshot["trained"] is True
    assert body["corpus"]["documents"] == 1
    assert body["corpus"]["pages"] == ingest_body["pages"]
    assert body["corpus"]["chunks"] == ingest_body["chunks"]
    assert body["documents"] == [
        {
            "filename": "sample.pdf",
            "pages": ingest_body["pages"],
            "chunks": ingest_body["chunks"],
        }
    ]
    chunking = body["chunking"]
    assert chunking["min_chunk_tokens"] > 0
    assert chunking["max_chunk_tokens"] >= chunking["min_chunk_tokens"]
    assert chunking["average_chunk_tokens"] > 0
    assert chunking["median_chunk_tokens"] > 0
    assert body["storage"]["faiss_index_bytes"] > 0
    assert body["storage"]["chunks_metadata_bytes"] > 0
    assert body["storage"]["documents_metadata_bytes"] > 0
    assert _forbidden_keys(body) == []
    assert "openai_api_key" not in json.dumps(body)
    assert "Hello Seevu stats page one" not in json.dumps(body)


def test_stats_token_counts_use_token_chunker(client) -> None:
    payload = pdf_bytes("token counting sample text")
    client.post(
        "/documents",
        files={"file": ("tokens.pdf", payload, "application/pdf")},
    )
    store = client.app.state.store
    chunker = TokenChunker(
        model="text-embedding-3-small",
        chunk_size=600,
        chunk_overlap=100,
    )
    expected = [chunker.token_count(chunk.text) for chunk in store.chunks()]
    body = client.get("/stats").json()["chunking"]
    assert body["min_chunk_tokens"] == min(expected)
    assert body["max_chunk_tokens"] == max(expected)


def test_ingest_emits_structured_info_events(client) -> None:
    messages: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            messages.append(record.getMessage())

    logger = logging.getLogger("seevu")
    handler = Capture()
    logger.addHandler(handler)
    try:
        response = client.post(
            "/documents",
            files={"file": ("logged.pdf", pdf_bytes("Logged ingest text"), "application/pdf")},
        )
    finally:
        logger.removeHandler(handler)
    assert response.status_code == 200
    names = _event_names(messages)
    assert names == [
        "ingest.start",
        "pdf.extracted",
        "chunking.summary",
        "embeddings.start",
        "embeddings.done",
        "faiss.persisted",
        "ingest.done",
    ]
    summary = json.loads(messages[2])
    assert summary["event"] == "chunking.summary"
    for key in (
        "document_id",
        "filename",
        "pages",
        "chunks",
        "chunk_size",
        "chunk_overlap",
        "min_tokens",
        "max_tokens",
        "avg_tokens",
        "median_tokens",
    ):
        assert key in summary
    joined = "\n".join(messages)
    assert "Logged ingest text" not in joined
    assert all("traceback" not in message.lower() for message in messages)


def test_health_still_works_with_stats_router(settings, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app
    from tests.fakes import assert_never_openai

    assert_never_openai(monkeypatch)
    client = TestClient(create_app(settings))
    health = client.get("/health")
    stats = client.get("/stats")
    assert health.json() == {"status": "ok"}
    assert stats.status_code == 200
    assert stats.json()["corpus"]["documents"] == 0
