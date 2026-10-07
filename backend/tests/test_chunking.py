import pytest

from app.core.config import get_settings
from app.rag.loader import PageText
from app.rag.splitter import split_pages


def make_text(prefix: str, word_count: int) -> str:
    """Build text like 'alpha000 alpha001 alpha002 ...'.

    Every word is unique, so we can tell exactly which words ended up in
    which chunk. This is a helper, not a test: its name does not start with
    'test_', so pytest does not run it on its own.
    """
    return " ".join(f"{prefix}{i:03d}" for i in range(word_count))


def split(pages, **kwargs):
    """Shortcut: call split_pages with fixed document details."""
    return split_pages(pages, document_id="doc-1", document_name="notes.pdf", **kwargs)


# ---------- empty and short input ----------


def test_empty_page_list_gives_no_chunks():
    assert split([], chunk_size=100, chunk_overlap=20) == []


def test_whitespace_only_page_gives_no_chunks():
    pages = [PageText(page_number=1, text="   \n\n   ")]

    assert split(pages, chunk_size=100, chunk_overlap=20) == []


def test_short_text_becomes_one_chunk():
    pages = [PageText(page_number=1, text="Overfitting means memorising the training data.")]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    assert len(chunks) == 1
    assert chunks[0].text == "Overfitting means memorising the training data."


# ---------- long text: size and overlap ----------


def test_long_text_is_split_into_chunks_within_the_size_limit():
    pages = [PageText(page_number=1, text=make_text("word", 60))]  # about 480 characters

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 100 for chunk in chunks)


def test_neighbouring_chunks_share_text_when_overlap_is_used():
    pages = [PageText(page_number=1, text=make_text("word", 60))]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    for first, second in zip(chunks, chunks[1:]):
        shared_words = set(first.text.split()) & set(second.text.split())
        assert shared_words, "neighbouring chunks should repeat some words"


def test_neighbouring_chunks_share_nothing_without_overlap():
    pages = [PageText(page_number=1, text=make_text("word", 60))]

    chunks = split(pages, chunk_size=100, chunk_overlap=0)

    for first, second in zip(chunks, chunks[1:]):
        assert not set(first.text.split()) & set(second.text.split())


# ---------- metadata ----------


def test_metadata_is_copied_onto_every_chunk():
    pages = [PageText(page_number=7, text=make_text("word", 40))]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.document_id == "doc-1"
        assert chunk.document_name == "notes.pdf"
        assert chunk.page_number == 7


def test_chunk_index_is_sequential_across_pages():
    pages = [
        PageText(page_number=1, text=make_text("alpha", 40)),
        PageText(page_number=2, text=make_text("beta", 40)),
    ]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    # The numbering continues across pages: 0, 1, 2, ... with no gaps or repeats.
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_chunks_never_cross_a_page_boundary():
    pages = [
        PageText(page_number=1, text=make_text("alpha", 40)),
        PageText(page_number=2, text=make_text("beta", 40)),
    ]
    prefix_for_page = {1: "alpha", 2: "beta"}

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    assert {chunk.page_number for chunk in chunks} == {1, 2}
    for chunk in chunks:
        expected_prefix = prefix_for_page[chunk.page_number]
        # Every word in the chunk must come from the page the chunk claims.
        assert all(word.startswith(expected_prefix) for word in chunk.text.split())


def test_no_chunk_is_empty_or_has_stray_whitespace():
    pages = [PageText(page_number=1, text="\n\n" + make_text("word", 50) + "\n\n   ")]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    for chunk in chunks:
        assert chunk.text != ""
        assert chunk.text == chunk.text.strip()


# ---------- invalid settings ----------


# parametrize runs the same test once for each row below, so we do not have to
# copy and paste five almost identical tests.
@pytest.mark.parametrize(
    "chunk_size, chunk_overlap",
    [
        (0, 0),       # size must be greater than 0
        (-5, 0),      # negative size
        (100, 100),   # overlap equal to size could never move forward
        (100, 150),   # overlap bigger than size
        (100, -1),    # negative overlap
    ],
)
def test_invalid_size_or_overlap_is_rejected(chunk_size, chunk_overlap):
    pages = [PageText(page_number=1, text="Some text.")]

    # pytest.raises passes only if the code inside raises this error.
    with pytest.raises(ValueError, match="chunk_"):
        split(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


# ---------- settings and overrides ----------


def test_defaults_come_from_settings(monkeypatch):
    settings = get_settings()
    # monkeypatch changes the value for this test only and restores it afterwards.
    monkeypatch.setattr(settings, "chunk_size", 50)
    monkeypatch.setattr(settings, "chunk_overlap", 10)
    pages = [PageText(page_number=1, text=make_text("word", 60))]

    chunks = split(pages)  # no chunk_size given, so settings are used

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 50 for chunk in chunks)


def test_explicit_values_override_settings(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "chunk_size", 50)
    monkeypatch.setattr(settings, "chunk_overlap", 10)
    pages = [PageText(page_number=1, text=make_text("word", 60))]

    chunks = split(pages, chunk_size=200, chunk_overlap=20)

    lengths = [len(chunk.text) for chunk in chunks]
    assert max(lengths) > 50   # bigger than the settings value allows
    assert max(lengths) <= 200


# ---------- known weakness (documented, not fixed yet) ----------


def test_tiny_pages_currently_become_tiny_chunks():
    """This documents what happens today with footer-only pages.

    Your notes.pdf has pages containing only a title and a footer. They become
    their own tiny chunks, which pollute retrieval. If we later filter tiny
    chunks, this test should be changed on purpose, which is the point of
    writing it down.
    """
    pages = [
        PageText(page_number=3, text="0. Announcement Page 3"),
        PageText(page_number=4, text=make_text("word", 40)),
    ]

    chunks = split(pages, chunk_size=100, chunk_overlap=20)

    assert chunks[0].text == "0. Announcement Page 3"
    assert chunks[0].page_number == 3