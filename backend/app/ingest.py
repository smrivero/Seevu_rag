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
from app.events import emit, emit_debug, text_preview
from app.ids import document_id_for
from app.models import IndexedDocument
from app.pdf import is_pdf_upload, parse_pdf
from app.stats import summarize_tokens
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
        safe_name = filename or "upload.pdf"
        emit(
            "ingest.start",
            document_id=document_id,
            filename=safe_name,
            bytes=len(payload),
        )
        existing = self._store.get_document(document_id)
        if existing is not None:
            emit(
                "ingest.done",
                document_id=existing.document_id,
                filename=existing.filename,
                pages=existing.pages,
                chunks=existing.chunks,
                status=existing.status,
                duplicate=True,
            )
            return existing

        pages = parse_pdf(payload)
        emit(
            "pdf.extracted",
            document_id=document_id,
            filename=safe_name,
            pages=len(pages),
        )
        chunks = self._chunker.chunk(
            pages,
            document_id=document_id,
            filename=safe_name,
        )
        if not chunks:
            raise EmptyPdfError()

        token_counts = [self._chunker.token_count(chunk.text) for chunk in chunks]
        tokens = summarize_tokens(token_counts)
        emit(
            "chunking.summary",
            document_id=document_id,
            filename=safe_name,
            pages=len(pages),
            chunks=len(chunks),
            chunk_size=self._chunker.chunk_size,
            chunk_overlap=self._chunker.chunk_overlap,
            min_tokens=tokens.minimum,
            max_tokens=tokens.maximum,
            avg_tokens=tokens.average,
            median_tokens=tokens.median,
        )
        for chunk, token_count in zip(chunks, token_counts, strict=True):
            emit_debug(
                "chunk.detail",
                page=chunk.page,
                chunk_index=chunk.chunk_index,
                token_count=token_count,
                character_count=len(chunk.text),
                preview=text_preview(chunk.text),
            )

        try:
            emit(
                "embeddings.start",
                document_id=document_id,
                chunks=len(chunks),
                model=self._embeddings.model,
            )
            vectors = self._embeddings.embed([chunk.text for chunk in chunks])
            emit(
                "embeddings.done",
                document_id=document_id,
                chunks=len(chunks),
                model=self._embeddings.model,
            )
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
            storage = self._store.storage_snapshot()
            snapshot = self._store.index_snapshot()
            emit(
                "faiss.persisted",
                document_id=document_id,
                vectors=snapshot.vectors,
                faiss_index_bytes=storage.faiss_index_bytes,
                chunks_metadata_bytes=storage.chunks_metadata_bytes,
                documents_metadata_bytes=storage.documents_metadata_bytes,
            )
        except IngestError:
            raise
        except Exception as exc:
            raise IndexingError() from exc
        emit(
            "ingest.done",
            document_id=record.document_id,
            filename=record.filename,
            pages=record.pages,
            chunks=record.chunks,
            status=record.status,
        )
        return record

    def list_documents(self) -> Sequence[IndexedDocument]:
        return self._store.documents()
