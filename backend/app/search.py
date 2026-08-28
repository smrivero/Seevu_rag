from __future__ import annotations

import time
from dataclasses import dataclass

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.embeddings import EmbeddingProvider
from app.errors import (
    AppError,
    EmptyQueryError,
    InvalidTopKError,
    SearchFailedError,
)
from app.events import emit, text_preview
from app.models import SearchHit
from app.store import VectorStore

DEFAULT_TOP_K = 5
MAX_TOP_K = 100

router = APIRouter()


@dataclass(frozen=True)
class SearchAnswer:
    query: str
    results: tuple[SearchHit, ...]


class SearchService:
    def __init__(self, *, embeddings: EmbeddingProvider, store: VectorStore) -> None:
        self._embeddings = embeddings
        self._store = store

    def search(self, *, query: str, top_k: int) -> SearchAnswer:
        stripped = query.strip()
        if not stripped:
            raise EmptyQueryError()
        if top_k < 1 or top_k > MAX_TOP_K:
            raise InvalidTopKError()

        emit("search.start", query=stripped, top_k=top_k)
        try:
            vectors = self._embeddings.embed([stripped])
        except AppError:
            raise
        except Exception as exc:
            raise SearchFailedError() from exc
        if len(vectors) != 1:
            raise SearchFailedError()
        emit(
            "search.embedding.done",
            query=stripped,
            model=self._embeddings.model,
        )

        started = time.perf_counter()
        try:
            hits = self._store.search(vectors[0], limit=top_k)
        except AppError:
            raise
        except Exception as exc:
            raise SearchFailedError() from exc
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        ordered = tuple(sorted(hits, key=lambda item: item.score, reverse=True))
        best_score = ordered[0].score if ordered else None
        emit(
            "search.faiss.done",
            query=stripped,
            requested_top_k=top_k,
            returned_results=len(ordered),
            best_score=best_score,
            latency_ms=latency_ms,
        )
        emit(
            "search.result",
            query=stripped,
            count=len(ordered),
            results=[
                {
                    "score": hit.score,
                    "chunk_id": hit.chunk_id,
                    "filename": hit.filename,
                    "page": hit.page,
                    "chunk_index": hit.chunk_index,
                    "preview": text_preview(hit.text),
                }
                for hit in ordered
            ],
        )
        return SearchAnswer(query=stripped, results=ordered)


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=MAX_TOP_K)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("A search query is required.")
        return stripped


class SearchHitModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float
    chunk_id: str
    document_id: str
    filename: str
    page: int
    chunk_index: int
    text: str

    @classmethod
    def from_domain(cls, hit: SearchHit) -> SearchHitModel:
        return cls(
            score=hit.score,
            chunk_id=hit.chunk_id,
            document_id=hit.document_id,
            filename=hit.filename,
            page=hit.page,
            chunk_index=hit.chunk_index,
            text=hit.text,
        )


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    results: list[SearchHitModel]

    @classmethod
    def from_domain(cls, answer: SearchAnswer) -> SearchResponse:
        return cls(
            query=answer.query,
            results=[SearchHitModel.from_domain(hit) for hit in answer.results],
        )


@router.post("/search", response_model=SearchResponse)
def post_search(request: Request, body: SearchRequest) -> SearchResponse:
    try:
        answer = request.app.state.search.search(query=body.query, top_k=body.top_k)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.public_message) from None
    return SearchResponse.from_domain(answer)
