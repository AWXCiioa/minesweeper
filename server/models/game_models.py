"""
Pydantic models for the Minesweeper API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class GameResult(BaseModel):
    """Model for submitting a game result."""
    
    player_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Name of the player"
    )
    difficulty: str = Field(
        ..., 
        description="Game difficulty level"
    )
    time_seconds: int = Field(
        ..., 
        gt=0,
        description="Time taken to complete the game in seconds"
    )
    won: bool = Field(
        ...,
        description="Whether the game was won or lost"
    )
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        """Validate difficulty level."""
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('Difficulty must be easy, medium, or hard')
        return v
    
    @validator('player_name')
    def validate_player_name(cls, v):
        """Validate player name."""
        if not v.strip():
            raise ValueError('Player name cannot be empty')
        return v.strip()


class GameResultResponse(BaseModel):
    """Model for game result response."""
    
    id: int = Field(..., description="Unique game result ID")
    player_name: str = Field(..., description="Name of the player")
    difficulty: str = Field(..., description="Game difficulty level")
    time_seconds: int = Field(..., description="Time taken in seconds")
    won: bool = Field(..., description="Whether the game was won")
    score: int = Field(..., description="Calculated score")
    submitted_at: datetime = Field(..., description="When the result was submitted")


class LeaderboardEntry(BaseModel):
    """Model for a leaderboard entry."""
    
    rank: int = Field(..., description="Player's rank on the leaderboard")
    player_name: str = Field(..., description="Name of the player")
    difficulty: str = Field(..., description="Game difficulty level")
    time_seconds: int = Field(..., description="Time taken in seconds")
    score: int = Field(..., description="Player's score")
    submitted_at: datetime = Field(..., description="When the result was submitted")


class LeaderboardResponse(BaseModel):
    """Model for leaderboard response."""
    
    entries: List[LeaderboardEntry] = Field(
        ..., 
        description="List of leaderboard entries"
    )
    total_entries: int = Field(
        ..., 
        description="Total number of entries in the database"
    )
    difficulty_filter: Optional[str] = Field(
        None, 
        description="Applied difficulty filter"
    )
    limit: int = Field(..., description="Maximum number of entries returned")


class HealthResponse(BaseModel):
    """Model for health check response."""
    
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
