from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, ConfigDict

from app.errors import IngestError, MissingFileError
from app.ingest import IngestService
from app.models import IndexedDocument

router = APIRouter()


class DocumentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    filename: str
    pages: int
    chunks: int
    embedding_model: str
    vector_store: str
    status: str

    @classmethod
    def from_domain(cls, document: IndexedDocument) -> "DocumentRecord":
        return cls(**document.to_public())


class DocumentList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    documents: list[DocumentRecord]


def _service(request: Request) -> IngestService:
    return request.app.state.ingest


@router.post("/documents", response_model=DocumentRecord)
async def upload_document(
    request: Request,
    file: UploadFile | None = File(default=None),
) -> DocumentRecord:
    if file is None:
        error = MissingFileError()
        raise HTTPException(status_code=error.status_code, detail=error.public_message)
    try:
        payload = await file.read()
        document = _service(request).ingest(
            filename=file.filename,
            content_type=file.content_type,
            payload=payload,
        )
    except IngestError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.public_message) from None
    return DocumentRecord.from_domain(document)


@router.get("/documents", response_model=DocumentList)
def list_documents(request: Request) -> DocumentList:
    documents = [
        DocumentRecord.from_domain(item) for item in _service(request).list_documents()
    ]
    return DocumentList(documents=documents)
