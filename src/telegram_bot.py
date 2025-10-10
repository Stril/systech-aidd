"""Telegram bot main class"""
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from src.message_handler import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class handling initialization and polling"""
    
    def __init__(self, token: str, message_handler: MessageHandler):
        """Initialize Telegram bot
        
        Args:
            token: Telegram bot token
            message_handler: Message handler instance
        """
        self._bot = Bot(token=token)
        self._dp = Dispatcher()
        self._message_handler = message_handler
        
        logger.info("telegram_bot|status=initialized")
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register message handlers for commands"""
        # Register /start command
        self._dp.message.register(
            self._message_handler.handle_start,
            Command(commands=["start"])
        )
        
        # Register /help command
        self._dp.message.register(
            self._message_handler.handle_help,
            Command(commands=["help"])
        )
        
        # Register handler for all text messages (not commands)
        self._dp.message.register(
            self._message_handler.handle_text_message
        )
        
        logger.info("telegram_bot|handlers=registered|count=3")
    
    async def start(self) -> None:
        """Start bot polling"""
        logger.info("telegram_bot|status=starting_polling")
        
        try:
            # Delete webhook if exists (for clean start)
            await self._bot.delete_webhook(drop_pending_updates=True)
            
            # Start polling
            await self._dp.start_polling(self._bot)
        except Exception as e:
            logger.error(f"telegram_bot|error=polling_failed|details={str(e)}")
            raise
        finally:
            await self._bot.session.close()

