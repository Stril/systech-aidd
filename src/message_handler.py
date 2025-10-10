"""Message handler for processing bot commands"""
import logging
from typing import Optional
from aiogram.types import Message
from src.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming messages and commands from users"""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None, system_prompt: str = ""):
        """Initialize message handler
        
        Args:
            openai_client: OpenAI client for LLM interactions (optional for now)
            system_prompt: System prompt for LLM
        """
        self._openai_client = openai_client
        self._system_prompt = system_prompt
    
    async def handle_start(self, message: Message) -> None:
        """Handle /start command
        
        Args:
            message: Incoming Telegram message
        """
        user_id = message.from_user.id if message.from_user else 0
        username = message.from_user.username if message.from_user else "Unknown"
        
        logger.info(f"user_command|user_id={user_id}|username={username}|command=start")
        
        welcome_text = (
            "👋 Привет! Я LLM-бот помощник.\n\n"
            "Я могу помочь вам с различными вопросами и задачами.\n\n"
            "Используйте /help для просмотра доступных команд."
        )
        
        await message.answer(welcome_text)
    
    async def handle_help(self, message: Message) -> None:
        """Handle /help command
        
        Args:
            message: Incoming Telegram message
        """
        user_id = message.from_user.id if message.from_user else 0
        username = message.from_user.username if message.from_user else "Unknown"
        
        logger.info(f"user_command|user_id={user_id}|username={username}|command=help")
        
        help_text = (
            "📚 Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n\n"
            "Просто отправьте мне сообщение, и я постараюсь помочь!"
        )
        
        await message.answer(help_text)
    
    async def handle_text_message(self, message: Message) -> None:
        """Handle regular text messages
        
        Args:
            message: Incoming Telegram message
        """
        if not self._openai_client:
            await message.answer("LLM не настроен. Обратитесь к администратору.")
            return
        
        user_id = message.from_user.id if message.from_user else 0
        username = message.from_user.username if message.from_user else "Unknown"
        text = message.text or ""
        
        logger.info(f"user_text_message|user_id={user_id}|username={username}|message_length={len(text)}")
        
        # Simple request to LLM (without context for now)
        messages = [{"role": "user", "content": text}]
        
        try:
            # Send typing action
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Get response from LLM
            response = self._openai_client.send_message(messages, self._system_prompt)
            
            # Send response to user
            await message.answer(response)
            
            logger.info(f"message_handled|user_id={user_id}|response_length={len(response)}")
            
        except Exception as e:
            logger.error(f"message_error|user_id={user_id}|error={str(e)}")
            await message.answer(
                "😔 Извините, произошла ошибка при обработке вашего сообщения. "
                "Пожалуйста, попробуйте позже."
            )

