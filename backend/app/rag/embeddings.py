import logging
import time

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.rag.gemini_errors import is_invalid_key_error

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
# Free tier allows 100 embedding requests per minute (each text counts as one).
# We stay below that so large documents do not trigger 429 errors.
MAX_TEXTS_PER_MINUTE = 80
MAX_ATTEMPTS = 4
WAIT_SECONDS = 20  # wait before a retry: 20s, 40s, 60s

# Temporary problems worth retrying: 429 = rate limit, 503 = Gemini is busy.
RETRYABLE_CODES = (429, 503)


class EmbeddingError(Exception):
    """Raised when embeddings cannot be created. The message is safe to show users."""


def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise EmbeddingError(
            "The Gemini API key is missing. Add GEMINI_API_KEY to backend/.env."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _friendly_message(error: Exception | None) -> str:
    """Turn a Gemini error into a message that is safe to show users.

    The raw error text is never included: it goes to the log only.
    """
    code = getattr(error, "code", None)
    if is_invalid_key_error(error):
        return "Gemini rejected the request. Check that your API key is valid."
    if code == 429:
        return "Gemini rate limit reached. Please wait a few minutes and try again."
    if code == 503:
        return "Gemini is busy right now. Please try again shortly."
    return "Could not create embeddings with Gemini. Please try again."


def _embed_batch(
    client: genai.Client, model: str, batch: list[str], task_type: str
) -> list[list[float]]:
    """Embed one batch, retrying temporary errors (429 and 503)."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.embed_content(
                model=model,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            return [item.values for item in response.embeddings]
        except Exception as exc:
            code = getattr(exc, "code", None)
            logger.warning(
                "Gemini embedding failed (attempt %s of %s): %s",
                attempt, MAX_ATTEMPTS, str(exc)[:300],
            )
            if code in RETRYABLE_CODES and attempt < MAX_ATTEMPTS:
                time.sleep(WAIT_SECONDS * attempt)
                continue
            raise EmbeddingError(_friendly_message(exc)) from exc

    raise EmbeddingError(_friendly_message(None))  # not normally reached


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    """Send texts to Gemini and return one vector per text, in the same order."""
    if not texts:
        raise EmbeddingError("There is no text to embed.")

    settings = get_settings()
    client = _get_client()
    vectors: list[list[float]] = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for number, start in enumerate(range(0, len(texts), BATCH_SIZE), start=1):
        batch = texts[start : start + BATCH_SIZE]
        vectors.extend(
            _embed_batch(client, settings.gemini_embedding_model, batch, task_type)
        )

        # Pace ourselves between batches (not after the last one).
        if number < total_batches:
            print(f"Embedded batch {number} of {total_batches}...", flush=True)
            time.sleep(len(batch) * 60 / MAX_TEXTS_PER_MINUTE)

    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed chunks that will be stored (task type: RETRIEVAL_DOCUMENT)."""
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    """Embed a user's question (task type: RETRIEVAL_QUERY)."""
    if not text.strip():
        raise EmbeddingError("The question is empty.")
    return _embed([text], "RETRIEVAL_QUERY")[0]