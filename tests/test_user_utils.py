"""Tests for user utilities"""

import pytest

from api.user_utils import parse_username_to_user_id, validate_username


@pytest.mark.unit
class TestValidateUsername:
    """Tests for validate_username function"""

    def test_valid_username(self) -> None:
        """Test validation of valid usernames"""
        assert validate_username("User_12345") is True
        assert validate_username("User_00001") is True
        assert validate_username("User_99999") is True

    def test_invalid_username_format(self) -> None:
        """Test validation of invalid username formats"""
        assert validate_username("InvalidFormat") is False
        assert validate_username("User_123") is False  # Too few digits
        assert validate_username("User_1234567") is False  # Too many digits
        assert validate_username("user_12345") is False  # Lowercase
        assert validate_username("USER_12345") is False  # Uppercase
        assert validate_username("User12345") is False  # Missing underscore
        assert validate_username("User_abcde") is False  # Letters instead of digits

    def test_empty_username(self) -> None:
        """Test validation of empty username"""
        assert validate_username("") is False


@pytest.mark.unit
class TestParseUsernameToUserId:
    """Tests for parse_username_to_user_id function"""

    def test_parse_valid_username(self) -> None:
        """Test parsing valid usernames to user_id"""
        assert parse_username_to_user_id("User_12345") == -12345
        assert parse_username_to_user_id("User_00001") == -1
        assert parse_username_to_user_id("User_99999") == -99999
        assert parse_username_to_user_id("User_54321") == -54321

    def test_parse_invalid_username_raises_error(self) -> None:
        """Test that invalid usernames raise ValueError"""
        with pytest.raises(ValueError, match="Invalid username format"):
            parse_username_to_user_id("InvalidFormat")

        with pytest.raises(ValueError, match="Invalid username format"):
            parse_username_to_user_id("User_123")

        with pytest.raises(ValueError, match="Invalid username format"):
            parse_username_to_user_id("user_12345")

    def test_parse_empty_username(self) -> None:
        """Test parsing empty username raises ValueError"""
        with pytest.raises(ValueError, match="Invalid username format"):
            parse_username_to_user_id("")

    def test_result_is_always_negative(self) -> None:
        """Test that result is always negative"""
        result = parse_username_to_user_id("User_12345")
        assert result < 0
