# LearnExa Project State

## Project Goal
Rebuild LearnExa as a clean, explainable full-stack RAG learning assistant
(Next.js + FastAPI + Chroma + Gemini). The owner must be able to explain every
component in an interview.

## Current Phase
Phase 1 — Project Setup (Step 1.1 done, Step 1.2 pending)

## Completed Phases
None yet.

## Completed Files
- .gitignore
- backend/requirements.txt
- backend/.env.example
- backend/app/__init__.py, api/__init__.py, core/__init__.py
- backend/app/core/config.py
- backend/app/api/health.py
- backend/app/main.py

## Current File
None (Step 1.1 complete)

## Next File
Frontend scaffold via create-next-app (Step 1.2)

## Working Features
- GET /health returns status JSON
- Swagger docs at /docs

## Commands Used
- git init
- python -m venv .venv ; pip install -r requirements.txt
- uvicorn app.main:app --reload   (run from backend/)
- git add . ; git commit -m "Set up FastAPI backend with health endpoint"

## Dependencies
fastapi, uvicorn[standard], pydantic-settings, pytest, httpx

## Environment Variables
ENVIRONMENT, FRONTEND_ORIGIN, GEMINI_API_KEY, GEMINI_MODEL, GEMINI_EMBEDDING_MODEL

## Known Issues
- GEMINI_MODEL intentionally empty; choose a current model before Phase 7.

## Architecture Decisions
- Settings centralised in core/config.py (pydantic-settings)
- Routers per feature in app/api/
- CORS allows only FRONTEND_ORIGIN
- Dependencies added only when a phase needs them

## Next Exact Step
Step 1.2: create the Next.js app (TypeScript, Tailwind, App Router) in frontend/
and make it call /health.