"""Settings module for application configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str

    # OpenRouter/LLM
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENAI_MODEL: str = "openai/gpt-oss-20b:free"

    # System
    LOG_LEVEL: str = "INFO"
    DEFAULT_SYSTEM_PROMPT: str = (
        "Ты - универсальный помощник, готовый помочь с различными вопросами. "
        "Отвечай дружелюбно, информативно и по существу. "
        "Если не знаешь ответа, честно скажи об этом."
    )
