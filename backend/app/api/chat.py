from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse, SourceResponse
from app.rag.embeddings import EmbeddingError
from app.rag.generator import GenerationError
from app.rag.pipeline import ask
from app.rag.retriever import RetrievalError
from app.rag.vector_store import VectorStoreError

router = APIRouter(prefix="/api", tags=["chat"])

HANDLED_ERRORS = (
    RetrievalError,
    EmbeddingError,
    VectorStoreError,
    GenerationError,
)


def _to_http_error(error: Exception) -> HTTPException:
    """Translate one of our errors into an HTTP error with the right status code."""
    if isinstance(error, RetrievalError):
        code = status.HTTP_400_BAD_REQUEST  # the request itself was invalid
    elif isinstance(error, (EmbeddingError, GenerationError)):
        code = status.HTTP_502_BAD_GATEWAY  # Gemini (upstream) failed
    else:
        code = status.HTTP_503_SERVICE_UNAVAILABLE  # VectorStoreError: our database
    return HTTPException(status_code=code, detail=str(error))


# Plain "def" on purpose: embedding + Gemini calls (with retries) are blocking,
# so FastAPI runs this in a worker thread and the server stays responsive.
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = ask(request.question, document_id=request.document_id)
    except HANDLED_ERRORS as error:
        raise _to_http_error(error) from error

    return ChatResponse(
        answer=result.answer,
        # SearchResult (dataclass) -> SourceResponse (Pydantic), field by field.
        sources=[SourceResponse.model_validate(source) for source in result.sources],
    )