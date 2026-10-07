from dataclasses import dataclass
from pathlib import Path

from app.rag.embeddings import embed_documents
from app.rag.generator import generate_answer
from app.rag.loader import load_document
from app.rag.retriever import retrieve
from app.rag.splitter import split_pages
from app.rag.vector_store import SearchResult, add_chunks, delete_document

# Shown when nothing relevant can be searched (e.g. no document uploaded yet).
# Gemini is NOT called in this case: no context means nothing to ground an answer in.
NO_DOCUMENTS_MESSAGE = (
    "I could not find any uploaded documents to search. "
    "Please upload a document first, then ask your question."
)


@dataclass
class IngestResult:
    """What happened when a document was ingested."""

    document_id: str
    document_name: str
    pages: int   # pages that contained text
    chunks: int  # chunks stored in Chroma


@dataclass
class Answer:
    """The final result of asking a question: the answer plus where it came from."""

    answer: str
    sources: list[SearchResult]


def ingest_document(path: Path, document_id: str, name: str) -> IngestResult:
    """Document -> text -> chunks -> embeddings -> Chroma.

    Raises the user-safe errors of each step (DocumentLoadError, EmbeddingError,
    VectorStoreError); the API layer (Phase 9) will turn them into HTTP responses.
    """
    # Step 1: extract text, page by page.
    pages = load_document(path)

    # Step 2: split pages into overlapping chunks that carry their metadata.
    chunks = split_pages(pages, document_id=document_id, document_name=name)

    # Step 3: turn every chunk's text into a vector (Gemini embeddings).
    vectors = embed_documents([chunk.text for chunk in chunks])

    # Step 4: store text + vectors + metadata in Chroma.
    # If this document_id was ingested before, remove the old chunks first so we
    # never keep two versions. We do this AFTER embedding succeeded, so a failed
    # embedding (e.g. rate limit) cannot destroy the older copy.
    delete_document(document_id)
    stored = add_chunks(chunks, vectors)

    return IngestResult(
        document_id=document_id,
        document_name=name,
        pages=len(pages),
        chunks=stored,
    )


def ask(question: str, document_id: str | None = None) -> Answer:
    """Question -> query embedding -> Chroma search -> prompt -> Gemini -> answer.

    If document_id is given, only that document is searched.
    """
    # Steps 1-2: embed the question and fetch the top-k nearest chunks.
    # (retrieve() validates the question and raises RetrievalError if it is empty.)
    results = retrieve(question, document_id=document_id)

    # Nothing to search: answer honestly without spending a Gemini call.
    if not results:
        return Answer(answer=NO_DOCUMENTS_MESSAGE, sources=[])

    # Steps 3-4: build the prompt from the chunks and let Gemini answer.
    answer_text = generate_answer(question, results)

    return Answer(answer=answer_text, sources=results)
