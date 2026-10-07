import sys
from pathlib import Path

from app.core.config import get_settings
from app.rag.embeddings import EmbeddingError, embed_documents, embed_query
from app.rag.loader import DocumentLoadError, load_document
from app.rag.splitter import split_pages
from app.rag.vector_store import (
    VectorStoreError,
    add_chunks,
    count_chunks,
    delete_document,
    search,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOC_ID = "test-doc"

USAGE = """Usage:
  python try_chroma.py ingest <file>
  python try_chroma.py search "<question>"
  python try_chroma.py delete"""

if len(sys.argv) < 2:
    print(USAGE)
    sys.exit(1)

command = sys.argv[1]

try:
    if command == "ingest":
        path = Path(sys.argv[2])
        pages = load_document(path)
        chunks = split_pages(pages, DOC_ID, path.name)
        print(f"Loaded {len(pages)} pages, made {len(chunks)} chunks")

        removed = delete_document(DOC_ID)  # avoid duplicates if re-ingesting
        if removed:
            print(f"Removed {removed} old chunks of this document")

        vectors = embed_documents([c.text for c in chunks])
        stored = add_chunks(chunks, vectors)
        print(f"Stored {stored} chunks in Chroma")
        print(f"Total chunks in database: {count_chunks()}")

    elif command == "search":
        question = sys.argv[2]
        query_vector = embed_query(question)
        results = search(query_vector, top_k=get_settings().top_k)
        print(f"Question: {question}")
        print(f"Chunks in database: {count_chunks()}")
        if not results:
            print("No results. Did you run ingest first?")
        for result in results:
            print(
                f"\n  {result.similarity:.3f}  {result.document_name}, "
                f"page {result.page_number}, chunk {result.chunk_index}"
            )
            print(f"  {result.text[:200]}")

    elif command == "delete":
        print(f"Deleted {delete_document(DOC_ID)} chunks")
        print(f"Total chunks in database: {count_chunks()}")

    else:
        print(USAGE)

except (DocumentLoadError, EmbeddingError, VectorStoreError) as error:
    print(f"ERROR: {error}")