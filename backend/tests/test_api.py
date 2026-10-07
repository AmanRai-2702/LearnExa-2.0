from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import chat as chat_api
from app.api import documents as documents_api
from app.main import app
from app.models.schemas import DocumentResponse
from app.rag.embeddings import EmbeddingError
from app.rag.generator import GenerationError
from app.rag.loader import DocumentLoadError
from app.rag.pipeline import NO_DOCUMENTS_MESSAGE, Answer
from app.rag.retriever import RetrievalError
from app.rag.vector_store import SearchResult, VectorStoreError
from app.services import document_service
from app.services.document_service import (
    MAX_UPLOAD_BYTES,
    DocumentNotFoundError,
    DocumentServiceError,
    FileTooLargeError,
    InvalidDocumentError,
)


def make_document(name="notes.txt"):
    return DocumentResponse(
        document_id="abc123",
        name=name,
        pages=2,
        chunks=5,
        uploaded_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )


def make_source():
    return SearchResult(
        text="Overfitting means memorising the training data.",
        document_id="abc123",
        document_name="notes.txt",
        page_number=3,
        chunk_index=7,
        similarity=0.82,
    )


def upload(client, filename="notes.txt", content=b"hello"):
    """Send a file the way the browser's upload form does."""
    return client.post(
        "/api/documents/upload",
        files={"file": (filename, content, "application/octet-stream")},
    )


# ====================== documents: upload ======================


def test_upload_returns_201_and_the_document(client, monkeypatch):
    received = {}

    def fake_add_document(filename, content):
        received["filename"] = filename
        received["content"] = content
        return make_document()

    monkeypatch.setattr(documents_api, "add_document", fake_add_document)

    response = upload(client, "notes.txt", b"hello")

    assert response.status_code == 201
    assert set(response.json()) == {"document_id", "name", "pages", "chunks", "uploaded_at"}
    assert response.json()["name"] == "notes.txt"
    assert received == {"filename": "notes.txt", "content": b"hello"}


def test_upload_without_a_file_is_a_422(client):
    # FastAPI validates the request itself, before any of our code runs.
    assert client.post("/api/documents/upload").status_code == 422


# Each of our errors must become the right HTTP status, with a readable message.
ERROR_STATUS_CASES = [
    (InvalidDocumentError, 400),
    (FileTooLargeError, 413),
    (DocumentNotFoundError, 404),
    (DocumentLoadError, 422),
    (EmbeddingError, 502),
    (VectorStoreError, 503),
    (DocumentServiceError, 500),
]


@pytest.mark.parametrize("error_class, expected_status", ERROR_STATUS_CASES)
def test_upload_errors_become_the_right_status(client, monkeypatch, error_class, expected_status):
    def failing_add_document(filename, content):
        raise error_class("A message that is safe to show.")

    monkeypatch.setattr(documents_api, "add_document", failing_add_document)

    response = upload(client)

    assert response.status_code == expected_status
    assert response.json() == {"detail": "A message that is safe to show."}


@pytest.fixture
def guarded_service(tmp_path, monkeypatch):
    """Use the REAL upload validation, but make real ingestion impossible.

    Folders point into a temporary directory, and if ingestion ever runs,
    the test fails loudly instead of calling Gemini.
    """
    monkeypatch.setattr(document_service, "DATA_DIR", tmp_path)
    monkeypatch.setattr(document_service, "UPLOADS_DIR", tmp_path / "uploads")
    monkeypatch.setattr(document_service, "REGISTRY_FILE", tmp_path / "documents.json")

    def must_not_run(*args, **kwargs):
        raise AssertionError("Ingestion must not run for an invalid upload.")

    monkeypatch.setattr(document_service, "ingest_document", must_not_run)


@pytest.mark.parametrize(
    "filename, content, expected_status, expected_text",
    [
        ("photo.png", b"not a document", 400, "Unsupported file type"),
        ("notes.txt", b"", 400, "empty"),
    ],
)
def test_invalid_uploads_are_rejected_by_the_real_validation(
    client, guarded_service, filename, content, expected_status, expected_text
):
    response = upload(client, filename, content)

    assert response.status_code == expected_status
    assert expected_text in response.json()["detail"]


def test_a_file_over_the_limit_gets_a_413(client, guarded_service):
    response = upload(client, "notes.txt", b"a" * (MAX_UPLOAD_BYTES + 1))

    assert response.status_code == 413
    assert "too large" in response.json()["detail"]


# ====================== documents: list and delete ======================


def test_list_returns_the_documents(client, monkeypatch):
    monkeypatch.setattr(
        documents_api,
        "list_documents",
        lambda: [make_document("a.txt"), make_document("b.txt")],
    )

    response = client.get("/api/documents")

    assert response.status_code == 200
    assert [doc["name"] for doc in response.json()] == ["a.txt", "b.txt"]


