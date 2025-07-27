"""
SQLite database operations for Minesweeper game.
"""

import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..utils.config import settings

logger = logging.getLogger(__name__)


class SQLiteDatabase:
    """SQLite database handler for Minesweeper game."""
    
    def __init__(self, db_path: str = "minesweeper.db"):
        """Initialize the database handler."""
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """Initialize the database and create tables if they don't exist."""
        if self._initialized:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
                        time_seconds INTEGER NOT NULL CHECK (time_seconds > 0),
                        won BOOLEAN NOT NULL,
                        score INTEGER NOT NULL DEFAULT 0,
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_games_difficulty 
                    ON games(difficulty)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_games_score 
                    ON games(score DESC)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_games_submitted_at 
                    ON games(submitted_at DESC)
                """)
                
                await db.commit()
                logger.info("Database initialized successfully")
                self._initialized = True
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def insert_game_result(
        self, 
        player_name: str, 
        difficulty: str, 
        time_seconds: int, 
        won: bool, 
        score: int
    ) -> int:
        """
        Insert a game result into the database.
        
        Args:
            player_name: Name of the player
            difficulty: Game difficulty (easy, medium, hard)
            time_seconds: Time taken to complete the game
            won: Whether the game was won
            score: Calculated score
            
        Returns:
            int: The ID of the inserted record
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO games (player_name, difficulty, time_seconds, won, score, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (player_name, difficulty, time_seconds, won, score, datetime.utcnow()))
                
                await db.commit()
                game_id = cursor.lastrowid
                logger.info(f"Inserted game result with ID: {game_id}")
                return game_id
                
        except Exception as e:
            logger.error(f"Failed to insert game result: {e}")
            raise
    
    async def get_leaderboard(self, difficulty: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get leaderboard entries.
        
        Args:
            difficulty: Optional difficulty filter
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict]: List of leaderboard entries
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if difficulty:
                    cursor = await db.execute("""
                        SELECT player_name, difficulty, time_seconds, score, submitted_at
                        FROM games 
                        WHERE difficulty = ? AND won = 1
                        ORDER BY score DESC, time_seconds ASC
                        LIMIT ?
                    """, (difficulty, limit))
                else:
                    cursor = await db.execute("""
                        SELECT player_name, difficulty, time_seconds, score, submitted_at
                        FROM games 
                        WHERE won = 1
                        ORDER BY score DESC, time_seconds ASC
                        LIMIT ?
                    """, (limit,))
                
                rows = await cursor.fetchall()
                entries = [dict(row) for row in rows]
                
                logger.info(f"Retrieved {len(entries)} leaderboard entries")
                return entries
                
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            raise
    
    async def get_total_games_count(self, difficulty: Optional[str] = None) -> int:
        """
        Get the total number of games in the database.
        
        Args:
            difficulty: Optional difficulty filter
            
        Returns:
            int: Total number of games
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if difficulty:
                    cursor = await db.execute("""
                        SELECT COUNT(*) FROM games WHERE difficulty = ?
                    """, (difficulty,))
                else:
                    cursor = await db.execute("SELECT COUNT(*) FROM games")
                
                result = await cursor.fetchone()
                count = result[0] if result else 0
                
                logger.info(f"Total games count: {count}")
                return count
                
        except Exception as e:
            logger.error(f"Failed to get games count: {e}")
            raise
    
    async def clear_all_games(self) -> None:
        """Clear all games from the database."""
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM games")
                await db.commit()
                logger.info("All games cleared from database")
                
        except Exception as e:
            logger.error(f"Failed to clear games: {e}")
            raise
    
    async def get_game_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the games in the database.
        
        Returns:
            Dict: Statistics including total games, games by difficulty, etc.
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Total games
                cursor = await db.execute("SELECT COUNT(*) as total FROM games")
                total_result = await cursor.fetchone()
                total_games = total_result[0] if total_result else 0
                
                # Games by difficulty
                cursor = await db.execute("""
                    SELECT difficulty, COUNT(*) as count 
                    FROM games 
                    GROUP BY difficulty
                """)
                difficulty_results = await cursor.fetchall()
                games_by_difficulty = {row['difficulty']: row['count'] for row in difficulty_results}
                
                # Win rate
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins
                    FROM games
                """)
                win_result = await cursor.fetchone()
                total = win_result['total'] if win_result else 0
                wins = win_result['wins'] if win_result else 0
                win_rate = (wins / total * 100) if total > 0 else 0
                
                # Average times by difficulty
                cursor = await db.execute("""
                    SELECT difficulty, AVG(time_seconds) as avg_time
                    FROM games 
                    WHERE won = 1
                    GROUP BY difficulty
                """)
                time_results = await cursor.fetchall()
                avg_times = {row['difficulty']: round(row['avg_time'], 2) for row in time_results}
                
                stats = {
                    "total_games": total_games,
                    "games_by_difficulty": games_by_difficulty,
                    "win_rate": round(win_rate, 2),
                    "average_times": avg_times,
                    "total_wins": wins
                }
                
                logger.info("Retrieved game statistics")
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get game statistics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT 1")
                await cursor.fetchone()
                return True
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Create a global database instance
database = SQLiteDatabase()
