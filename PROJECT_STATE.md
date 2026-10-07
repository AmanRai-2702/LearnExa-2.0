# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 12 — Testing (all five test areas written; 80 tests confirmed passing by the
user; API tests in test_api.py written, awaiting the user's run, expected 111 total)

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

## Completed Files
- .gitignore, backend/requirements.txt, backend/.env.example
- backend/pytest.ini
- backend/tests/conftest.py (shared `client` fixture)
- backend/tests/test_health.py (6 tests)
- backend/tests/test_chunking.py (18 tests)
- backend/tests/test_loader.py (15 tests)
- backend/tests/test_document_service.py (18 tests)
- backend/tests/test_retrieval.py (23 tests: vector store + retriever)
- backend/tests/test_api.py (31 tests: documents + chat endpoints; awaiting run)
- backend/app/core/config.py, main.py
- backend/app/api/: health.py, documents.py, chat.py
- backend/app/rag/: loader.py, splitter.py, embeddings.py, vector_store.py,
  retriever.py, prompts.py, generator.py, pipeline.py
- backend/app/models/schemas.py
- backend/app/services/document_service.py
- backend/try_*.py helpers (temporary, delete later)
- frontend/lib/types.ts, frontend/lib/api.ts
- frontend/app/layout.tsx, app/globals.css, components/layout/Navbar.tsx
- frontend/app/page.tsx (Dashboard)
- frontend/app/documents/page.tsx + layout.tsx; frontend/app/chat/page.tsx + layout.tsx
- frontend/components/documents/: DocumentCard, DocumentList, UploadZone
- frontend/components/chat/: SourceCard, ChatMessage, ChatInput, ChatWindow

## Current File
backend/tests/test_api.py

## Next File
None in Phase 12 after the API tests pass. Phase 13 starts with a review of
backend/app/api/*.py, backend/app/rag/*.py error handling and
frontend/lib/api.ts error handling.

## Working Features
- All backend endpoints: /health, /api/documents (upload/list/delete), /api/chat
- Frontend: Dashboard, Documents (list/delete/upload), Chat (markdown answers,
  sources, selector, errors), per-page titles, system-theme dark mode
- pytest: 80 passed confirmed; 111 expected once test_api.py passes

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
- SECURITY: backend/.env was inside the project zip sent to Claude (twice).
  It is NOT tracked by Git (verified), but if any zip was shared, rotate the
  Gemini key. Always zip without backend/.env.
- Free tier: 100 embedded texts/min; big PDFs upload slowly (UI shows a timer).
- Gemini 503/429 spikes are Google-side (shown as a red error bubble).
- Scanned PDFs rejected (no OCR).
- Footer-only tiny chunks pollute retrieval; retrieval always returns nearest
  chunks even if irrelevant. A chunking test documents this behaviour today.
- print() in embeddings.py; switch to logging later.
- Repo is local only (not on GitHub yet).
- documents.json registry is single-user only; upload limit constant in service.
- Failed ingestion may leave partial Chroma chunks.
- Upload request blocks until ingestion finishes (production fix: background job + polling).
- 422 validation errors have list-shaped detail (api.ts handles both shapes).
- test_api.py not yet run by the user; one possible surprise is an empty-file upload
  returning 422 instead of 400 (multipart handling).
- No automated frontend tests (only tsc/lint/build checks).
- Backend must be running or the frontend shows "Cannot reach the backend".
- Limits duplicated in frontend and backend (10 MB upload, 1000-char question).
- Chat history is React state only; no conversation memory sent to the backend.
- Markdown rendering has no GFM (tables, strikethrough); would need remark-gfm.
- No in-app theme toggle (follows the OS theme).
- Delete uses window.confirm (simple, not a styled modal).
- Dashboard stats are summed client-side from the full document list.
- "Gemini configured" pill only means a key exists, not that it is valid.
- User has NOT yet reported npm tsc / lint / build output for several steps (ask again).
- try_*.py helper scripts still in backend/ (delete before the documentation phase).

## Architecture Decisions
- Settings in core/config.py; routers per feature; CORS only FRONTEND_ORIGIN
- Frontend talks to backend only via lib/api.ts (single request() wrapper,
  ApiError with human-readable message)
- Plain dataclasses inside rag/ (PageText, Chunk, SearchResult); Pydantic
  schemas only at the API boundary
- google-genai SDK used directly; own small retriever; prompts in prompts.py
- Each rag module has its own user-safe error class
- Service layer takes filename + bytes (not UploadFile)
- Uploads saved as <uuid><ext>; display names in backend/data/documents.json
- Documents errors: 400/413/404/422/502/503 (500 for other service errors);
  chat errors: 400/502/503
- No chat_service.py: pipeline.ask() is the service
- Splitting is per page so page citations stay exact
- Frontend type is UploadedDocument (not Document: clashes with the DOM type)
- Next 16 facts: layouts/pages are server components by default; metadata exports are
  server-only (client pages get a tiny server layout.tsx for titles); title.template
  applies to child segments only; useSearchParams needs a Suspense boundary or
  `npm run build` fails; LayoutProps<"/"> is a global helper
- Styling: Tailwind v4 (mobile-first), zinc neutrals + indigo accent, dark mode via
  prefers-color-scheme
- Markdown: react-markdown for ASSISTANT messages only; links open in a new tab
- Page owns data and API calls; child components get data via props and report
  events via callbacks
- Testing: pytest.ini sets pythonpath=. and testpaths=tests; shared `client` fixture
  in tests/conftest.py; tests use TestClient (no server) and monkeypatch; tests must
  NEVER call Gemini and must NEVER touch the real data/chroma folder or documents.json
  (use tmp_path + monkeypatch of module constants such as vector_store.CHROMA_DIR and
  document_service.DATA_DIR/UPLOADS_DIR/REGISTRY_FILE)
- Test strategy: chunking/loader tested with tiny hand-written inputs; vector store
  tested with the REAL Chroma in a temp folder and hand-made 3-number vectors; Gemini
  always faked; API tests patch the names used inside the routers
  (app.api.chat.ask, app.api.documents.add_document, ...); one test proves unexpected
  errors never leak details (TestClient(raise_server_exceptions=False))
- Backend modules have no import-time side effects (Gemini client and Chroma are
  created inside functions), so importing app.main in tests is safe
- Git repo root is C:\LearnExa

## Next Exact Step
Run `pytest -v` and confirm 111 passed (paste any failure in full), commit
("Add API tests and share the client fixture"), and report npm tsc/lint/build output.
Then Phase 13 (error handling review): list every failure case from the master prompt
(missing/invalid key, Gemini errors, invalid/empty/oversized file, PDF extraction
failure, embedding/Chroma failure, empty question, no relevant context), verify each
with a real manual test or an automated test, fix gaps, and check the frontend shows a
clear message for each.