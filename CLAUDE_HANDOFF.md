# LearnExa Claude Handoff

## Current Phase
Phase 5 of 15 — Chroma

## Last Completed Step
5.1 — vector_store.py written; tested with try_chroma.py

## Last Completed File
backend/app/rag/vector_store.py

## Current Working Feature
add_chunks(chunks, embeddings), search(query_embedding, top_k, document_id),
count_chunks(), delete_document(). Persistent Chroma at backend/data/chroma.

## Next File
backend/app/rag/retriever.py

## Next Exact Task
Phase 6: retriever.py combines embed_query + vector_store.search using
TOP_K from settings. Return SearchResult list. Handle empty question and
no results. Explain top-k (too small / too large), irrelevant retrieval.
Test with a script. Do not add rerankers or thresholds yet.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd frontend ; npm run dev
python try_chroma.py ingest data\uploads\notes.pdf
python try_chroma.py search "What is LangChain?"

## Important Decisions
- One step at a time, complete file contents, WHAT/WHY/HOW/INTERVIEW
- No overengineering (no agents, LangGraph, Redux, etc.)
- Gemini key stays in backend/.env only; never paste in chat or commit
- User is a beginner on Windows, VS Code, cmd terminal (activate.bat);
  go slowly, explain every command and file
- Project root is C:\LearnExa
- Test PDF: backend/data/uploads/notes.pdf (143 pages, OneNote export)
- Measured embedding length: 3072 (gemini-embedding-001)

## Known Problems
None.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables