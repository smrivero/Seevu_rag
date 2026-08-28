from app.errors import EmbeddingProviderError
from app.ids import document_id_for
from tests.pdf_fixtures import pdf_bytes


def test_missing_file_returns_400(client) -> None:
    response = client.post("/documents")
    assert response.status_code in {400, 422}


def test_non_pdf_returns_400(client) -> None:
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]
    assert "traceback" not in response.text.lower()


def test_empty_pdf_bytes_return_400(client) -> None:
    response = client.post(
        "/documents",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400


def test_invalid_pdf_returns_422(client) -> None:
    response = client.post(
        "/documents",
        files={"file": ("bad.pdf", b"not-a-pdf", "application/pdf")},
    )
    assert response.status_code == 422
    assert "valid PDF" in response.json()["detail"]


def test_pdf_without_text_returns_422(client) -> None:
    response = client.post(
        "/documents",
        files={"file": ("blank.pdf", pdf_bytes(""), "application/pdf")},
    )
    assert response.status_code == 422


def test_upload_indexes_and_lists_document(client, fake_embeddings) -> None:
    payload = pdf_bytes("Hello Seevu page one", "Hello Seevu page two")
    response = client.post(
        "/documents",
        files={"file": ("example.pdf", payload, "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id_for(payload)
    assert body["filename"] == "example.pdf"
    assert body["pages"] == 2
    assert body["chunks"] > 0
    assert body["embedding_model"] == "text-embedding-3-small"
    assert body["vector_store"] == "faiss"
    assert body["status"] == "indexed"
    assert fake_embeddings.calls

    listed = client.get("/documents")
    assert listed.status_code == 200
    documents = listed.json()["documents"]
    assert len(documents) == 1
    assert documents[0]["document_id"] == body["document_id"]


def test_duplicate_upload_does_not_reembed(client, fake_embeddings) -> None:
    payload = pdf_bytes("Same document twice")
    files = {"file": ("dup.pdf", payload, "application/pdf")}
    first = client.post("/documents", files=files)
    calls = len(fake_embeddings.calls)
    second = client.post(
        "/documents",
        files={"file": ("dup.pdf", payload, "application/pdf")},
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["document_id"] == second.json()["document_id"]
    assert len(fake_embeddings.calls) == calls
    listed = client.get("/documents").json()["documents"]
    assert len(listed) == 1


def test_index_survives_reload(settings, fake_embeddings, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.chunking import TokenChunker
    from app.ingest import IngestService
    from app.main import create_app
    from tests.fakes import assert_never_openai

    assert_never_openai(monkeypatch)
    payload = pdf_bytes("Persisted text")
    first_app = create_app(settings)
    first_app.state.ingest = IngestService(
        chunker=TokenChunker(
            model=settings.embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        ),
        embeddings=fake_embeddings,
        store=first_app.state.store,
        max_upload_bytes=settings.max_upload_bytes,
    )
    first = TestClient(first_app).post(
        "/documents",
        files={"file": ("keep.pdf", payload, "application/pdf")},
    )
    assert first.status_code == 200
    document_id = first.json()["document_id"]

    second_app = create_app(settings)
    listed = TestClient(second_app).get("/documents")
    assert listed.status_code == 200
    ids = [item["document_id"] for item in listed.json()["documents"]]
    assert document_id in ids
    assert (settings.index_dir / "faiss.index").exists()
    assert (settings.index_dir / "chunks.json").exists()
    assert (settings.index_dir / "documents.json").exists()


def test_file_too_large_returns_413(settings, fake_embeddings, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.chunking import TokenChunker
    from app.ingest import IngestService
    from app.main import create_app
    from tests.fakes import assert_never_openai

    assert_never_openai(monkeypatch)
    settings.max_upload_bytes = 32
    application = create_app(settings)
    application.state.ingest = IngestService(
        chunker=TokenChunker(
            model=settings.embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        ),
        embeddings=fake_embeddings,
        store=application.state.store,
        max_upload_bytes=32,
    )
    payload = pdf_bytes("This fixture is larger than thirty two bytes")
    response = TestClient(application).post(
        "/documents",
        files={"file": ("big.pdf", payload, "application/pdf")},
    )
    assert response.status_code == 413


def test_list_starts_empty(client) -> None:
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == {"documents": []}


def test_embedding_failure_returns_502(client, settings) -> None:
    from app.chunking import TokenChunker
    from app.errors import EmbeddingProviderError
    from app.ingest import IngestService

    class BoomEmbeddings:
        model = "text-embedding-3-small"

        def embed(self, texts: list[str]) -> list[list[float]]:
            raise EmbeddingProviderError()

    client.app.state.ingest = IngestService(
        chunker=TokenChunker(
            model=settings.embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        ),
        embeddings=BoomEmbeddings(),
        store=client.app.state.store,
        max_upload_bytes=settings.max_upload_bytes,
    )
    response = client.post(
        "/documents",
        files={"file": ("fail.pdf", pdf_bytes("needs embeddings"), "application/pdf")},
    )
    assert response.status_code == 502
    assert "embedding" in response.json()["detail"].lower()
    assert "traceback" not in response.text.lower()
