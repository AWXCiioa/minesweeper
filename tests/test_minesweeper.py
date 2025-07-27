"""
Comprehensive test suite for the Minesweeper application.
Tests API endpoints, database operations, game logic, and error handling.
"""

import pytest
import tempfile
import os
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import application components
from server.main import app
from server.db.sqlite_database import DatabaseManager
from server.controllers.game_controller import GameController
from server.models.game_models import GameResult, LeaderboardEntry


class TestDatabaseManager:
    """Test database operations."""
    
    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database table creation."""
        # Database should be initialized without errors
        assert self.db.health_check() is True
        
        # Check if tables exist by trying to query them
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
            result = cursor.fetchone()
            assert result is not None
    
    def test_score_calculation(self):
        """Test score calculation logic."""
        # Test winning game scores
        easy_score = self.db.calculate_score('easy', 60, True)
        medium_score = self.db.calculate_score('medium', 60, True)
        hard_score = self.db.calculate_score('hard', 60, True)
        
        assert easy_score > 0
        assert medium_score > easy_score  # Medium should have higher multiplier
        assert hard_score > medium_score  # Hard should have highest multiplier
        
        # Test losing game score
        losing_score = self.db.calculate_score('easy', 60, False)
        assert losing_score == 0.0
        
        # Test minimum score
        very_slow_score = self.db.calculate_score('easy', 10000, True)
        assert very_slow_score >= 100.0  # Minimum score should be 100
    
    def test_save_game_result(self):
        """Test saving game results."""
        game_id = self.db.save_game_result(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        
        assert game_id is not None
        assert game_id > 0
        
        # Verify the game was saved correctly
        leaderboard = self.db.get_leaderboard()
        assert len(leaderboard) == 1
        assert leaderboard[0]['player_name'] == "TestPlayer"
        assert leaderboard[0]['difficulty'] == "easy"
        assert leaderboard[0]['time_seconds'] == 120
        assert leaderboard[0]['won'] is True
    
    def test_get_leaderboard(self):
        """Test leaderboard retrieval."""
        # Add test data
        self.db.save_game_result("Player1", "easy", 60, True)
        self.db.save_game_result("Player2", "easy", 90, True)
        self.db.save_game_result("Player3", "medium", 120, True)
        self.db.save_game_result("Player4", "easy", 180, False)  # Lost game
        
        # Test all difficulties
        all_leaderboard = self.db.get_leaderboard()
        assert len(all_leaderboard) == 3  # Only winning games
        
        # Test difficulty filter
        easy_leaderboard = self.db.get_leaderboard(difficulty="easy")
        assert len(easy_leaderboard) == 2
        
        medium_leaderboard = self.db.get_leaderboard(difficulty="medium")
        assert len(medium_leaderboard) == 1
        
        # Test ordering (should be by score DESC, then time ASC)
        assert easy_leaderboard[0]['time_seconds'] <= easy_leaderboard[1]['time_seconds']
    
    def test_get_leaderboard_count(self):
        """Test leaderboard count functionality."""
        # Add test data
        self.db.save_game_result("Player1", "easy", 60, True)
        self.db.save_game_result("Player2", "medium", 90, True)
        self.db.save_game_result("Player3", "easy", 120, False)  # Lost game
        
        total_count = self.db.get_leaderboard_count()
        assert total_count == 2  # Only winning games
        
        easy_count = self.db.get_leaderboard_count(difficulty="easy")
        assert easy_count == 1
        
        medium_count = self.db.get_leaderboard_count(difficulty="medium")
        assert medium_count == 1
    
    def test_clear_leaderboard(self):
        """Test clearing leaderboard."""
        # Add test data
        self.db.save_game_result("Player1", "easy", 60, True)
        self.db.save_game_result("Player2", "medium", 90, True)
        
        # Clear leaderboard
        cleared_count = self.db.clear_leaderboard()
        assert cleared_count == 2
        
        # Verify leaderboard is empty
        leaderboard = self.db.get_leaderboard()
        assert len(leaderboard) == 0
    
    def test_get_player_stats(self):
        """Test player statistics retrieval."""
        # Add test data for a player
        self.db.save_game_result("TestPlayer", "easy", 60, True)
        self.db.save_game_result("TestPlayer", "easy", 90, True)
        self.db.save_game_result("TestPlayer", "easy", 120, False)
        self.db.save_game_result("TestPlayer", "medium", 180, True)
        
        stats = self.db.get_player_stats("TestPlayer")
        
        # Check easy difficulty stats
        assert "easy" in stats
        easy_stats = stats["easy"]
        assert easy_stats["games_played"] == 3
        assert easy_stats["games_won"] == 2
        assert easy_stats["win_rate"] == 2/3
        assert easy_stats["best_time"] == 60
        
        # Check medium difficulty stats
        assert "medium" in stats
        medium_stats = stats["medium"]
        assert medium_stats["games_played"] == 1
        assert medium_stats["games_won"] == 1
        assert medium_stats["win_rate"] == 1.0


class TestGameController:
    """Test game controller business logic."""
    
    def setup_method(self):
        """Set up test controller for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create controller with test database
        self.controller = GameController()
        self.controller.db = DatabaseManager(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    @pytest.mark.asyncio
    async def test_submit_game_result(self):
        """Test game result submission."""
        game_result = GameResult(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        
        result = await self.controller.submit_game_result(game_result)
        
        assert result["player_name"] == "TestPlayer"
        assert result["difficulty"] == "easy"
        assert result["time_seconds"] == 120
        assert result["won"] is True
        assert result["score"] > 0
        assert "id" in result
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_get_leaderboard(self):
        """Test leaderboard retrieval through controller."""
        # Add test data
        game_result = GameResult(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        await self.controller.submit_game_result(game_result)
        
        # Get leaderboard
        leaderboard = await self.controller.get_leaderboard()
        
        assert len(leaderboard.entries) == 1
        assert leaderboard.total_count == 1
        assert leaderboard.entries[0].player_name == "TestPlayer"
    
    @pytest.mark.asyncio
    async def test_get_leaderboard_with_difficulty_filter(self):
        """Test leaderboard with difficulty filter."""
        # Add test data for different difficulties
        easy_result = GameResult(
            player_name="EasyPlayer",
            difficulty="easy",
            time_seconds=60,
            won=True
        )
        medium_result = GameResult(
            player_name="MediumPlayer",
            difficulty="medium",
            time_seconds=120,
            won=True
        )
        
        await self.controller.submit_game_result(easy_result)
        await self.controller.submit_game_result(medium_result)
        
        # Test filtered leaderboard
        easy_leaderboard = await self.controller.get_leaderboard(difficulty="easy")
        assert len(easy_leaderboard.entries) == 1
        assert easy_leaderboard.entries[0].difficulty == "easy"
        
        # Test invalid difficulty
        with pytest.raises(ValueError):
            await self.controller.get_leaderboard(difficulty="invalid")
    
    @pytest.mark.asyncio
    async def test_clear_leaderboard(self):
        """Test leaderboard clearing through controller."""
        # Add test data
        game_result = GameResult(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        await self.controller.submit_game_result(game_result)
        
        # Clear leaderboard
        result = await self.controller.clear_leaderboard()
        
        assert result["cleared_entries"] == 1
        assert "message" in result
        assert "timestamp" in result
        
        # Verify leaderboard is empty
        leaderboard = await self.controller.get_leaderboard()
        assert len(leaderboard.entries) == 0
    
    @pytest.mark.asyncio
    async def test_get_player_statistics(self):
        """Test player statistics through controller."""
        # Add test data
        game_result = GameResult(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        await self.controller.submit_game_result(game_result)
        
        # Get player statistics
        stats = await self.controller.get_player_statistics("TestPlayer")
        
        assert stats["player_name"] == "TestPlayer"
        assert "overall_stats" in stats
        assert "difficulty_stats" in stats
        assert "timestamp" in stats
        
        # Test invalid player name
        with pytest.raises(ValueError):
            await self.controller.get_player_statistics("")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test controller health check."""
        health = await self.controller.health_check()
        assert health is True


class TestAPIEndpoints:
    """Test FastAPI endpoints."""
    
    def setup_method(self):
        """Set up test client for each test."""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create a test controller with isolated database
        self.test_controller = GameController()
        self.test_controller.db = DatabaseManager(self.temp_db.name)
        
        # Patch the global controller instance
        self.controller_patcher = patch('server.routes.game_routes.game_controller', self.test_controller)
        self.controller_patcher.start()
        
        # Also patch the controller in main.py for health checks
        self.main_patcher = patch('server.main.game_controller', self.test_controller)
        self.main_patcher.start()
        
        self.client = TestClient(app)
    
    def teardown_method(self):
        """Clean up after each test."""
        self.controller_patcher.stop()
        self.main_patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_submit_game_result_endpoint(self):
        """Test game result submission endpoint."""
        game_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy",
            "time_seconds": 120,
            "won": True
        }
        
        response = self.client.post("/api/v1/games", json=game_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Game result submitted successfully"
        assert "data" in data
        assert data["data"]["player_name"] == "TestPlayer"
    
    def test_submit_invalid_game_result(self):
        """Test submitting invalid game result."""
        # Missing required fields
        invalid_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy"
            # Missing time_seconds and won
        }
        
        response = self.client.post("/api/v1/games", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_submit_game_result_invalid_difficulty(self):
        """Test submitting game result with invalid difficulty."""
        invalid_data = {
            "player_name": "TestPlayer",
            "difficulty": "invalid",
            "time_seconds": 120,
            "won": True
        }
        
        response = self.client.post("/api/v1/games", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_submit_game_result_invalid_time(self):
        """Test submitting game result with invalid time."""
        invalid_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy",
            "time_seconds": -10,  # Negative time
            "won": True
        }
        
        response = self.client.post("/api/v1/games", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_leaderboard_endpoint(self):
        """Test leaderboard retrieval endpoint."""
        # First submit a game result
        game_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy",
            "time_seconds": 120,
            "won": True
        }
        self.client.post("/api/v1/games", json=game_data)
        
        # Get leaderboard
        response = self.client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "entries" in data
        assert "total_count" in data
        assert len(data["entries"]) == 1
    
    def test_get_leaderboard_with_difficulty_filter(self):
        """Test leaderboard with difficulty filter."""
        # Submit games for different difficulties
        easy_game = {
            "player_name": "EasyPlayer",
            "difficulty": "easy",
            "time_seconds": 60,
            "won": True
        }
        medium_game = {
            "player_name": "MediumPlayer",
            "difficulty": "medium",
            "time_seconds": 120,
            "won": True
        }
        
        self.client.post("/api/v1/games", json=easy_game)
        self.client.post("/api/v1/games", json=medium_game)
        
        # Test filtered leaderboard
        response = self.client.get("/api/v1/leaderboard?difficulty=easy")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["entries"]) == 1
        assert data["entries"][0]["difficulty"] == "easy"
    
    def test_get_leaderboard_invalid_difficulty(self):
        """Test leaderboard with invalid difficulty filter."""
        response = self.client.get("/api/v1/leaderboard?difficulty=invalid")
        assert response.status_code == 422  # Validation error (correct for FastAPI)
    
    def test_clear_leaderboard_endpoint(self):
        """Test leaderboard clearing endpoint."""
        # First submit a game result
        game_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy",
            "time_seconds": 120,
            "won": True
        }
        self.client.post("/api/v1/games", json=game_data)
        
        # Clear leaderboard
        response = self.client.delete("/api/v1/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "cleared_entries" in data
        assert data["cleared_entries"] >= 1
    
    def test_get_player_statistics_endpoint(self):
        """Test player statistics endpoint."""
        # First submit a game result
        game_data = {
            "player_name": "TestPlayer",
            "difficulty": "easy",
            "time_seconds": 120,
            "won": True
        }
        self.client.post("/api/v1/games", json=game_data)
        
        # Get player statistics
        response = self.client.get("/api/v1/players/TestPlayer/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Player statistics retrieved successfully"
        assert "data" in data
        assert data["data"]["player_name"] == "TestPlayer"
    
    def test_serve_frontend_endpoint(self):
        """Test frontend serving endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        # Should serve HTML content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_404_api_endpoint(self):
        """Test 404 handling for API endpoints."""
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"] == "Not Found"


class TestGameModels:
    """Test Pydantic models."""
    
    def test_game_result_model_valid(self):
        """Test valid GameResult model."""
        game_result = GameResult(
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        
        assert game_result.player_name == "TestPlayer"
        assert game_result.difficulty == "easy"
        assert game_result.time_seconds == 120
        assert game_result.won is True
    
    def test_game_result_model_validation(self):
        """Test GameResult model validation."""
        # Test empty player name
        with pytest.raises(ValueError):
            GameResult(
                player_name="",
                difficulty="easy",
                time_seconds=120,
                won=True
            )
        
        # Test invalid difficulty
        with pytest.raises(ValueError):
            GameResult(
                player_name="TestPlayer",
                difficulty="invalid",
                time_seconds=120,
                won=True
            )
        
        # Test invalid time
        with pytest.raises(ValueError):
            GameResult(
                player_name="TestPlayer",
                difficulty="easy",
                time_seconds=0,  # Must be >= 1
                won=True
            )
        
        # Test excessive time
        with pytest.raises(ValueError):
            GameResult(
                player_name="TestPlayer",
                difficulty="easy",
                time_seconds=100000,  # Too long
                won=True
            )
    
    def test_game_result_name_cleaning(self):
        """Test player name cleaning."""
        game_result = GameResult(
            player_name="  TestPlayer  ",  # With whitespace
            difficulty="easy",
            time_seconds=120,
            won=True
        )
        
        assert game_result.player_name == "TestPlayer"  # Should be trimmed
    
    def test_leaderboard_entry_model(self):
        """Test LeaderboardEntry model."""
        entry = LeaderboardEntry(
            id=1,
            player_name="TestPlayer",
            difficulty="easy",
            time_seconds=120,
            won=True,
            score=8800.0,
            created_at=datetime.utcnow()
        )
        
        assert entry.id == 1
        assert entry.player_name == "TestPlayer"
        assert entry.score == 8800.0


class TestIntegration:
    """Integration tests for the complete application."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.client = TestClient(app)
        
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Patch database manager
        self.db_patcher = patch('server.db.sqlite_database.db_manager')
        self.mock_db = self.db_patcher.start()
        self.mock_db.return_value = DatabaseManager(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up integration test environment."""
        self.db_patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_complete_game_workflow(self):
        """Test complete game workflow from submission to leaderboard."""
        # Submit multiple game results
        games = [
            {
                "player_name": "Alice",
                "difficulty": "easy",
                "time_seconds": 60,
                "won": True
            },
            {
                "player_name": "Bob",
                "difficulty": "easy",
                "time_seconds": 90,
                "won": True
            },
            {
                "player_name": "Charlie",
                "difficulty": "medium",
                "time_seconds": 180,
                "won": True
            },
            {
                "player_name": "David",
                "difficulty": "easy",
                "time_seconds": 120,
                "won": False  # Lost game
            }
        ]
        
        # Submit all games
        for game in games:
            response = self.client.post("/api/v1/games", json=game)
            assert response.status_code == 201
        
        # Check overall leaderboard
        response = self.client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["entries"]) == 3  # Only winning games
        assert data["total_count"] == 3
        
        # Check that scores are ordered correctly (higher scores first)
        scores = [entry["score"] for entry in data["entries"]]
        assert scores == sorted(scores, reverse=True)
        
        # Check easy difficulty leaderboard
        response = self.client.get("/api/v1/leaderboard?difficulty=easy")
        assert response.status_code == 200
        
        easy_data = response.json()
        assert len(easy_data["entries"]) == 2  # Alice and Bob
        
        # Alice should be first (faster time = higher score)
        assert easy_data["entries"][0]["player_name"] == "Alice"
        assert easy_data["entries"][1]["player_name"] == "Bob"
        
        # Check player statistics
        response = self.client.get("/api/v1/players/Alice/stats")
        assert response.status_code == 200
        
        stats_data = response.json()
        alice_stats = stats_data["data"]
        assert alice_stats["overall_stats"]["total_games"] == 1
        assert alice_stats["overall_stats"]["total_wins"] == 1
        assert alice_stats["overall_stats"]["overall_win_rate"] == 1.0
        
        # Clear leaderboard
        response = self.client.delete("/api/v1/leaderboard")
        assert response.status_code == 200
        
        clear_data = response.json()
        assert clear_data["cleared_entries"] == 4  # All games (including lost)
        
        # Verify leaderboard is empty
        response = self.client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        
        empty_data = response.json()
        assert len(empty_data["entries"]) == 0
        assert empty_data["total_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
