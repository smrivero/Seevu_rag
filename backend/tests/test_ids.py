import hashlib

from app.ids import document_id_for


def test_document_id_is_sha256_hex() -> None:
    payload = b"%PDF-1.4 sample"
    digest = document_id_for(payload)
    assert len(digest) == 64
    assert digest == hashlib.sha256(payload).hexdigest()


def test_document_id_is_deterministic() -> None:
    payload = b"same-bytes"
    assert document_id_for(payload) == document_id_for(payload)


def test_different_bytes_get_different_ids() -> None:
    assert document_id_for(b"a") != document_id_for(b"b")
