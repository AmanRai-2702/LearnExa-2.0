# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 13 — Error Handling. Step 13.1 (backend hardening) is done and committed
(bfa6248). Step 13.2 (manual frontend error walkthrough + measured similarity
experiment) is next.

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking (notes.pdf: 143 pages -> 149 chunks)
- Phase 4 — Embeddings (vector length 3072)
- Phase 5 — Chroma (149 chunks stored)
- Phase 6 — Retrieval
- Phase 7 — Gemini Generation
- Phase 8 — Complete RAG (pipeline.py)
- Phase 9 — FastAPI Integration (documents + chat endpoints)
- Phase 10 — Next.js Frontend (all pages)
- Phase 11 — UI Polish (markdown rendering, titles, safe links, mobile navbar)
- Phase 12 — Testing (111 tests, confirmed passing)
- Phase 13.1 — Backend error handling (141 tests total, confirmed passing)

## Completed Files
- .gitignore, backend/requirements.txt, backend/.env.example, backend/pytest.ini
- backend/tests/: conftest.py (shared `client` fixture), test_health.py (6),
  test_chunking.py (18), test_loader.py (15), test_document_service.py (18),
  test_retrieval.py (23), test_api.py (31), test_gemini_errors.py (21, new),
  test_cleanup.py (9, new)  -> 141 passed
- backend/app/core/config.py, main.py
- backend/app/api/: health.py, documents.py, chat.py
- backend/app/rag/: loader.py, splitter.py, embeddings.py, vector_store.py,
  retriever.py, prompts.py, generator.py, pipeline.py,
  gemini_errors.py (new: is_invalid_key_error)
- backend/app/models/schemas.py
- backend/app/services/document_service.py
- backend/try_*.py helpers (temporary, delete before Phase 14)
- frontend/lib/types.ts, frontend/lib/api.ts
- frontend/app/: layout.tsx, globals.css, page.tsx (Dashboard),
  documents/page.tsx + layout.tsx, chat/page.tsx + layout.tsx
- frontend/components/: layout/Navbar, documents/{DocumentCard, DocumentList,
  UploadZone}, chat/{SourceCard, ChatMessage, ChatInput, ChatWindow}

## Current File
None (13.2 is a manual check plus one temporary script)

## Next File
backend/try_similarity.py (temporary measurement script for 13.2, Part B)

## Working Features
- All backend endpoints: /health, /api/documents (upload/list/delete), /api/chat
- Frontend: Dashboard, Documents (list/delete/upload), Chat (markdown answers,
  sources, document selector, error bubbles), per-page titles, system dark mode
- Gemini errors: 429 and 503 retried with growing waits in embeddings AND
  generator; wrong key detected for 401/403 and for 400 mentioning "api key"
  (one shared helper); other errors fail at once with a friendly message
- Undo on failure: failed Chroma save removes partial chunks; failed registry
  save removes the file and the chunks; cleanup errors never hide the original
- pytest: 141 passed (confirmed by the user)

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd backend ; .venv\Scripts\activate.bat ; pytest -v
- pytest tests\<file>.py -v   (one file only)
- Swagger UI: http://localhost:8000/docs
- cd frontend ; npm run dev ; npx tsc --noEmit ; npm run lint ; npm run build
  (stop the dev server before building)
- python try_models.py
- python try_pipeline.py ingest data\uploads\sample.txt
- python try_pipeline.py ask "<question>" [document_id]
- python try_documents.py add <file> | list | delete <id>
- git status ; git add . ; git commit -m "..." ; git log --oneline
- Zip for sharing WITHOUT .env: git archive -o learnexa-phase13.zip HEAD
- Next docs: frontend/node_modules/next/dist/docs/01-app/

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters, google-genai, chromadb, python-multipart
Frontend: next 16.4.0, react 19.3.0, TypeScript, Tailwind CSS 4, react-markdown

## Environment Variables
Backend: ENVIRONMENT, FRONTEND_ORIGIN (must be exactly http://localhost:3000),
GEMINI_API_KEY (backend/.env only), GEMINI_MODEL, GEMINI_EMBEDDING_MODEL,
CHUNK_SIZE, CHUNK_OVERLAP, TOP_K
Frontend: NEXT_PUBLIC_API_URL (optional, default http://127.0.0.1:8000)

## Known Issues
- SECURITY: backend/.env was inside earlier project zips sent to Claude. If any
  zip containing it was shared, rotate the Gemini key. Use git archive to zip.
- Free tier: 100 embedded texts/min; big PDFs upload slowly (UI shows a timer).
  A busy Gemini can add up to 2 minutes of retry waiting per embedding batch.
- Gemini 503/429 spikes are Google-side (shown as a red error bubble).
- Scanned PDFs rejected (no OCR).
- Footer-only tiny chunks pollute retrieval; retrieval always returns nearest
  chunks even if irrelevant, so only the prompt prevents an off-topic answer.
  A similarity cutoff has NOT been measured yet (13.2 Part B).
- print() in embeddings.py for progress; switch to logging later.
- Repo is local only (not on GitHub yet).
- documents.json registry is single-user only; upload limit constant in service.
- Upload request blocks until ingestion finishes (production fix: background
  job + polling).
- 422 validation errors have list-shaped detail (api.ts handles both shapes).
- No automated frontend tests (only tsc/lint/build checks).
- npm tsc / lint / build output has NEVER been shown by the user (ask again).
- Frontend manual error walkthrough (13.2 Part A) not yet reported.
- Backend must be running or the frontend shows "Cannot reach the backend".
- Limits duplicated in frontend and backend (10 MB upload, 1000-char question).
- Chat history is React state only; no conversation memory sent to the backend.
- Markdown rendering has no GFM (tables, strikethrough); needs remark-gfm.
- No in-app theme toggle (follows the OS theme).
- Delete uses window.confirm (simple, not a styled modal).
- Dashboard stats are summed client-side from the full document list.
- "Gemini configured" pill only means a key exists, not that it is valid.
- try_*.py helper scripts still in backend/ (delete before the documentation phase).
- Failed delete after Chroma removal leaves a record with no chunks; retrying
  the delete works (deleting zero chunks is fine).

## Architecture Decisions
- Settings in core/config.py; routers per feature; CORS only FRONTEND_ORIGIN
- Frontend talks to backend only via lib/api.ts (single request() wrapper,
  ApiError with human-readable message)
- Plain dataclasses inside rag/ (PageText, Chunk, SearchResult, IngestResult,
  Answer); Pydantic schemas only at the API boundary
- google-genai SDK used directly; own small retriever; prompts in prompts.py
- Each rag module has its own user-safe error class
- Service layer takes filename + bytes (not UploadFile)
- Uploads saved as <uuid><ext>; display names in backend/data/documents.json
- Documents errors: 400/413/404/422/502/503 (500 for other service errors);
  chat errors: 400/502/503
- No chat_service.py: pipeline.ask() is the service
- Splitting is per page so page citations stay exact
- ask() returns a fixed message WITHOUT calling Gemini when retrieval is empty
- ingest_document(): embed first, then delete old copy, then store; if storing
  fails, partial chunks are deleted
- Retry only temporary Gemini errors (429, 503) with growing waits; permanent
  errors (bad key, bad request, 404 model) fail immediately
- Frontend type is UploadedDocument (not Document: clashes with the DOM type)
- Next 16 facts: layouts/pages are server components by default; metadata
  exports are server-only (client pages get a tiny server layout.tsx for
  titles); useSearchParams needs a Suspense boundary or `npm run build` fails
- Styling: Tailwind v4 (mobile-first), zinc neutrals + indigo accent, dark mode
  via prefers-color-scheme
- Markdown: react-markdown for ASSISTANT messages only; links open in a new tab
- Page owns data and API calls; child components get data via props and report
  events via callbacks
- Testing: pytest.ini sets pythonpath=. and testpaths=tests; shared `client`
  fixture in conftest.py; tests NEVER call Gemini and NEVER touch the real
  data/chroma folder or documents.json (tmp_path + monkeypatch); Gemini is
  faked with scripted outcomes and time.sleep is replaced
- Backend modules have no import-time side effects
- Git repo root is C:\LearnExa

## Next Exact Step
Report npx tsc --noEmit, npm run lint, npm run build results, and what each row
of the manual walkthrough showed (backend off, bad file types, empty, too
large, fake PDF, success, no documents, wrong API key, backend stopped mid-chat,
off-topic question, deleted document link). Then 13.2 Part B: write the
temporary try_similarity.py to measure similarity scores for related versus
unrelated questions, and decide from the real numbers whether a cutoff helps.
Then Phase 14 (delete try_*.py first) and Phase 15.