def test_list_is_an_empty_list_when_nothing_is_uploaded(client, monkeypatch):
    monkeypatch.setattr(documents_api, "list_documents", lambda: [])

    response = client.get("/api/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_list_failure_is_reported_without_details(client, monkeypatch):
    def failing_list():
        raise DocumentServiceError("Could not read the list of documents.")

    monkeypatch.setattr(documents_api, "list_documents", failing_list)

    response = client.get("/api/documents")

    assert response.status_code == 500
    assert response.json() == {"detail": "Could not read the list of documents."}


def test_delete_returns_204_with_no_body(client, monkeypatch):
    deleted = []
    monkeypatch.setattr(documents_api, "remove_document", deleted.append)

    response = client.delete("/api/documents/abc123")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted == ["abc123"]


def test_delete_of_an_unknown_document_is_a_404(client, monkeypatch):
    def failing_remove(document_id):
        raise DocumentNotFoundError("Document not found.")

    monkeypatch.setattr(documents_api, "remove_document", failing_remove)

    response = client.delete("/api/documents/nope")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found."}


# ====================== chat ======================


def test_chat_returns_the_answer_and_its_sources(client, monkeypatch):
    monkeypatch.setattr(
        chat_api,
        "ask",
        lambda question, document_id=None: Answer(
            answer="Overfitting is when a model memorises its training data.",
            sources=[make_source()],
        ),
    )

    response = client.post("/api/chat", json={"question": "What is overfitting?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("Overfitting is")
    assert len(body["sources"]) == 1
    # The frontend's Source type (lib/types.ts) relies on exactly these fields.
    assert set(body["sources"][0]) == {
        "document_id",
        "document_name",
        "page_number",
        "chunk_index",
        "similarity",
        "text",
    }
    assert body["sources"][0]["page_number"] == 3


def test_chat_passes_the_document_id_to_the_pipeline(client, monkeypatch):
    received = {}

    def fake_ask(question, document_id=None):
        received["question"] = question
        received["document_id"] = document_id
        return Answer(answer="ok", sources=[])

    monkeypatch.setattr(chat_api, "ask", fake_ask)

    client.post("/api/chat", json={"question": "What is overfitting?", "document_id": "abc123"})
    assert received == {"question": "What is overfitting?", "document_id": "abc123"}

    client.post("/api/chat", json={"question": "What is overfitting?"})
    assert received["document_id"] is None  # None means "search all documents"


def test_chat_trims_spaces_around_the_question(client, monkeypatch):
    received = {}

    def fake_ask(question, document_id=None):
        received["question"] = question
        return Answer(answer="ok", sources=[])

    monkeypatch.setattr(chat_api, "ask", fake_ask)

    client.post("/api/chat", json={"question": "   What is overfitting?   "})

    assert received["question"] == "What is overfitting?"


def test_chat_accepts_a_question_of_exactly_1000_characters(client, monkeypatch):
    monkeypatch.setattr(
        chat_api, "ask", lambda question, document_id=None: Answer(answer="ok", sources=[])
    )

    response = client.post("/api/chat", json={"question": "a" * 1000})

    assert response.status_code == 200


@pytest.mark.parametrize(
    "body",
    [
        {},                          # question missing
        {"question": ""},            # empty
        {"question": "     "},       # only spaces (trimmed to empty)
        {"question": "a" * 1001},    # one character too long
    ],
)
def test_invalid_chat_requests_are_a_422_and_never_reach_the_pipeline(client, monkeypatch, body):
    def must_not_run(question, document_id=None):
        raise AssertionError("The pipeline must not run for an invalid request.")

    monkeypatch.setattr(chat_api, "ask", must_not_run)

    assert client.post("/api/chat", json=body).status_code == 422


def test_chat_with_no_documents_returns_the_friendly_message_and_no_sources(client, monkeypatch):
    monkeypatch.setattr(
        chat_api,
        "ask",
        lambda question, document_id=None: Answer(answer=NO_DOCUMENTS_MESSAGE, sources=[]),
    )

    response = client.post("/api/chat", json={"question": "What is overfitting?"})

    assert response.status_code == 200
    assert response.json() == {"answer": NO_DOCUMENTS_MESSAGE, "sources": []}


@pytest.mark.parametrize(
    "error_class, expected_status",
    [
        (RetrievalError, 400),      # the request itself was invalid
        (EmbeddingError, 502),      # Gemini failed
        (GenerationError, 502),     # Gemini failed
        (VectorStoreError, 503),    # our database failed
    ],
)
def test_chat_errors_become_the_right_status(client, monkeypatch, error_class, expected_status):
    def failing_ask(question, document_id=None):
        raise error_class("A message that is safe to show.")

    monkeypatch.setattr(chat_api, "ask", failing_ask)

    response = client.post("/api/chat", json={"question": "What is overfitting?"})

    assert response.status_code == expected_status
    assert response.json() == {"detail": "A message that is safe to show."}


def test_an_unexpected_bug_never_leaks_internal_details(monkeypatch):
    def buggy_ask(question, document_id=None):
        raise RuntimeError("secret internal detail: C:\\Users\\someone\\key.txt")

    monkeypatch.setattr(chat_api, "ask", buggy_ask)
    # By default TestClient re-raises server errors so you notice them in tests.
    # Here we want to see what a real browser would receive instead.
    quiet_client = TestClient(app, raise_server_exceptions=False)

    response = quiet_client.post("/api/chat", json={"question": "What is overfitting?"})

    assert response.status_code == 500
    assert "secret internal detail" not in response.text
    assert "Traceback" not in response.text