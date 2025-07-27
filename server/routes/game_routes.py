"""
Game API routes for Minesweeper application.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..controllers.game_controller import game_controller
from ..models.game_models import (
    GameResult, GameResultResponse, LeaderboardEntry, 
    LeaderboardResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1",
    tags=["games"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/games",
             response_model=GameResultResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Submit Game Result",
             description="Submit a completed game result to the leaderboard")
async def submit_game_result(game_result: GameResult):
    """
    Submit a game result to the leaderboard.
    
    Args:
        game_result: The game result data including player name, difficulty, time, and outcome
        
    Returns:
        GameResultResponse: Confirmation of the submitted game result with calculated score
        
    Raises:
        HTTPException: If there's an error processing the game result
    """
    try:
        logger.info(f"Submitting game result for player: {game_result.player_name}")
        
        # Submit the game result through the controller
        result = await game_controller.submit_game_result(game_result)
        
        logger.info(f"Game result submitted successfully with score: {result.score}")
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid game result data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting game result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit game result"
        )


@router.get("/leaderboard",
            response_model=LeaderboardResponse,
            summary="Get Leaderboard",
            description="Retrieve the leaderboard with optional filtering by difficulty")
async def get_leaderboard(
    difficulty: Optional[str] = Query(
        None, 
        description="Filter by difficulty (easy, medium, hard)",
        regex="^(easy|medium|hard)$"
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=100, 
        description="Maximum number of entries to return"
    )
):
    """
    Get the leaderboard entries, optionally filtered by difficulty.
    
    Args:
        difficulty: Optional difficulty filter (easy, medium, hard)
        limit: Maximum number of entries to return (1-100)
        
    Returns:
        LeaderboardResponse: List of leaderboard entries with metadata
        
    Raises:
        HTTPException: If there's an error retrieving the leaderboard
    """
    try:
        logger.info(f"Retrieving leaderboard (difficulty={difficulty}, limit={limit})")
        
        # Get leaderboard through the controller
        leaderboard = await game_controller.get_leaderboard(difficulty, limit)
        
        logger.info(f"Retrieved leaderboard: {len(leaderboard.entries)} entries")
        return leaderboard
        
    except ValueError as e:
        logger.warning(f"Invalid leaderboard request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard"
        )


@router.delete("/leaderboard",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Clear Leaderboard",
               description="Clear all entries from the leaderboard")
async def clear_leaderboard():
    """
    Clear all entries from the leaderboard.
    
    This is a destructive operation that removes all leaderboard data.
    
    Raises:
        HTTPException: If there's an error clearing the leaderboard
    """
    try:
        logger.info("Clearing leaderboard")
        
        # Clear leaderboard through the controller
        await game_controller.clear_leaderboard()
        
        logger.info("Leaderboard cleared successfully")
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except Exception as e:
        logger.error(f"Error clearing leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear leaderboard"
        )


@router.get("/leaderboard/stats",
            summary="Get Leaderboard Statistics",
            description="Get statistics about the leaderboard")
async def get_leaderboard_stats():
    """
    Get statistics about the leaderboard.
    
    Returns:
        dict: Statistics including total games, games by difficulty, etc.
        
    Raises:
        HTTPException: If there's an error retrieving statistics
    """
    try:
        logger.info("Retrieving leaderboard statistics")
        
        # Get statistics through the controller
        stats = await game_controller.get_leaderboard_stats()
        
        logger.info("Retrieved leaderboard statistics successfully")
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving leaderboard statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard statistics"
        )
