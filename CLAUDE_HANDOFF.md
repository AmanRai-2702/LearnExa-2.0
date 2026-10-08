# LearnExa Claude Handoff

## Current Phase
Phase 14 of 15 — Documentation (14.1 done: try_*.py deleted, README.md written)

## Last Completed Step
14.1 — Phase 13 was closed without the manual website walkthrough or a
measured similarity cutoff (user was short on time; recorded as known issues).
try_*.py scripts were deleted and README.md (all 15 master-prompt sections plus
Limitations) was written from the real code. The user still has to run pytest
(expect 141 passed) and commit.

## Last Completed File
README.md

## Current Working Feature
Full app works end to end (141 backend tests passed, npm run build passed).

## Next File
docs/architecture.md

## Next Exact Task
1. Confirm pytest shows 141 passed and the commit was made.
2. Step 14.2: docs/architecture.md — components and responsibilities, the exact
   upload flow and chat flow (browser -> api.ts -> endpoint -> service/pipeline
   -> Gemini/Chroma and back), the error-handling map (which error becomes which
   HTTP status and message), key design decisions and trade-offs, and honest
   limitations. Base it on the real source files in the user's zip; ask for a
   fresh git archive zip if code changed.
3. Step 14.3: docs/rag-explanation.md — RAG concepts explained with THIS
   project's actual values (chunk 1000/150, top-k 5, cosine, task types,
   prompt rules). Do not claim hallucinations are eliminated; no invented
   metrics.
4. Phase 15: docs/interview-preparation.md with questions from the master
   prompt, answered from the real implementation.
5. Gently remind (once) about the unreported npm run lint and the skipped
   website walkthrough.

## Working Commands
cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
cd backend ; .venv\Scripts\activate.bat ; pytest -v
cd frontend ; npm run dev ; npx tsc --noEmit ; npm run lint ; npm run build
Swagger: http://localhost:8000/docs
git archive -o learnexa-phase14.zip HEAD   (zip without .env)

## Important Decisions
- One step at a time, WHAT/WHY/HOW/INTERVIEW, CURRENT PROGRESS footer
- GIVE CODE DIRECTLY IN CHAT as code blocks (no file cards)
- Always provide complete files; no overengineering
- EVERY RESPONSE ends with the COMPLETE updated PROJECT_STATE.md and
  CLAUDE_HANDOFF.md (the user asked for this explicitly)
- ALWAYS include a Git section (exact commands) after every step
- Gemini key only in backend/.env, never in chat, zips or Git; zip with
  git archive; rotate the key if a zip containing .env was ever shared
- User is a beginner on Windows, VS Code, cmd (activate.bat); go slowly; the
  user is short on time, so keep steps lean and do not insist on skipped checks
- Project root C:\LearnExa
- Frontend type names: UploadedDocument, Source, Message; errors are
  ApiError(message, status)
- UI style: Tailwind, zinc neutrals + indigo accent
- Do not add dependencies without explaining
- Tests: never call Gemini, never touch real data/chroma or documents.json
- Claude's sandbox has no internet and cannot install the app's dependencies:
  it cannot run the real tests, so say plainly when tests were not run by Claude
- Read the real source files from the user's zip before writing code or docs
  that depend on them; never open or print backend/.env
- Never invent metrics; docs must state limitations honestly

## Known Problems
Footer-only chunks; irrelevant retrieval relies on the prompt only (no cutoff
measured or added); Gemini 503/429 spikes; JSON registry single-user; upload
blocks until ingestion completes; duplicated limits in frontend and backend; no
chat memory; no GFM tables in answers; no frontend tests; lint output never
shown; website walkthrough never run; README screenshots are a placeholder;
frontend/README.md is still the default one.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables