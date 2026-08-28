from collections.abc import Sequence

from app.chunking import Chunker
from app.embeddings import EmbeddingProvider
from app.errors import (
    EmptyFileError,
    EmptyPdfError,
    FileTooLargeError,
    IndexingError,
    IngestError,
    InvalidContentTypeError,
    MissingFileError,
)
from app.ids import document_id_for
from app.models import IndexedDocument
from app.pdf import is_pdf_upload, parse_pdf
from app.store import VectorStore


class IngestService:
    def __init__(
        self,
        *,
        chunker: Chunker,
        embeddings: EmbeddingProvider,
        store: VectorStore,
        max_upload_bytes: int,
    ) -> None:
        self._chunker = chunker
        self._embeddings = embeddings
        self._store = store
        self._max_upload_bytes = max_upload_bytes

    def ingest(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        payload: bytes,
    ) -> IndexedDocument:
        if not filename and not payload:
            raise MissingFileError()
        if not is_pdf_upload(filename, content_type):
            raise InvalidContentTypeError()
        if not payload:
            raise EmptyFileError()
        if len(payload) > self._max_upload_bytes:
            raise FileTooLargeError()

        document_id = document_id_for(payload)
        existing = self._store.get_document(document_id)
        if existing is not None:
            return existing

        pages = parse_pdf(payload)
        safe_name = filename or "upload.pdf"
        chunks = self._chunker.chunk(
            pages,
            document_id=document_id,
            filename=safe_name,
        )
        if not chunks:
            raise EmptyPdfError()

        try:
            vectors = self._embeddings.embed([chunk.text for chunk in chunks])
            self._store.add(chunks, vectors)
            record = IndexedDocument(
                document_id=document_id,
                filename=safe_name,
                pages=len(pages),
                chunks=len(chunks),
                embedding_model=self._embeddings.model,
                vector_store=self._store.name,
                status="indexed",
            )
            self._store.put_document(record)
            self._store.save()
        except IngestError:
            raise
        except Exception as exc:
            raise IndexingError() from exc
        return record

    def list_documents(self) -> Sequence[IndexedDocument]:
        return self._store.documents()
