# LearnExa Claude Handoff

## Current Phase
Phase 13 of 15 — Error Handling (13.1 done and committed; 13.2 = manual
website check, in progress)

## Last Completed Step
13.2 setup — gave the user an 11-row website walkthrough with exact test files
and commands. 13.1 was confirmed: 141 pytest tests passed, commit bfa6248.
npm run build also confirmed passing.

## Last Completed File
backend/try_similarity.py (optional; the website's "Similarity" on source cards
is the main way to read scores now)

## Current Working Feature
Full app works end to end. Backend failures are retried or reported with a
friendly message, and failed saves leave no orphan chunks or files.

## Next File
None until the walkthrough is reported.

## Next Exact Task
1. User reports each walkthrough row (ok, or the exact message seen) plus the
   Similarity numbers and Gemini's answer for the related question
   ("What is overfitting?") and the off-topic one ("Who won the 2018 World Cup?").
2. Fix any gap found (message wording, wrong status code, UI problem).
3. Decide a similarity cutoff ONLY from the measured numbers. If related and
   unrelated scores overlap, or Gemini already says "not found" for off-topic
   questions, recommend NO cutoff and explain why. If they separate clearly,
   treat it as a hint from few questions and propose a small configurable
   MIN_SIMILARITY setting in config.py with tests; never invent a number.
4. End of Phase 13: give COMPLETE state files and Git commands.
5. Phase 14: delete try_*.py, write README.md, docs/architecture.md,
   docs/rag-explanation.md. Phase 15: docs/interview-preparation.md from the
   real implementation.
6. Gently remind (once) about npm run lint, never reported.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd backend ; .venv\Scripts\activate.bat ; pytest -v
cd frontend ; npm run dev ; npx tsc --noEmit ; npm run lint ; npm run build
Swagger: http://localhost:8000/docs
python try_documents.py add data\uploads\sample.txt   (seed a test document)
python try_similarity.py [document_id]
git archive -o learnexa-phase13.zip HEAD   (zip without .env)

## Important Decisions
- One step at a time, WHAT/WHY/HOW/INTERVIEW, CURRENT PROGRESS footer
- GIVE CODE DIRECTLY IN CHAT as code blocks (no file cards)
- Always provide complete files; no overengineering
- EVERY RESPONSE ends with the COMPLETE updated PROJECT_STATE.md and
  CLAUDE_HANDOFF.md (the user asked for this explicitly)
- ALWAYS include a Git section (exact commands) after every step
- Gemini key only in backend/.env, never in chat, zips or Git; zip with
  git archive; rotate the key if a zip containing .env was ever shared
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly
- Project root C:\LearnExa; test files backend/data/uploads/notes.pdf (12.9 MB,
  over the 10 MB limit: use only for "too large" tests), sample.txt,
  study_notes.txt, empty.txt, fake.pdf, photo.png
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
  lint/pytest output and the walkthrough results

## Known Problems
Footer-only chunks; irrelevant retrieval relies on the prompt only (cutoff being
measured); Gemini 503/429 spikes; JSON registry single-user; upload blocks until
ingestion completes; duplicated limits in frontend and backend; no chat memory;
no GFM tables in answers; no frontend tests; lint output never shown;
walkthrough results not yet reported.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables