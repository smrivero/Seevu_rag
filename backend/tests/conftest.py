from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.chunking import TokenChunker
from app.config import Settings
from app.faiss_store import FAISSVectorStore
from app.ingest import IngestService
from app.main import create_app
from app.search import SearchService
from tests.fakes import FakeEmbeddings, assert_never_openai


@pytest.fixture
def fake_embeddings() -> FakeEmbeddings:
    return FakeEmbeddings()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        openai_api_key="",
        embedding_model="text-embedding-3-small",
        vector_store="faiss",
        chunk_size=600,
        chunk_overlap=100,
        max_upload_bytes=1_048_576,
        index_dir=tmp_path / "index",
    )


@pytest.fixture
def client(settings: Settings, fake_embeddings: FakeEmbeddings, monkeypatch) -> TestClient:
    assert_never_openai(monkeypatch)
    application = create_app(settings)
    store = application.state.store
    assert isinstance(store, FAISSVectorStore)
    application.state.ingest = IngestService(
        chunker=TokenChunker(
            model=settings.embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        ),
        embeddings=fake_embeddings,
        store=store,
        max_upload_bytes=settings.max_upload_bytes,
    )
    application.state.search = SearchService(
        embeddings=fake_embeddings,
        store=store,
    )
    return TestClient(application)
