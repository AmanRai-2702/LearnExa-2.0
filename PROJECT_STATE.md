# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 9 — FastAPI Integration (step 1: schemas)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking (notes.pdf: 143 pages -> 149 chunks)
- Phase 4 — Embeddings (vector length 3072)
- Phase 5 — Chroma (149 chunks stored)
- Phase 6 — Retrieval
- Phase 7 — Gemini Generation
- Phase 8 — Complete RAG (pipeline.py; committed)

## Completed Files
- .gitignore, backend/requirements.txt, backend/.env.example
- backend/app/core/config.py, api/health.py, main.py
- backend/app/rag/: loader.py, splitter.py, embeddings.py, vector_store.py,
  retriever.py, prompts.py, generator.py, pipeline.py
- backend/app/models/schemas.py (new, testing)
- backend/try_*.py helpers (loader, splitter, embeddings, chroma, retriever,
  models, generate, pipeline) — temporary, delete later
- frontend/ (Next.js 16), lib/api.ts, app/page.tsx (health status)

## Current File
backend/app/models/schemas.py

## Next File
backend/app/services/document_service.py

## Working Features
- /health, frontend health page
- ingest_document(path, document_id, name) and ask(question, document_id)
- Gemini generation with 5 retries on 429/503, AFC disabled

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_models.py
- python try_pipeline.py ingest data\uploads\sample.txt
- python try_pipeline.py ask "<question>" [document_id]

## Dependencies
Backend: fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, pypdf,
langchain-text-splitters, google-genai, chromadb
Frontend: Next.js 16, React, TypeScript, Tailwind CSS

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY (backend/.env only),
GEMINI_MODEL (pick from try_models.py output), GEMINI_EMBEDDING_MODEL,
CHUNK_SIZE, CHUNK_OVERLAP, TOP_K

## Known Issues
- Free tier: 100 embedded texts/min (ingest paced); generation limits are low.
- Gemini 503 "high demand" spikes are Google-side; if persistent, change GEMINI_MODEL.
- Scanned PDFs rejected (no OCR).
- Footer-only tiny chunks pollute retrieval; consider filtering.
- Retrieval always returns nearest chunks even if irrelevant; rely on the
  prompt's "not found" rule; measure before adding a threshold.
- print() in embeddings.py for progress; switch to logging later.
- Repo is local only (not on GitHub yet).
- Never share backend/.env when uploading the project; rotate the API key.
- Chroma stores no page count or upload time; document_service must keep them.

## Architecture Decisions
- Settings in core/config.py; routers per feature; CORS only FRONTEND_ORIGIN
- Frontend talks to backend only via lib/api.ts
- Plain dataclasses inside rag/ (PageText, Chunk, SearchResult, IngestResult,
  Answer); Pydantic schemas only at the API boundary (models/schemas.py)
- google-genai SDK used directly; own small retriever (no LangChain retriever)
- Prompts only in prompts.py
- Each rag module has its own user-safe error class; API layer maps them to HTTP codes
- ask() returns a fixed message WITHOUT calling Gemini when retrieval is empty
- ingest_document() embeds first, then deletes old copy, then stores
- ErrorResponse uses {"detail": str} to match FastAPI's default errors
- Git repo root is C:\LearnExa

## Next Exact Step
Confirm schemas test, commit, then design where document metadata (pages,
upload time) is kept and write document_service.py.