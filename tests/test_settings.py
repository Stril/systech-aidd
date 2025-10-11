"""Tests for Settings class"""

import pytest
from pydantic import ValidationError

from src.settings import Settings


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
def test_settings_case_insensitive(monkeypatch):
    """Test that settings are case-insensitive for environment variables"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("log_level", "DEBUG")  # lowercase

    settings = Settings()

    # Should read lowercase env var
    assert settings.LOG_LEVEL == "DEBUG"


@pytest.mark.unit
def test_settings_default_system_prompt(monkeypatch):
    """Test that default system prompt is set"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_telegram_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

    settings = Settings()

    assert len(settings.DEFAULT_SYSTEM_PROMPT) > 0
    assert "помощник" in settings.DEFAULT_SYSTEM_PROMPT.lower()


@pytest.mark.unit
def test_settings_load_system_prompt_from_file(monkeypatch, tmp_path):
    """Test loading system prompt from file"""
    # Arrange - create temp .env and system_prompt.txt
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_token\nOPENAI_API_KEY=test_key\n")

    prompt_file = tmp_path / "system_prompt.txt"
    test_prompt = "You are a helpful technical assistant specialized in Python development."
    prompt_file.write_text(test_prompt, encoding="utf-8")

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.chdir(tmp_path)

    # Act
    settings = Settings()
    loaded_prompt = settings.system_prompt

    # Assert
    assert loaded_prompt == test_prompt
    assert "technical assistant" in loaded_prompt


@pytest.mark.unit
def test_settings_system_prompt_file_not_found(monkeypatch, tmp_path):
    """Test that FileNotFoundError is raised when prompt file doesn't exist"""
    # Arrange - create .env but NOT system_prompt.txt
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_token\nOPENAI_API_KEY=test_key\n")

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.chdir(tmp_path)

    # Act & Assert
    settings = Settings()
    with pytest.raises(FileNotFoundError) as exc_info:
        _ = settings.system_prompt

    assert "system_prompt.txt" in str(exc_info.value)


@pytest.mark.unit
def test_settings_system_prompt_file_empty(monkeypatch, tmp_path):
    """Test that ValueError is raised when prompt file is empty"""
    # Arrange - create empty prompt file
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_token\nOPENAI_API_KEY=test_key\n")

    prompt_file = tmp_path / "system_prompt.txt"
    prompt_file.write_text("", encoding="utf-8")  # Empty file

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.chdir(tmp_path)

    # Act & Assert
    settings = Settings()
    with pytest.raises(ValueError) as exc_info:
        _ = settings.system_prompt

    assert "empty" in str(exc_info.value).lower()


@pytest.mark.unit
def test_settings_system_prompt_custom_file(monkeypatch, tmp_path):
    """Test loading system prompt from custom file path"""
    # Arrange - create custom prompt file
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TELEGRAM_BOT_TOKEN=test_token\n"
        "OPENAI_API_KEY=test_key\n"
        "SYSTEM_PROMPT_FILE=custom_prompt.txt\n"
    )

    custom_prompt_file = tmp_path / "custom_prompt.txt"
    custom_prompt = "You are a creative writing assistant."
    custom_prompt_file.write_text(custom_prompt, encoding="utf-8")

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("SYSTEM_PROMPT_FILE", "custom_prompt.txt")
    monkeypatch.chdir(tmp_path)

    # Act
    settings = Settings()
    loaded_prompt = settings.system_prompt

    # Assert
    assert loaded_prompt == custom_prompt
    assert "creative writing" in loaded_prompt


@pytest.mark.unit
def test_settings_system_prompt_whitespace_only(monkeypatch, tmp_path):
    """Test that ValueError is raised when prompt file contains only whitespace"""
    # Arrange - create prompt file with only whitespace
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=test_token\nOPENAI_API_KEY=test_key\n")

    prompt_file = tmp_path / "system_prompt.txt"
    prompt_file.write_text("   \n\t\n   ", encoding="utf-8")  # Only whitespace

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.chdir(tmp_path)

    # Act & Assert
    settings = Settings()
    with pytest.raises(ValueError) as exc_info:
        _ = settings.system_prompt

    assert "empty" in str(exc_info.value).lower()
