"""Main entry point for the LLM Telegram Bot"""
import asyncio
import logging
import sys
import os
from datetime import datetime
from src.settings import Settings
from src.telegram_bot import TelegramBot
from src.message_handler import MessageHandler
from src.openai_client import OpenAIClient
from src.context_manager import ContextManager
from src.memory_storage import MemoryStorage


def setup_logging(log_level: str) -> None:
    """Configure logging to console and file
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Log file name based on current date
    log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Configure logging with both console and file handlers
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s|%(name)s|%(levelname)s|%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler(log_file, encoding='utf-8')  # File output
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
        
        # Initialize context manager
        context_manager = ContextManager(max_messages=10)
        
        # Initialize memory storage
        storage = MemoryStorage()
        
        # Initialize components
        message_handler = MessageHandler(
            openai_client=openai_client,
            system_prompt=settings.DEFAULT_SYSTEM_PROMPT,
            context_manager=context_manager,
            storage=storage
        )
        bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN, message_handler)
        
        # Log initial metrics
        logger.info(f"application|metrics|users={storage.get_total_users()}|messages={storage.get_total_messages()}")
        
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

