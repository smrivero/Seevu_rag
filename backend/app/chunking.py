from collections.abc import Sequence
from typing import Protocol

import tiktoken

from app.ids import chunk_id_for
from app.models import Chunk, PageText


class Chunker(Protocol):
    def chunk(
        self,
        pages: Sequence[PageText],
        *,
        document_id: str,
        filename: str,
    ) -> list[Chunk]:
        ...


class TokenChunker:
    def __init__(self, *, model: str, chunk_size: int, chunk_overlap: int) -> None:
        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(
        self,
        pages: Sequence[PageText],
        *,
        document_id: str,
        filename: str,
    ) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page in pages:
            chunks.extend(
                self._chunk_page(
                    page,
                    document_id=document_id,
                    filename=filename,
                )
            )
        return chunks

    def _chunk_page(
        self,
        page: PageText,
        *,
        document_id: str,
        filename: str,
    ) -> list[Chunk]:
        tokens = self._encoding.encode(page.text)
        if not tokens:
            return []
        pieces: list[Chunk] = []
        start = 0
        index = 0
        while start < len(tokens):
            end = min(start + self._chunk_size, len(tokens))
            text = self._encoding.decode(tokens[start:end]).strip()
            if text:
                pieces.append(
                    Chunk(
                        id=chunk_id_for(document_id, page.page, index),
                        document_id=document_id,
                        filename=filename,
                        page=page.page,
                        chunk_index=index,
                        text=text,
                    )
                )
                index += 1
            if end == len(tokens):
                break
            start = max(end - self._chunk_overlap, start + 1)
        return pieces
