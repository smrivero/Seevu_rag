from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    filename: str
    page: int
    chunk_index: int
    text: str

    def to_metadata(self) -> dict[str, str | int]:
        return asdict(self)

    @classmethod
    def from_metadata(cls, payload: dict[str, object]) -> Chunk:
        return cls(
            id=str(payload["id"]),
            document_id=str(payload["document_id"]),
            filename=str(payload["filename"]),
            page=int(payload["page"]),
            chunk_index=int(payload["chunk_index"]),
            text=str(payload["text"]),
        )


@dataclass(frozen=True)
class IndexedDocument:
    document_id: str
    filename: str
    pages: int
    chunks: int
    embedding_model: str
    vector_store: str
    status: str

    def to_public(self) -> dict[str, str | int]:
        return asdict(self)

    @classmethod
    def from_public(cls, payload: dict[str, object]) -> IndexedDocument:
        return cls(
            document_id=str(payload["document_id"]),
            filename=str(payload["filename"]),
            pages=int(payload["pages"]),
            chunks=int(payload["chunks"]),
            embedding_model=str(payload["embedding_model"]),
            vector_store=str(payload["vector_store"]),
            status=str(payload["status"]),
        )
