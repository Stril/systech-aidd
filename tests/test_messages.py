"""Tests for BotMessages class"""

import pytest

from src.messages import BotMessages


@pytest.mark.unit
def test_bot_messages_welcome():
    """Test WELCOME message constant"""
    assert "Привет" in BotMessages.WELCOME
    assert "LLM-бот помощник" in BotMessages.WELCOME
    assert "/help" in BotMessages.WELCOME


@pytest.mark.unit
def test_bot_messages_help():
    """Test HELP message constant"""
    assert "Доступные команды" in BotMessages.HELP
    assert "/start" in BotMessages.HELP
    assert "/help" in BotMessages.HELP
    assert "/role" in BotMessages.HELP
    assert "/reset" in BotMessages.HELP
    assert "/profile" in BotMessages.HELP


@pytest.mark.unit
def test_bot_messages_reset_success():
    """Test RESET_SUCCESS message constant"""
    assert "История диалога очищена" in BotMessages.RESET_SUCCESS


@pytest.mark.unit
def test_bot_messages_reset_no_context():
    """Test RESET_NO_CONTEXT message constant"""
    assert "не настроено" in BotMessages.RESET_NO_CONTEXT


@pytest.mark.unit
def test_bot_messages_no_llm():
    """Test NO_LLM message constant"""
    assert "LLM не настроен" in BotMessages.NO_LLM


@pytest.mark.unit
def test_bot_messages_error_connection():
    """Test ERROR_CONNECTION message constant"""
    assert "подключиться" in BotMessages.ERROR_CONNECTION


@pytest.mark.unit
def test_bot_messages_error_timeout():
    """Test ERROR_TIMEOUT message constant"""
    assert "время ожидания" in BotMessages.ERROR_TIMEOUT


@pytest.mark.unit
def test_bot_messages_error_rate_limit():
    """Test ERROR_RATE_LIMIT message constant"""
    assert "лимит запросов" in BotMessages.ERROR_RATE_LIMIT


@pytest.mark.unit
def test_bot_messages_error_api():
    """Test ERROR_API message constant"""
    assert "Ошибка сервиса" in BotMessages.ERROR_API


@pytest.mark.unit
def test_bot_messages_error_llm():
    """Test ERROR_LLM message constant"""
    assert "ошибка при обработке" in BotMessages.ERROR_LLM


@pytest.mark.unit
def test_bot_messages_error_unexpected():
    """Test ERROR_UNEXPECTED message constant"""
    assert "непредвиденная ошибка" in BotMessages.ERROR_UNEXPECTED


@pytest.mark.unit
def test_bot_messages_error_method_no_llm():
    """Test error() method with 'no_llm' type"""
    message = BotMessages.error("no_llm")
    assert message == BotMessages.NO_LLM


@pytest.mark.unit
def test_bot_messages_error_method_connection():
    """Test error() method with 'connection' type"""
    message = BotMessages.error("connection")
    assert message == BotMessages.ERROR_CONNECTION


@pytest.mark.unit
def test_bot_messages_error_method_timeout():
    """Test error() method with 'timeout' type"""
    message = BotMessages.error("timeout")
    assert message == BotMessages.ERROR_TIMEOUT


@pytest.mark.unit
def test_bot_messages_error_method_rate_limit():
    """Test error() method with 'rate_limit' type"""
    message = BotMessages.error("rate_limit")
    assert message == BotMessages.ERROR_RATE_LIMIT


@pytest.mark.unit
def test_bot_messages_error_method_api():
    """Test error() method with 'api' type"""
    message = BotMessages.error("api")
    assert message == BotMessages.ERROR_API


@pytest.mark.unit
def test_bot_messages_error_method_llm():
    """Test error() method with 'llm' type"""
    message = BotMessages.error("llm")
    assert message == BotMessages.ERROR_LLM


@pytest.mark.unit
def test_bot_messages_error_method_unexpected():
    """Test error() method with 'unexpected' type"""
    message = BotMessages.error("unexpected")
    assert message == BotMessages.ERROR_UNEXPECTED


@pytest.mark.unit
def test_bot_messages_error_method_unknown_type():
    """Test error() method with unknown error type - should return default"""
    message = BotMessages.error("unknown_error_type")
    assert message == BotMessages.ERROR_UNEXPECTED


@pytest.mark.unit
def test_bot_messages_role_info():
    """Test ROLE_INFO message constant"""
    assert "роль" in BotMessages.ROLE_INFO.lower()
    assert "{role_description}" in BotMessages.ROLE_INFO


@pytest.mark.unit
def test_bot_messages_role_info_formatting():
    """Test ROLE_INFO can be formatted with role description"""
    test_role = "You are a helpful technical assistant."
    formatted = BotMessages.ROLE_INFO.format(role_description=test_role)
    assert test_role in formatted
    assert "роль" in formatted.lower()
    assert "{role_description}" not in formatted


@pytest.mark.unit
def test_bot_messages_profile_info():
    """Test PROFILE_INFO message constant"""
    assert "профиль" in BotMessages.PROFILE_INFO.lower()
    assert "{user_id}" in BotMessages.PROFILE_INFO
    assert "{first_name}" in BotMessages.PROFILE_INFO
    assert "{last_name}" in BotMessages.PROFILE_INFO
    assert "{username}" in BotMessages.PROFILE_INFO
    assert "{language_code}" in BotMessages.PROFILE_INFO
    assert "{message_count}" in BotMessages.PROFILE_INFO
    assert "{created_at}" in BotMessages.PROFILE_INFO


@pytest.mark.unit
def test_bot_messages_profile_info_formatting():
    """Test PROFILE_INFO can be formatted with user data"""
    formatted = BotMessages.PROFILE_INFO.format(
        user_id=123,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="en",
        message_count=10,
        created_at="16.10.2025 12:00",
    )
    assert "123" in formatted
    assert "Test" in formatted
    assert "User" in formatted
    assert "testuser" in formatted
    assert "en" in formatted
    assert "10" in formatted
    assert "16.10.2025 12:00" in formatted


@pytest.mark.unit
def test_bot_messages_profile_not_found():
    """Test PROFILE_NOT_FOUND message constant"""
    assert "Профиль не найден" in BotMessages.PROFILE_NOT_FOUND
    assert "/start" in BotMessages.PROFILE_NOT_FOUND


@pytest.mark.unit
def test_bot_messages_profile_unavailable():
    """Test PROFILE_UNAVAILABLE message constant"""
    assert "Профиль недоступен" in BotMessages.PROFILE_UNAVAILABLE
