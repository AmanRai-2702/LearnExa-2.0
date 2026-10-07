# LearnExa Claude Handoff

## Current Phase
Phase 9 of 15 — FastAPI Integration

## Last Completed Step
9.1 — models/schemas.py written (awaiting the user's test result)

## Last Completed File
backend/app/models/schemas.py

## Current Working Feature
Phase 8 pipeline is committed and working: ingest_document(), ask().
Schemas: DocumentResponse, ChatRequest, SourceResponse, ChatResponse, ErrorResponse.

## Next File
backend/app/services/document_service.py

## Next Exact Task
Decide where document metadata (pages, chunks, upload time) is stored since
Chroma lacks pages/upload time (simple option: small JSON registry in
backend/data). Then write document_service.py (uuid ids, saving uploads,
validation, list, delete), then api/documents.py, then api/chat.py, then
register routers in main.py. One file at a time.

## Working Commands
cd backend ; .venv\Scripts\activate.bat
python try_pipeline.py ingest data\uploads\sample.txt
python try_pipeline.py ask "question" sample

## Important Decisions
- One step at a time, WHAT/WHY/HOW/INTERVIEW, CURRENT PROGRESS footer
- GIVE CODE DIRECTLY IN CHAT as code blocks (the user does not want file cards)
- Always provide complete files; no overengineering
- Gemini key only in backend/.env, never in chat, zips or Git
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly
- Project root C:\LearnExa; test files backend/data/uploads/notes.pdf, sample.txt
- Free-tier limits matter

## Known Problems
Footer-only chunks; retrieval returns nearest chunks even if unrelated;
Gemini 503 spikes (wait, retry, or change GEMINI_MODEL).

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables