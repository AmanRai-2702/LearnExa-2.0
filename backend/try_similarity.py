import sys

from app.rag.embeddings import EmbeddingError, embed_query
from app.rag.vector_store import VectorStoreError, search

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOP_K = 5

# EDIT THIS: questions your uploaded document DOES answer.
# Use real questions about what is inside the document you ingested.
RELATED = [
    "EDIT ME: a question your document answers",
    "EDIT ME: another question your document answers",
    "EDIT ME: a third question your document answers",
    "EDIT ME: a fourth question your document answers",
]

# Questions that have nothing to do with a study document.
UNRELATED = [
    "Who won the FIFA World Cup in 2018?",
    "What is a good recipe for chocolate cake?",
    "How tall is Mount Everest?",
    "What is the capital city of Australia?",
]

if any(question.startswith("EDIT ME") for question in RELATED):
    print("Open backend/try_similarity.py and replace the EDIT ME questions")
    print("with real questions that your uploaded document answers.")
    sys.exit(1)

# Optional: python try_similarity.py <document_id> searches only that document.
document_id = sys.argv[1] if len(sys.argv) > 1 else None

best_scores = {"related": [], "unrelated": []}

try:
    for kind, questions in (("related", RELATED), ("unrelated", UNRELATED)):
        for question in questions:
            results = search(embed_query(question), top_k=TOP_K, document_id=document_id)
            if not results:
                print(f"{kind:9}  (no chunks stored)  {question}")
                continue

            best = results[0].similarity
            last = results[-1].similarity
            best_scores[kind].append(best)
            snippet = results[0].text[:90].replace("\n", " ")

            print(f"{kind:9}  best {best:.3f}  chunk {len(results)} {last:.3f}  {question[:55]}")
            print(f"           top chunk (page {results[0].page_number}): {snippet}")
except (EmbeddingError, VectorStoreError) as error:
    print(f"ERROR: {error}")
    sys.exit(1)

print()
if best_scores["related"] and best_scores["unrelated"]:
    lowest_related = min(best_scores["related"])
    highest_unrelated = max(best_scores["unrelated"])
    print(f"Lowest best-score among RELATED questions:     {lowest_related:.3f}")
    print(f"Highest best-score among UNRELATED questions:  {highest_unrelated:.3f}")
    gap = lowest_related - highest_unrelated
    if gap > 0:
        print(f"Gap: {gap:.3f}. On these questions the two groups do not overlap.")
        print("That is a hint, not proof: try more questions before trusting any cutoff.")
    else:
        print(f"Overlap: {-gap:.3f}. Some unrelated questions scored as high as related ones.")
        print("A cutoff would wrongly drop good answers or let bad ones through.")