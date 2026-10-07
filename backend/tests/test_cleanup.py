from types import SimpleNamespace

import pytest

from app.core.config import get_settings
from app.rag import pipeline, vector_store
from app.rag.embeddings import EmbeddingError
from app.rag.pipeline import NO_DOCUMENTS_MESSAGE, IngestResult, ask, ingest_document
from app.rag.vector_store import SearchResult, VectorStoreError, count_chunks
from app.services import document_service
from app.services.document_service import DocumentServiceError, add_document


def write_text_file(folder, name, text):
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def make_result():
    return SearchResult(
        text="Overfitting means memorising the training data.",
        document_id="doc-1",
        document_name="notes.txt",
        page_number=1,
        chunk_index=0,
        similarity=0.9,
    )


@pytest.fixture
def temp_store(tmp_path, monkeypatch):
    """A temporary Chroma folder, and a fake embedding step (no Gemini)."""
    monkeypatch.setattr(vector_store, "CHROMA_DIR", tmp_path / "chroma")
    monkeypatch.setattr(
        pipeline, "embed_documents", lambda texts: [[1.0, 0.0, 0.0] for _ in texts]
    )


# ====================== pipeline: ingest ======================


def test_ingest_stores_the_document_and_reports_the_numbers(temp_store, tmp_path):
    file = write_text_file(tmp_path, "notes.txt", "Overfitting means memorising data.")

    result = ingest_document(file, document_id="doc-1", name="notes.txt")

    assert result.document_name == "notes.txt"
    assert result.pages == 1
    assert result.chunks >= 1
    assert result.chunks == count_chunks("doc-1")


def test_ingesting_the_same_document_again_replaces_the_old_chunks(
    temp_store, tmp_path, monkeypatch
):
    monkeypatch.setattr(get_settings(), "chunk_size", 100)
    monkeypatch.setattr(get_settings(), "chunk_overlap", 10)
    long_text = " ".join(f"word{i:03d}" for i in range(60))
    first = write_text_file(tmp_path, "long.txt", long_text)
    second = write_text_file(tmp_path, "tiny.txt", "A tiny note.")

    ingest_document(first, document_id="doc-1", name="long.txt")
    assert count_chunks("doc-1") > 1

    ingest_document(second, document_id="doc-1", name="tiny.txt")

    assert count_chunks("doc-1") == 1  # the old chunks are gone, not added to


def test_a_failed_embedding_keeps_the_older_copy(temp_store, tmp_path, monkeypatch):
    first = write_text_file(tmp_path, "notes.txt", "Overfitting means memorising data.")
    ingest_document(first, document_id="doc-1", name="notes.txt")
    chunks_before = count_chunks("doc-1")

    def failing_embed(texts):
        raise EmbeddingError("Gemini rate limit reached.")

    monkeypatch.setattr(pipeline, "embed_documents", failing_embed)
    second = write_text_file(tmp_path, "new.txt", "A different note.")

    with pytest.raises(EmbeddingError):
        ingest_document(second, document_id="doc-1", name="new.txt")

    assert count_chunks("doc-1") == chunks_before  # the old copy survived


def test_a_failed_save_removes_the_chunks_that_were_already_stored(
    temp_store, tmp_path, monkeypatch
):
    def partly_failing_add(chunks, embeddings):
        # Store one chunk for real, then fail, like a later batch failing.
        vector_store.add_chunks(chunks[:1], embeddings[:1])
        raise VectorStoreError("Could not save this document to the database.")

    monkeypatch.setattr(pipeline, "add_chunks", partly_failing_add)
    file = write_text_file(tmp_path, "notes.txt", "Overfitting means memorising data.")

    with pytest.raises(VectorStoreError, match="Could not save"):
        ingest_document(file, document_id="doc-1", name="notes.txt")

    assert count_chunks("doc-1") == 0  # no orphan chunks left behind


# ====================== pipeline: ask ======================


def test_asking_with_nothing_stored_answers_without_calling_gemini(monkeypatch):
    monkeypatch.setattr(pipeline, "retrieve", lambda question, document_id=None: [])

    def must_not_run(question, results):
        raise AssertionError("Gemini must not be called when there is no context.")

    monkeypatch.setattr(pipeline, "generate_answer", must_not_run)

    result = ask("What is overfitting?")

    assert result.answer == NO_DOCUMENTS_MESSAGE
    assert result.sources == []


def test_asking_returns_the_answer_together_with_its_sources(monkeypatch):
    results = [make_result()]
    monkeypatch.setattr(pipeline, "retrieve", lambda question, document_id=None: results)
    received = {}

    def fake_generate(question, chunks):
        received["question"] = question
        received["chunks"] = chunks
        return "Final answer."

    monkeypatch.setattr(pipeline, "generate_answer", fake_generate)

    result = ask("What is overfitting?")

    assert result.answer == "Final answer."
    assert result.sources == results
    assert received == {"question": "What is overfitting?", "chunks": results}


def test_asking_passes_the_document_id_to_retrieval(monkeypatch):
    received = {}

    def fake_retrieve(question, document_id=None):
        received["document_id"] = document_id
        return []

    monkeypatch.setattr(pipeline, "retrieve", fake_retrieve)

    ask("What is overfitting?", document_id="doc-7")

    assert received["document_id"] == "doc-7"


# ====================== service: undo on failure ======================


@pytest.fixture
def service_env(tmp_path, monkeypatch):
    """The document service in a sandbox, with fake ingestion and fake Chroma delete."""
    uploads = tmp_path / "uploads"
    monkeypatch.setattr(document_service, "DATA_DIR", tmp_path)
    monkeypatch.setattr(document_service, "UPLOADS_DIR", uploads)
    monkeypatch.setattr(document_service, "REGISTRY_FILE", tmp_path / "documents.json")

    ingested_ids = []

    def fake_ingest(path, document_id, name):
        ingested_ids.append(document_id)
        return IngestResult(document_id=document_id, document_name=name, pages=1, chunks=1)

    monkeypatch.setattr(document_service, "ingest_document", fake_ingest)

    deleted_ids = []

    def fake_delete(document_id):
        deleted_ids.append(document_id)
        return 1

    monkeypatch.setattr(document_service.vector_store, "delete_document", fake_delete)

    def failing_write(records):
        raise DocumentServiceError("Could not save the list of documents.")

    monkeypatch.setattr(document_service, "_write_registry", failing_write)

    return SimpleNamespace(uploads=uploads, ingested_ids=ingested_ids, deleted_ids=deleted_ids)


def test_a_failed_registry_save_undoes_the_file_and_the_chunks(service_env):
    with pytest.raises(DocumentServiceError, match="Could not save"):
        add_document("notes.txt", b"hello")

    assert list(service_env.uploads.iterdir()) == []              # file removed
    assert service_env.deleted_ids == service_env.ingested_ids    # chunks removed


def test_a_failed_cleanup_does_not_hide_the_original_error(service_env, monkeypatch):
    def failing_delete(document_id):
        raise VectorStoreError("Could not delete this document from the database.")

    monkeypatch.setattr(document_service.vector_store, "delete_document", failing_delete)

    # The user must still see the real problem (saving the list), not the cleanup one.
    with pytest.raises(DocumentServiceError, match="Could not save the list"):
        add_document("notes.txt", b"hello")

    assert list(service_env.uploads.iterdir()) == []