"""
Game controller for handling Minesweeper game logic and database operations.
"""

import logging
from datetime import datetime
from typing import List, Optional

from ..db.sqlite_database import database
from ..models.game_models import (
    GameResult, GameResultResponse, LeaderboardEntry, 
    LeaderboardResponse
)

logger = logging.getLogger(__name__)


class GameController:
    """Controller for handling game-related operations."""
    
    def __init__(self):
        """Initialize the game controller."""
        self.db = database
    
    async def submit_game_result(self, game_result: GameResult) -> GameResultResponse:
        """
        Submit a game result to the database.
        
        Args:
            game_result: The game result to submit
            
        Returns:
            GameResultResponse: The submitted game result with calculated score
            
        Raises:
            ValueError: If the game result data is invalid
        """
        try:
            # Validate game result
            if not game_result.player_name.strip():
                raise ValueError("Player name cannot be empty")
            
            if game_result.difficulty not in ["easy", "medium", "hard"]:
                raise ValueError("Invalid difficulty level")
            
            if game_result.time_seconds <= 0:
                raise ValueError("Time must be positive")
            
            # Calculate score based on difficulty and time
            score = self._calculate_score(
                game_result.difficulty, 
                game_result.time_seconds, 
                game_result.won
            )
            
            # Insert into database
            game_id = await self.db.insert_game_result(
                player_name=game_result.player_name,
                difficulty=game_result.difficulty,
                time_seconds=game_result.time_seconds,
                won=game_result.won,
                score=score
            )
            
            logger.info(f"Game result submitted: ID={game_id}, Player={game_result.player_name}, Score={score}")
            
            return GameResultResponse(
                id=game_id,
                player_name=game_result.player_name,
                difficulty=game_result.difficulty,
                time_seconds=game_result.time_seconds,
                won=game_result.won,
                score=score,
                submitted_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error submitting game result: {e}")
            raise
    
    async def get_leaderboard(self, difficulty: Optional[str] = None, limit: int = 10) -> LeaderboardResponse:
        """
        Get the leaderboard entries.
        
        Args:
            difficulty: Optional difficulty filter
            limit: Maximum number of entries to return
            
        Returns:
            LeaderboardResponse: The leaderboard entries with metadata
        """
        try:
            # Get entries from database
            entries = await self.db.get_leaderboard(difficulty, limit)
            
            # Convert to LeaderboardEntry objects
            leaderboard_entries = [
                LeaderboardEntry(
                    rank=i + 1,
                    player_name=entry["player_name"],
                    difficulty=entry["difficulty"],
                    time_seconds=entry["time_seconds"],
                    score=entry["score"],
                    submitted_at=entry["submitted_at"]
                )
                for i, entry in enumerate(entries)
            ]
            
            # Get total count for metadata
            total_entries = await self.db.get_total_games_count(difficulty)
            
            logger.info(f"Retrieved leaderboard: {len(leaderboard_entries)} entries (difficulty={difficulty}, total={total_entries})")
            
            return LeaderboardResponse(
                entries=leaderboard_entries,
                total_entries=total_entries,
                difficulty_filter=difficulty,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {e}")
            raise
    
    async def clear_leaderboard(self) -> None:
        """
        Clear all entries from the leaderboard.
        """
        try:
            await self.db.clear_all_games()
            logger.info("Leaderboard cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing leaderboard: {e}")
            raise
    
    async def get_leaderboard_stats(self) -> dict:
        """
        Get statistics about the leaderboard.
        
        Returns:
            dict: Statistics including total games, games by difficulty, etc.
        """
        try:
            stats = await self.db.get_game_statistics()
            logger.info("Retrieved leaderboard statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving leaderboard statistics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            return await self.db.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def _calculate_score(self, difficulty: str, time_seconds: int, won: bool) -> int:
        """
        Calculate the score based on difficulty, time, and outcome.
        
        Args:
            difficulty: The game difficulty
            time_seconds: Time taken to complete the game
            won: Whether the game was won
            
        Returns:
            int: The calculated score
        """
        if not won:
            return 0
        
        # Base scores for each difficulty
        base_scores = {
            "easy": 1000,
            "medium": 2000,
            "hard": 3000
        }
        
        base_score = base_scores.get(difficulty, 1000)
        
        # Time bonus (more points for faster completion)
        # Maximum time bonuses
        max_times = {
            "easy": 300,    # 5 minutes
            "medium": 600,  # 10 minutes
            "hard": 1200    # 20 minutes
        }
        
        max_time = max_times.get(difficulty, 300)
        time_bonus = max(0, (max_time - time_seconds) * 2)
        
        total_score = base_score + time_bonus
        return max(0, total_score)


# Create a global instance
game_controller = GameController()
