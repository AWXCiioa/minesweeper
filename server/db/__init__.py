"""
Database layer for the Minesweeper application.
"""

from .sqlite_database import DatabaseManager, db_manager

__all__ = ["DatabaseManager", "db_manager"]
