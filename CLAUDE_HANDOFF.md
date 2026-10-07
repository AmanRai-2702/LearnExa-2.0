# LearnExa Claude Handoff

## Current Phase
Phase 13 of 15 — Error Handling (13.1 done and committed; 13.2 next)

## Last Completed Step
13.1 — gemini_errors.py (new), embeddings.py, generator.py, pipeline.py and
document_service.py hardened; test_gemini_errors.py and test_cleanup.py added.
User confirmed 141 passed and committed (bfa6248).

## Last Completed File
backend/tests/test_cleanup.py

## Current Working Feature
Full app works end to end. Backend failures are retried or reported with a
friendly message, and failed saves leave no orphan chunks or files.

## Next File
backend/try_similarity.py (temporary measurement script, 13.2 Part B)

## Next Exact Task
1. Ask for npx tsc --noEmit, npm run lint, npm run build output (never shown)
   and the manual walkthrough results (backend off; .png; empty file; 12.9 MB
   notes.pdf; fake PDF; valid txt; no documents + chat; WRONG API KEY in
   backend/.env then chat and upload; backend stopped mid-chat; off-topic
   question; deleted-document chat link). Fix any gap found.
2. When the user says "next": write try_similarity.py. It embeds related and
   unrelated questions with embed_query and prints the top similarity per
   question (embedding calls only, NO generation calls). Decide a cutoff only
   from the user's real numbers; if the numbers overlap, recommend no cutoff.
3. End of Phase 13: give COMPLETE state files, commit.
4. Phase 14: delete try_*.py, write README.md, docs/architecture.md,
   docs/rag-explanation.md. Phase 15: docs/interview-preparation.md from the
   real implementation.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd backend ; .venv\Scripts\activate.bat ; pytest -v
cd frontend ; npm run dev ; npx tsc --noEmit ; npm run lint ; npm run build
Swagger: http://localhost:8000/docs
python try_documents.py add data\uploads\sample.txt   (seed a test document)
git archive -o learnexa-phase13.zip HEAD   (zip without .env)

## Important Decisions
- One step at a time, WHAT/WHY/HOW/INTERVIEW, CURRENT PROGRESS footer
- GIVE CODE DIRECTLY IN CHAT as code blocks (no file cards)
- Always provide complete files; no overengineering
- AFTER EVERY PHASE give the COMPLETE PROJECT_STATE.md and CLAUDE_HANDOFF.md
- ALWAYS include a Git section (exact commands) after every step
- Gemini key only in backend/.env, never in chat, zips or Git; zip with
  git archive; rotate the key if a zip containing .env was ever shared
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly
- Project root C:\LearnExa; test files backend/data/uploads/notes.pdf (12.9 MB,
  over the 10 MB limit: use only for "too large" tests), sample.txt
- Frontend type names: UploadedDocument, Source, Message; errors are
  ApiError(message, status)
- UI style: Tailwind, zinc neutrals + indigo accent
- Page owns data; child components use props + callbacks
- Any page using useSearchParams must wrap it in Suspense
- Do not add dependencies without explaining
- Tests: never call Gemini, never touch real data/chroma or documents.json
- Claude's sandbox has no internet and cannot install the app's dependencies:
  it cannot run the real tests, so say plainly when tests were not run by Claude
- Read the real source files from the user's zip before writing code that
  depends on them; never open or print backend/.env
- Never invent metrics: measure similarity scores before choosing a cutoff
- The user often replies "move on" without reporting results: gently ask for
  build/lint output and pytest output, and check the pass count matches

## Known Problems
Footer-only chunks; irrelevant retrieval relies on the prompt only (no measured
cutoff yet); Gemini 503/429 spikes; JSON registry single-user; upload blocks
until ingestion completes; duplicated limits in frontend and backend; no chat
memory; no GFM tables in answers; no frontend tests; tsc/lint/build output
never shown; manual error walkthrough not reported.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables