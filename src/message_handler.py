"""Message handler for processing bot commands"""

import logging
from datetime import datetime

from aiogram.types import Message

from src.context_manager import ContextManager
from src.exceptions import (
    LLMAPIError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from src.memory_storage import MemoryStorage
from src.message_extractor import MessageExtractor
from src.messages import BotMessages
from src.models import Message as StorageMessage
from src.models import User
from src.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming messages and commands from users"""

    def __init__(
        self,
        openai_client: OpenAIClient | None = None,
        system_prompt: str = "",
        context_manager: ContextManager | None = None,
        storage: MemoryStorage | None = None,
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
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=start")

        # Save user to storage
        if self._storage and ctx.user_id != 0:
            if not self._storage.user_exists(ctx.user_id):
                user = User(
                    user_id=ctx.user_id,
                    username=ctx.username if ctx.username != "Unknown" else None,
                    first_name=ctx.first_name,
                    created_at=datetime.now(),
                    message_count=0,
                )
                self._storage.add_user(user)

        await message.answer(BotMessages.WELCOME)

    async def handle_help(self, message: Message) -> None:
        """Handle /help command

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=help")

        await message.answer(BotMessages.HELP)

    async def handle_text_message(self, message: Message) -> None:
        """Handle regular text messages

        Args:
            message: Incoming Telegram message
        """
        if not self._openai_client:
            await message.answer(BotMessages.NO_LLM)
            return

        ctx = MessageExtractor.extract(message)

        logger.info(
            f"user_text_message|user_id={ctx.user_id}|username={ctx.username}|message_length={len(ctx.text)}"
        )

        # Add user message to context
        if self._context_manager:
            self._context_manager.add_message(ctx.user_id, "user", ctx.text)
            messages = self._context_manager.get_context(ctx.user_id)
        else:
            # Fallback to single message if no context manager
            messages = [{"role": "user", "content": ctx.text}]

        # Save user message to storage
        if self._storage and ctx.user_id != 0:
            user_msg = StorageMessage(
                user_id=ctx.user_id, role="user", content=ctx.text, timestamp=datetime.now()
            )
            self._storage.add_message_to_conversation(ctx.user_id, user_msg)
            self._storage.increment_user_message_count(ctx.user_id)

        try:
            # Send typing action
            if message.bot:
                await message.bot.send_chat_action(chat_id=ctx.chat_id, action="typing")

            # Get response from LLM
            response = await self._openai_client.send_message(messages, self._system_prompt)

            # Add assistant response to context
            if self._context_manager:
                self._context_manager.add_message(ctx.user_id, "assistant", response)

            # Save assistant response to storage
            if self._storage and ctx.user_id != 0:
                assistant_msg = StorageMessage(
                    user_id=ctx.user_id,
                    role="assistant",
                    content=response,
                    timestamp=datetime.now(),
                )
                self._storage.add_message_to_conversation(ctx.user_id, assistant_msg)

            # Send response to user
            await message.answer(response)

            logger.info(f"message_handled|user_id={ctx.user_id}|response_length={len(response)}")

        except LLMConnectionError:
            logger.error(f"message_error|user_id={ctx.user_id}|type=connection")
            await message.answer(BotMessages.ERROR_CONNECTION)

        except LLMTimeoutError:
            logger.error(f"message_error|user_id={ctx.user_id}|type=timeout")
            await message.answer(BotMessages.ERROR_TIMEOUT)

        except LLMRateLimitError:
            logger.error(f"message_error|user_id={ctx.user_id}|type=rate_limit")
            await message.answer(BotMessages.ERROR_RATE_LIMIT)

        except LLMAPIError as e:
            logger.error(f"message_error|user_id={ctx.user_id}|type=api_error|details={str(e)}")
            await message.answer(BotMessages.ERROR_API)

        except LLMError as e:
            logger.error(f"message_error|user_id={ctx.user_id}|type=llm_error|details={str(e)}")
            await message.answer(BotMessages.ERROR_LLM)

        except Exception as e:
            logger.error(f"message_error|user_id={ctx.user_id}|type=unexpected|error={str(e)}")
            await message.answer(BotMessages.ERROR_UNEXPECTED)

    async def handle_reset(self, message: Message) -> None:
        """Handle /reset command - clear conversation history

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=reset")

        # Clear context manager
        if self._context_manager:
            self._context_manager.reset_context(ctx.user_id)

        # Clear storage conversation
        if self._storage and ctx.user_id != 0:
            self._storage.clear_conversation(ctx.user_id)

        if self._context_manager or self._storage:
            await message.answer(BotMessages.RESET_SUCCESS)
        else:
            await message.answer(BotMessages.RESET_NO_CONTEXT)

    async def handle_role(self, message: Message) -> None:
        """Handle /role command - show current assistant role

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=role")

        # Format role message with system prompt
        role_message = BotMessages.ROLE_INFO.format(
            role_description=self._system_prompt if self._system_prompt else "Не задана"
        )

        await message.answer(role_message)
