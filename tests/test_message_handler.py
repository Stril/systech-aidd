"""Tests for MessageHandler class"""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.context_manager import ContextManager
from src.exceptions import LLMAPIError, LLMConnectionError, LLMRateLimitError, LLMTimeoutError
from src.memory_storage import MemoryStorage
from src.message_handler import MessageHandler
from src.openai_client import OpenAIClient


@pytest.fixture
def mock_openai_client():
    """Fixture for mock OpenAI client"""
    client = Mock(spec=OpenAIClient)
    client.send_message = AsyncMock(return_value="Test response from LLM")
    return client


@pytest.fixture
def mock_context_manager():
    """Fixture for mock ContextManager"""
    context_mgr = Mock(spec=ContextManager)
    context_mgr.add_message = Mock()
    context_mgr.get_context = Mock(return_value=[{"role": "user", "content": "Test"}])
    context_mgr.reset_context = Mock()
    return context_mgr


@pytest.fixture
def mock_storage():
    """Fixture for mock MemoryStorage"""
    storage = Mock(spec=MemoryStorage)
    storage.user_exists = Mock(return_value=False)
    storage.add_user = Mock()
    storage.add_message_to_conversation = Mock()
    storage.increment_user_message_count = Mock()
    storage.clear_conversation = Mock()
    return storage


@pytest.fixture
def message_handler(mock_openai_client, mock_context_manager, mock_storage):
    """Fixture for MessageHandler instance"""
    return MessageHandler(
        openai_client=mock_openai_client,
        system_prompt="Test system prompt",
        context_manager=mock_context_manager,
        storage=mock_storage,
    )


@pytest.fixture
def mock_message():
    """Fixture for mock Telegram message"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.answer = AsyncMock()
    return message


@pytest.mark.unit
async def test_handle_start_command(message_handler, mock_message):
    """Test /start command handler"""
    await message_handler.handle_start(mock_message)

    # Check that answer was called
    mock_message.answer.assert_called_once()

    # Check that welcome text is in the response
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет" in call_args
    assert "LLM-бот помощник" in call_args
    assert "/help" in call_args


@pytest.mark.unit
async def test_handle_help_command(message_handler, mock_message):
    """Test /help command handler"""
    await message_handler.handle_help(mock_message)

    # Check that answer was called
    mock_message.answer.assert_called_once()

    # Check that help text contains commands
    call_args = mock_message.answer.call_args[0][0]
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/reset" in call_args
    assert "команды" in call_args


@pytest.mark.unit
async def test_handle_start_without_user(message_handler):
    """Test /start command handler when user is None"""
    message = AsyncMock()
    message.from_user = None
    message.answer = AsyncMock()

    # Should not raise exception
    await message_handler.handle_start(message)

    # Should still send response
    message.answer.assert_called_once()


@pytest.mark.unit
async def test_handle_help_without_username(message_handler):
    """Test /help command handler when username is None"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = None
    message.answer = AsyncMock()

    # Should not raise exception
    await message_handler.handle_help(message)

    # Should still send response
    message.answer.assert_called_once()


@pytest.mark.unit
async def test_handle_text_message_success(
    message_handler, mock_openai_client, mock_context_manager
):
    """Test successful text message handling"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello, bot!"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify typing action was sent
    message.bot.send_chat_action.assert_called_once()

    # Verify user message was added to context
    mock_context_manager.add_message.assert_any_call(12345, "user", "Hello, bot!")

    # Verify LLM was called
    mock_openai_client.send_message.assert_called_once()

    # Verify assistant response was added to context
    mock_context_manager.add_message.assert_any_call(12345, "assistant", "Test response from LLM")

    # Verify response was sent to user
    message.answer.assert_called_once_with("Test response from LLM")


@pytest.mark.unit
async def test_handle_text_message_without_openai_client():
    """Test text message handling without OpenAI client"""
    handler = MessageHandler(openai_client=None, system_prompt="", context_manager=None)

    message = AsyncMock()
    message.answer = AsyncMock()

    await handler.handle_text_message(message)

    # Should send error message
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "не настроен" in call_args


@pytest.mark.unit
async def test_handle_text_message_llm_error(
    message_handler, mock_openai_client, mock_context_manager
):
    """Test text message handling when LLM fails"""
    # Make LLM raise exception
    mock_openai_client.send_message = AsyncMock(side_effect=Exception("LLM Error"))

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify user message was added to context
    mock_context_manager.add_message.assert_called_once_with(12345, "user", "Hello")

    # Should send error message to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "ошибка" in call_args


@pytest.mark.unit
async def test_handle_text_message_empty_text(
    message_handler, mock_openai_client, mock_context_manager
):
    """Test handling message with empty text"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = ""
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify empty message was added to context
    mock_context_manager.add_message.assert_any_call(12345, "user", "")

    # Should still process (LLM will handle empty message)
    mock_openai_client.send_message.assert_called_once()


