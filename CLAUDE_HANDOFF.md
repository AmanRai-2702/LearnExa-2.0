# LearnExa Claude Handoff

## Current Phase
Phase 4 of 15 — Embeddings

## Last Completed Step
4.1 — embeddings.py written; tested with try_embeddings.py

## Last Completed File
backend/app/rag/embeddings.py

## Current Working Feature
embed_documents(texts) and embed_query(text) return Gemini vectors;
EmbeddingError has user-safe messages.

## Next File
backend/app/rag/vector_store.py

## Next Exact Task
Phase 5: add chromadb to requirements, write vector_store.py using a
PersistentClient at backend/data/chroma, one collection, add_chunks()
(store text, our own embeddings, metadata: document_id, document_name,
page_number, chunk_index), delete by document_id. Explain collections,
metadata, and how similarity search works. Test with a script.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd frontend ; npm run dev
python try_embeddings.py data\uploads\notes.pdf "What is LangChain?"

## Important Decisions
- One step at a time, complete file contents, WHAT/WHY/HOW/INTERVIEW
- No overengineering (no agents, LangGraph, Redux, etc.)
- Gemini key stays in backend/.env only; never paste in chat or commit
- User is a beginner on Windows, VS Code, cmd terminal (activate.bat);
  go slowly, explain every command and file
- Project root is C:\LearnExa
- Test PDF: backend/data/uploads/notes.pdf (143 pages, OneNote export)

## Known Problems
None.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables