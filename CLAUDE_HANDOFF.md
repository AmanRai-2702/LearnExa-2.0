# LearnExa Claude Handoff

## Current Phase
Phase 3 of 15 — Chunking

## Last Completed Step
3.1 — splitter.py written; tested with try_splitter.py

## Last Completed File
backend/app/rag/splitter.py

## Current Working Feature
split_pages(pages, document_id, document_name) returns list[Chunk]

## Next File
backend/app/rag/embeddings.py

## Next Exact Task
Phase 4: user must get a Gemini API key from Google AI Studio and put it in
backend/.env (never commit it). Add the Gemini SDK to requirements.txt (verify
the current package name first), write embeddings.py with document embeddings
and query embeddings (configurable GEMINI_EMBEDDING_MODEL), test on a few chunks.
Explain what embeddings are. Do not claim a fixed vector dimension unless verified.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd frontend ; npm run dev
python try_splitter.py data\uploads\notes.pdf

## Important Decisions
- One step at a time, complete file contents, WHAT/WHY/HOW/INTERVIEW
- No overengineering (no agents, LangGraph, Redux, etc.)
- Gemini key stays in backend only
- User is a beginner on Windows, VS Code, uses cmd terminal (activate.bat);
  go slowly, explain every command and file, create files via Explorer
- Project root is C:\LearnExa
- Test PDF: backend/data/uploads/notes.pdf (143 pages, OneNote export)

## Known Problems
None.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables