"""
Test utilities and helper functions.

This module contains utility functions and classes that support testing.
"""

from typing import Dict, List, Any
from src.app import activities


def get_activity_participants(activity_name: str) -> List[str]:
    """Get the list of participants for a given activity."""
    if activity_name not in activities:
        raise ValueError(f"Activity '{activity_name}' not found")
    return activities[activity_name]["participants"].copy()


def count_activity_participants(activity_name: str) -> int:
    """Get the number of participants for a given activity."""
    return len(get_activity_participants(activity_name))


def is_student_registered(activity_name: str, email: str) -> bool:
    """Check if a student is registered for a specific activity."""
    participants = get_activity_participants(activity_name)
    return email in participants


def get_all_activities() -> Dict[str, Any]:
    """Get a copy of all activities data."""
    return activities.copy()


def reset_activities_data():
    """Reset activities to their initial state (for testing)."""
    # This would need to be implemented if we want to reset to original state
    # For now, the conftest.py fixture handles this
    pass


def validate_email_format(email: str) -> bool:
    """Basic email validation function."""
    return "@" in email and "." in email and len(email) > 5


def generate_test_email(prefix: str = "test", domain: str = "example.com") -> str:
    """Generate a test email address."""
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{prefix}_{random_suffix}@{domain}"