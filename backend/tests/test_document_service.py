import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from app.rag.loader import DocumentLoadError
from app.rag.pipeline import IngestResult
from app.services import document_service
from app.services.document_service import (
    MAX_UPLOAD_BYTES,
    DocumentNotFoundError,
    DocumentServiceError,
    FileTooLargeError,
    InvalidDocumentError,
    add_document,
    list_documents,
    remove_document,
)


@pytest.fixture
def env(tmp_path, monkeypatch):
    """A safe sandbox for the document service.

    - Folders and the registry file point into a temporary folder.
    - ingest_document (Gemini + Chroma) is replaced by a fake.
    - Chroma's delete is replaced by a fake that records the ids.
    Nothing real is ever touched.
    """
    uploads = tmp_path / "uploads"
    registry = tmp_path / "documents.json"
    monkeypatch.setattr(document_service, "DATA_DIR", tmp_path)
    monkeypatch.setattr(document_service, "UPLOADS_DIR", uploads)
    monkeypatch.setattr(document_service, "REGISTRY_FILE", registry)

    ingest_calls = []

    def fake_ingest(path, document_id, name):
        # Record what the service handed us, including whether the file
        # already existed on disk at this moment.
        ingest_calls.append(
            {
                "path": path,
                "document_id": document_id,
                "name": name,
                "existed": path.exists(),
                "content": path.read_bytes(),
            }
        )
        return IngestResult(document_id=document_id, document_name=name, pages=2, chunks=5)

    monkeypatch.setattr(document_service, "ingest_document", fake_ingest)

    deleted_ids = []

    def fake_vector_delete(document_id):
        deleted_ids.append(document_id)
        return 0

    monkeypatch.setattr(document_service.vector_store, "delete_document", fake_vector_delete)

    return SimpleNamespace(
        uploads=uploads,
        registry=registry,
        ingest_calls=ingest_calls,
        deleted_ids=deleted_ids,
    )


def saved_files(env):
    """Names of the files currently in the (temporary) uploads folder."""
    if not env.uploads.exists():
        return []
    return [path.name for path in env.uploads.iterdir()]


def registry_records(env):
    return json.loads(env.registry.read_text(encoding="utf-8"))


# ---------- validation ----------


@pytest.mark.parametrize("filename", ["photo.png", "report.docx", "no_extension"])
def test_unsupported_file_type_is_rejected(env, filename):
    with pytest.raises(InvalidDocumentError, match="Unsupported file type"):
        add_document(filename, b"some content")

    assert env.ingest_calls == []   # we never started ingesting
    assert saved_files(env) == []   # and nothing was saved


def test_empty_file_is_rejected(env):
    with pytest.raises(InvalidDocumentError, match="empty"):
        add_document("notes.txt", b"")

    assert env.ingest_calls == []
    assert saved_files(env) == []


def test_file_over_the_limit_is_rejected(env):
    too_big = b"a" * (MAX_UPLOAD_BYTES + 1)

    with pytest.raises(FileTooLargeError, match="too large") as error:
        add_document("notes.txt", too_big)

    assert "10 MB" in str(error.value)
    assert env.ingest_calls == []
    assert saved_files(env) == []


def test_file_exactly_at_the_limit_is_accepted(env):
    just_right = b"a" * MAX_UPLOAD_BYTES

    document = add_document("notes.txt", just_right)

    assert document.name == "notes.txt"


def test_error_classes_share_one_base_class():
    # documents.py catches DocumentServiceError to cover all of these at once.
    for error_class in (InvalidDocumentError, FileTooLargeError, DocumentNotFoundError):
        assert issubclass(error_class, DocumentServiceError)


# ---------- successful upload ----------


def test_successful_upload_returns_the_ingest_numbers(env):
    document = add_document("notes.txt", b"hello world")

    assert document.name == "notes.txt"
    assert document.pages == 2    # from the fake ingest result
    assert document.chunks == 5
    assert isinstance(document.uploaded_at, datetime)
    int(document.document_id, 16)  # a hex id (raises ValueError if it is not)
    assert len(document.document_id) == 32


def test_file_is_saved_under_a_generated_name_before_ingestion(env):
    document = add_document("Notes.TXT", b"hello world")

    call = env.ingest_calls[0]
    assert call["existed"] is True                     # saved before ingest ran
    assert call["content"] == b"hello world"
    assert call["document_id"] == document.document_id
    assert call["name"] == "Notes.TXT"
    # Saved as <id><lowercase extension>, not under the user's file name.
    assert saved_files(env) == [f"{document.document_id}.txt"]


@pytest.mark.parametrize(
    "filename, expected_name",
    [
        ("folder/sub/notes.txt", "notes.txt"),
        ("../../evil.txt", "evil.txt"),  # path traversal attempt
    ],
)
def test_display_name_drops_any_folder_part(env, filename, expected_name):
    document = add_document(filename, b"hello")

    assert document.name == expected_name
    # The file always lands directly inside the uploads folder, nowhere else.
    assert env.ingest_calls[0]["path"].parent == env.uploads


def test_upload_is_recorded_in_the_registry(env):
    document = add_document("notes.txt", b"hello")

    records = registry_records(env)
    assert len(records) == 1
    assert set(records[0]) == {"document_id", "name", "pages", "chunks", "uploaded_at"}
    assert records[0]["document_id"] == document.document_id
    # The temporary file used for safe saving must not be left behind.
    assert not env.registry.with_suffix(".json.tmp").exists()


def test_failed_ingestion_cleans_up_and_re_raises(env, monkeypatch):
    def failing_ingest(path, document_id, name):
        raise DocumentLoadError("This file is unreadable.")

    monkeypatch.setattr(document_service, "ingest_document", failing_ingest)

    with pytest.raises(DocumentLoadError, match="unreadable"):
        add_document("notes.txt", b"hello")

    assert saved_files(env) == []        # the unusable file was removed
    assert not env.registry.exists()     # and nothing was recorded


# ---------- listing ----------


def test_list_is_empty_before_any_upload(env):
    assert list_documents() == []


def test_list_is_newest_first(env):
    records = [
        {
            "document_id": "old",
            "name": "old.txt",
            "pages": 1,
            "chunks": 1,
            "uploaded_at": "2026-01-01T10:00:00+00:00",
        },
        {
            "document_id": "new",
            "name": "new.txt",
            "pages": 1,
            "chunks": 1,
            "uploaded_at": "2026-02-01T10:00:00+00:00",
        },
    ]
    env.registry.write_text(json.dumps(records), encoding="utf-8")

    assert [doc.document_id for doc in list_documents()] == ["new", "old"]


def test_unreadable_registry_gives_a_friendly_error(env):
    env.registry.write_text("{this is not json", encoding="utf-8")

    with pytest.raises(DocumentServiceError, match="Could not read"):
        list_documents()


# ---------- deleting ----------


def test_removing_an_unknown_document_is_an_error(env):
    add_document("notes.txt", b"hello")

    with pytest.raises(DocumentNotFoundError, match="not found"):
        remove_document("does-not-exist")

    assert env.deleted_ids == []              # Chroma was not touched
    assert len(registry_records(env)) == 1    # the real document is untouched


def test_removing_a_document_deletes_chunks_file_and_record(env):
    first = add_document("a.txt", b"first")
    second = add_document("b.txt", b"second")

    remove_document(first.document_id)

    assert env.deleted_ids == [first.document_id]                  # chunks removed
    assert saved_files(env) == [f"{second.document_id}.txt"]       # file removed
    assert [r["document_id"] for r in registry_records(env)] == [second.document_id]