"""Unit tests for ChatSessionManager"""

import pytest

from api.chat_session_manager import ChatSessionManager


@pytest.mark.unit
def test_create_session() -> None:
    """Test creating a new chat session"""
    manager = ChatSessionManager(max_context_messages=5)

    # Create session
    session_id = manager.create_session(mode="normal")

    # Verify session exists
    assert manager.session_exists(session_id)
    assert manager.get_session_mode(session_id) == "normal"


@pytest.mark.unit
def test_session_context() -> None:
    """Test adding and retrieving session context"""
    manager = ChatSessionManager(max_context_messages=5)
    session_id = manager.create_session(mode="normal")

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
    manager = ChatSessionManager(max_context_messages=5)
    session_id = manager.create_session(mode="normal")

    # Add some messages
    manager.add_message(session_id, "user", "Test message")

    # Clear session
    manager.clear_session(session_id)

    # Verify session no longer exists
    assert not manager.session_exists(session_id)


@pytest.mark.unit
def test_session_not_found() -> None:
    """Test accessing non-existent session raises error"""
    manager = ChatSessionManager(max_context_messages=5)

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
    manager = ChatSessionManager(max_context_messages=3)
    session_id = manager.create_session(mode="normal")

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
    manager = ChatSessionManager(max_context_messages=5)

    # Create multiple sessions
    session1 = manager.create_session(mode="normal")
    session2 = manager.create_session(mode="admin")

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
