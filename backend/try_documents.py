import sys
from pathlib import Path

from app.rag.embeddings import EmbeddingError
from app.rag.loader import DocumentLoadError
from app.rag.vector_store import VectorStoreError
from app.services.document_service import (
    DocumentServiceError,
    add_document,
    list_documents,
    remove_document,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USAGE = (
    "Usage:\n"
    "  python try_documents.py add <file path>\n"
    "  python try_documents.py list\n"
    "  python try_documents.py delete <document_id>"
)

ERRORS = (DocumentServiceError, DocumentLoadError, EmbeddingError, VectorStoreError)

command = sys.argv[1] if len(sys.argv) > 1 else ""

try:
    if command == "add" and len(sys.argv) > 2:
        path = Path(sys.argv[2])
        document = add_document(path.name, path.read_bytes())
        print(f"Added: {document}")
    elif command == "list":
        documents = list_documents()
        print(f"{len(documents)} document(s)")
        for doc in documents:
            print(f"  {doc.document_id}  {doc.name}  {doc.pages} pages  {doc.chunks} chunks  {doc.uploaded_at}")
    elif command == "delete" and len(sys.argv) > 2:
        remove_document(sys.argv[2])
        print("Deleted.")
    else:
        print(USAGE)
except ERRORS as error:
    print(f"ERROR: {error}")