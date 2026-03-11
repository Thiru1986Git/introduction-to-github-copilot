"""
Test the test utilities and helper functions.

This module tests the utility functions in test_utils.py.
"""

import pytest
from tests.test_utils import (
    get_activity_participants,
    count_activity_participants,
    is_student_registered,
    get_all_activities,
    validate_email_format,
    generate_test_email
)


class TestActivityUtilities:
    """Tests for activity-related utility functions."""

    def test_get_activity_participants_existing_activity(self):
        """Test getting participants for an existing activity."""
        participants = get_activity_participants("Chess Club")
        assert isinstance(participants, list)
        assert "michael@mergington.edu" in participants
        assert "daniel@mergington.edu" in participants

    def test_get_activity_participants_nonexistent_activity(self):
        """Test getting participants for a non-existent activity."""
        with pytest.raises(ValueError, match="not found"):
            get_activity_participants("NonExistent Activity")

    def test_count_activity_participants(self):
        """Test counting participants in an activity."""
        count = count_activity_participants("Chess Club")
        assert count == 2  # michael and daniel

        # Test empty activity
        count = count_activity_participants("Art Studio")
        assert count == 0

    def test_is_student_registered(self):
        """Test checking if a student is registered."""
        # Test registered student
        assert is_student_registered("Chess Club", "michael@mergington.edu")

        # Test unregistered student
        assert not is_student_registered("Chess Club", "not_registered@example.com")

        # Test non-existent activity
        with pytest.raises(ValueError):
            is_student_registered("NonExistent", "test@example.com")

    def test_get_all_activities(self):
        """Test getting all activities data."""
        activities = get_all_activities()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities

        # Verify it's a copy, not the original
        original_count = len(activities["Chess Club"]["participants"])
        activities["Chess Club"]["participants"].append("test@example.com")
        assert len(get_all_activities()["Chess Club"]["participants"]) == original_count


class TestEmailUtilities:
    """Tests for email-related utility functions."""

    def test_validate_email_format_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@gmail.com"
        ]

        for email in valid_emails:
            assert validate_email_format(email)

    def test_validate_email_format_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@domain.com",
            "test@.com",
            "test..test@example.com"
        ]

        for email in invalid_emails:
            assert not validate_email_format(email)

    def test_generate_test_email(self):
        """Test generating test email addresses."""
        email = generate_test_email()
        assert "@" in email
        assert email.endswith("@example.com")
        assert "test_" in email

        # Test custom parameters
        email = generate_test_email("custom", "test.com")
        assert email.startswith("custom_")
        assert email.endswith("@test.com")

    def test_generate_test_email_uniqueness(self):
        """Test that generated emails are unique."""
        emails = [generate_test_email() for _ in range(10)]
        assert len(set(emails)) == len(emails)  # All unique