# LearnExa Claude Handoff

## Current Phase
Phase 1 of 15 — Project Setup

## Last Completed Step
1.1 — Git repo + FastAPI backend skeleton + /health

## Last Completed File
backend/app/main.py

## Current Working Feature
GET /health on http://127.0.0.1:8000

## Next File
frontend/ (create-next-app output), then frontend/lib/api.ts

## Next Exact Task
Step 1.2: scaffold Next.js (App Router, TypeScript, Tailwind), show backend
health status on the home page. Explain React components, state, useEffect,
and why the page is a client component.

## Working Commands
cd backend ; uvicorn app.main:app --reload
git add . ; git commit -m "..."

## Important Decisions
- One file at a time, always complete file contents
- No overengineering (no agents, LangGraph, Redux, etc.)
- Gemini key stays in backend only
- Explain WHAT / WHY / HOW / INTERVIEW for each component
- User is on Windows, using VS Code with PowerShell; beginner level, go slowly

## Known Problems
None.

## Do Not Change
- Folder structure in the master prompt
- Backend-only Gemini access
- Configurable models via environment variables
