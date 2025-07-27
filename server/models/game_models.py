"""
Pydantic models for the Minesweeper game API.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


class GameResult(BaseModel):
    """Model for game result submission."""
    
    player_name: str = Field(..., min_length=1, max_length=50, description="Player's name")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Game difficulty level")
    time_seconds: int = Field(..., ge=1, description="Time taken to complete the game in seconds")
    won: bool = Field(..., description="Whether the player won the game")
    
    @validator('player_name')
    def validate_player_name(cls, v):
        """Validate and clean player name."""
        if not v or not v.strip():
            raise ValueError('Player name cannot be empty')
        return v.strip()
    
    @validator('time_seconds')
    def validate_time(cls, v):
        """Validate game time is reasonable."""
        if v > 86400:  # 24 hours max
            raise ValueError('Game time cannot exceed 24 hours')
        return v


class LeaderboardEntry(BaseModel):
    """Model for leaderboard entry response."""
    
    id: int = Field(..., description="Unique entry ID")
    player_name: str = Field(..., description="Player's name")
    difficulty: str = Field(..., description="Game difficulty level")
    time_seconds: int = Field(..., description="Time taken in seconds")
    won: bool = Field(..., description="Whether the player won")
    score: float = Field(..., description="Calculated score")
    created_at: datetime = Field(..., description="When the game was completed")
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Model for leaderboard API response."""
    
    entries: list[LeaderboardEntry] = Field(..., description="List of leaderboard entries")
    total_count: int = Field(..., description="Total number of entries")
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Model for health check response."""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Error timestamp")
