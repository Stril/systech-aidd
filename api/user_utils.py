"""Utilities for web chat user management"""

import re


def parse_username_to_user_id(username: str) -> int:
    """Extract user_id from username like 'User_12345'

    Args:
        username: Username in format 'User_NNNNN'

    Returns:
        Negative integer like -12345

    Raises:
        ValueError: If username format is invalid
    """
    if not validate_username(username):
        raise ValueError(f"Invalid username format: {username}")

    # Extract number and make negative
    number = int(username.split("_")[1])
    return -number


def validate_username(username: str) -> bool:
    """Validate username format (User_NNNNN)

    Args:
        username: Username to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^User_\d{5}$"
    return bool(re.match(pattern, username))

