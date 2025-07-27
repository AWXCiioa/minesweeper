"""
Configuration management for the Minesweeper application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    database_url: str = "sqlite:///./minesweeper.db"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Game Configuration
    max_leaderboard_entries: int = 100
    score_multipliers: dict = {
        "easy": 1.0,
        "medium": 2.0,
        "hard": 3.0
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
