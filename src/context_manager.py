import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages conversation context for each user"""

    def __init__(self, max_messages: int = 10):
        """
        Initialize ContextManager

        Args:
            max_messages: Maximum number of messages to keep in context
        """
        self._contexts: dict[int, list[dict[str, str]]] = {}
        self._max_messages = max_messages
        logger.info(f"context_manager|initialized|max_messages={max_messages}")

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Add a message to user's context

        Args:
            user_id: Telegram user ID
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        if user_id not in self._contexts:
            self._contexts[user_id] = []
            logger.info(f"context_manager|new_user|user_id={user_id}")

        self._contexts[user_id].append({"role": role, "content": content})

        self._trim_context(user_id)

        logger.info(
            f"context_manager|message_added|user_id={user_id}|"
            f"role={role}|context_length={len(self._contexts[user_id])}"
        )

    def get_context(self, user_id: int) -> list[dict[str, str]]:
        """
        Get user's conversation context

        Args:
            user_id: Telegram user ID

        Returns:
            List of messages in format [{"role": "user", "content": "..."}, ...]
        """
        context = self._contexts.get(user_id, [])
        logger.info(f"context_manager|get_context|user_id={user_id}|length={len(context)}")
        return context

    def reset_context(self, user_id: int) -> None:
        """
        Clear user's conversation context

        Args:
            user_id: Telegram user ID
        """
        if user_id in self._contexts:
            old_length = len(self._contexts[user_id])
            self._contexts[user_id] = []
            logger.info(f"context_manager|reset|user_id={user_id}|cleared_messages={old_length}")
        else:
            logger.info(f"context_manager|reset|user_id={user_id}|no_context_found")

    def load_context(self, user_id: int, messages: list[dict[str, str]]) -> None:
        """
        Load context from message list (e.g., from database)

        Args:
            user_id: Telegram user ID
            messages: List of messages in format [{"role": "...", "content": "..."}, ...]
        """
        # Take only last max_messages
        limited_messages = messages[-self._max_messages :] if messages else []

        # Set context directly without triggering add_message logic
        self._contexts[user_id] = limited_messages

        logger.info(
            f"context_manager|context_loaded|user_id={user_id}|"
            f"total_messages={len(messages)}|loaded_messages={len(limited_messages)}"
        )

    def _trim_context(self, user_id: int) -> None:
        """
        Trim context to max_messages limit

        Args:
            user_id: Telegram user ID
        """
        if len(self._contexts[user_id]) > self._max_messages:
            removed = len(self._contexts[user_id]) - self._max_messages
            self._contexts[user_id] = self._contexts[user_id][-self._max_messages :]
            logger.info(
                f"context_manager|trim|user_id={user_id}|"
                f"removed={removed}|remaining={len(self._contexts[user_id])}"
            )
