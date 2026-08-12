"""
NetixSol Real Estate AI Platform — Production Configuration
All settings loaded from environment variables with validation.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Central configuration class. All values come from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # ── Application ─────────────────────────────────────────────────────────
    app_name: str = "NetixSol Real Estate AI Platform"
    app_version: str = "1.0.0"
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    dev_skip_auth: bool = Field(default=False, env="DEV_SKIP_AUTH")

    # ── API Security ─────────────────────────────────────────────────────────
    api_key_header: str = "X-API-Key"
    api_keys: str = Field(default="", env="API_KEYS")  # Comma-separated valid API keys
    jwt_secret: str = Field(default="CHANGE_ME_IN_PRODUCTION", env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # ── AI / LLM ─────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    xai_api_key: str = Field(default="", env="XAI_API_KEY")
    llm_model: str = Field(default="grok-3-mini", env="LLM_MODEL")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # ── STT / TTS ─────────────────────────────────────────────────────────────
    deepgram_api_key: str = Field(default="", env="DEEPGRAM_API_KEY")

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./production.db", env="DATABASE_URL"
    )
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")

    # ── Vector Database (ChromaDB) ────────────────────────────────────────────
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8001, env="CHROMA_PORT")
    chroma_persist_dir: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIR")
    chroma_collection: str = Field(default="real_estate_knowledge", env="CHROMA_COLLECTION")

    # ── Redis (Rate Limiting / Sessions) ─────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # ── Google Calendar ───────────────────────────────────────────────────────
    google_credentials_path: str = Field(
        default="./credentials.json", env="GOOGLE_CREDENTIALS_PATH"
    )
    google_calendar_id: str = Field(default="primary", env="GOOGLE_CALENDAR_ID")

    # ── n8n Automation ────────────────────────────────────────────────────────
    n8n_webhook_url: str = Field(default="", env="N8N_WEBHOOK_URL")
    n8n_api_key: str = Field(default="", env="N8N_API_KEY")

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")

    # ── SMTP Email ────────────────────────────────────────────────────────────
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="no-reply@aksrealestate.com", env="SMTP_FROM_EMAIL")
    agent_email: str = Field(default="agent@aksrealestate.com", env="AGENT_EMAIL")

    # ── Monitoring ────────────────────────────────────────────────────────────
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    otel_endpoint: str = Field(default="", env="OTEL_ENDPOINT")

    # ── Voice / STT / TTS ────────────────────────────────────────────────────
    stt_provider: str = Field(default="google", env="STT_PROVIDER")
    tts_provider: str = Field(default="google", env="TTS_PROVIDER")
    tts_voice: str = Field(default="ur-PK-UzmaNeural", env="TTS_VOICE")
    voice_language: str = Field(default="ur-PK", env="VOICE_LANGUAGE")

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: str = Field(default="*")

    @property
    def api_keys_list(self) -> list[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# Singleton — import this everywhere
settings = Settings()
