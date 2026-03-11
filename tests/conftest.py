"""
Configuration for pytest.

This file contains pytest configuration and shared fixtures for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="session")
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "description": "Test activity description",
        "schedule": "Test schedule",
        "max_participants": 10,
        "participants": []
    }


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test to ensure test isolation."""
    from src import app as app_module

    # Store original activities
    original_activities = app_module.activities.copy()

    yield

    # Restore original activities after test
    app_module.activities = original_activities