@pytest.mark.unit
async def test_handle_reset_command(message_handler, mock_context_manager):
    """Test /reset command handler"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.answer = AsyncMock()

    await message_handler.handle_reset(message)

    # Verify context was reset
    mock_context_manager.reset_context.assert_called_once_with(12345)

    # Verify confirmation message was sent
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "очищена" in call_args


@pytest.mark.unit
async def test_handle_reset_without_context_manager():
    """Test /reset command without context manager"""
    handler = MessageHandler(openai_client=None, system_prompt="", context_manager=None)

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.answer = AsyncMock()

    await handler.handle_reset(message)

    # Should send error message
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "не настроен" in call_args


@pytest.mark.unit
async def test_handle_text_message_without_context_manager(mock_openai_client):
    """Test text message handling without context manager (fallback mode)"""
    handler = MessageHandler(
        openai_client=mock_openai_client, system_prompt="Test", context_manager=None
    )

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await handler.handle_text_message(message)

    # Verify LLM was called with single message (no context)
    mock_openai_client.send_message.assert_called_once()
    call_args = mock_openai_client.send_message.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]["content"] == "Hello"

    # Verify response was sent
    message.answer.assert_called_once_with("Test response from LLM")


@pytest.mark.unit
async def test_handle_start_saves_user_to_storage(mock_storage):
    """Test that /start saves new user to storage"""
    handler = MessageHandler(
        openai_client=None, system_prompt="Test", context_manager=None, storage=mock_storage
    )

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.answer = AsyncMock()

    await handler.handle_start(message)

    # Verify storage was checked for user
    mock_storage.user_exists.assert_called_once_with(12345)

    # Verify user was added to storage
    mock_storage.add_user.assert_called_once()
    call_args = mock_storage.add_user.call_args[0][0]
    assert call_args.user_id == 12345
    assert call_args.username == "testuser"
    assert call_args.first_name == "Test"


@pytest.mark.unit
async def test_handle_text_message_saves_to_storage(
    message_handler, mock_openai_client, mock_context_manager, mock_storage
):
    """Test that text messages are saved to storage"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello bot"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify user message was saved to storage (2 calls: user + assistant)
    assert mock_storage.add_message_to_conversation.call_count == 2

    # Verify user message count was incremented
    mock_storage.increment_user_message_count.assert_called_once_with(12345)

    # Check first call (user message)
    first_call = mock_storage.add_message_to_conversation.call_args_list[0]
    assert first_call[0][0] == 12345  # user_id
    assert first_call[0][1].role == "user"
    assert first_call[0][1].content == "Hello bot"

    # Check second call (assistant message)
    second_call = mock_storage.add_message_to_conversation.call_args_list[1]
    assert second_call[0][0] == 12345  # user_id
    assert second_call[0][1].role == "assistant"
    assert second_call[0][1].content == "Test response from LLM"


@pytest.mark.unit
async def test_handle_reset_clears_storage(message_handler, mock_context_manager, mock_storage):
    """Test that /reset clears storage conversation"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.answer = AsyncMock()

    await message_handler.handle_reset(message)

    # Verify context manager was reset
    mock_context_manager.reset_context.assert_called_once_with(12345)

    # Verify storage conversation was cleared
    mock_storage.clear_conversation.assert_called_once_with(12345)


@pytest.mark.unit
async def test_handle_text_message_connection_error(
    message_handler, mock_openai_client, mock_storage
):
    """Test handling of connection errors"""
    mock_openai_client.send_message = AsyncMock(side_effect=LLMConnectionError("Connection failed"))

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify error message was sent to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "подключиться" in call_args.lower()


@pytest.mark.unit
async def test_handle_text_message_timeout_error(message_handler, mock_openai_client, mock_storage):
    """Test handling of timeout errors"""
    mock_openai_client.send_message = AsyncMock(side_effect=LLMTimeoutError("Timeout"))

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify error message was sent to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "время" in call_args.lower() or "таймаут" in call_args.lower()


@pytest.mark.unit
async def test_handle_text_message_rate_limit_error(
    message_handler, mock_openai_client, mock_storage
):
    """Test handling of rate limit errors"""
    mock_openai_client.send_message = AsyncMock(side_effect=LLMRateLimitError("Rate limit"))

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify error message was sent to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "лимит" in call_args.lower()


@pytest.mark.unit
async def test_handle_text_message_api_error(message_handler, mock_openai_client, mock_storage):
    """Test handling of API errors"""
    mock_openai_client.send_message = AsyncMock(side_effect=LLMAPIError("API error"))

    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.chat = MagicMock()
    message.chat.id = 67890
    message.bot = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    message.answer = AsyncMock()

    await message_handler.handle_text_message(message)

    # Verify error message was sent to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "ошибка" in call_args.lower()


@pytest.mark.unit
async def test_handle_role_command():
    """Test /role command shows current assistant role"""
    # Arrange
    system_prompt = "You are a helpful technical assistant specialized in Python."
    handler = MessageHandler(system_prompt=system_prompt)

    message = AsyncMock()
    message.from_user = Mock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.text = "/role"
    message.chat = Mock()
    message.chat.id = 456

    # Act
    await handler.handle_role(message)

    # Assert
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "роль" in call_args.lower()
    assert system_prompt in call_args


@pytest.mark.unit
async def test_handle_role_without_system_prompt():
    """Test /role command with empty system prompt"""
    # Arrange
    handler = MessageHandler(system_prompt="")

    message = AsyncMock()
    message.from_user = Mock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.text = "/role"
    message.chat = Mock()
    message.chat.id = 456

    # Act
    await handler.handle_role(message)

    # Assert
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "роль" in call_args.lower()
