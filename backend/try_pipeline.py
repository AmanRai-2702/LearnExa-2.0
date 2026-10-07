import sys
from pathlib import Path

from app.rag.embeddings import EmbeddingError
from app.rag.generator import GenerationError
from app.rag.loader import DocumentLoadError
from app.rag.pipeline import ask, ingest_document
from app.rag.retriever import RetrievalError
from app.rag.vector_store import VectorStoreError

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USAGE = (
    "Usage:\n"
    "  python try_pipeline.py ingest <file path>\n"
    '  python try_pipeline.py ask "<question>" [document_id]'
)

ERRORS = (
    DocumentLoadError,
    EmbeddingError,
    VectorStoreError,
    RetrievalError,
    GenerationError,
)

if len(sys.argv) < 3:
    print(USAGE)
    sys.exit(1)

command = sys.argv[1]

try:
    if command == "ingest":
        path = Path(sys.argv[2])
        # For this test script the file name (without extension) is the document id.
        result = ingest_document(path, document_id=path.stem, name=path.name)
        print(
            f"Ingested '{result.document_name}' (id: {result.document_id}): "
            f"{result.pages} pages, {result.chunks} chunks stored."
        )
    elif command == "ask":
        question = sys.argv[2]
        document_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = ask(question, document_id=document_id)
        print("ANSWER:")
        print(result.answer)
        print("\nSOURCES:")
        if not result.sources:
            print("  (none)")
        for number, source in enumerate(result.sources, start=1):
            print(
                f"  Source {number}: {source.document_name}, page {source.page_number}, "
                f"chunk {source.chunk_index} (similarity {source.similarity:.3f})"
            )
    else:
        print(USAGE)
except ERRORS as error:
    print(f"ERROR: {error}")
