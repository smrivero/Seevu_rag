import hashlib


def document_id_for(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def chunk_id_for(document_id: str, page: int, chunk_index: int) -> str:
    return f"{document_id}:{page}:{chunk_index}"
