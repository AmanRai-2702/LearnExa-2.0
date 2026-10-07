# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 5 — Chroma (code written, being tested)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking (notes.pdf: 143 pages -> 149 chunks, avg 218 chars)
- Phase 4 — Embeddings (measured vector length: 3072)

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
- backend/app/rag/embeddings.py
- backend/app/rag/vector_store.py
- backend/try_loader.py, try_splitter.py, try_embeddings.py, try_chroma.py
  (temporary helpers, delete later)
- frontend/ (Next.js 16, TypeScript, Tailwind, App Router)
- frontend/lib/api.ts
- frontend/app/page.tsx (shows backend health)

## Current File
backend/app/rag/vector_store.py (testing)

## Next File
backend/app/rag/retriever.py (Phase 6)

## Working Features
- GET /health, Swagger docs at /docs
- Frontend page calls /health and shows status
- Loader: PDF/TXT -> list[PageText]
- Splitter: list[PageText] -> list[Chunk] with metadata
- Embeddings: embed_documents(list[str]), embed_query(str)
- Vector store: add_chunks, search (top_k, optional document filter),
  count_chunks, delete_document; persistent in backend/data/chroma

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_loader.py <file>
- python try_splitter.py <file> [chunk_size] [chunk_overlap]
- python try_embeddings.py [file] [query]
- python try_chroma.py ingest <file> | search "<question>" | delete
- git add . ; git commit -m "..."

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters, google-genai, chromadb
Frontend: Next.js 16, React, TypeScript, Tailwind CSS

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY (in backend/.env only),
GEMINI_MODEL, GEMINI_EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

## Known Issues
- GEMINI_MODEL intentionally empty; choose a current model before Phase 7.
- Scanned PDFs rejected (no OCR).
- notes.pdf has many tiny chunks and a repeated footer line; consider a
  text-heavy test PDF.
- Splitting is per page, so ideas spanning a page break are cut.
- Similarity scores are relative (unrelated text scored ~0.58); rely on
  ranking and measure any threshold.
- Chroma hnsw:space setting may be deprecated in newer versions; verify warnings.

## Architecture Decisions
- Settings centralised in core/config.py (pydantic-settings)
- Routers per feature in app/api/
- CORS allows only FRONTEND_ORIGIN (use localhost:3000)
- Frontend talks to backend only through frontend/lib/api.ts
- Loader returns PageText; splitter returns Chunk (plain dataclasses)
- Splitting per page for exact page citations
- Embeddings use google-genai SDK directly; document vs query task types
- Chroma: one persistent collection "learnexa_chunks", cosine distance,
  our own embeddings, id = document_id + chunk_index, metadata filter by
  document_id
- Each rag module has its own user-safe error class
- Git repo root is C:\LearnExa

## Next Exact Step
Phase 6: write retriever.py (embed the question, call vector_store.search,
return top-k results with sources), test with a script.