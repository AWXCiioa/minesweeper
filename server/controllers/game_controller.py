"""
Business logic controller for Minesweeper game operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..db.sqlite_database import db_manager
from ..models.game_models import GameResult, LeaderboardEntry, LeaderboardResponse
from ..utils.config import settings


logger = logging.getLogger(__name__)


class GameController:
    """Controller for game-related business logic."""
    
    def __init__(self):
        """Initialize the game controller."""
        self.db = db_manager
    
    async def submit_game_result(self, game_result: GameResult) -> Dict[str, Any]:
        """
        Submit a game result and return the saved entry with calculated score.
        
        Args:
            game_result: The game result data
            
        Returns:
            Dictionary containing the saved game data
            
        Raises:
            ValueError: If the game result data is invalid
            Exception: If database operation fails
        """
        try:
            # Validate that only winning games are submitted for leaderboard
            if not game_result.won:
                logger.info(f"Game loss submitted by {game_result.player_name} "
                           f"on {game_result.difficulty} difficulty")
            
            # Save to database
            game_id = self.db.save_game_result(
                player_name=game_result.player_name,
                difficulty=game_result.difficulty,
                time_seconds=game_result.time_seconds,
                won=game_result.won
            )
            
            # Calculate score for response
            score = self.db.calculate_score(
                game_result.difficulty,
                game_result.time_seconds,
                game_result.won
            )
            
            result = {
                "id": game_id,
                "player_name": game_result.player_name,
                "difficulty": game_result.difficulty,
                "time_seconds": game_result.time_seconds,
                "won": game_result.won,
                "score": score,
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully submitted game result: ID={game_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to submit game result: {e}")
            raise
    
    async def get_leaderboard(self, difficulty: Optional[str] = None, 
                            limit: int = None) -> LeaderboardResponse:
        """
        Get leaderboard entries, optionally filtered by difficulty.
        
        Args:
            difficulty: Optional difficulty filter ('easy', 'medium', 'hard')
            limit: Maximum number of entries to return
            
        Returns:
            LeaderboardResponse containing entries and total count
            
        Raises:
            ValueError: If difficulty is invalid
            Exception: If database operation fails
        """
        try:
            # Validate difficulty if provided
            if difficulty and difficulty not in ['easy', 'medium', 'hard']:
                raise ValueError(f"Invalid difficulty: {difficulty}")
            
            # Use configured limit if not provided
            if limit is None:
                limit = settings.max_leaderboard_entries
            
            # Get leaderboard data
            entries_data = self.db.get_leaderboard(difficulty=difficulty, limit=limit)
            total_count = self.db.get_leaderboard_count(difficulty=difficulty)
            
            # Convert to Pydantic models
            entries = [LeaderboardEntry(**entry) for entry in entries_data]
            
            response = LeaderboardResponse(
                entries=entries,
                total_count=total_count
            )
            
            logger.info(f"Retrieved leaderboard: {len(entries)} entries "
                       f"(difficulty={difficulty}, total={total_count})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            raise
    
    async def clear_leaderboard(self) -> Dict[str, Any]:
        """
        Clear all leaderboard entries.
        
        Returns:
            Dictionary containing the number of cleared entries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            cleared_count = self.db.clear_leaderboard()
            
            result = {
                "message": "Leaderboard cleared successfully",
                "cleared_entries": cleared_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Cleared leaderboard: {cleared_count} entries removed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to clear leaderboard: {e}")
            raise
    
    async def get_player_statistics(self, player_name: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Dictionary containing player statistics
            
        Raises:
            ValueError: If player name is invalid
            Exception: If database operation fails
        """
        try:
            if not player_name or not player_name.strip():
                raise ValueError("Player name cannot be empty")
            
            stats = self.db.get_player_stats(player_name.strip())
            
            # Add overall statistics
            total_games = sum(diff_stats["games_played"] for diff_stats in stats.values())
            total_wins = sum(diff_stats["games_won"] for diff_stats in stats.values())
            overall_win_rate = total_wins / total_games if total_games > 0 else 0
            
            result = {
                "player_name": player_name.strip(),
                "overall_stats": {
                    "total_games": total_games,
                    "total_wins": total_wins,
                    "overall_win_rate": overall_win_rate
                },
                "difficulty_stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved player statistics for: {player_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get player statistics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the game controller and database.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            return self.db.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global controller instance
game_controller = GameController()
