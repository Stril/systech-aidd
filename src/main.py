"""Main entry point for the LLM Telegram Bot"""
import asyncio
import logging
import sys
from src.settings import Settings
from src.telegram_bot import TelegramBot
from src.message_handler import MessageHandler
from src.openai_client import OpenAIClient


def setup_logging(log_level: str) -> None:
    """Configure basic logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s|%(name)s|%(levelname)s|%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def main() -> None:
    """Main application entry point"""
    try:
        # Load settings
        settings = Settings()
        
        # Setup logging
        setup_logging(settings.LOG_LEVEL)
        
        logger = logging.getLogger(__name__)
        logger.info("application|status=starting")
        
        # Initialize OpenAI client
        openai_client = OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL
        )
        
        # Initialize components
        message_handler = MessageHandler(
            openai_client=openai_client,
            system_prompt=settings.DEFAULT_SYSTEM_PROMPT
        )
        bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN, message_handler)
        
        # Start bot
        logger.info("application|status=bot_starting")
        await bot.start()
        
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("application|status=stopped_by_user")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"application|error=startup_failed|details={str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

