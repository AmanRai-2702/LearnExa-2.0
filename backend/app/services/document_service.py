import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import DocumentResponse
from app.rag import vector_store
from app.rag.loader import SUPPORTED_EXTENSIONS
from app.rag.pipeline import ingest_document

# backend/app/services/document_service.py -> parents[2] is the backend folder.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REGISTRY_FILE = DATA_DIR / "documents.json"

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


class DocumentServiceError(Exception):
    """Base class. Messages are safe to show to users."""


class InvalidDocumentError(DocumentServiceError):
    """The file is not acceptable (wrong type or empty)."""


class FileTooLargeError(DocumentServiceError):
    """The file is bigger than MAX_UPLOAD_BYTES."""


class DocumentNotFoundError(DocumentServiceError):
    """No document exists with the given id."""


def _read_registry() -> list[dict]:
    """Load the list of document records (empty list if nothing uploaded yet)."""
    if not REGISTRY_FILE.exists():
        return []
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise DocumentServiceError("Could not read the list of documents.") from exc


def _write_registry(records: list[dict]) -> None:
    """Save the records. We write a temp file first, then swap it in, so a crash
    in the middle of writing cannot leave a half-written registry."""
    try:
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp_file = REGISTRY_FILE.with_suffix(".json.tmp")
        temp_file.write_text(json.dumps(records, indent=2), encoding="utf-8")
        temp_file.replace(REGISTRY_FILE)
    except OSError as exc:
        raise DocumentServiceError("Could not save the list of documents.") from exc


def add_document(filename: str, content: bytes) -> DocumentResponse:
    """Validate, save and ingest an uploaded file, then record it."""
    display_name = Path(filename).name  # drop any folder part
    extension = Path(display_name).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise InvalidDocumentError(
            "Unsupported file type. Please upload a PDF or TXT file."
        )
    if not content:
        raise InvalidDocumentError("This file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise FileTooLargeError(
            f"This file is too large. The limit is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )

    document_id = uuid.uuid4().hex
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOADS_DIR / f"{document_id}{extension}"
    saved_path.write_bytes(content)

    try:
        result = ingest_document(saved_path, document_id=document_id, name=display_name)
    except Exception:
        # Ingestion failed: do not keep an unusable file around, then re-raise
        # so the caller sees the original user-safe error.
        saved_path.unlink(missing_ok=True)
        raise

    record = {
        "document_id": document_id,
        "name": display_name,
        "pages": result.pages,
        "chunks": result.chunks,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    records = _read_registry()
    records.append(record)
    _write_registry(records)

    return DocumentResponse(**record)


def list_documents() -> list[DocumentResponse]:
    """All uploaded documents, newest first."""
    records = _read_registry()
    documents = [DocumentResponse(**record) for record in records]
    return sorted(documents, key=lambda doc: doc.uploaded_at, reverse=True)


def remove_document(document_id: str) -> None:
    """Delete a document's chunks, its saved file and its record."""
    records = _read_registry()
    remaining = [r for r in records if r["document_id"] != document_id]

    if len(remaining) == len(records):
        raise DocumentNotFoundError("Document not found.")

    # 1. Remove its chunks from Chroma.
    vector_store.delete_document(document_id)

    # 2. Remove the saved file (we do not know the extension, so use a pattern).
    for path in UPLOADS_DIR.glob(f"{document_id}.*"):
        path.unlink(missing_ok=True)

    # 3. Remove the record.
    _write_registry(remaining)