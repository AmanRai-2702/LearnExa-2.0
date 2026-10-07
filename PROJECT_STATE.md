# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 3 — Chunking (code written, being tested)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading (tested on a 143-page PDF)

## Completed Files
- .gitignore
- backend/requirements.txt (includes pypdf, langchain-text-splitters)
- backend/.env.example (includes CHUNK_SIZE, CHUNK_OVERLAP, TOP_K)
- backend/app/__init__.py, api/__init__.py, core/__init__.py, rag/__init__.py
- backend/app/core/config.py (chunk_size, chunk_overlap, top_k added)
- backend/app/api/health.py
- backend/app/main.py
- backend/app/rag/loader.py
- backend/app/rag/splitter.py
- backend/try_loader.py, backend/try_splitter.py (temporary helpers, delete later)
- frontend/ (Next.js 16, TypeScript, Tailwind, App Router)
- frontend/lib/api.ts
- frontend/app/page.tsx (shows backend health)

## Current File
backend/app/rag/splitter.py (testing)

## Next File
backend/app/rag/embeddings.py (Phase 4)

## Working Features
- GET /health, Swagger docs at /docs
- Frontend page calls /health and shows status
- Loader: PDF/TXT -> list[PageText] with friendly errors
- Splitter: list[PageText] -> list[Chunk] with document_id, document_name,
  page_number, chunk_index

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_loader.py <file>
- python try_splitter.py <file> [chunk_size] [chunk_overlap]
- git add . ; git commit -m "..."

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters
Frontend: Next.js 16, React, TypeScript, Tailwind CSS

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY, GEMINI_MODEL,
GEMINI_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

## Known Issues
- GEMINI_MODEL intentionally empty; choose a current model before Phase 7.
- Scanned (image-only) PDFs are rejected; OCR not supported.
- Very short pages (titles only) produce tiny chunks; decide on filtering later.
- Splitting is per page, so ideas spanning a page break are cut.

## Architecture Decisions
- Settings centralised in core/config.py (pydantic-settings)
- Routers per feature in app/api/
- CORS allows only FRONTEND_ORIGIN (use localhost:3000, not 127.0.0.1)
- Frontend talks to backend only through frontend/lib/api.ts
- Loader returns PageText; splitter returns Chunk (plain dataclasses)
- Splitting is per page to keep page citations exact
- Dependencies added only when a phase needs them
- Git repo root is C:\LearnExa

## Next Exact Step
Phase 4: add the Gemini SDK, create embeddings.py, and embed a few chunks
(needs a GEMINI_API_KEY in backend/.env).