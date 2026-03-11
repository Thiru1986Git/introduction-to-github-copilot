"""
Test the data models and validation for the FastAPI application.

This module contains tests for data validation, models, and type checking.
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient


class TestRequestValidation:
    """Tests for request data validation."""

    def test_signup_request_validation(self, client: TestClient):
        """Test validation of signup request data."""
        activity_name = "Chess Club"

        # Valid request
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": "valid@example.com"}
        )
        assert response.status_code == 200

        # Missing email field
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={}
        )
        assert response.status_code == 422

        # Extra fields (should be ignored)
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": "extra@example.com", "extra_field": "ignored"}
        )
        assert response.status_code == 200

    def test_unregister_request_validation(self, client: TestClient):
        """Test validation of unregister request data."""
        activity_name = "Programming Class"

        # Valid request (even if not registered)
        response = client.post(
            f"/activities/{activity_name}/unregister",
            json={"email": "valid@example.com"}
        )
        assert response.status_code == 400  # Not registered, but valid request

        # Missing email field
        response = client.post(
            f"/activities/{activity_name}/unregister",
            json={}
        )
        assert response.status_code == 422

    def test_email_field_type_validation(self, client: TestClient):
        """Test that email field accepts strings only."""
        activity_name = "Gym Class"

        # String email - should work
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": "string@example.com"}
        )
        assert response.status_code == 200

        # Non-string email - should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": 12345}
        )
        assert response.status_code == 422

        # Null email - should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": None}
        )
        assert response.status_code == 422


class TestResponseValidation:
    """Tests for response data validation."""

    def test_activities_response_structure(self, client: TestClient):
        """Test that /activities response has correct structure."""
        response = client.get("/activities")
        data = response.json()

        assert isinstance(data, dict)

        # Check each activity
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)

            # Required fields
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

            # Field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

            # Participants should be list of strings
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)

    def test_signup_response_structure(self, client: TestClient):
        """Test that signup response has correct structure."""
        activity_name = "Basketball Team"
        email = "response_test@example.com"

        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_error_response_structure(self, client: TestClient):
        """Test that error responses have correct structure."""
        # Test 404 error
        response = client.post(
            "/activities/NonExistent/signup",
            json={"email": "test@example.com"}
        )

        assert response.status_code == 404
        data = response.json()

        assert isinstance(data, dict)
        assert "detail" in data
        assert isinstance(data["detail"], str)

        # Test 400 error
        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": "michael@mergington.edu"}  # Already registered
        )

        assert response.status_code == 400
        data = response.json()

        assert isinstance(data, dict)
        assert "detail" in data
        assert isinstance(data["detail"], str)


class TestDataTypeConsistency:
    """Tests for data type consistency across operations."""

    def test_participants_always_list_of_strings(self, client: TestClient):
        """Test that participants field is always a list of strings."""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()

        for activity_name, activity_data in initial_data.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)

        # Perform operations
        client.post("/activities/Art Studio/signup", json={"email": "type_test@example.com"})
        client.post("/activities/Art Studio/unregister", json={"email": "type_test@example.com"})

        # Check again
        response = client.get("/activities")
        final_data = response.json()

        for activity_name, activity_data in final_data.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)

    def test_max_participants_always_integer(self, client: TestClient):
        """Test that max_participants is always an integer."""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_activity_data_immutable_fields(self, client: TestClient):
        """Test that certain activity fields don't change during operations."""
        # Get initial data
        response = client.get("/activities")
        initial_data = response.json()

        # Perform operations
        client.post("/activities/Chess Club/signup", json={"email": "immutable_test@example.com"})
        client.post("/activities/Chess Club/unregister", json={"email": "immutable_test@example.com"})

        # Get final data
        response = client.get("/activities")
        final_data = response.json()

        # Immutable fields should be identical
        for activity_name in initial_data:
            assert initial_data[activity_name]["description"] == final_data[activity_name]["description"]
            assert initial_data[activity_name]["schedule"] == final_data[activity_name]["schedule"]
            assert initial_data[activity_name]["max_participants"] == final_data[activity_name]["max_participants"]