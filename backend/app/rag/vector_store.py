from dataclasses import dataclass
from pathlib import Path

import chromadb

from app.rag.splitter import Chunk

# backend/app/rag/vector_store.py -> parents[2] is the backend folder.
# Using an absolute path means it works no matter where we run Python from.
CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma"
COLLECTION_NAME = "learnexa_chunks"

# Chroma limits how many records can be added in one call; we add in groups.
ADD_BATCH_SIZE = 500


class VectorStoreError(Exception):
    """Raised when the vector database fails. The message is safe to show users."""


@dataclass
class SearchResult:
    """One retrieved chunk, with its metadata and how close it was to the query."""

    text: str
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    similarity: float  # cosine similarity: higher means more similar


def _get_collection():
    """Open (or create) the persistent collection."""
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            # Compare vectors by cosine distance (distance = 1 - cosine similarity).
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        raise VectorStoreError(
            "Could not open the document database. Please try again."
        ) from exc


def add_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> int:
    """Store chunks together with their embeddings and metadata."""
    if not chunks:
        raise VectorStoreError("There are no chunks to store.")
    if len(chunks) != len(embeddings):
        raise VectorStoreError("Chunks and embeddings do not match.")

    collection = _get_collection()

    try:
        for start in range(0, len(chunks), ADD_BATCH_SIZE):
            batch = chunks[start : start + ADD_BATCH_SIZE]
            collection.add(
                ids=[f"{c.document_id}_{c.chunk_index}" for c in batch],
                documents=[c.text for c in batch],
                embeddings=embeddings[start : start + ADD_BATCH_SIZE],
                metadatas=[
                    {
                        "document_id": c.document_id,
                        "document_name": c.document_name,
                        "page_number": c.page_number,
                        "chunk_index": c.chunk_index,
                    }
                    for c in batch
                ],
            )
    except Exception as exc:
        raise VectorStoreError(
            "Could not save this document to the database. Please try again."
        ) from exc

    return len(chunks)


def search(
    query_embedding: list[float],
    top_k: int,
    document_id: str | None = None,
) -> list[SearchResult]:
    """Return the top_k chunks closest to the query vector (best first).

    If document_id is given, only chunks of that document are searched.
    """
    if top_k <= 0:
        raise VectorStoreError("top_k must be greater than 0.")

    collection = _get_collection()

    try:
        if collection.count() == 0:
            return []

        response = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"document_id": document_id} if document_id else None,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise VectorStoreError(
            "Could not search the document database. Please try again."
        ) from exc

    # Chroma returns one list per query; we sent one query, so take index 0.
    texts = response["documents"][0]
    metadatas = response["metadatas"][0]
    distances = response["distances"][0]

    return [
        SearchResult(
            text=text,
            document_id=meta["document_id"],
            document_name=meta["document_name"],
            page_number=meta["page_number"],
            chunk_index=meta["chunk_index"],
            similarity=1 - distance,
        )
        for text, meta, distance in zip(texts, metadatas, distances)
    ]


def count_chunks(document_id: str | None = None) -> int:
    """Count stored chunks, for all documents or for one."""
    collection = _get_collection()
    try:
        if document_id is None:
            return collection.count()
        found = collection.get(where={"document_id": document_id}, include=[])
        return len(found["ids"])
    except Exception as exc:
        raise VectorStoreError("Could not read the document database.") from exc


def delete_document(document_id: str) -> int:
    """Delete every chunk of one document. Returns how many were removed."""
    collection = _get_collection()
    try:
        found = collection.get(where={"document_id": document_id}, include=[])
        ids = found["ids"]
        if ids:
            collection.delete(ids=ids)
        return len(ids)
    except Exception as exc:
        raise VectorStoreError(
            "Could not delete this document from the database."
        ) from exc