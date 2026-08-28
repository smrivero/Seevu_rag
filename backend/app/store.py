from collections.abc import Sequence
from typing import Protocol

from app.models import Chunk, IndexedDocument


class VectorStore(Protocol):
    name: str

    def add(
        self,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        ...

    def search(self, vector: Sequence[float], *, limit: int) -> list[Chunk]:
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
