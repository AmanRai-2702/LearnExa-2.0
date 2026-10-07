# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 4 — Embeddings (code written, being tested)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking

## Completed Files
- .gitignore
- backend/requirements.txt (pypdf, langchain-text-splitters, google-genai)
- backend/.env.example
- backend/app/__init__.py, api/__init__.py, core/__init__.py, rag/__init__.py
- backend/app/core/config.py
- backend/app/api/health.py
- backend/app/main.py
- backend/app/rag/loader.py
- backend/app/rag/splitter.py
- backend/app/rag/embeddings.py
- backend/try_loader.py, try_splitter.py, try_embeddings.py (temporary helpers)
- frontend/ (Next.js 16, TypeScript, Tailwind, App Router)
- frontend/lib/api.ts
- frontend/app/page.tsx (shows backend health)

## Current File
backend/app/rag/embeddings.py (testing)

## Next File
backend/app/rag/vector_store.py (Phase 5, Chroma)

## Working Features
- GET /health, Swagger docs at /docs
- Frontend page calls /health and shows status
- Loader: PDF/TXT -> list[PageText]
- Splitter: list[PageText] -> list[Chunk] with metadata
- Embeddings: embed_documents(list[str]), embed_query(str) using Gemini

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_loader.py <file>
- python try_splitter.py <file> [chunk_size] [chunk_overlap]
- python try_embeddings.py [file] [query]
- git add . ; git commit -m "..."

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters, google-genai
Frontend: Next.js 16, React, TypeScript, Tailwind CSS

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY (in backend/.env only),
GEMINI_MODEL, GEMINI_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

## Known Issues
- GEMINI_MODEL intentionally empty; choose a current model before Phase 7.
- Scanned PDFs rejected (no OCR).
- Very short pages produce tiny chunks; decide on filtering later.
- Splitting is per page, so ideas spanning a page break are cut.
- Embedding vector length not assumed; measured by try_embeddings.py.

## Architecture Decisions
- Settings centralised in core/config.py (pydantic-settings)
- Routers per feature in app/api/
- CORS allows only FRONTEND_ORIGIN (use localhost:3000)
- Frontend talks to backend only through frontend/lib/api.ts
- Loader returns PageText; splitter returns Chunk (plain dataclasses)
- Splitting per page for exact page citations
- Embeddings use google-genai SDK directly (not a LangChain wrapper) for clarity
- Document vs query embeddings use different Gemini task types
- Git repo root is C:\LearnExa

## Next Exact Step
Phase 5: add chromadb, create vector_store.py (persistent client in
backend/data/chroma, a collection, add chunks with embeddings + metadata).