import time
from types import SimpleNamespace

import pytest
from google import genai

from app.core.config import get_settings
from app.rag import embeddings, generator
from app.rag.embeddings import EmbeddingError, embed_documents, embed_query
from app.rag.generator import GenerationError, generate_answer
from app.rag.vector_store import SearchResult


class FakeApiError(Exception):
    """Looks like a Gemini error: an exception that carries an HTTP code."""

    def __init__(self, code, message="error"):
        super().__init__(message)
        self.code = code


class FakeModels:
    """Plays back a script. An Exception in the list is raised, anything else is returned.

    When only one outcome is left, it repeats forever (so [FakeApiError(429)]
    means "always fails with 429").
    """

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def _next(self):
        outcome = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def embed_content(self, model, contents, config):
        self.calls.append({"model": model, "contents": contents})
        self._next()  # raises if this step is a failure
        return SimpleNamespace(
            embeddings=[SimpleNamespace(values=[0.1, 0.2, 0.3]) for _ in contents]
        )

    def generate_content(self, model, contents, config):
        self.calls.append({"model": model, "contents": contents})
        return SimpleNamespace(text=self._next())


@pytest.fixture
def gemini(monkeypatch):
    """A safe fake Gemini: a test key and model, no waiting, no network."""
    settings = get_settings()
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(settings, "gemini_model", "test-model")

    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)  # record, do not wait

    def install(outcomes):
        models = FakeModels(outcomes)
        monkeypatch.setattr(genai, "Client", lambda api_key=None: SimpleNamespace(models=models))
        return models

    return SimpleNamespace(install=install, sleeps=sleeps)


def make_results():
    return [
        SearchResult(
            text="Overfitting means memorising the training data.",
            document_id="d1",
            document_name="notes.txt",
            page_number=3,
            chunk_index=0,
            similarity=0.9,
        )
    ]


# ====================== embeddings ======================


def test_embedding_with_a_missing_key_is_a_clear_error(gemini, monkeypatch):
    monkeypatch.setattr(get_settings(), "gemini_api_key", "")

    def must_not_be_created(*args, **kwargs):
        raise AssertionError("No Gemini client should be created without a key.")

    monkeypatch.setattr(genai, "Client", must_not_be_created)

    with pytest.raises(EmbeddingError, match="key is missing"):
        embed_documents(["hello"])


@pytest.mark.parametrize(
    "code, message",
    [
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (400, "API key not valid. Please pass a valid API key."),
    ],
)
def test_rejected_key_gives_the_key_message_without_retrying(gemini, code, message):
    models = gemini.install([FakeApiError(code, message)])

    with pytest.raises(EmbeddingError, match="API key is valid"):
        embed_query("hello")

    assert len(models.calls) == 1  # retrying a wrong key would be pointless


def test_a_400_that_is_not_about_the_key_is_not_blamed_on_the_key(gemini):
    gemini.install([FakeApiError(400, "Request contains an invalid argument.")])

    with pytest.raises(EmbeddingError, match="Could not create embeddings") as error:
        embed_query("hello")

    assert "API key" not in str(error.value)


@pytest.mark.parametrize("code", [429, 503])
def test_temporary_errors_are_retried_until_they_succeed(gemini, code):
    models = gemini.install([FakeApiError(code), "ok"])

    vectors = embed_documents(["hello"])

    assert vectors == [[0.1, 0.2, 0.3]]
    assert len(models.calls) == 2
    assert gemini.sleeps == [embeddings.WAIT_SECONDS]  # waited once, then it worked


def test_embedding_gives_up_after_the_maximum_attempts(gemini):
    models = gemini.install([FakeApiError(429)])  # always fails

    with pytest.raises(EmbeddingError, match="rate limit"):
        embed_documents(["hello"])

    assert len(models.calls) == embeddings.MAX_ATTEMPTS
    # The waits grow each time: 20s, 40s, 60s.
    assert gemini.sleeps == [
        embeddings.WAIT_SECONDS * n for n in range(1, embeddings.MAX_ATTEMPTS)
    ]


