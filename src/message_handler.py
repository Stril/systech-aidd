"""Message handler for processing bot commands"""

import logging
from datetime import datetime
from typing import Protocol

from aiogram.types import Message

from src.context_manager import ContextManager
from src.exceptions import (
    LLMAPIError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from src.message_extractor import MessageExtractor
from src.messages import BotMessages
from src.models import Conversation, User
from src.models import Message as StorageMessage
from src.openai_client import OpenAIClient


class Storage(Protocol):
    """Protocol for storage implementations"""

    async def add_user(self, user: User) -> None: ...

    async def user_exists(self, user_id: int) -> bool: ...

    async def get_user(self, user_id: int) -> User | None: ...

    async def add_message_to_conversation(self, user_id: int, message: StorageMessage) -> None: ...

    async def increment_user_message_count(self, user_id: int) -> None: ...

    async def get_conversation(self, user_id: int) -> Conversation | None: ...

    async def clear_conversation(self, user_id: int) -> None: ...


logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles incoming messages and commands from users"""

    def __init__(
        self,
        openai_client: OpenAIClient | None = None,
        system_prompt: str = "",
        context_manager: ContextManager | None = None,
        storage: Storage | None = None,
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
        self._storage: Storage | None = storage

    async def handle_start(self, message: Message) -> None:
        """Handle /start command

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=start")

        # Save user to storage
        if self._storage and ctx.user_id != 0:
            if not await self._storage.user_exists(ctx.user_id):
                user = User(
                    user_id=ctx.user_id,
                    username=ctx.username if ctx.username != "Unknown" else None,
                    first_name=ctx.first_name,
                    last_name=ctx.last_name,
                    language_code=ctx.language_code,
                    created_at=datetime.now(),
                    message_count=0,
                )
                await self._storage.add_user(user)

        await message.answer(BotMessages.WELCOME)

    async def handle_help(self, message: Message) -> None:
        """Handle /help command

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=help")

        await message.answer(BotMessages.HELP)

    async def _restore_context_if_needed(self, user_id: int) -> None:
        """
        Restore context from database if needed (lazy loading)

        Args:
            user_id: Telegram user ID
        """
        if not self._context_manager or not self._storage:
            return

        current_context = self._context_manager.get_context(user_id)

        # If context is empty - try to load from database
        if len(current_context) == 0:
            conversation = await self._storage.get_conversation(user_id)
            if conversation and conversation.messages:
                # Convert Message objects to context format
                context_messages = [
                    {"role": msg.role, "content": msg.content} for msg in conversation.messages
                ]
                self._context_manager.load_context(user_id, context_messages)
                logger.info(f"context_restored|user_id={user_id}|messages={len(context_messages)}")

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

        # Restore context from DB if needed (lazy loading on first message)
        await self._restore_context_if_needed(ctx.user_id)

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
                user_id=ctx.user_id,
                role="user",
                content=ctx.text,
                created_at=datetime.now(),
                content_length=len(ctx.text),
            )
            await self._storage.add_message_to_conversation(ctx.user_id, user_msg)
            await self._storage.increment_user_message_count(ctx.user_id)

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
                    created_at=datetime.now(),
                    content_length=len(response),
                )
                await self._storage.add_message_to_conversation(ctx.user_id, assistant_msg)

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
            await self._storage.clear_conversation(ctx.user_id)

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

    async def handle_profile(self, message: Message) -> None:
        """Handle /profile command - show user data

        Args:
            message: Incoming Telegram message
        """
        ctx = MessageExtractor.extract(message)

        logger.info(f"user_command|user_id={ctx.user_id}|username={ctx.username}|command=profile")

        if self._storage and ctx.user_id != 0:
            user = await self._storage.get_user(ctx.user_id)
            if user:
                profile_msg = BotMessages.PROFILE_INFO.format(
                    user_id=user.user_id,
                    first_name=user.first_name or "Не указано",
                    last_name=user.last_name or "Не указано",
                    username=user.username or "Не указано",
                    language_code=user.language_code or "Не указано",
                    message_count=user.message_count,
                    created_at=user.created_at.strftime("%d.%m.%Y %H:%M"),
                )
                await message.answer(profile_msg)
            else:
                await message.answer(BotMessages.PROFILE_NOT_FOUND)
        else:
            await message.answer(BotMessages.PROFILE_UNAVAILABLE)
