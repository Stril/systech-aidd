"""Tests for Settings class"""

import pytest
from pydantic import ValidationError

from src.settings import Settings


def test_settings_with_valid_tokens(monkeypatch, tmp_path):
    """Test Settings initialization with valid tokens"""
    # Create temp .env to isolate from real .env
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_telegram_token\nOPENAI_API_KEY=test_openai_key\n")

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.TELEGRAM_BOT_TOKEN == "test_telegram_token"
    assert settings.OPENAI_API_KEY == "test_openai_key"
    assert settings.LOG_LEVEL == "INFO"  # Default value
    assert settings.OPENAI_BASE_URL == "https://openrouter.ai/api/v1"  # Default
    assert settings.OPENAI_MODEL == "openai/gpt-oss-20b:free"  # Default


def test_settings_with_custom_values(monkeypatch):
    """Test Settings with custom values"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OPENAI_MODEL", "openai/gpt-4")

    settings = Settings()

    assert settings.TELEGRAM_BOT_TOKEN == "test_telegram_token"
    assert settings.OPENAI_API_KEY == "test_openai_key"
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.OPENAI_MODEL == "openai/gpt-4"


def test_settings_missing_telegram_token(monkeypatch, tmp_path):
    """Test Settings fails without required Telegram token"""
    # Create empty .env file to prevent reading from actual .env
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test_key\n")

    # Remove token from environment
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")

    # Change to temp directory to use temp .env
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()


def test_settings_missing_openai_key(monkeypatch, tmp_path):
    """Test Settings fails without required OpenAI key"""
    # Create temp .env with only Telegram token
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_token\n")

    # Remove OpenAI key if exists
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()


def test_settings_case_insensitive(monkeypatch):
    """Test that settings are case-insensitive for environment variables"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("log_level", "DEBUG")  # lowercase

    settings = Settings()

    # Should read lowercase env var
    assert settings.LOG_LEVEL == "DEBUG"


def test_settings_default_system_prompt(monkeypatch):
    """Test that default system prompt is set"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

    settings = Settings()

    assert len(settings.DEFAULT_SYSTEM_PROMPT) > 0
    assert "помощник" in settings.DEFAULT_SYSTEM_PROMPT.lower()
