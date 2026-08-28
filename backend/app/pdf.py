from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PyPdfError

from app.errors import EmptyFileError, EmptyPdfError, InvalidPdfError
from app.models import PageText

_PDF_TYPES = {"application/pdf", "application/x-pdf"}


def is_pdf_upload(filename: str | None, content_type: str | None) -> bool:
    name = (filename or "").lower()
    media = (content_type or "").split(";")[0].strip().lower()
    if media in _PDF_TYPES:
        return True
    return name.endswith(".pdf") and media in {"", "application/octet-stream"}


def parse_pdf(payload: bytes) -> list[PageText]:
    if not payload:
        raise EmptyFileError()
    try:
        reader = PdfReader(BytesIO(payload))
        pages: list[PageText] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(PageText(page=index, text=text))
    except (PdfReadError, PyPdfError, ValueError, OSError) as exc:
        raise InvalidPdfError() from exc
    if not pages:
        raise EmptyPdfError()
    if not any(page.text.strip() for page in pages):
        raise EmptyPdfError()
    return pages
