"""
Integration tests for the FastAPI application.

This module contains integration tests that test the full application flow,
including multiple operations and state consistency.
"""

import pytest
from fastapi.testclient import TestClient


class TestActivityWorkflow:
    """Integration tests for complete activity signup/unregister workflows."""

    def test_complete_signup_unregister_workflow(self, client: TestClient):
        """Test a complete workflow: signup -> verify -> unregister -> verify."""
        activity_name = "Gym Class"
        email = "workflow_test@example.com"

        # Initial state - get activities
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()

        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )
        assert signup_response.status_code == 200

        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == len(initial_participants) + 1

        # Try to sign up again - should fail
        duplicate_response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )
        assert duplicate_response.status_code == 400

        # Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            json={"email": email}
        )
        assert unregister_response.status_code == 200

        # Verify unregistration
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == len(initial_participants)

        # Try to unregister again - should fail
        duplicate_unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            json={"email": email}
        )
        assert duplicate_unregister_response.status_code == 400

    def test_multiple_students_signup_workflow(self, client: TestClient):
        """Test multiple students signing up for the same activity."""
        activity_name = "Basketball Team"
        emails = ["student1@example.com", "student2@example.com", "student3@example.com"]

        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])

        # Sign up multiple students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                json={"email": email}
            )
            assert response.status_code == 200

        # Verify all are signed up
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert len(participants) == initial_count + len(emails)

        for email in emails:
            assert email in participants

        # Unregister one student
        email_to_remove = emails[0]
        response = client.post(
            f"/activities/{activity_name}/unregister",
            json={"email": email_to_remove}
        )
        assert response.status_code == 200

        # Verify removal
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert len(participants) == initial_count + len(emails) - 1
        assert email_to_remove not in participants

        # Other students should still be registered
        for email in emails[1:]:
            assert email in participants


class TestDataConsistency:
    """Tests to ensure data consistency across operations."""

    def test_participant_count_accuracy(self, client: TestClient):
        """Test that participant counts are always accurate after operations."""
        activity_name = "Tennis Club"

        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Add several participants
        emails = [f"user{i}@example.com" for i in range(3)]
        for email in emails:
            client.post(f"/activities/{activity_name}/signup", json={"email": email})

        # Check count
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == initial_count + 3

        # Remove one
        client.post(f"/activities/{activity_name}/unregister", json={"email": emails[0]})

        # Check count again
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == initial_count + 2

        # Verify remaining participants
        remaining_emails = emails[1:]
        for email in remaining_emails:
            assert email in data[activity_name]["participants"]

    def test_activities_data_integrity(self, client: TestClient):
        """Test that activity data structure remains intact after operations."""
        # Get initial data
        response = client.get("/activities")
        initial_data = response.json()

        # Perform some operations
        client.post("/activities/Chess Club/signup", json={"email": "integrity@example.com"})
        client.post("/activities/Chess Club/unregister", json={"email": "integrity@example.com"})

        # Get data again
        response = client.get("/activities")
        final_data = response.json()

        # Structure should be identical except for participants
        for activity_name in initial_data:
            assert activity_name in final_data
            initial_activity = initial_data[activity_name]
            final_activity = final_data[activity_name]

            # These fields should never change
            assert initial_activity["description"] == final_activity["description"]
            assert initial_activity["schedule"] == final_activity["schedule"]
            assert initial_activity["max_participants"] == final_activity["max_participants"]

            # Participants list should be a list
            assert isinstance(final_activity["participants"], list)