from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.models import Chunk, IndexedDocument, SearchHit


@dataclass(frozen=True)
class IndexSnapshot:
    type: str
    index_type: str
    vectors: int
    dimension: int
    metric: str
    trained: bool


@dataclass(frozen=True)
class StorageSnapshot:
    faiss_index_bytes: int
    chunks_metadata_bytes: int
    documents_metadata_bytes: int


class VectorStore(Protocol):
    name: str

    def add(
        self,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        ...

    def search(self, vector: Sequence[float], *, limit: int) -> list[SearchHit]:
        ...

    def save(self) -> None:
        ...

    def load(self) -> None:
        ...

    def documents(self) -> list[IndexedDocument]:
        ...

    def get_document(self, document_id: str) -> IndexedDocument | None:
        ...

    def put_document(self, document: IndexedDocument) -> None:
        ...

    def chunks(self) -> list[Chunk]:
        ...

    def index_snapshot(self) -> IndexSnapshot:
        ...

    def storage_snapshot(self) -> StorageSnapshot:
        ...
