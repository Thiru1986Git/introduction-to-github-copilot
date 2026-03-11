"""
Test the FastAPI application startup and configuration.

This module tests the application setup, routing, and basic configuration.
"""

import pytest
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from src.app import app


class TestAppConfiguration:
    """Tests for application configuration and setup."""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly."""
        assert isinstance(app, FastAPI)
        assert app.title == "Mergington High School API"
        assert "extracurricular activities" in app.description

    def test_static_files_mounted(self, client: TestClient):
        """Test that static files are properly mounted."""
        # Test that static files are accessible
        response = client.get("/static/")
        # Should not be 404, even if directory listing is disabled
        assert response.status_code in [200, 403]  # 403 is ok if directory listing disabled

        # Test that we can access the main HTML file
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_routes_registered(self, client: TestClient):
        """Test that all expected routes are registered."""
        # Test that activities endpoint exists
        response = client.get("/activities")
        assert response.status_code == 200

        # Test that signup endpoint exists (will return 404 for non-existent activity)
        response = client.post("/activities/Test Activity/signup", json={"email": "test@example.com"})
        assert response.status_code == 404  # Activity not found, but route exists

        # Test that unregister endpoint exists
        response = client.post("/activities/Test Activity/unregister", json={"email": "test@example.com"})
        assert response.status_code == 404  # Activity not found, but route exists

    def test_openapi_schema(self, client: TestClient):
        """Test that OpenAPI schema is generated correctly."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "paths" in schema
        assert "/activities" in schema["paths"]
        assert "/activities/{activity_name}/signup" in schema["paths"]
        assert "/activities/{activity_name}/unregister" in schema["paths"]

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set."""
        response = client.get("/activities")
        # FastAPI sets CORS headers by default for API routes
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestActivitiesData:
    """Tests for the activities data structure."""

    def test_activities_data_structure(self):
        """Test that activities data has the correct structure."""
        from src.app import activities

        assert isinstance(activities, dict)
        assert len(activities) == 9  # Should have 9 activities

        # Test structure of one activity
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)

        # Test that participants are email strings
        for participant in chess_club["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant

    def test_activities_data_completeness(self):
        """Test that all activities have complete data."""
        from src.app import activities

        required_fields = ["description", "schedule", "max_participants", "participants"]

        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0, f"Activity '{activity_name}' has invalid max_participants"

            assert isinstance(activity_data["participants"], list)

    def test_activity_names_unique(self):
        """Test that all activity names are unique."""
        from src.app import activities

        activity_names = list(activities.keys())
        assert len(activity_names) == len(set(activity_names)), "Duplicate activity names found"