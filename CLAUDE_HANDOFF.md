# LearnExa Claude Handoff

## Current Phase
Phase 12 of 15 — Testing (finishing); Phase 13 (error handling) is next

## Last Completed Step
12.6 — tests/conftest.py, tests/test_api.py written and tests/test_health.py updated
(client fixture moved to conftest). Expected total: 111 passed. User confirmed 80
passed before this step.

## Last Completed File
backend/tests/test_api.py

## Current Working Feature
Full app works end to end. Backend test suite covers health/CORS, chunking, loader,
document service, vector store, retriever and both API routers.

## Next File
None for Phase 12 once pytest shows 111 passed. Phase 13 starts with a review.

## Next Exact Task
Confirm `pytest -v` shows 111 passed (from backend, venv active) and commit with
"Add API tests and share the client fixture". If test_api.py fails, fix from the pasted
output (possible: empty-file upload returning 422 instead of 400). Ask again for the
output of npm run tsc/lint/build (never shown). Then Phase 13: go through the master
prompt's error list one by one (missing Gemini key, invalid key, Gemini API errors,
invalid file type, empty file, oversized file, PDF extraction failure, embedding
failure, Chroma failure, empty question, retrieval failure, no relevant context).
For each: say where it is handled, verify it (manual test or automated test), fix gaps,
and check the frontend message. Ideas to examine: partial Chroma chunks after failed
ingestion, "Gemini configured" only meaning a key exists, 422 list-shaped detail.
Then Phase 14 (README, docs/architecture.md, docs/rag-explanation.md; delete try_*.py
first) and Phase 15 (docs/interview-preparation.md based on the real implementation).

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
- Claude's sandbox has no internet and cannot install the app's dependencies: it cannot
  run the real tests, so say plainly when tests were not run by Claude (loader behaviours
  were verified against real pypdf)
- Read the real source files from the user's zip before writing code that depends on
  them (never guess names); never open or print backend/.env
- The user often replies "move on" without reporting results: gently ask for build/lint
  output and pytest output, and check the pass count matches the expected number

## Known Problems
Footer-only chunks (documented by a test, not fixed); irrelevant retrieval; Gemini
503/429 spikes; JSON registry single-user; upload blocks until ingestion completes;
duplicated limits in frontend and backend; no chat memory; no GFM tables in answers;
no frontend tests; build/lint output never shown; test_api.py not yet run by the user;
backend/.env was included in shared zips.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables