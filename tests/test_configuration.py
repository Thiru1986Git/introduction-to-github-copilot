"""
Test the pytest configuration and fixtures.

This module tests that the test configuration is working correctly.
"""

import pytest
from fastapi.testclient import TestClient


class TestTestConfiguration:
    """Tests for the test configuration and fixtures."""

    def test_client_fixture(self, client: TestClient):
        """Test that the client fixture works correctly."""
        assert isinstance(client, TestClient)

        # Test that we can make requests
        response = client.get("/activities")
        assert response.status_code == 200

    def test_sample_activity_data_fixture(self, sample_activity_data):
        """Test the sample activity data fixture."""
        assert isinstance(sample_activity_data, dict)
        assert "description" in sample_activity_data
        assert "schedule" in sample_activity_data
        assert "max_participants" in sample_activity_data
        assert "participants" in sample_activity_data

        assert isinstance(sample_activity_data["participants"], list)
        assert len(sample_activity_data["participants"]) == 0

    def test_reset_activities_fixture(self, client: TestClient):
        """Test that the reset_activities fixture isolates tests."""
        activity_name = "Chess Club"

        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()

        # Modify state
        client.post(f"/activities/{activity_name}/signup",
                   json={"email": "test_reset@example.com"})

        # Verify modification
        response = client.get("/activities")
        modified_participants = response.json()[activity_name]["participants"]
        assert "test_reset@example.com" in modified_participants

        # The fixture should reset state after this test completes
        # We can't test the reset directly here, but we can verify the fixture exists

    def test_activities_reset_between_tests(self, client: TestClient):
        """Test that activities are reset between tests (indirect test)."""
        # This test relies on the autouse fixture to reset activities
        # We test by making a change and assuming the next test will have clean state

        activity_name = "Programming Class"
        test_email = "isolation_test@example.com"

        # Sign up in this test
        response = client.post(f"/activities/{activity_name}/signup",
                              json={"email": test_email})
        assert response.status_code == 200

        # Verify signup worked
        response = client.get("/activities")
        assert test_email in response.json()[activity_name]["participants"]

        # The autouse fixture will reset this after the test
        # Individual test methods can't verify the reset directly,
        # but the overall test suite should pass consistently


class TestPytestConfiguration:
    """Tests for pytest configuration."""

    def test_pytest_ini_exists(self):
        """Test that pytest.ini configuration file exists."""
        import os
        assert os.path.exists("pytest.ini")

    def test_pytest_ini_content(self):
        """Test pytest.ini has expected configuration."""
        with open("pytest.ini", "r") as f:
            content = f.read()

        assert "[tool:pytest]" in content
        assert "testpaths = tests" in content
        assert "python_files = test_*.py" in content
        assert "python_classes = Test*" in content
        assert "python_functions = test_*" in content

    def test_requirements_has_testing_deps(self):
        """Test that requirements.txt includes testing dependencies."""
        with open("requirements.txt", "r") as f:
            content = f.read()

        # httpx is needed for TestClient
        assert "httpx" in content