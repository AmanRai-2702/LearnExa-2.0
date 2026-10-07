import sys

from app.rag.embeddings import EmbeddingError
from app.rag.generator import GenerationError, generate_answer
from app.rag.retriever import RetrievalError, retrieve
from app.rag.vector_store import VectorStoreError

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

question = sys.argv[1] if len(sys.argv) > 1 else ""

try:
    results = retrieve(question)
    print(f"Question: {question}")
    print(f"Retrieved {len(results)} chunks\n")

    answer = generate_answer(question, results)
    print("ANSWER:")
    print(answer)

    print("\nSOURCES:")
    for number, result in enumerate(results, start=1):
        print(
            f"  Source {number}: {result.document_name}, page {result.page_number} "
            f"(similarity {result.similarity:.3f})"
        )
except (RetrievalError, EmbeddingError, VectorStoreError, GenerationError) as error:
    print(f"ERROR: {error}")