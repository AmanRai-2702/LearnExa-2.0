import math
import sys
from pathlib import Path

from app.rag.embeddings import EmbeddingError, embed_documents, embed_query
from app.rag.loader import load_document
from app.rag.splitter import split_pages

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """cos(angle) = (a . b) / (|a| * |b|)"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


try:
    # --- Demo 1: meaning vs. keywords ---
    sentences = [
        "A model that memorises its training data performs badly on new data.",
        "Gradient descent updates weights to reduce the loss.",
        "My favourite food is pizza with extra cheese.",
    ]
    question = "What is overfitting?"

    sentence_vectors = embed_documents(sentences)
    question_vector = embed_query(question)

    print(f"Vector length (measured): {len(question_vector)}")
    print(f"First 5 numbers: {question_vector[:5]}")
    print(f"\nQuestion: {question}")
    for sentence, vector in zip(sentences, sentence_vectors):
        score = cosine_similarity(question_vector, vector)
        print(f"  {score:.3f}  {sentence}")

    # --- Demo 2: mini retrieval over your own PDF (first 20 chunks) ---
    if len(sys.argv) > 1:
        pages = load_document(Path(sys.argv[1]))
        chunks = split_pages(pages, "test-doc", Path(sys.argv[1]).name)[:20]
        chunk_vectors = embed_documents([c.text for c in chunks])

        query = sys.argv[2] if len(sys.argv) > 2 else "What is LangChain?"
        query_vector = embed_query(query)

        ranked = sorted(
            zip(chunks, chunk_vectors),
            key=lambda pair: cosine_similarity(query_vector, pair[1]),
            reverse=True,
        )
        print(f"\nQuery: {query}  (searching the first {len(chunks)} chunks)")
        for chunk, vector in ranked[:3]:
            score = cosine_similarity(query_vector, vector)
            print(f"\n  {score:.3f}  page {chunk.page_number}, chunk {chunk.chunk_index}")
            print(f"  {chunk.text[:200]}")

except EmbeddingError as error:
    print(f"ERROR: {error}")