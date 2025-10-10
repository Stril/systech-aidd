"""Tests for MessageHandler class"""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from src.message_handler import MessageHandler
from src.openai_client import OpenAIClient
from src.context_manager import ContextManager


@pytest.fixture
def mock_openai_client():
    """Fixture for mock OpenAI client"""
    client = Mock(spec=OpenAIClient)
    client.send_message = Mock(return_value="Test response from LLM")
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
def message_handler(mock_openai_client, mock_context_manager):
    """Fixture for MessageHandler instance"""
    return MessageHandler(
        openai_client=mock_openai_client,
        system_prompt="Test system prompt",
        context_manager=mock_context_manager
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


async def test_handle_start_without_user(message_handler):
    """Test /start command handler when user is None"""
    message = AsyncMock()
    message.from_user = None
    message.answer = AsyncMock()
    
    # Should not raise exception
    await message_handler.handle_start(message)
    
    # Should still send response
    message.answer.assert_called_once()


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


async def test_handle_text_message_success(message_handler, mock_openai_client, mock_context_manager):
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


async def test_handle_text_message_llm_error(message_handler, mock_openai_client, mock_context_manager):
    """Test text message handling when LLM fails"""
    # Make LLM raise exception
    mock_openai_client.send_message = Mock(side_effect=Exception("LLM Error"))
    
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


async def test_handle_text_message_empty_text(message_handler, mock_openai_client, mock_context_manager):
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


async def test_handle_text_message_without_context_manager(mock_openai_client):
    """Test text message handling without context manager (fallback mode)"""
    handler = MessageHandler(
        openai_client=mock_openai_client,
        system_prompt="Test",
        context_manager=None
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

