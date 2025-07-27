"""
API routes for Minesweeper game endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..models.game_models import (
    GameResult, 
    LeaderboardResponse, 
    ErrorResponse
)
from ..controllers.game_controller import game_controller


logger = logging.getLogger(__name__)

# Create router for game-related endpoints
router = APIRouter(prefix="/api/v1", tags=["game"])


@router.post("/games", 
             status_code=status.HTTP_201_CREATED,
             summary="Submit Game Result",
             description="Submit a completed game result to the leaderboard")
async def submit_game_result(game_result: GameResult):
    """
    Submit a game result for leaderboard tracking.
    
    - **player_name**: Name of the player (1-50 characters)
    - **difficulty**: Game difficulty level (easy, medium, hard)
    - **time_seconds**: Time taken to complete the game in seconds
    - **won**: Whether the player won the game
    
    Returns the saved game entry with calculated score.
    """
    try:
        result = await game_controller.submit_game_result(game_result)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Game result submitted successfully",
                "data": result
            }
        )
    except ValueError as e:
        logger.warning(f"Invalid game result submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to submit game result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit game result"
        )


@router.get("/leaderboard",
            response_model=LeaderboardResponse,
            summary="Get Leaderboard",
            description="Retrieve leaderboard entries, optionally filtered by difficulty")
async def get_leaderboard(
    difficulty: Optional[str] = Query(
        None, 
        description="Filter by difficulty level",
        regex="^(easy|medium|hard)$"
    ),
    limit: Optional[int] = Query(
        None,
        description="Maximum number of entries to return",
        ge=1,
        le=1000
    )
):
    """
    Get leaderboard entries with optional filtering.
    
    - **difficulty**: Optional filter by difficulty (easy, medium, hard)
    - **limit**: Maximum number of entries to return (default: 100)
    
    Returns leaderboard entries sorted by score (highest first).
    """
    try:
        leaderboard = await game_controller.get_leaderboard(
            difficulty=difficulty,
            limit=limit
        )
        return leaderboard
    except ValueError as e:
        logger.warning(f"Invalid leaderboard request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard"
        )


@router.delete("/leaderboard",
               status_code=status.HTTP_200_OK,
               summary="Clear Leaderboard",
               description="Clear all leaderboard entries")
async def clear_leaderboard():
    """
    Clear all leaderboard entries from the database.
    
    This action cannot be undone. Returns the number of entries that were cleared.
    """
    try:
        result = await game_controller.clear_leaderboard()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    except Exception as e:
        logger.error(f"Failed to clear leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear leaderboard"
        )


@router.get("/players/{player_name}/stats",
            summary="Get Player Statistics",
            description="Get detailed statistics for a specific player")
async def get_player_statistics(player_name: str):
    """
    Get comprehensive statistics for a specific player.
    
    - **player_name**: Name of the player to get statistics for
    
    Returns detailed statistics including games played, win rate, best times, etc.
    """
    try:
        stats = await game_controller.get_player_statistics(player_name)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Player statistics retrieved successfully",
                "data": stats
            }
        )
    except ValueError as e:
        logger.warning(f"Invalid player statistics request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get player statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve player statistics"
        )
