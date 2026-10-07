import logging
import time

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.rag.gemini_errors import is_invalid_key_error
from app.rag.prompts import SYSTEM_INSTRUCTION, build_user_prompt
from app.rag.vector_store import SearchResult

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
WAIT_SECONDS = 10  # waits 10s, 20s, 30s, 40s between attempts when Gemini is busy

# Temporary problems worth retrying: 429 = rate limit, 503 = Gemini is busy.
RETRYABLE_CODES = (429, 503)


class GenerationError(Exception):
    """Raised when an answer cannot be generated. The message is safe to show users."""


def _friendly_message(error: Exception | None) -> str:
    """Turn a Gemini error into a message that is safe to show users."""
    code = getattr(error, "code", None)
    if is_invalid_key_error(error):
        return "Gemini rejected the request. Check that your API key is valid."
    if code == 404:
        return "The configured Gemini model was not found. Check GEMINI_MODEL in backend/.env."
    if code == 429:
        return "Gemini rate limit reached. Please wait a minute and try again."
    if code == 503:
        return "Gemini is busy right now. Please try again shortly."
    return "Could not generate an answer with Gemini. Please try again."


def generate_answer(question: str, results: list[SearchResult]) -> str:
    """Ask Gemini to answer the question using the retrieved chunks."""
    settings = get_settings()

    if not settings.gemini_api_key:
        raise GenerationError(
            "The Gemini API key is missing. Add GEMINI_API_KEY to backend/.env."
        )
    if not settings.gemini_model:
        raise GenerationError("No Gemini model is set. Add GEMINI_MODEL to backend/.env.")
    if not question.strip():
        raise GenerationError("Please enter a question.")
    if not results:
        raise GenerationError("There is no document context to answer from.")

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = build_user_prompt(question, results)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,  # low = stick to the context, less creative
                    # We pass no tools, so turn off automatic function calling.
                    # This also removes the SDK's AFC warning message.
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
            answer = (response.text or "").strip()
            if not answer:
                raise GenerationError(
                    "Gemini returned an empty answer. Try rephrasing the question."
                )
            return answer
        except GenerationError:
            raise
        except Exception as exc:
            code = getattr(exc, "code", None)
            logger.warning(
                "Gemini generation failed (attempt %s of %s): %s",
                attempt, MAX_ATTEMPTS, str(exc)[:300],
            )
            if code in RETRYABLE_CODES and attempt < MAX_ATTEMPTS:
                time.sleep(WAIT_SECONDS * attempt)
                continue
            raise GenerationError(_friendly_message(exc)) from exc

    raise GenerationError(_friendly_message(None))  # not normally reached