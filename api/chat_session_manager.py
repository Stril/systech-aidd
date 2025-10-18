"""Chat session manager for managing user chat sessions"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from src.context_manager import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Session data container"""

    context_manager: ContextManager
    mode: str
    created_at: datetime
    username: str
    user_id: int


class ChatSessionManager:
    """Manages chat sessions with context history"""

    def __init__(self, max_context_messages: int = 10):
        """Initialize session manager

        Args:
            max_context_messages: Maximum number of messages to keep in context
        """
        self._sessions: dict[str, SessionData] = {}
        self._max_context_messages = max_context_messages
        logger.info(f"chat_session_manager|initialized|max_context={max_context_messages}")

    def create_session(self, mode: str, username: str, user_id: int) -> str:
        """Create a new chat session

        Args:
            mode: Chat mode ('normal' or 'admin')
            username: Username in format 'User_NNNNN'
            user_id: User ID (negative for web users)

        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        context_manager = ContextManager(max_messages=self._max_context_messages)

        self._sessions[session_id] = SessionData(
            context_manager=context_manager,
            mode=mode,
            created_at=datetime.now(),
            username=username,
            user_id=user_id,
        )

        logger.info(
            f"chat_session_manager|session_created|session_id={session_id}|"
            f"mode={mode}|username={username}|user_id={user_id}"
        )
        return session_id

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists

        Args:
            session_id: Session identifier

        Returns:
            True if session exists, False otherwise
        """
        return session_id in self._sessions

    def get_session_context(self, session_id: str) -> list[dict[str, str]]:
        """Get session conversation context

        Args:
            session_id: Session identifier

        Returns:
            List of messages in format [{"role": "user", "content": "..."}, ...]

        Raises:
            KeyError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")

        session = self._sessions[session_id]
        context = session.context_manager.get_context(user_id=session.user_id)
        logger.info(f"chat_session_manager|get_context|session_id={session_id}|length={len(context)}")
        return context

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add message to session context

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content

        Raises:
            KeyError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")

        session = self._sessions[session_id]
        session.context_manager.add_message(user_id=session.user_id, role=role, content=content)
        logger.info(
            f"chat_session_manager|message_added|session_id={session_id}|"
            f"role={role}|content_length={len(content)}"
        )

    def clear_session(self, session_id: str) -> None:
        """Clear session and remove it

        Args:
            session_id: Session identifier

        Raises:
            KeyError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")

        del self._sessions[session_id]
        logger.info(f"chat_session_manager|session_cleared|session_id={session_id}")

    def get_session_mode(self, session_id: str) -> str:
        """Get session mode

        Args:
            session_id: Session identifier

        Returns:
            Session mode ('normal' or 'admin')

        Raises:
            KeyError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")

        return self._sessions[session_id].mode

    def get_session_user(self, session_id: str) -> tuple[str, int]:
        """Get session user information

        Args:
            session_id: Session identifier

        Returns:
            Tuple of (username, user_id)

        Raises:
            KeyError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")

        session = self._sessions[session_id]
        return (session.username, session.user_id)

