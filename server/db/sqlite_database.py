"""
SQLite database operations for the Minesweeper application.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from ..utils.config import settings


logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite database manager for Minesweeper game data."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or settings.database_url.replace("sqlite:///", "")
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
                    time_seconds INTEGER NOT NULL,
                    won BOOLEAN NOT NULL,
                    score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_difficulty_score 
                ON games(difficulty, score DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_created_at 
                ON games(created_at DESC)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def calculate_score(self, difficulty: str, time_seconds: int, won: bool) -> float:
        """Calculate game score based on difficulty, time, and result."""
        if not won:
            return 0.0
        
        base_score = 10000  # Base score for winning
        time_penalty = time_seconds * 10  # Penalty for longer times
        difficulty_multiplier = settings.score_multipliers.get(difficulty, 1.0)
        
        score = (base_score - time_penalty) * difficulty_multiplier
        return max(score, 100.0)  # Minimum score of 100 for any win
    
    def save_game_result(self, player_name: str, difficulty: str, 
                        time_seconds: int, won: bool) -> int:
        """Save a game result to the database."""
        score = self.calculate_score(difficulty, time_seconds, won)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (player_name, difficulty, time_seconds, won, score)
                VALUES (?, ?, ?, ?, ?)
            """, (player_name, difficulty, time_seconds, won, score))
            
            game_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Saved game result: ID={game_id}, Player={player_name}, "
                       f"Difficulty={difficulty}, Won={won}, Score={score}")
            
            return game_id
    
    def get_leaderboard(self, difficulty: Optional[str] = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard entries, optionally filtered by difficulty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if difficulty:
                query = """
                    SELECT id, player_name, difficulty, time_seconds, won, score, created_at
                    FROM games 
                    WHERE difficulty = ? AND won = 1
                    ORDER BY score DESC, time_seconds ASC
                    LIMIT ?
                """
                cursor.execute(query, (difficulty, limit))
            else:
                query = """
                    SELECT id, player_name, difficulty, time_seconds, won, score, created_at
                    FROM games 
                    WHERE won = 1
                    ORDER BY score DESC, time_seconds ASC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            leaderboard = []
            for row in rows:
                entry = {
                    "id": row["id"],
                    "player_name": row["player_name"],
                    "difficulty": row["difficulty"],
                    "time_seconds": row["time_seconds"],
                    "won": bool(row["won"]),
                    "score": row["score"],
                    "created_at": datetime.fromisoformat(row["created_at"])
                }
                leaderboard.append(entry)
            
            return leaderboard
    
    def get_leaderboard_count(self, difficulty: Optional[str] = None) -> int:
        """Get total count of leaderboard entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if difficulty:
                cursor.execute("""
                    SELECT COUNT(*) FROM games 
                    WHERE difficulty = ? AND won = 1
                """, (difficulty,))
            else:
                cursor.execute("SELECT COUNT(*) FROM games WHERE won = 1")
            
            return cursor.fetchone()[0]
    
    def clear_leaderboard(self) -> int:
        """Clear all game records from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM games")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM games")
            conn.commit()
            
            logger.info(f"Cleared {count} game records from database")
            return count
    
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get statistics for a specific player."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    difficulty,
                    COUNT(*) as games_played,
                    SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as games_won,
                    MIN(CASE WHEN won = 1 THEN time_seconds END) as best_time,
                    MAX(score) as best_score
                FROM games 
                WHERE player_name = ?
                GROUP BY difficulty
            """, (player_name,))
            
            rows = cursor.fetchall()
            
            stats = {}
            for row in rows:
                stats[row["difficulty"]] = {
                    "games_played": row["games_played"],
                    "games_won": row["games_won"],
                    "win_rate": row["games_won"] / row["games_played"] if row["games_played"] > 0 else 0,
                    "best_time": row["best_time"],
                    "best_score": row["best_score"]
                }
            
            return stats
    
    def health_check(self) -> bool:
        """Perform a health check on the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db_manager = DatabaseManager()
