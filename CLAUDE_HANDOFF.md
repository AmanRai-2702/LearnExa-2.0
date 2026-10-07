# LearnExa Claude Handoff

## Current Phase
Phase 8 of 15 — Complete RAG

## Last Completed Step
8.1 — pipeline.py and try_pipeline.py written (not yet run by the user)

## Last Completed File
backend/app/rag/pipeline.py

## Current Working Feature
ingest_document(path, document_id, name) and ask(question, document_id=None)
returning Answer(answer, sources). Empty retrieval returns a fixed message
without calling Gemini.

## Next File
backend/app/api/documents.py (Phase 9), once the user confirms the test results

## Next Exact Task
Confirm pipeline test output with the user. Then Phase 9: schemas
(models/schemas.py), document_service.py (uuid ids, saving uploads, listing,
deleting), then POST /api/documents/upload, GET /api/documents,
DELETE /api/documents/{id}, POST /api/chat. Map the rag error classes to HTTP
status codes. One file at a time.

## Working Commands
cd backend ; .venv\Scripts\activate.bat
python try_pipeline.py ingest data\uploads\sample.txt
python try_pipeline.py ask "your question about sample.txt" sample
python try_pipeline.py ask "anything" does_not_exist

## Important Decisions
- One step at a time, complete files, WHAT/WHY/HOW/INTERVIEW
- No overengineering; Gemini key only in backend/.env, never in chat, zips or Git
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly
- Project root C:\LearnExa; test PDF backend/data/uploads/notes.pdf
- Free-tier limits matter: embeddings 100 texts/min, low generation limits
- Prefer sample.txt for quick pipeline tests (notes.pdf takes minutes to embed)

## Known Problems
Footer-only chunks; retrieval returns nearest chunks even if unrelated.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables
