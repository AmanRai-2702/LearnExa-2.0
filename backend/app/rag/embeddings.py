from google import genai
from google.genai import types

from app.core.config import get_settings

# Gemini accepts many texts in one request; we send them in groups.
BATCH_SIZE = 100


class EmbeddingError(Exception):
    """Raised when embeddings cannot be created. The message is safe to show users."""


def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise EmbeddingError(
            "The Gemini API key is missing. Add GEMINI_API_KEY to backend/.env."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    """Send texts to Gemini and return one vector per text, in the same order."""
    if not texts:
        raise EmbeddingError("There is no text to embed.")

    settings = get_settings()
    client = _get_client()
    vectors: list[list[float]] = []

    try:
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]
            response = client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            vectors.extend(item.values for item in response.embeddings)
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code in (400, 401, 403):
            message = "Gemini rejected the request. Check that your API key is valid."
        elif code == 429:
            message = "Gemini rate limit reached. Please wait a moment and try again."
        else:
            message = "Could not create embeddings with Gemini. Please try again."
        raise EmbeddingError(message) from exc

    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed chunks that will be stored (task type: RETRIEVAL_DOCUMENT)."""
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    """Embed a user's question (task type: RETRIEVAL_QUERY)."""
    if not text.strip():
        raise EmbeddingError("The question is empty.")
    return _embed([text], "RETRIEVAL_QUERY")[0]