from collections.abc import Sequence

from fastapi import FastAPI

from app import documents, health
from app.chunking import TokenChunker
from app.config import Settings
from app.embeddings import OpenAIEmbeddingProvider
from app.ingest import IngestService
from app.vector_stores import open_vector_store


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    store = open_vector_store(resolved)
    embeddings = _LazyOpenAI(resolved)
    ingest = IngestService(
        chunker=TokenChunker(
            model=resolved.embedding_model,
            chunk_size=resolved.chunk_size,
            chunk_overlap=resolved.chunk_overlap,
        ),
        embeddings=embeddings,
        store=store,
        max_upload_bytes=resolved.max_upload_bytes,
    )
    application = FastAPI()
    application.state.settings = resolved
    application.state.store = store
    application.state.ingest = ingest
    application.include_router(health.router)
    application.include_router(documents.router)
    return application


class _LazyOpenAI:
    model: str

    def __init__(self, settings: Settings) -> None:
        self.model = settings.embedding_model
        self._settings = settings
        self._inner: OpenAIEmbeddingProvider | None = None

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if self._inner is None:
            self._inner = OpenAIEmbeddingProvider(
                api_key=self._settings.openai_api_key,
                model=self._settings.embedding_model,
            )
        return self._inner.embed(texts)


app = create_app()
