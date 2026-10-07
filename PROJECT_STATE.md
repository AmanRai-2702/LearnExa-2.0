# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 8 — Complete RAG (pipeline.py written, being tested)

## Completed Phases
- Phase 1 — Project Setup
- Phase 2 — Document Loading
- Phase 3 — Chunking (notes.pdf: 143 pages -> 149 chunks)
- Phase 4 — Embeddings (vector length 3072)
- Phase 5 — Chroma (149 chunks stored)
- Phase 6 — Retrieval (retriever.py)
- Phase 7 — Gemini Generation (prompts.py, generator.py)

## Completed Files
- .gitignore, backend/requirements.txt, backend/.env.example
- backend/app/core/config.py, api/health.py, main.py
- backend/app/rag/: loader.py, splitter.py, embeddings.py, vector_store.py,
  retriever.py, prompts.py, generator.py, pipeline.py (new, untested)
- backend/try_*.py helpers (loader, splitter, embeddings, chroma, retriever,
  models, generate, pipeline) — temporary, delete later
- frontend/ (Next.js 16), lib/api.ts, app/page.tsx (health status)

## Current File
backend/app/rag/pipeline.py (testing with try_pipeline.py)

## Next File
backend/app/api/documents.py + chat.py + schemas (Phase 9), after pipeline is confirmed

## Working Features
- /health, frontend health page
- Load -> split -> embed -> store in Chroma
- retrieve(question) -> SearchResult list
- generate_answer(question, results) -> answer text
- ingest_document(path, document_id, name) -> IngestResult (to be confirmed)
- ask(question, document_id=None) -> Answer(answer, sources) (to be confirmed)

## Commands Used
- cd backend ; .venv\Scripts\activate.bat ; uvicorn app.main:app --reload
- cd frontend ; npm run dev
- python try_chroma.py ingest data\uploads\notes.pdf
- python try_models.py
- python try_generate.py "<question>"
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
- Scanned PDFs rejected (no OCR).
- Footer-only tiny chunks pollute retrieval; consider filtering.
- Retrieval always returns nearest chunks even if irrelevant; rely on the
  prompt's "not found" rule; measure before adding a threshold.
- Model names change; verify with try_models.py.
- print() in embeddings.py for progress; switch to logging later.
- Repo is local only (not on GitHub yet).
- Never share backend/.env (it holds the API key) when uploading the project.

## Architecture Decisions
- Settings in core/config.py; routers per feature; CORS only FRONTEND_ORIGIN
- Frontend talks to backend only via lib/api.ts
- Plain dataclasses: PageText, Chunk, SearchResult, IngestResult, Answer
- google-genai SDK used directly; own small retriever (no LangChain retriever)
- Prompts only in prompts.py; system instruction + context/question message
- Each rag module has its own user-safe error class; pipeline.py lets them
  propagate and the API layer (Phase 9) maps them to HTTP responses
- ask() returns a fixed message WITHOUT calling Gemini when retrieval is empty
- ingest_document() embeds first, then deletes any old copy of the same
  document_id, then stores (a failed embedding never destroys older data)
- Git repo root is C:\LearnExa

## Next Exact Step
Test pipeline.py: ingest sample.txt, ask a question about it, ask with an
unknown document_id (expect the "no documents" message, no Gemini call).
Then commit, then Phase 9: FastAPI endpoints.
