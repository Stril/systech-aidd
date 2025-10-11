"""Message handler for processing bot commands"""
import logging
from typing import Optional
from datetime import datetime
from aiogram.types import Message
from src.openai_client import OpenAIClient
from src.context_manager import ContextManager
from src.memory_storage import MemoryStorage
from src.models import User, Message as StorageMessage
from src.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAPIError,
    LLMError
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming messages and commands from users"""
    
    def __init__(
        self, 
        openai_client: Optional[OpenAIClient] = None, 
        system_prompt: str = "",
        context_manager: Optional[ContextManager] = None,
        storage: Optional[MemoryStorage] = None
    ):
        """Initialize message handler
        
        Args:
            openai_client: OpenAI client for LLM interactions (optional for now)
            system_prompt: System prompt for LLM
            context_manager: Context manager for conversation history
            storage: Memory storage for users and conversations
        """
        self._openai_client = openai_client
        self._system_prompt = system_prompt
        self._context_manager = context_manager
        self._storage = storage
    
    async def handle_start(self, message: Message) -> None:
        """Handle /start command
        
        Args:
            message: Incoming Telegram message
        """
        user_id = message.from_user.id if message.from_user else 0
        username = message.from_user.username if message.from_user else "Unknown"
        first_name = message.from_user.first_name if message.from_user else None
        
        logger.info(f"user_command|user_id={user_id}|username={username}|command=start")
        
        # Save user to storage
        if self._storage and user_id != 0:
            if not self._storage.user_exists(user_id):
                user = User(
                    user_id=user_id,
                    username=username if username != "Unknown" else None,
                    first_name=first_name,
                    created_at=datetime.now(),
                    message_count=0
                )
                self._storage.add_user(user)
        
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
            "/help - Показать эту справку\n"
            "/reset - Очистить историю диалога\n\n"
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
        
        # Add user message to context
        if self._context_manager:
            self._context_manager.add_message(user_id, "user", text)
            messages = self._context_manager.get_context(user_id)
        else:
            # Fallback to single message if no context manager
            messages = [{"role": "user", "content": text}]
        
        # Save user message to storage
        if self._storage and user_id != 0:
            user_msg = StorageMessage(
                user_id=user_id,
                role="user",
                content=text,
                timestamp=datetime.now()
            )
            self._storage.add_message_to_conversation(user_id, user_msg)
            self._storage.increment_user_message_count(user_id)
        
        try:
            # Send typing action
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Get response from LLM
            response = self._openai_client.send_message(messages, self._system_prompt)
            
            # Add assistant response to context
            if self._context_manager:
                self._context_manager.add_message(user_id, "assistant", response)
            
            # Save assistant response to storage
            if self._storage and user_id != 0:
                assistant_msg = StorageMessage(
                    user_id=user_id,
                    role="assistant",
                    content=response,
                    timestamp=datetime.now()
                )
                self._storage.add_message_to_conversation(user_id, assistant_msg)
            
            # Send response to user
            await message.answer(response)
            
            logger.info(f"message_handled|user_id={user_id}|response_length={len(response)}")
            
        except LLMConnectionError:
            logger.error(f"message_error|user_id={user_id}|type=connection")
            await message.answer(
                "⚠️ Не удалось подключиться к сервису ИИ.\n"
                "Пожалуйста, попробуйте через несколько минут."
            )
            
        except LLMTimeoutError:
            logger.error(f"message_error|user_id={user_id}|type=timeout")
            await message.answer(
                "⏱️ Превышено время ожидания ответа.\n"
                "Попробуйте отправить сообщение еще раз."
            )
            
        except LLMRateLimitError:
            logger.error(f"message_error|user_id={user_id}|type=rate_limit")
            await message.answer(
                "🚫 Превышен лимит запросов к сервису ИИ.\n"
                "Пожалуйста, подождите немного перед следующим запросом."
            )
            
        except LLMAPIError as e:
            logger.error(f"message_error|user_id={user_id}|type=api_error|details={str(e)}")
            await message.answer(
                "❌ Ошибка сервиса ИИ.\n"
                "Попробуйте позже или обратитесь к администратору."
            )
            
        except LLMError as e:
            logger.error(f"message_error|user_id={user_id}|type=llm_error|details={str(e)}")
            await message.answer(
                "😔 Произошла ошибка при обработке вашего сообщения.\n"
                "Пожалуйста, попробуйте еще раз."
            )
            
        except Exception as e:
            logger.error(f"message_error|user_id={user_id}|type=unexpected|error={str(e)}")
            await message.answer(
                "😔 Произошла непредвиденная ошибка.\n"
                "Пожалуйста, попробуйте позже."
            )
    
    async def handle_reset(self, message: Message) -> None:
        """Handle /reset command - clear conversation history
        
        Args:
            message: Incoming Telegram message
        """
        user_id = message.from_user.id if message.from_user else 0
        username = message.from_user.username if message.from_user else "Unknown"
        
        logger.info(f"user_command|user_id={user_id}|username={username}|command=reset")
        
        # Clear context manager
        if self._context_manager:
            self._context_manager.reset_context(user_id)
        
        # Clear storage conversation
        if self._storage and user_id != 0:
            self._storage.clear_conversation(user_id)
        
        if self._context_manager or self._storage:
            await message.answer("🔄 История диалога очищена. Начнем сначала!")
        else:
            await message.answer("⚠️ Управление контекстом не настроено.")

