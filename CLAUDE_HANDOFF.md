# LearnExa Claude Handoff

## Current Phase
Phase 6 of 15 — Retrieval

## Last Completed Step
6.1 — retriever.py written; tested with try_retriever.py

## Last Completed File
backend/app/rag/retriever.py

## Current Working Feature
retrieve(question, top_k=None, document_id=None) -> list[SearchResult]
(embeds question, searches Chroma). Raises RetrievalError for empty question.

## Next File
backend/app/rag/prompts.py, then a Gemini generation module

## Next Exact Task
Phase 7: user must pick a current Gemini model for GEMINI_MODEL (verify the
name; do not guess; model names change). Write prompts.py (short RAG prompt:
use only context, say when not found, cite sources), a generation function
using google-genai, test with retrieve() output. Handle rate limits and
errors with a user-safe GenerationError. Explain hallucination honestly
(RAG reduces, does not eliminate).

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd frontend ; npm run dev
python try_retriever.py "What is LangChain?"

## Important Decisions
- One step at a time, complete file contents, WHAT/WHY/HOW/INTERVIEW
- No overengineering (no agents, LangGraph, Redux, etc.)
- Gemini key stays in backend/.env only; never paste in chat or commit
- User is a beginner on Windows, VS Code, cmd terminal (activate.bat);
  go slowly, explain every command and file
- Project root is C:\LearnExa
- Test PDF: backend/data/uploads/notes.pdf (143 pages, OneNote export)
- Measured embedding length: 3072 (gemini-embedding-001)
- Free tier embedding limit: 100 texts/minute (ingest is paced)

## Known Problems
Retrieval returns tiny footer-only chunks and always returns nearest chunks
even when unrelated.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables