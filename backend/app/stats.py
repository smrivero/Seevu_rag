from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from statistics import mean, median

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from app.chunking import TokenChunker
from app.models import Chunk, IndexedDocument
from app.store import IndexSnapshot, StorageSnapshot, VectorStore

router = APIRouter()


@dataclass(frozen=True)
class TokenSummary:
    minimum: int
    maximum: int
    average: float
    median: float


@dataclass(frozen=True)
class DocumentStat:
    filename: str
    pages: int
    chunks: int


@dataclass(frozen=True)
class RuntimeStats:
    vector_store: IndexSnapshot
    documents_count: int
    pages: int
    chunks: int
    document_stats: tuple[DocumentStat, ...]
    chunk_size: int
    chunk_overlap: int
    token_summary: TokenSummary
    embedding_provider: str
    embedding_model: str
    storage: StorageSnapshot


def summarize_tokens(counts: Sequence[int]) -> TokenSummary:
    if not counts:
        return TokenSummary(minimum=0, maximum=0, average=0.0, median=0.0)
    return TokenSummary(
        minimum=min(counts),
        maximum=max(counts),
        average=round(float(mean(counts)), 2),
        median=round(float(median(counts)), 2),
    )


def assemble_runtime_stats(
    *,
    index: IndexSnapshot,
    documents: Sequence[IndexedDocument],
    chunks: Sequence[Chunk],
    storage: StorageSnapshot,
    chunk_size: int,
    chunk_overlap: int,
    token_counts: Sequence[int],
    embedding_model: str,
    embedding_provider: str = "openai",
) -> RuntimeStats:
    ordered = tuple(
        DocumentStat(filename=item.filename, pages=item.pages, chunks=item.chunks)
        for item in sorted(documents, key=lambda item: item.filename)
    )
    return RuntimeStats(
        vector_store=index,
        documents_count=len(documents),
        pages=sum(item.pages for item in documents),
        chunks=len(chunks),
        document_stats=ordered,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        token_summary=summarize_tokens(token_counts),
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        storage=storage,
    )


class VectorStoreStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    index_type: str
    vectors: int
    dimension: int
    metric: str
    trained: bool


class CorpusStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    documents: int
    pages: int
    chunks: int


class DocumentStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str
    pages: int
    chunks: int


class ChunkingStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_size: int
    chunk_overlap: int
    min_chunk_tokens: int
    max_chunk_tokens: int
    average_chunk_tokens: float
    median_chunk_tokens: float


class EmbeddingsStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str


class StorageStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    faiss_index_bytes: int
    chunks_metadata_bytes: int
    documents_metadata_bytes: int


class RuntimeStatsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector_store: VectorStoreStatsModel
    corpus: CorpusStatsModel
    documents: list[DocumentStatsModel]
    chunking: ChunkingStatsModel
    embeddings: EmbeddingsStatsModel
    storage: StorageStatsModel

    @classmethod
    def from_domain(cls, stats: RuntimeStats) -> RuntimeStatsModel:
        snapshot = stats.vector_store
        tokens = stats.token_summary
        storage = stats.storage
        return cls(
            vector_store=VectorStoreStatsModel(
                type=snapshot.type,
                index_type=snapshot.index_type,
                vectors=snapshot.vectors,
                dimension=snapshot.dimension,
                metric=snapshot.metric,
                trained=snapshot.trained,
            ),
            corpus=CorpusStatsModel(
                documents=stats.documents_count,
                pages=stats.pages,
                chunks=stats.chunks,
            ),
            documents=[
                DocumentStatsModel(
                    filename=item.filename,
                    pages=item.pages,
                    chunks=item.chunks,
                )
                for item in stats.document_stats
            ],
            chunking=ChunkingStatsModel(
                chunk_size=stats.chunk_size,
                chunk_overlap=stats.chunk_overlap,
                min_chunk_tokens=tokens.minimum,
                max_chunk_tokens=tokens.maximum,
                average_chunk_tokens=tokens.average,
                median_chunk_tokens=tokens.median,
            ),
            embeddings=EmbeddingsStatsModel(
                provider=stats.embedding_provider,
                model=stats.embedding_model,
            ),
            storage=StorageStatsModel(
                faiss_index_bytes=storage.faiss_index_bytes,
                chunks_metadata_bytes=storage.chunks_metadata_bytes,
                documents_metadata_bytes=storage.documents_metadata_bytes,
            ),
        )


def collect_runtime_stats(
    *,
    store: VectorStore,
    chunker: TokenChunker,
    embedding_model: str,
) -> RuntimeStats:
    chunks = store.chunks()
    return assemble_runtime_stats(
        index=store.index_snapshot(),
        documents=store.documents(),
        chunks=chunks,
        storage=store.storage_snapshot(),
        chunk_size=chunker.chunk_size,
        chunk_overlap=chunker.chunk_overlap,
        token_counts=[chunker.token_count(chunk.text) for chunk in chunks],
        embedding_model=embedding_model,
    )


@router.get("/stats", response_model=RuntimeStatsModel)
def get_stats(request: Request) -> RuntimeStatsModel:
    return RuntimeStatsModel.from_domain(
        collect_runtime_stats(
            store=request.app.state.store,
            chunker=request.app.state.chunker,
            embedding_model=request.app.state.settings.embedding_model,
        )
    )
