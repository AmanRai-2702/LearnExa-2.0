import pytest

from app.core.config import get_settings
from app.rag import retriever, vector_store
from app.rag.retriever import RetrievalError, retrieve
from app.rag.splitter import Chunk
from app.rag.vector_store import (
    VectorStoreError,
    add_chunks,
    count_chunks,
    delete_document,
    search,
)

# Tiny 3-number "embeddings" we control, so we know which chunk should win.
QUERY = [1.0, 0.0, 0.0]


def make_chunk(document_id, index, text, page, name="notes.pdf"):
    return Chunk(
        text=text,
        document_id=document_id,
        document_name=name,
        page_number=page,
        chunk_index=index,
    )


@pytest.fixture
def empty_store(tmp_path, monkeypatch):
    """Point the vector store at a temporary folder, so the real database is untouched."""
    monkeypatch.setattr(vector_store, "CHROMA_DIR", tmp_path / "chroma")


@pytest.fixture
def seeded_store(empty_store):
    """A temporary database holding two documents and four chunks."""
    chunks = [
        make_chunk("doc-1", 0, "Overfitting means memorising the training data.", 1, "ml_notes.pdf"),
        make_chunk("doc-1", 1, "Gradient descent reduces the loss.", 2, "ml_notes.pdf"),
        make_chunk("doc-1", 2, "Pizza is tasty.", 3, "ml_notes.pdf"),
        make_chunk("doc-2", 0, "Underfitting means the model is too simple.", 1, "other.txt"),
    ]
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.7, 0.7, 0.0],
    ]
    add_chunks(chunks, embeddings)


@pytest.fixture
def fake_embed(monkeypatch):
    """Replace the Gemini call in the retriever. Returns the list of questions it received."""
    received = []

    def fake_embed_query(question):
        received.append(question)
        return QUERY

    monkeypatch.setattr(retriever, "embed_query", fake_embed_query)
    return received


# ====================== vector store ======================


def test_add_chunks_stores_everything_and_returns_the_count(empty_store):
    chunks = [
        make_chunk("doc-1", 0, "first", 1),
        make_chunk("doc-1", 1, "second", 1),
    ]

    stored = add_chunks(chunks, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    assert stored == 2
    assert count_chunks() == 2


def test_adding_no_chunks_is_an_error(empty_store):
    with pytest.raises(VectorStoreError, match="no chunks"):
        add_chunks([], [])


def test_mismatched_chunks_and_embeddings_are_rejected(empty_store):
    chunks = [make_chunk("doc-1", 0, "only one chunk", 1)]

    # Two vectors for one chunk would pair text with the wrong vector.
    with pytest.raises(VectorStoreError, match="do not match"):
        add_chunks(chunks, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])


def test_search_returns_the_closest_chunk_first_with_its_metadata(seeded_store):
    results = search(QUERY, top_k=1)

    assert len(results) == 1
    best = results[0]
    assert best.text == "Overfitting means memorising the training data."
    assert best.document_id == "doc-1"
    assert best.document_name == "ml_notes.pdf"
    assert best.page_number == 1
    assert best.chunk_index == 0
    assert best.similarity == pytest.approx(1.0, abs=0.01)  # identical direction


def test_search_results_are_ordered_best_first(seeded_store):
    results = search(QUERY, top_k=4)

    similarities = [result.similarity for result in results]
    assert similarities == sorted(similarities, reverse=True)
    assert results[0].text.startswith("Overfitting")
    assert results[1].text.startswith("Underfitting")
    assert results[1].similarity == pytest.approx(0.71, abs=0.02)


def test_search_respects_top_k(seeded_store):
    assert len(search(QUERY, top_k=2)) == 2


def test_top_k_larger_than_stored_returns_everything(seeded_store):
    # Four chunks exist; asking for ten must give four, not an error.
    assert len(search(QUERY, top_k=10)) == 4


def test_search_on_an_empty_database_returns_nothing(empty_store):
    assert search(QUERY, top_k=5) == []


@pytest.mark.parametrize("bad_top_k", [0, -1])
def test_search_rejects_a_non_positive_top_k(empty_store, bad_top_k):
    with pytest.raises(VectorStoreError, match="top_k"):
        search(QUERY, top_k=bad_top_k)


def test_search_can_be_limited_to_one_document(seeded_store):
    results = search(QUERY, top_k=5, document_id="doc-2")

    assert len(results) == 1
    assert results[0].document_id == "doc-2"
    assert results[0].text.startswith("Underfitting")


def test_count_chunks_total_and_per_document(seeded_store):
    assert count_chunks() == 4
    assert count_chunks("doc-1") == 3
    assert count_chunks("doc-2") == 1
    assert count_chunks("no-such-document") == 0


def test_delete_document_removes_only_that_document(seeded_store):
    removed = delete_document("doc-1")

    assert removed == 3
    assert count_chunks() == 1
    # Everything that remains belongs to doc-2.
    assert all(result.document_id == "doc-2" for result in search(QUERY, top_k=5))


def test_deleting_an_unknown_document_removes_nothing(seeded_store):
    assert delete_document("no-such-document") == 0
    assert count_chunks() == 4


# ====================== retriever ======================


@pytest.mark.parametrize("question", ["", "   "])
def test_empty_question_is_rejected_without_calling_gemini(empty_store, fake_embed, question):
    with pytest.raises(RetrievalError, match="enter a question"):
        retrieve(question)

    assert fake_embed == []  # no embedding call, so no quota wasted


@pytest.mark.parametrize("bad_top_k", [0, -3])
def test_retriever_rejects_a_non_positive_top_k(empty_store, fake_embed, bad_top_k):
    with pytest.raises(RetrievalError, match="top_k"):
        retrieve("What is overfitting?", top_k=bad_top_k)

    assert fake_embed == []


def test_question_is_trimmed_embedded_and_then_searched(seeded_store, fake_embed):
    results = retrieve("  What is overfitting?  ")

    assert fake_embed == ["What is overfitting?"]  # trimmed before embedding
    assert results[0].text.startswith("Overfitting")


def test_top_k_defaults_to_the_setting(seeded_store, fake_embed, monkeypatch):
    monkeypatch.setattr(get_settings(), "top_k", 2)

    assert len(retrieve("anything")) == 2


def test_explicit_top_k_overrides_the_setting(seeded_store, fake_embed, monkeypatch):
    monkeypatch.setattr(get_settings(), "top_k", 2)

    assert len(retrieve("anything", top_k=1)) == 1


def test_retrieval_can_be_limited_to_one_document(seeded_store, fake_embed):
    results = retrieve("anything", document_id="doc-2")

    assert [result.document_id for result in results] == ["doc-2"]


def test_retrieval_with_nothing_stored_returns_an_empty_list(empty_store, fake_embed):
    assert retrieve("anything") == []
    assert fake_embed == ["anything"]  # the question was still embedded