"""
API routes for the Minesweeper application.
"""

from .game_routes import router as game_router

__all__ = ["game_router"]
