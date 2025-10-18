"""Unit tests for TelegramBot class"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.message_handler import MessageHandler
from src.telegram_bot import TelegramBot


@pytest.fixture
def mock_message_handler():
    """Fixture for mock MessageHandler"""
    handler = Mock(spec=MessageHandler)
    handler.handle_start = AsyncMock()
    handler.handle_help = AsyncMock()
    handler.handle_reset = AsyncMock()
    handler.handle_profile = AsyncMock()
    handler.handle_text_message = AsyncMock()
    return handler


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_telegram_bot_initialization(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test TelegramBot initializes correctly"""
    # Create bot instance
    bot = TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Verify Bot was created with correct token
    mock_bot_cls.assert_called_once_with(token="test_token")

    # Verify Dispatcher was created
    mock_dispatcher_cls.assert_called_once()

    # Verify internal attributes are set
    assert bot._message_handler == mock_message_handler
    assert bot._bot is not None
    assert bot._dp is not None


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_handlers_called_on_init(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test that _register_handlers is called during initialization"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    # Create bot - should automatically register handlers
    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Verify message.register was called 6 times (start, help, role, reset, profile, text)
    assert mock_dp.message.register.call_count == 6


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_start_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test /start command handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get first register call (should be /start)
    first_call = mock_dp.message.register.call_args_list[0]
    assert first_call[0][0] == mock_message_handler.handle_start


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_help_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test /help command handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get second register call (should be /help)
    second_call = mock_dp.message.register.call_args_list[1]
    assert second_call[0][0] == mock_message_handler.handle_help


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_role_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test /role command handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get third register call (should be /role)
    third_call = mock_dp.message.register.call_args_list[2]
    assert third_call[0][0] == mock_message_handler.handle_role


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_reset_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test /reset command handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get fourth register call (should be /reset)
    fourth_call = mock_dp.message.register.call_args_list[3]
    assert fourth_call[0][0] == mock_message_handler.handle_reset


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_profile_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test /profile command handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get fifth register call (should be /profile)
    fifth_call = mock_dp.message.register.call_args_list[4]
    assert fifth_call[0][0] == mock_message_handler.handle_profile


@pytest.mark.unit
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
def test_register_text_handler(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test text message handler registration"""
    mock_dp = MagicMock()
    mock_dispatcher_cls.return_value = mock_dp

    TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Get sixth register call (should be text messages)
    sixth_call = mock_dp.message.register.call_args_list[5]
    assert sixth_call[0][0] == mock_message_handler.handle_text_message


@pytest.mark.unit
@pytest.mark.asyncio
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
async def test_start_polling_success(mock_dispatcher_cls, mock_bot_cls, mock_message_handler):
    """Test bot starts polling successfully"""
    mock_bot = MagicMock()
    mock_bot.delete_webhook = AsyncMock()
    mock_bot.session.close = AsyncMock()
    mock_bot_cls.return_value = mock_bot

    mock_dp = MagicMock()
    mock_dp.start_polling = AsyncMock()
    mock_dispatcher_cls.return_value = mock_dp

    bot = TelegramBot(token="test_token", message_handler=mock_message_handler)

    await bot.start()

    # Verify webhook was deleted
    mock_bot.delete_webhook.assert_called_once_with(drop_pending_updates=True)

    # Verify polling started
    mock_dp.start_polling.assert_called_once_with(mock_bot)

    # Verify session was closed
    mock_bot.session.close.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
async def test_start_polling_error_closes_session(
    mock_dispatcher_cls, mock_bot_cls, mock_message_handler
):
    """Test that session is closed even when polling fails"""
    mock_bot = MagicMock()
    mock_bot.delete_webhook = AsyncMock()
    mock_bot.session.close = AsyncMock()
    mock_bot_cls.return_value = mock_bot

    mock_dp = MagicMock()
    mock_dp.start_polling = AsyncMock(side_effect=Exception("Polling failed"))
    mock_dispatcher_cls.return_value = mock_dp

    bot = TelegramBot(token="test_token", message_handler=mock_message_handler)

    # Should raise exception but close session
    with pytest.raises(Exception, match="Polling failed"):
        await bot.start()

    # Verify session was closed even after error
    mock_bot.session.close.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("src.telegram_bot.Bot")
@patch("src.telegram_bot.Dispatcher")
async def test_delete_webhook_called_before_polling(
    mock_dispatcher_cls, mock_bot_cls, mock_message_handler
):
    """Test that webhook is deleted before starting polling"""
    mock_bot = MagicMock()
    mock_bot.delete_webhook = AsyncMock()
    mock_bot.session.close = AsyncMock()
    mock_bot_cls.return_value = mock_bot

    mock_dp = MagicMock()
    call_order = []

    async def record_delete_webhook(*args, **kwargs):
        call_order.append("delete_webhook")

    async def record_start_polling(*args, **kwargs):
        call_order.append("start_polling")

    mock_bot.delete_webhook = record_delete_webhook
    mock_dp.start_polling = record_start_polling
    mock_dispatcher_cls.return_value = mock_dp

    bot = TelegramBot(token="test_token", message_handler=mock_message_handler)
    await bot.start()

    # Verify delete_webhook was called before start_polling
    assert call_order == ["delete_webhook", "start_polling"]
