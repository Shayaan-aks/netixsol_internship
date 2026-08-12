from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Real Estate Business Assistant"
    ENVIRONMENT: str = "production"
    
    # DB
    DATABASE_URL: str = "sqlite:///./crm.db"
    
    # Google Calendar (Path to Service Account JSON)
    GOOGLE_APPLICATION_CREDENTIALS: str = "credentials.json"
    
    # Email (SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # n8n Webhook
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/real-estate"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
