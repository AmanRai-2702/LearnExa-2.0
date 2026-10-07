import sys

from app.rag.embeddings import EmbeddingError
from app.rag.retriever import RetrievalError, retrieve
from app.rag.vector_store import VectorStoreError

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

question = sys.argv[1] if len(sys.argv) > 1 else ""
top_k = int(sys.argv[2]) if len(sys.argv) > 2 else None

try:
    results = retrieve(question, top_k=top_k)
    print(f"Question: {question}")
    print(f"Results returned: {len(results)}")
    if not results:
        print("Nothing found. Did you ingest a document first?")
    for rank, result in enumerate(results, start=1):
        print(
            f"\n#{rank}  similarity {result.similarity:.3f}  "
            f"{result.document_name}, page {result.page_number}, "
            f"chunk {result.chunk_index}, {len(result.text)} chars"
        )
        print(f"    {result.text[:150]}")
except (RetrievalError, EmbeddingError, VectorStoreError) as error:
    print(f"ERROR: {error}")