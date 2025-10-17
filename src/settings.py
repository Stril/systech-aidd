"""Settings module for application configuration"""

from pathlib import Path

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

    # System prompt file
    SYSTEM_PROMPT_FILE: str = "system_prompt.txt"

    # Text2SQL prompt file for admin chat mode
    TEXT2SQL_PROMPT_FILE: str = "text2sql_prompt.txt"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/bot.db"

    # API StatCollector mode
    USE_MOCK_STAT_COLLECTOR: bool = False  # True = Mock, False = Real

    @property
    def system_prompt(self) -> str:
        """Load system prompt from file

        Returns:
            System prompt content from file

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt file is empty or contains only whitespace
        """
        prompt_path = Path(self.SYSTEM_PROMPT_FILE)

        # Check if file exists
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt file not found: {self.SYSTEM_PROMPT_FILE}")

        # Read file content
        content = prompt_path.read_text(encoding="utf-8")

        # Validate content is not empty
        if not content.strip():
            raise ValueError(
                f"System prompt file is empty or contains only whitespace: {self.SYSTEM_PROMPT_FILE}"
            )

        return content.strip()

    @property
    def text2sql_prompt(self) -> str:
        """Load text2sql prompt from file

        Returns:
            Text2SQL prompt content from file

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt file is empty or contains only whitespace
        """
        prompt_path = Path(self.TEXT2SQL_PROMPT_FILE)

        # Check if file exists
        if not prompt_path.exists():
            raise FileNotFoundError(f"Text2SQL prompt file not found: {self.TEXT2SQL_PROMPT_FILE}")

        # Read file content
        content = prompt_path.read_text(encoding="utf-8")

        # Validate content is not empty
        if not content.strip():
            raise ValueError(
                f"Text2SQL prompt file is empty or contains only whitespace: {self.TEXT2SQL_PROMPT_FILE}"
            )

        return content.strip()
