from app.rag.vector_store import SearchResult

SYSTEM_INSTRUCTION = """You are LearnExa, a study assistant.
Answer the question using ONLY the context provided by the user.
- If the context does not contain the answer, say clearly that you could not find it in the uploaded documents. Do not guess or use outside knowledge.
- Explain concepts clearly and simply.
- Mention the source number (for example "Source 2") when you use information from it.
- Do not invent facts, page numbers or quotes."""


def build_context(results: list[SearchResult]) -> str:
    """Label each retrieved chunk so the model (and we) can refer to it."""
    blocks = []
    for number, result in enumerate(results, start=1):
        header = f"[Source {number}: {result.document_name}, page {result.page_number}]"
        blocks.append(f"{header}\n{result.text}")
    return "\n\n".join(blocks)


def build_user_prompt(question: str, results: list[SearchResult]) -> str:
    """Combine the retrieved context and the question into one message."""
    return (
        f"Context:\n{build_context(results)}\n\n"
        f"Question: {question.strip()}\n\n"
        "Answer:"
    )