from app.core.config import get_settings
from app.rag.embeddings import embed_query
from app.rag.vector_store import SearchResult, search


class RetrievalError(Exception):
    """Raised for invalid retrieval requests. The message is safe to show users."""


def retrieve(
    question: str,
    top_k: int | None = None,
    document_id: str | None = None,
) -> list[SearchResult]:
    """Find the chunks most relevant to a question (best first).

    top_k defaults to the TOP_K setting. If document_id is given, only that
    document is searched. An empty list means nothing is stored yet.
    """
    question = question.strip()
    if not question:
        raise RetrievalError("Please enter a question.")

    k = top_k if top_k is not None else get_settings().top_k
    if k <= 0:
        raise RetrievalError("top_k must be greater than 0.")

    # Step 1: turn the question into a vector (same model as the chunks).
    query_vector = embed_query(question)

    # Step 2: ask Chroma for the nearest stored vectors.
    return search(query_vector, top_k=k, document_id=document_id)