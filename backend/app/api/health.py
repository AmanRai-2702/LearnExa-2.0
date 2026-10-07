from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        # Only report whether a key exists. Never return the key itself.
        "gemini_configured": bool(settings.gemini_api_key),
    }