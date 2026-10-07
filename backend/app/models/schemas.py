from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    """One uploaded document, as shown to the frontend."""

    document_id: str
    name: str
    pages: int
    chunks: int
    uploaded_at: datetime


class ChatRequest(BaseModel):
    """What the frontend sends to POST /api/chat."""

    # Spaces around the question are removed BEFORE the length check,
    # so a question made only of spaces is rejected as empty.
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=1000)
    # Optional: search only one document. None means search all documents.
    document_id: str | None = None


class SourceResponse(BaseModel):
    """One piece of evidence behind an answer (a retrieved chunk)."""

    # Lets us build this directly from our SearchResult dataclass.
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    similarity: float
    text: str


class ChatResponse(BaseModel):
    """What POST /api/chat returns: the answer plus where it came from."""

    answer: str
    sources: list[SourceResponse]


class ErrorResponse(BaseModel):
    """The shape of every error. FastAPI's HTTPException sends {"detail": ...}."""

    detail: str