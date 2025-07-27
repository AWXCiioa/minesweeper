"""
Configuration settings for the Minesweeper API.
"""

import os
from typing import List


class Settings:
    """Application settings."""
    
    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./minesweeper.db")
    
    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"  # Allow all origins for development
    ]
    
    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API settings
    api_title: str = "Minesweeper API"
    api_description: str = "A modern web API for the classic Minesweeper game with leaderboard functionality"
    api_version: str = "1.0.0"


# Create global settings instance
settings = Settings()
