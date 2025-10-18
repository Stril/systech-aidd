"""Unit tests for ChatHandler"""

from unittest.mock import AsyncMock, Mock

import pytest

from api.chat_handler import ChatHandler
from api.chat_models import ChatResponse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_normal_mode() -> None:
    """Test handling message in normal mode"""
    # Setup mocks
    mock_openai = Mock()
    mock_openai.send_message = AsyncMock(return_value="Hello! How can I help you?")

    mock_text2sql = Mock()

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.get_session_context.return_value = [{"role": "user", "content": "Hi"}]
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    response = await handler.handle_message(session_id="test-session", message="Hi", mode="normal")

    # Verify response
    assert isinstance(response, ChatResponse)
    assert response.content == "Hello! How can I help you?"
    assert response.sql_query is None

    # Verify calls
    mock_session_manager.session_exists.assert_called_once_with("test-session")
    assert mock_session_manager.add_message.call_count == 2  # user + assistant
    mock_openai.send_message.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_admin_mode() -> None:
    """Test handling message in admin mode"""
    # Setup mocks
    mock_openai = Mock()

    mock_text2sql = Mock()
    mock_text2sql.process_question = AsyncMock(
        return_value=("SELECT COUNT(*) FROM users", "There are 100 users")
    )

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    response = await handler.handle_message(
        session_id="test-session", message="How many users?", mode="admin"
    )

    # Verify response
    assert isinstance(response, ChatResponse)
    assert response.content == "There are 100 users"
    assert response.sql_query == "SELECT COUNT(*) FROM users"

    # Verify calls
    mock_text2sql.process_question.assert_called_once_with("How many users?")
    assert mock_session_manager.add_message.call_count == 2  # user + assistant


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_session_not_found() -> None:
    """Test handling message with non-existent session"""
    # Setup mocks
    mock_openai = Mock()
    mock_text2sql = Mock()
    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = False

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Should raise KeyError
    with pytest.raises(KeyError, match="Session not found"):
        await handler.handle_message(session_id="non-existent", message="Test", mode="normal")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_openai_error() -> None:
    """Test handling message when OpenAI fails"""
    # Setup mocks
    mock_openai = Mock()
    mock_openai.send_message = AsyncMock(side_effect=Exception("API Error"))

    mock_text2sql = Mock()

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.get_session_context.return_value = []
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Should propagate exception
    with pytest.raises(Exception, match="API Error"):
        await handler.handle_message(session_id="test-session", message="Test", mode="normal")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_text2sql_error() -> None:
    """Test handling message when text2sql fails in admin mode"""
    # Setup mocks
    mock_openai = Mock()

    mock_text2sql = Mock()
    mock_text2sql.process_question = AsyncMock(return_value=("", "Error processing query"))

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    response = await handler.handle_message(
        session_id="test-session", message="Invalid query", mode="admin"
    )

    # Should still return response with error message
    assert response.content == "Error processing query"
    assert response.sql_query is None  # Empty SQL becomes None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_saves_user_message_to_storage() -> None:
    """Test that user messages are saved to storage"""
    # Setup mocks
    mock_openai = Mock()
    mock_openai.send_message = AsyncMock(return_value="Response")

    mock_text2sql = Mock()

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.get_session_context.return_value = []
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="Test prompt",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    await handler.handle_message(session_id="test-session", message="Test message", mode="normal")

    # Verify storage was called
    mock_storage.add_message_to_conversation.assert_called_once()
    call_args = mock_storage.add_message_to_conversation.call_args
    user_id = call_args[0][0]
    message = call_args[0][1]

    assert user_id == -12345
    assert message.role == "user"
    assert message.content == "Test message"
    assert message.content_length == len("Test message")
    assert message.user_id == -12345


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_saves_user_message_admin_mode() -> None:
    """Test that user messages are saved to storage in admin mode"""
    # Setup mocks
    mock_openai = Mock()

    mock_text2sql = Mock()
    mock_text2sql.process_question = AsyncMock(return_value=("SELECT 1", "Result"))

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_99999", -99999)
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="Test prompt",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    await handler.handle_message(session_id="test-session", message="How many users?", mode="admin")

    # Verify storage was called
    mock_storage.add_message_to_conversation.assert_called_once()
    call_args = mock_storage.add_message_to_conversation.call_args
    user_id = call_args[0][0]
    message = call_args[0][1]

    assert user_id == -99999
    assert message.role == "user"
    assert message.content == "How many users?"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_does_not_save_assistant_message() -> None:
    """Test that assistant responses are NOT saved to storage"""
    # Setup mocks
    mock_openai = Mock()
    mock_openai.send_message = AsyncMock(return_value="Assistant response")

    mock_text2sql = Mock()

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock()

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.get_session_context.return_value = []
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="Test prompt",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Handle message
    await handler.handle_message(session_id="test-session", message="Hello", mode="normal")

    # Verify storage was called ONLY once (for user message, not assistant)
    assert mock_storage.add_message_to_conversation.call_count == 1

    # Verify the saved message is user's, not assistant's
    call_args = mock_storage.add_message_to_conversation.call_args
    message = call_args[0][1]
    assert message.role == "user"
    assert message.content == "Hello"
    assert message.content != "Assistant response"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_message_storage_error_propagates() -> None:
    """Test that storage errors are propagated"""
    # Setup mocks
    mock_openai = Mock()

    mock_text2sql = Mock()

    mock_storage = Mock()
    mock_storage.add_message_to_conversation = AsyncMock(side_effect=Exception("DB Error"))

    mock_session_manager = Mock()
    mock_session_manager.session_exists.return_value = True
    mock_session_manager.get_session_user.return_value = ("User_12345", -12345)
    mock_session_manager.add_message = Mock()
    mock_session_manager.get_storage.return_value = mock_storage

    # Create handler
    handler = ChatHandler(
        openai_client=mock_openai,
        system_prompt="Test prompt",
        text2sql_handler=mock_text2sql,
        session_manager=mock_session_manager,
    )

    # Should propagate storage exception
    with pytest.raises(Exception, match="DB Error"):
        await handler.handle_message(session_id="test-session", message="Test", mode="normal")
