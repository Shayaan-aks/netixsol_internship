from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Pakistani Real Estate Voice Agent"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Provider API Keys
    GEMINI_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    FISH_AUDIO_API_KEY: Optional[str] = None
    
    # Latency Targets
    MAX_LATENCY_MS: int = 2000
    LLM_MODEL: str = "gemini-1.5-flash" # Optimized for speed
    
    class Config:
        env_file = ".env"

settings = Settings()
