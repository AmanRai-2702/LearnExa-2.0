# LearnExa Claude Handoff

## Current Phase
Phase 12 of 15 — Testing

## Last Completed Step
12.2 — backend/tests/test_chunking.py written (18 tests; expected total 24 passed
with the 6 health tests), awaiting the user's pytest run

## Last Completed File
backend/tests/test_chunking.py

## Current Working Feature
Full app works end to end. pytest infrastructure is in place (pytest.ini,
test_health.py committed; test_chunking.py written).

## Next File
backend/tests/test_loader.py

## Next Exact Task
Confirm `pytest -v` shows 24 passed (from backend, venv active) and commit with
"Add chunking tests". Ask again for the output of npm run tsc/lint/build (never shown).
Then 12.3: write tests/test_loader.py (complete file) using tmp_path files:
txt loads as one page with page_number 1, empty/whitespace txt raises
DocumentLoadError, unsupported extension raises, non-UTF-8 txt raises, corrupted PDF
raises. Real names: load_document(path), load_txt, load_pdf, PageText(page_number, text),
DocumentLoadError, SUPPORTED_EXTENSIONS. Never use the real documents or Gemini.
Then 12.4 document_service validation tests (monkeypatch ingest_document and the
module's DATA_DIR/UPLOADS_DIR/REGISTRY_FILE to tmp_path), 12.5 retrieval/vector store
tests with fake embeddings and a temp Chroma dir (monkeypatch vector_store.CHROMA_DIR)
and retriever with embed_query monkeypatched, 12.6 API tests for /api/documents and
/api/chat with pipeline/service functions monkeypatched. Move the `client` fixture to
tests/conftest.py when a second test file needs it. Then Phase 13 (error handling),
14 (documentation), 15 (interview preparation).

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd backend ; .venv\Scripts\activate.bat ; pytest -v
cd frontend ; npm run dev ; npx tsc --noEmit ; npm run lint ; npm run build
Swagger: http://localhost:8000/docs
python try_documents.py add data\uploads\sample.txt   (seed a test document)

## Important Decisions
- One step at a time, WHAT/WHY/HOW/INTERVIEW, CURRENT PROGRESS footer
- GIVE CODE DIRECTLY IN CHAT as code blocks (no file cards)
- Always provide complete files; no overengineering
- AFTER EVERY PHASE give the COMPLETE PROJECT_STATE.md and CLAUDE_HANDOFF.md
  (full files, never small edits)
- ALWAYS include a Git section (exact commands) after every step
- Gemini key only in backend/.env, never in chat, zips or Git. The user has
  zipped backend/.env twice: remind them to exclude it and to rotate the key if shared
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly
- Project root C:\LearnExa; test files backend/data/uploads/notes.pdf (12.9 MB, over
  the 10 MB limit: use it only for "too large" tests), sample.txt
- Frontend type names: UploadedDocument, Source, Message; errors are ApiError(message, status)
- UI style: Tailwind, zinc neutrals + indigo accent
- Page owns data; child components use props + callbacks
- Any page using useSearchParams must wrap it in Suspense (verify with npm run build)
- Do not add dependencies without explaining
- Tests: never call Gemini, never touch real data/chroma or documents.json
- Claude's sandbox has no internet: it cannot install packages or run the real
  splitter/Chroma/Gemini, so tell the user plainly when tests were not run by Claude
- The user often replies "move on" without reporting results: gently ask for build/lint
  output and pytest output

## Known Problems
Footer-only chunks (documented by a test, not fixed); irrelevant retrieval; Gemini
503/429 spikes; JSON registry single-user; upload blocks until ingestion completes;
duplicated limits in frontend and backend; no chat memory; no GFM tables in answers;
build/lint output never shown; chunking tests not yet run by the user; backend/.env
was included in shared zips.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables