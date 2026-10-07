from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.rag.loader import PageText


@dataclass
class Chunk:
    """One piece of a document, plus where it came from (its metadata)."""

    text: str
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int  # position of this chunk within the whole document, from 0


def split_pages(
    pages: list[PageText],
    document_id: str,
    document_name: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """Split each page into chunks, keeping page numbers and metadata.

    If chunk_size / chunk_overlap are not given, the values from settings are used.
    """
    settings = get_settings()
    size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap

    if size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0 or overlap >= size:
        raise ValueError("chunk_overlap must be at least 0 and smaller than chunk_size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )

    chunks: list[Chunk] = []
    chunk_index = 0

    for page in pages:
        for piece in splitter.split_text(page.text):
            piece = piece.strip()
            if not piece:  # never keep empty chunks
                continue
            chunks.append(
                Chunk(
                    text=piece,
                    document_id=document_id,
                    document_name=document_name,
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1

    return chunks