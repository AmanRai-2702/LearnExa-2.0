from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

# CORS: browsers block a page on localhost:3000 from calling an API on
# localhost:8000 unless the API explicitly allows that origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)