"""
Configuration settings for the application.
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings class.
    """
    # API Settings
    API_KEY: str
    PORT: int = 5050
    ENVIRONMENT: str = "development"
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validates the environment setting."""
        allowed_environments = ["development", "production", "testing"]
        if v.lower() not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_environments}")
        return v.lower()
    
    class Config:
        """Configuration for the settings class."""
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 