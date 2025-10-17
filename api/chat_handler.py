"""Chat handler for processing chat requests"""

import logging

from api.chat_models import ChatResponse
from api.chat_session_manager import ChatSessionManager
from api.text2sql_handler import Text2SQLHandler
from src.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class ChatHandler:
    """Handles chat requests in normal and admin modes"""

    def __init__(
        self,
        openai_client: OpenAIClient,
        system_prompt: str,
        text2sql_handler: Text2SQLHandler,
        session_manager: ChatSessionManager,
    ):
        """Initialize chat handler

        Args:
            openai_client: OpenAI client for LLM interactions
            system_prompt: System prompt for normal chat mode
            text2sql_handler: Handler for text-to-SQL operations
            session_manager: Session manager for context management
        """
        self._openai_client = openai_client
        self._system_prompt = system_prompt
        self._text2sql_handler = text2sql_handler
        self._session_manager = session_manager

        logger.info("chat_handler|initialized")

    async def handle_message(self, session_id: str, message: str, mode: str) -> ChatResponse:
        """Handle incoming chat message

        Args:
            session_id: Session identifier
            message: User message
            mode: Chat mode ('normal' or 'admin')

        Returns:
            ChatResponse with answer and optional SQL query

        Raises:
            KeyError: If session doesn't exist
            Exception: If message processing fails
        """
        logger.info(
            f"chat_handler|handle_message|session_id={session_id}|"
            f"mode={mode}|message_length={len(message)}"
        )

        if not self._session_manager.session_exists(session_id):
            raise KeyError(f"Session not found: {session_id}")

        # Add user message to session
        self._session_manager.add_message(session_id, "user", message)

        try:
            if mode == "admin":
                # Admin mode: use text2sql pipeline
                response = await self._handle_admin_mode(session_id, message)
            else:
                # Normal mode: standard chat
                response = await self._handle_normal_mode(session_id, message)

            # Add assistant response to session
            self._session_manager.add_message(session_id, "assistant", response.content)

            logger.info(
                f"chat_handler|message_handled|session_id={session_id}|"
                f"response_length={len(response.content)}"
            )

            return response

        except Exception as e:
            logger.error(f"chat_handler|error|session_id={session_id}|error={str(e)}")
            raise

    async def _handle_normal_mode(self, session_id: str, message: str) -> ChatResponse:
        """Handle message in normal chat mode

        Args:
            session_id: Session identifier
            message: User message

        Returns:
            ChatResponse with answer
        """
        # Get conversation context
        context = self._session_manager.get_session_context(session_id)

        # Send to LLM
        answer = await self._openai_client.send_message(context, self._system_prompt)

        return ChatResponse(content=answer, sql_query=None)

    async def _handle_admin_mode(self, session_id: str, message: str) -> ChatResponse:
        """Handle message in admin mode with text2sql

        Args:
            session_id: Session identifier
            message: User message (question about statistics)

        Returns:
            ChatResponse with answer and SQL query
        """
        # Process question through text2sql pipeline
        sql_query, answer = await self._text2sql_handler.process_question(message)

        return ChatResponse(content=answer, sql_query=sql_query if sql_query else None)

