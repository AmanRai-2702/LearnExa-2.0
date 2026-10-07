from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env file."""

    app_name: str = "LearnExa API"
    environment: str = "development"

    # Which frontend URL is allowed to call this API (CORS)
    frontend_origin: str = "http://localhost:3000"

    # Gemini configuration (used from Phase 4 onward)
    gemini_api_key: str = ""
    gemini_model: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"

    # RAG tuning values (starting points, not universal optimums)
    chunk_size: int = 1000      # max characters per chunk
    chunk_overlap: int = 150    # characters repeated between neighbouring chunks
    top_k: int = 5              # how many chunks to retrieve (used in Phase 6)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Create the Settings object once and reuse it."""
    return Settings()