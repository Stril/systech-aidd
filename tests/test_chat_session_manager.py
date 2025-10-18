"""Unit tests for ChatSessionManager"""

from unittest.mock import Mock

import pytest

from api.chat_session_manager import ChatSessionManager


@pytest.mark.unit
def test_create_session() -> None:
    """Test creating a new chat session"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    # Create session
    session_id = manager.create_session(mode="normal", username="User_12345", user_id=-12345)

    # Verify session exists
    assert manager.session_exists(session_id)
    assert manager.get_session_mode(session_id) == "normal"

    # Verify user info
    username, user_id = manager.get_session_user(session_id)
    assert username == "User_12345"
    assert user_id == -12345


@pytest.mark.unit
def test_session_context() -> None:
    """Test adding and retrieving session context"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)
    session_id = manager.create_session(mode="normal", username="User_12345", user_id=-12345)

    # Initially empty
    context = manager.get_session_context(session_id)
    assert len(context) == 0

    # Add messages
    manager.add_message(session_id, "user", "Hello")
    manager.add_message(session_id, "assistant", "Hi there!")

    # Verify context
    context = manager.get_session_context(session_id)
    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Hi there!"


@pytest.mark.unit
def test_clear_session() -> None:
    """Test clearing a session"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)
    session_id = manager.create_session(mode="normal", username="User_12345", user_id=-12345)

    # Add some messages
    manager.add_message(session_id, "user", "Test message")

    # Clear session
    manager.clear_session(session_id)

    # Verify session no longer exists
    assert not manager.session_exists(session_id)


@pytest.mark.unit
def test_session_not_found() -> None:
    """Test accessing non-existent session raises error"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    # Should raise KeyError
    with pytest.raises(KeyError):
        manager.get_session_context("non-existent-id")

    with pytest.raises(KeyError):
        manager.add_message("non-existent-id", "user", "message")

    with pytest.raises(KeyError):
        manager.clear_session("non-existent-id")


@pytest.mark.unit
def test_context_trimming() -> None:
    """Test that context is trimmed to max_messages"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=3)
    session_id = manager.create_session(mode="normal", username="User_12345", user_id=-12345)

    # Add more messages than max
    for i in range(5):
        manager.add_message(session_id, "user", f"Message {i}")

    # Should only keep last 3
    context = manager.get_session_context(session_id)
    assert len(context) == 3
    assert context[0]["content"] == "Message 2"
    assert context[2]["content"] == "Message 4"


@pytest.mark.unit
def test_multiple_sessions() -> None:
    """Test managing multiple sessions simultaneously"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    # Create multiple sessions
    session1 = manager.create_session(mode="normal", username="User_12345", user_id=-12345)
    session2 = manager.create_session(mode="admin", username="User_67890", user_id=-67890)

    # Add messages to each
    manager.add_message(session1, "user", "Session 1 message")
    manager.add_message(session2, "user", "Session 2 message")

    # Verify isolation
    context1 = manager.get_session_context(session1)
    context2 = manager.get_session_context(session2)

    assert len(context1) == 1
    assert len(context2) == 1
    assert context1[0]["content"] == "Session 1 message"
    assert context2[0]["content"] == "Session 2 message"


@pytest.mark.unit
def test_get_session_user() -> None:
    """Test getting session user information"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)
    session_id = manager.create_session(mode="normal", username="User_54321", user_id=-54321)

    # Get user info
    username, user_id = manager.get_session_user(session_id)

    # Verify
    assert username == "User_54321"
    assert user_id == -54321


@pytest.mark.unit
def test_get_session_user_not_found() -> None:
    """Test get_session_user raises KeyError for non-existent session"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    with pytest.raises(KeyError, match="Session not found"):
        manager.get_session_user("non-existent-id")


@pytest.mark.unit
def test_get_storage() -> None:
    """Test getting storage instance from session manager"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    # Get storage
    storage = manager.get_storage()

    # Verify it's the same instance
    assert storage is mock_storage


@pytest.mark.unit
def test_create_session_initializes_conversation_id_as_none() -> None:
    """Test that new session has conversation_id initialized as None"""
    mock_storage = Mock()
    manager = ChatSessionManager(storage=mock_storage, max_context_messages=5)

    # Create session
    session_id = manager.create_session(mode="normal", username="User_12345", user_id=-12345)

    # Session should exist and have conversation_id as None
    assert manager.session_exists(session_id)

    # Access internal session data to verify conversation_id is None
    session_data = manager._sessions[session_id]
    assert session_data.conversation_id is None
