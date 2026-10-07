from fastapi import APIRouter, HTTPException, UploadFile, status

from app.models.schemas import DocumentResponse
from app.rag.embeddings import EmbeddingError
from app.rag.loader import DocumentLoadError
from app.rag.vector_store import VectorStoreError
from app.services.document_service import (
    MAX_UPLOAD_BYTES,
    DocumentNotFoundError,
    DocumentServiceError,
    FileTooLargeError,
    InvalidDocumentError,
    add_document,
    list_documents,
    remove_document,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Every error our own code raises on purpose. Their messages are user-safe.
# Anything NOT in this tuple is a genuine bug: FastAPI turns it into a plain
# "Internal Server Error" 500, without exposing a stack trace to the client.
HANDLED_ERRORS = (
    DocumentServiceError,
    DocumentLoadError,
    EmbeddingError,
    VectorStoreError,
)


def _to_http_error(error: Exception) -> HTTPException:
    """Translate one of our errors into an HTTP error with the right status code."""
    # Order matters: the specific service errors must be checked before their
    # parent class DocumentServiceError.
    if isinstance(error, InvalidDocumentError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(error, FileTooLargeError):
        code = status.HTTP_413_CONTENT_TOO_LARGE
    elif isinstance(error, DocumentNotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, DocumentLoadError):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT  # right type, unreadable content
    elif isinstance(error, EmbeddingError):
        code = status.HTTP_502_BAD_GATEWAY  # Gemini (upstream) failed
    elif isinstance(error, VectorStoreError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE  # our database failed
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR  # e.g. registry file problem
    return HTTPException(status_code=code, detail=str(error))


# NOTE: these are plain "def" functions on purpose. Ingestion is slow, blocking
# work (PDF reading, Gemini calls). FastAPI runs plain "def" endpoints in a
# worker thread, so one slow upload does not freeze the whole server.
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile) -> DocumentResponse:
    # Read at most one byte more than the limit. A huge file is not loaded fully
    # into memory, yet add_document() can still see it is too big and reject it.
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    try:
        return add_document(file.filename or "", content)
    except HANDLED_ERRORS as error:
        raise _to_http_error(error) from error


@router.get("", response_model=list[DocumentResponse])
def get_documents() -> list[DocumentResponse]:
    try:
        return list_documents()
    except HANDLED_ERRORS as error:
        raise _to_http_error(error) from error


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str) -> None:
    try:
        remove_document(document_id)
    except HANDLED_ERRORS as error:
        raise _to_http_error(error) from error