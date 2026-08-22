"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables / .env file.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────
    APP_NAME: str = "AdaptRoute-Edu"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Server ─────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── LLM & Router ───────────────────────────────────────────
    LLM_PROVIDER: str = "ollama"          # ollama | huggingface
    LLM_MODEL: str = "gemma3"
    ROUTER_POLICY: str = "heuristic"       # heuristic | bandit
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    HUGGINGFACE_MODEL_ID: str = "meta-llama/Llama-3.1-8B-Instruct"
    HUGGINGFACE_TOKEN: str = ""
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT_SECONDS: int = 120

    # ── CORS ───────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip().rstrip("/") for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── Logging ────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — safe to call anywhere."""
    return Settings()
