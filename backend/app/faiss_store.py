from __future__ import annotations

import json
import threading
from collections.abc import Sequence
from pathlib import Path

import faiss
import numpy as np

from app.errors import IndexingError
from app.models import Chunk, IndexedDocument, SearchHit
from app.store import IndexSnapshot, StorageSnapshot


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return matrix / norms


class FAISSVectorStore:
    name = "faiss"

    def __init__(self, index_dir: Path) -> None:
        self._dir = index_dir
        self._lock = threading.Lock()
        self._index: faiss.IndexFlatIP | None = None
        self._chunk_by_id: dict[str, Chunk] = {}
        self._row_ids: list[str] = []
        self._documents: dict[str, IndexedDocument] = {}

    def add(
        self,
        chunks: Sequence[Chunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise IndexingError()
        if not chunks:
            return
        matrix = np.ascontiguousarray(_normalize(np.asarray(vectors, dtype=np.float32)))
        if matrix.ndim != 2:
            raise IndexingError()
        with self._lock:
            if self._index is None:
                self._index = faiss.IndexFlatIP(matrix.shape[1])
            if matrix.shape[1] != self._index.d:
                raise IndexingError()
            self._index.add(matrix)
            for chunk in chunks:
                self._chunk_by_id[chunk.id] = chunk
                self._row_ids.append(chunk.id)

    def search(self, vector: Sequence[float], *, limit: int) -> list[SearchHit]:
        if limit <= 0:
            return []
        query = np.ascontiguousarray(_normalize(np.asarray([vector], dtype=np.float32)))
        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []
            k = min(limit, self._index.ntotal)
            scores, indices = self._index.search(query, k)
            found: list[SearchHit] = []
            for score, row in zip(scores[0], indices[0], strict=True):
                if row < 0 or row >= len(self._row_ids):
                    continue
                chunk = self._chunk_by_id.get(self._row_ids[int(row)])
                if chunk is None:
                    continue
                found.append(
                    SearchHit(
                        score=float(score),
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        filename=chunk.filename,
                        page=chunk.page,
                        chunk_index=chunk.chunk_index,
                        text=chunk.text,
                    )
                )
            return found

    def save(self) -> None:
        with self._lock:
            try:
                self._dir.mkdir(parents=True, exist_ok=True)
                documents = [doc.to_public() for doc in self._documents.values()]
                chunks = {
                    chunk_id: chunk.to_metadata()
                    for chunk_id, chunk in self._chunk_by_id.items()
                }
                payload = {
                    "row_ids": self._row_ids,
                    "chunks": chunks,
                }
                self._write_json("documents.json", documents)
                self._write_json("chunks.json", payload)
                if self._index is not None:
                    faiss.write_index(self._index, str(self._dir / "faiss.index"))
            except OSError as exc:
                raise IndexingError() from exc

    def load(self) -> None:
        with self._lock:
            documents_path = self._dir / "documents.json"
            chunks_path = self._dir / "chunks.json"
            index_path = self._dir / "faiss.index"
            present = (
                documents_path.exists(),
                chunks_path.exists(),
                index_path.exists(),
            )
            if not any(present):
                return
            if not all(present):
                raise IndexingError()
            try:
                documents_raw = json.loads(documents_path.read_text(encoding="utf-8"))
                chunks_raw = json.loads(chunks_path.read_text(encoding="utf-8"))
                self._documents = {
                    item["document_id"]: IndexedDocument.from_public(item)
                    for item in documents_raw
                }
                self._row_ids = list(chunks_raw["row_ids"])
                self._chunk_by_id = {
                    chunk_id: Chunk.from_metadata(meta)
                    for chunk_id, meta in chunks_raw["chunks"].items()
                }
                self._index = faiss.read_index(str(index_path))
                if self._index.ntotal != len(self._row_ids):
                    raise IndexingError()
            except (
                OSError,
                RuntimeError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                raise IndexingError() from exc

    def documents(self) -> list[IndexedDocument]:
        with self._lock:
            return list(self._documents.values())

    def get_document(self, document_id: str) -> IndexedDocument | None:
        with self._lock:
            return self._documents.get(document_id)

    def put_document(self, document: IndexedDocument) -> None:
        with self._lock:
            self._documents[document.document_id] = document

    def chunks(self) -> list[Chunk]:
        with self._lock:
            return [self._chunk_by_id[chunk_id] for chunk_id in self._row_ids if chunk_id in self._chunk_by_id]

    def index_snapshot(self) -> IndexSnapshot:
        with self._lock:
            if self._index is None:
                return IndexSnapshot(
                    type=self.name,
                    index_type="IndexFlatIP",
                    vectors=0,
                    dimension=0,
                    metric="cosine_similarity",
                    trained=False,
                )
            return IndexSnapshot(
                type=self.name,
                index_type=type(self._index).__name__,
                vectors=int(self._index.ntotal),
                dimension=int(self._index.d),
                metric="cosine_similarity",
                trained=bool(self._index.is_trained),
            )

    def storage_snapshot(self) -> StorageSnapshot:
        return StorageSnapshot(
            faiss_index_bytes=_file_size(self._dir / "faiss.index"),
            chunks_metadata_bytes=_file_size(self._dir / "chunks.json"),
            documents_metadata_bytes=_file_size(self._dir / "documents.json"),
        )

    def _write_json(self, name: str, payload: object) -> None:
        path = self._dir / name
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(path)


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0
