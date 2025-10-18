"""Tests for MessageExtractor class"""

from unittest.mock import Mock

import pytest

from src.message_extractor import MessageContext, MessageExtractor


@pytest.mark.unit
def test_message_extractor_with_full_data():
    """Test extracting message with all data present"""
    # Arrange
    message = Mock()
    message.from_user = Mock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.from_user.language_code = "en"
    message.text = "Hello, bot!"
    message.chat = Mock()
    message.chat.id = 456

    # Act
    context = MessageExtractor.extract(message)

    # Assert
    assert isinstance(context, MessageContext)
    assert context.user_id == 123
    assert context.username == "testuser"
    assert context.first_name == "Test"
    assert context.last_name == "User"
    assert context.language_code == "en"
    assert context.text == "Hello, bot!"
    assert context.chat_id == 456


@pytest.mark.unit
def test_message_extractor_without_user():
    """Test extracting message without user data"""
    # Arrange
    message = Mock()
    message.from_user = None
    message.text = "Hello"
    message.chat = Mock()
    message.chat.id = 789

    # Act
    context = MessageExtractor.extract(message)

    # Assert
    assert context.user_id == 0
    assert context.username == "Unknown"
    assert context.first_name is None
    assert context.last_name is None
    assert context.language_code is None
    assert context.text == "Hello"
    assert context.chat_id == 789


@pytest.mark.unit
def test_message_extractor_without_username():
    """Test extracting message without username"""
    # Arrange
    message = Mock()
    message.from_user = Mock()
    message.from_user.id = 123
    message.from_user.username = None
    message.from_user.first_name = "Test"
    message.from_user.last_name = None
    message.from_user.language_code = "ru"
    message.text = "Hi"
    message.chat = Mock()
    message.chat.id = 456

    # Act
    context = MessageExtractor.extract(message)

    # Assert
    assert context.user_id == 123
    assert context.username == "Unknown"
    assert context.first_name == "Test"
    assert context.last_name is None
    assert context.language_code == "ru"
    assert context.text == "Hi"


@pytest.mark.unit
def test_message_extractor_empty_text():
    """Test extracting message with empty text"""
    # Arrange
    message = Mock()
    message.from_user = Mock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.from_user.language_code = "en"
    message.text = None
    message.chat = Mock()
    message.chat.id = 456

    # Act
    context = MessageExtractor.extract(message)

    # Assert
    assert context.text == ""


@pytest.mark.unit
def test_message_context_repr():
    """Test MessageContext string representation"""
    # Arrange
    context = MessageContext(
        user_id=123,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        text="Hello",
        chat_id=456,
    )

    # Act
    repr_string = repr(context)

    # Assert
    assert "MessageContext" in repr_string
    assert "user_id=123" in repr_string
    assert "username=testuser" in repr_string
