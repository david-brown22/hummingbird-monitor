"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./hummingbird_monitor.db"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "hummingbird-embeddings"
    
    # CodeProject.AI
    codeproject_ai_url: str = "http://localhost:32168"
    
    # Blue Iris
    blue_iris_url: Optional[str] = None
    blue_iris_username: Optional[str] = None
    blue_iris_password: Optional[str] = None
    
    # Alert thresholds
    visit_threshold_for_alert: int = 50  # visits per day to trigger refill alert
    nectar_depletion_rate: float = 0.1  # estimated depletion per visit
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
