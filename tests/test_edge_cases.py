"""
Test edge cases and error conditions for the FastAPI application.

This module contains tests for edge cases, error handling, and boundary conditions.
"""

import pytest
from fastapi.testclient import TestClient


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_signup_with_special_characters_email(self, client: TestClient):
        """Test signup with email containing special characters."""
        activity_name = "Gym Class"
        email = "test.user+tag@example-domain.com"

        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )

        assert response.status_code == 200

        # Verify signup worked
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]

    def test_signup_with_long_email(self, client: TestClient):
        """Test signup with a very long email address."""
        activity_name = "Basketball Team"
        email = "a" * 200 + "@example.com"  # Very long local part

        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )

        assert response.status_code == 200

    def test_activity_name_with_spaces_and_special_chars(self, client: TestClient):
        """Test operations with activity names containing spaces and special characters."""
        # Note: URL encoding should handle spaces
        activity_name = "Tennis Club"  # Has space
        email = "spaces_test@example.com"

        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": email}
        )

        assert response.status_code == 200

    def test_multiple_operations_same_activity(self, client: TestClient):
        """Test multiple signup/unregister operations on the same activity."""
        activity_name = "Programming Class"
        emails = ["multi1@example.com", "multi2@example.com", "multi3@example.com"]

        # Sign up all
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup", json={"email": email})
            assert response.status_code == 200

        # Check all are registered
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        for email in emails:
            assert email in participants

        # Unregister first two
        for email in emails[:2]:
            response = client.post(f"/activities/{activity_name}/unregister", json={"email": email})
            assert response.status_code == 200

        # Check state
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert emails[0] not in participants
        assert emails[1] not in participants
        assert emails[2] in participants

    def test_case_sensitivity_activity_names(self, client: TestClient):
        """Test case sensitivity in activity names."""
        # Activity names are case-sensitive in URLs
        email = "case_test@example.com"

        # Try with different case
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            json={"email": email}
        )
        assert response.status_code == 404  # Should not find "chess club"

        # Correct case should work
        response = client.post(
            "/activities/Chess Club/signup",  # Correct case
            json={"email": email}
        )
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling and validation."""

    def test_malformed_json_requests(self, client: TestClient):
        """Test handling of malformed JSON in requests."""
        # Test with invalid JSON
        response = client.post(
            "/activities/Chess Club/signup",
            data="{invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

        # Test with wrong content type
        response = client.post(
            "/activities/Chess Club/signup",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422

    def test_empty_request_body(self, client: TestClient):
        """Test handling of empty request bodies."""
        response = client.post(
            "/activities/Chess Club/signup",
            json={}
        )
        assert response.status_code == 422

    def test_large_request_body(self, client: TestClient):
        """Test handling of very large request bodies."""
        large_email = "a" * 10000 + "@example.com"

        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": large_email}
        )
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 422]

    def test_concurrent_operations_simulation(self, client: TestClient):
        """Test simulating concurrent operations (basic version)."""
        activity_name = "Art Studio"
        email1 = "concurrent1@example.com"
        email2 = "concurrent2@example.com"

        # Both sign up
        resp1 = client.post(f"/activities/{activity_name}/signup", json={"email": email1})
        resp2 = client.post(f"/activities/{activity_name}/signup", json={"email": email2})

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # Both should be registered
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_sql_injection_like_attempts(self, client: TestClient):
        """Test that the API is not vulnerable to injection-like attacks."""
        # Since this is an in-memory dict, injection isn't really possible
        # But we can test with malicious-looking input
        malicious_email = "'; DROP TABLE users; --"

        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": malicious_email}
        )

        # Should either succeed (treating it as a string) or fail validation
        assert response.status_code in [200, 422]


class TestDataConsistencyEdgeCases:
    """Tests for data consistency in edge cases."""

    def test_rapid_signup_unregister_cycles(self, client: TestClient):
        """Test rapid signup/unregister cycles."""
        activity_name = "Music Band"
        email = "cycle_test@example.com"

        # Perform multiple cycles
        for _ in range(5):
            # Sign up
            response = client.post(f"/activities/{activity_name}/signup", json={"email": email})
            assert response.status_code == 200

            # Unregister
            response = client.post(f"/activities/{activity_name}/unregister", json={"email": email})
            assert response.status_code == 200

    def test_max_participants_boundary(self, client: TestClient):
        """Test behavior near max participants limit."""
        activity_name = "Chess Club"  # max_participants = 12, currently has 2

        # Fill up to max
        emails = [f"fill_{i}@example.com" for i in range(10)]  # Add 10 more

        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup", json={"email": email})
            assert response.status_code == 200

        # Check final count
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert len(participants) == 12  # Should be at max

        # Note: Current implementation doesn't prevent over-subscription
        # This test documents current behavior, not ideal behavior

    def test_empty_email_edge_cases(self, client: TestClient):
        """Test edge cases with empty or whitespace emails."""
        activity_name = "Tennis Club"

        # Empty string
        response = client.post(f"/activities/{activity_name}/signup", json={"email": ""})
        assert response.status_code == 200  # Currently accepts empty emails

        # Whitespace only
        response = client.post(f"/activities/{activity_name}/signup", json={"email": "   "})
        assert response.status_code == 200  # Currently accepts whitespace emails

        # Note: These tests document current behavior
        # In a real application, we'd want validation to reject these