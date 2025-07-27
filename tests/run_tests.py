#!/usr/bin/env python3
"""
Test runner script for the Minesweeper application.
Provides convenient test execution with coverage reporting.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run the complete test suite with coverage reporting."""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 Running Minesweeper Test Suite")
    print("=" * 50)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest", "pytest-asyncio", "pytest-cov", "httpx"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Run tests with coverage
    print("\n🔍 Running tests with coverage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=server",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=80"
        ], check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
            return True
        else:
            print(f"\n❌ Tests failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_test(test_name):
    """Run a specific test or test class."""
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/test_minesweeper.py::{test_name}",
            "-v",
            "--tb=short"
        ], check=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def run_integration_tests():
    """Run only integration tests."""
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_minesweeper.py::TestIntegration",
            "-v",
            "--tb=short"
        ], check=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False


def run_unit_tests():
    """Run only unit tests (excluding integration tests)."""
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_minesweeper.py",
            "-v",
            "--tb=short",
            "-k", "not TestIntegration"
        ], check=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False


def main():
    """Main entry point for the test runner."""
    
    if len(sys.argv) == 1:
        # Run all tests
        success = run_tests()
    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()
        
        if command == "unit":
            success = run_unit_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "help":
            print_help()
            return
        else:
            # Assume it's a specific test name
            success = run_specific_test(sys.argv[1])
    else:
        print("❌ Invalid arguments. Use 'python run_tests.py help' for usage.")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


def print_help():
    """Print help information."""
    
    help_text = """
🧪 Minesweeper Test Runner

Usage:
    python tests/run_tests.py                    # Run all tests with coverage
    python tests/run_tests.py unit              # Run only unit tests
    python tests/run_tests.py integration       # Run only integration tests
    python tests/run_tests.py TestClassName     # Run specific test class
    python tests/run_tests.py test_method_name  # Run specific test method
    python tests/run_tests.py help              # Show this help

Examples:
    python tests/run_tests.py TestDatabaseManager
    python tests/run_tests.py test_score_calculation
    python tests/run_tests.py TestAPIEndpoints::test_health_endpoint

Test Categories:
    • Unit Tests: Test individual components in isolation
    • Integration Tests: Test complete workflows end-to-end
    • API Tests: Test FastAPI endpoints and HTTP responses
    • Database Tests: Test SQLite operations and data persistence
    • Model Tests: Test Pydantic model validation

Coverage Report:
    After running tests, open htmlcov/index.html to view detailed coverage report.
    
Requirements:
    The test runner will automatically install required dependencies:
    • pytest: Test framework
    • pytest-asyncio: Async test support
    • pytest-cov: Coverage reporting
    • httpx: HTTP client for API testing
    """
    
    print(help_text)


if __name__ == "__main__":
    main()
