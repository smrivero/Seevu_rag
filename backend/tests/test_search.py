import json
import logging

from app.errors import EmbeddingProviderError
from app.search import SearchService
from tests.pdf_fixtures import pdf_bytes


def _event_names(messages: list[str]) -> list[str]:
    return [json.loads(message)["event"] for message in messages]


def test_empty_query_is_rejected(client) -> None:
    response = client.post("/search", json={"query": "   ", "top_k": 5})
    assert response.status_code in {400, 422}
    assert "traceback" not in response.text.lower()


def test_missing_query_is_rejected(client) -> None:
    response = client.post("/search", json={"top_k": 5})
    assert response.status_code == 422


def test_top_k_zero_is_rejected(client) -> None:
    response = client.post("/search", json={"query": "hello", "top_k": 0})
    assert response.status_code in {400, 422}


def test_empty_index_returns_no_results(client) -> None:
    response = client.post("/search", json={"query": "anything", "top_k": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "anything"
    assert body["results"] == []


def test_search_uses_mocked_embeddings_and_keeps_metadata(client, fake_embeddings) -> None:
    payload = pdf_bytes("alpha widgets on page one", "bravo gadgets on page two")
    uploaded = client.post(
        "/documents",
        files={"file": ("sample.pdf", payload, "application/pdf")},
    )
    assert uploaded.status_code == 200
    assert fake_embeddings.calls
    embed_calls = len(fake_embeddings.calls)

    response = client.post(
        "/search",
        json={"query": "alpha widgets on page one", "top_k": 5},
    )
    assert response.status_code == 200
    assert len(fake_embeddings.calls) == embed_calls + 1
    body = response.json()
    assert body["query"] == "alpha widgets on page one"
    assert body["results"]
    first = body["results"][0]
    assert first["filename"] == "sample.pdf"
    assert first["page"] >= 1
    assert first["chunk_index"] >= 0
    assert first["chunk_id"]
    assert first["document_id"] == uploaded.json()["document_id"]
    assert first["text"]
    assert isinstance(first["score"], float)
    assert "traceback" not in response.text.lower()


def test_results_are_ordered_highest_score_first(client) -> None:
    payload = pdf_bytes("unique alpha phrase about widgets", "unrelated bravo text about oceans")
    client.post(
        "/documents",
        files={"file": ("ranked.pdf", payload, "application/pdf")},
    )
    response = client.post(
        "/search",
        json={"query": "unique alpha phrase about widgets", "top_k": 5},
    )
    assert response.status_code == 200
    scores = [item["score"] for item in response.json()["results"]]
    assert scores == sorted(scores, reverse=True)
    assert "alpha" in response.json()["results"][0]["text"].lower()


def test_top_k_caps_at_indexed_chunks(client) -> None:
    payload = pdf_bytes("first page of a short pdf", "second page of a short pdf")
    uploaded = client.post(
        "/documents",
        files={"file": ("short.pdf", payload, "application/pdf")},
    )
    chunk_count = uploaded.json()["chunks"]
    response = client.post(
        "/search",
        json={"query": "short pdf", "top_k": 10},
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) == chunk_count
    limited = client.post(
        "/search",
        json={"query": "short pdf", "top_k": 1},
    )
    assert limited.status_code == 200
    assert len(limited.json()["results"]) == 1


def test_embedding_failure_returns_502(client, settings) -> None:
    class BoomEmbeddings:
        model = "text-embedding-3-small"

        def embed(self, texts: list[str]) -> list[list[float]]:
            raise EmbeddingProviderError()

    client.app.state.search = SearchService(
        embeddings=BoomEmbeddings(),
        store=client.app.state.store,
    )
    response = client.post("/search", json={"query": "needs embeddings", "top_k": 5})
    assert response.status_code == 502
    assert "embedding" in response.json()["detail"].lower()
    assert "traceback" not in response.text.lower()


def test_search_emits_structured_info_events(client) -> None:
    client.post(
        "/documents",
        files={"file": ("logged.pdf", pdf_bytes("Logged search text"), "application/pdf")},
    )
    messages: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            messages.append(record.getMessage())

    logger = logging.getLogger("seevu")
    handler = Capture()
    logger.addHandler(handler)
    try:
        response = client.post(
            "/search",
            json={"query": "Logged search text", "top_k": 5},
        )
    finally:
        logger.removeHandler(handler)
    assert response.status_code == 200
    names = _event_names(messages)
    assert names == [
        "search.start",
        "search.embedding.done",
        "search.faiss.done",
        "search.result",
    ]
    faiss_done = json.loads(messages[2])
    for key in (
        "query",
        "requested_top_k",
        "returned_results",
        "best_score",
        "latency_ms",
    ):
        assert key in faiss_done
    assert faiss_done["requested_top_k"] == 5
    assert faiss_done["returned_results"] >= 1
    result = json.loads(messages[3])
    assert "text" not in result["results"][0]
    assert len(result["results"][0]["preview"]) <= 120
