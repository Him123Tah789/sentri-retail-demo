"""
Core configuration settings for Sentri Retail Demo
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Mode: HACKATHON enables demo scenarios and retail labels
    SENTRI_MODE: str = "HACKATHON"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sentri_demo.db"
    
    # JWT Authentication
    JWT_SECRET: str = "sentri-demo-secret-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for demo
    
    # Application
    APP_NAME: str = "Sentri Retail Demo"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Demo seed token (for /demo/seed endpoint)
    DEMO_SEED_TOKEN: str = "sentri-seed-2026"
    
    # LLM Configuration (for chat explanations only - not risk decisions)
    LLM_PROVIDER: str = "openai"  # 'openai' or 'gemini'
    OPENAI_API_KEY: str = ""  # OpenAI API key
    LLM_API_KEY: str = ""  # Legacy/alternative API key
    LLM_MODEL: str = "gpt-4.1-mini"  # Default model
    LLM_BASE_URL: str = "https://api.openai.com/v1"  # OpenAI-compatible endpoint
    LLM_TIMEOUT: int = 30  # Timeout in seconds
    LLM_ENABLED: bool = True  # Enable/disable LLM features
    
    @property
    def is_llm_configured(self) -> bool:
        """Check if LLM is properly configured"""
        api_key = self.OPENAI_API_KEY or self.LLM_API_KEY
        return bool(api_key) and api_key != "YOUR_API_KEY" and self.LLM_ENABLED
    
    @property
    def is_hackathon_mode(self) -> bool:
        """Check if running in hackathon/demo mode"""
        return self.SENTRI_MODE.upper() == "HACKATHON"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars


# Global settings instance
settings = Settings()