def test_an_unexpected_embedding_error_is_not_retried_and_does_not_leak(gemini):
    models = gemini.install([FakeApiError(500, "secret internal detail")])

    with pytest.raises(EmbeddingError, match="Could not create embeddings") as error:
        embed_query("hello")

    assert len(models.calls) == 1
    assert "secret" not in str(error.value)


def test_many_texts_are_sent_in_batches_and_keep_their_order(gemini):
    models = gemini.install(["ok"])
    texts = [f"text {i}" for i in range(45)]

    vectors = embed_documents(texts)

    assert len(vectors) == 45
    assert [len(call["contents"]) for call in models.calls] == [20, 20, 5]
    assert len(gemini.sleeps) == 2  # paused between batches, not after the last


# ====================== generator ======================


def test_generation_with_a_missing_key_is_a_clear_error(gemini, monkeypatch):
    monkeypatch.setattr(get_settings(), "gemini_api_key", "")

    with pytest.raises(GenerationError, match="key is missing"):
        generate_answer("What is overfitting?", make_results())


def test_generation_with_no_model_set_is_a_clear_error(gemini, monkeypatch):
    monkeypatch.setattr(get_settings(), "gemini_model", "")

    with pytest.raises(GenerationError, match="No Gemini model"):
        generate_answer("What is overfitting?", make_results())


def test_generation_without_context_is_refused(gemini):
    with pytest.raises(GenerationError, match="no document context"):
        generate_answer("What is overfitting?", [])


@pytest.mark.parametrize(
    "code, message",
    [
        (403, "Forbidden"),
        (400, "API key not valid. Please pass a valid API key."),
    ],
)
def test_generation_with_a_rejected_key_gives_the_key_message(gemini, code, message):
    models = gemini.install([FakeApiError(code, message)])

    with pytest.raises(GenerationError, match="API key is valid"):
        generate_answer("What is overfitting?", make_results())

    assert len(models.calls) == 1


def test_an_unknown_model_points_to_the_setting(gemini):
    gemini.install([FakeApiError(404, "model not found")])

    with pytest.raises(GenerationError, match="GEMINI_MODEL"):
        generate_answer("What is overfitting?", make_results())


def test_a_busy_gemini_is_retried_until_it_answers(gemini):
    models = gemini.install([FakeApiError(503), "A good answer."])

    answer = generate_answer("What is overfitting?", make_results())

    assert answer == "A good answer."
    assert len(models.calls) == 2
    assert gemini.sleeps == [generator.WAIT_SECONDS]


def test_generation_gives_up_after_the_maximum_attempts(gemini):
    models = gemini.install([FakeApiError(429)])

    with pytest.raises(GenerationError, match="rate limit"):
        generate_answer("What is overfitting?", make_results())

    assert len(models.calls) == generator.MAX_ATTEMPTS


def test_an_empty_answer_is_reported(gemini):
    gemini.install(["   "])

    with pytest.raises(GenerationError, match="empty answer"):
        generate_answer("What is overfitting?", make_results())


def test_the_prompt_contains_the_question_and_labelled_sources(gemini):
    models = gemini.install(["  Final answer.  "])

    answer = generate_answer("What is overfitting?", make_results())

    assert answer == "Final answer."  # surrounding spaces are trimmed
    call = models.calls[0]
    assert call["model"] == "test-model"
    assert "What is overfitting?" in call["contents"]
    assert "[Source 1: notes.txt, page 3]" in call["contents"]
    assert "Overfitting means memorising the training data." in call["contents"]


def test_an_unexpected_generation_error_does_not_leak(gemini):
    models = gemini.install([FakeApiError(500, "secret internal detail")])

    with pytest.raises(GenerationError, match="Could not generate an answer") as error:
        generate_answer("What is overfitting?", make_results())

    assert len(models.calls) == 1
    assert "secret" not in str(error.value)