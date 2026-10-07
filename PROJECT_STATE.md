# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 6 — Retrieval (code written, being tested)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking (notes.pdf: 143 pages -> 149 chunks, avg 218 chars)
- Phase 4 — Embeddings (measured vector length: 3072)
- Phase 5 — Chroma (149 chunks stored; scores match hand-computed cosine)

## Completed Files
- .gitignore
- backend/requirements.txt (pypdf, langchain-text-splitters, google-genai, chromadb)
- backend/.env.example
- backend/app/__init__.py, api/__init__.py, core/__init__.py, rag/__init__.py
- backend/app/core/config.py
- backend/app/api/health.py
- backend/app/main.py
- backend/app/rag/loader.py
- backend/app/rag/splitter.py
- backend/app/rag/embeddings.py (batches of 20, paced to 80 texts/min, retry on 429)
- backend/app/rag/vector_store.py
- backend/app/rag/retriever.py
- backend/try_loader.py, try_splitter.py, try_embeddings.py, try_chroma.py,
  try_retriever.py (temporary helpers, delete later)
- frontend/ (Next.js 16, TypeScript, Tailwind, App Router)
- frontend/lib/api.ts
- frontend/app/page.tsx (shows backend health)

## Current File
backend/app/rag/retriever.py (testing)

## Next File
backend/app/rag/prompts.py (Phase 7)

## Working Features
- GET /health, Swagger docs at /docs
- Frontend page calls /health and shows status
- Loader, splitter, embeddings, Chroma store (all tested)
- retrieve(question, top_k, document_id) -> list[SearchResult]

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_chroma.py ingest <file> | search "<q>" | delete
- python try_retriever.py "<question>" [top_k]
- git add . ; git commit -m "..."

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters, google-genai, chromadb
Frontend: Next.js 16, React, TypeScript, Tailwind CSS

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY (backend/.env only),
GEMINI_MODEL, GEMINI_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

## Known Issues
- GEMINI_MODEL intentionally empty; choose a current model before Phase 7.
- Free tier: 100 embedded texts/minute, so ingest is paced (~2 min for 149 chunks).
- Scanned PDFs rejected (no OCR).
- notes.pdf has many tiny/footer-only chunks that pollute retrieval
  (a footer-only chunk ranked 4th). Consider filtering short chunks.
- Retrieval always returns nearest chunks even if irrelevant; prompt must
  handle "not found"; any similarity threshold must be measured.
- embeddings.py uses print() for progress; switch to logging later.
- Chroma hnsw:space setting may be deprecated in newer versions; verify warnings.
- Repo is local only (not pushed to GitHub yet).

## Architecture Decisions
- Settings centralised in core/config.py (pydantic-settings)
- Routers per feature in app/api/
- CORS allows only FRONTEND_ORIGIN (use localhost:3000)
- Frontend talks to backend only through frontend/lib/api.ts
- Loader returns PageText; splitter returns Chunk (plain dataclasses)
- Splitting per page for exact page citations
- Embeddings via google-genai SDK directly; document vs query task types
- Chroma: one persistent collection "learnexa_chunks", cosine distance,
  our own embeddings, id = document_id + chunk_index
- Own small retriever (no LangChain retriever) for transparency
- Each rag module has its own user-safe error class
- Git repo root is C:\LearnExa

## Next Exact Step
Phase 7: choose a current Gemini model name (verify in Google AI Studio docs),
write prompts.py and a generation function, test with retrieved chunks.