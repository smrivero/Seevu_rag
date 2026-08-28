import pytest

from app.errors import EmptyFileError, EmptyPdfError, InvalidPdfError
from app.pdf import is_pdf_upload, parse_pdf
from tests.pdf_fixtures import pdf_bytes


def test_pdf_content_type_accepted() -> None:
    assert is_pdf_upload("doc.pdf", "application/pdf")
    assert is_pdf_upload("doc.PDF", "application/octet-stream")
    assert is_pdf_upload("doc.pdf", None)


def test_non_pdf_rejected() -> None:
    assert not is_pdf_upload("notes.txt", "text/plain")
    assert not is_pdf_upload("notes.txt", None)


def test_parse_rejects_empty_bytes() -> None:
    with pytest.raises(EmptyFileError):
        parse_pdf(b"")


def test_parse_rejects_invalid_pdf() -> None:
    with pytest.raises(InvalidPdfError):
        parse_pdf(b"this is not a pdf")


def test_parse_keeps_page_boundaries() -> None:
    payload = pdf_bytes("Page one text", "Page two text")
    pages = parse_pdf(payload)
    assert [page.page for page in pages] == [1, 2]
    assert "Page one" in pages[0].text
    assert "Page two" in pages[1].text
    assert "Page two" not in pages[0].text


def test_parse_rejects_pdf_with_no_text() -> None:
    with pytest.raises(EmptyPdfError):
        parse_pdf(pdf_bytes("", ""))
