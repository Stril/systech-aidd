"""SQLite storage implementation with soft delete support"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database_models import ConversationDB, MessageDB, UserDB
from src.models import Conversation, Message, User

logger = logging.getLogger(__name__)


class SQLiteStorage:
    """SQLite-based storage for users, conversations and messages with soft delete"""

    def __init__(self, database_url: str) -> None:
        """
        Initialize SQLite storage

        Args:
            database_url: Database connection string (e.g. sqlite+aiosqlite:///data/bot.db)
        """
        self._engine = create_async_engine(database_url, echo=False)
        self._session_maker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(f"sqlite_storage|status=initialized|database_url={database_url}")

    async def close(self) -> None:
        """Close database connections"""
        await self._engine.dispose()
        logger.info("sqlite_storage|status=closed")

    # User operations

    async def add_user(self, user: User) -> None:
        """
        Add or update user

        Args:
            user: User object to store
        """
        async with self._session_maker() as session:
            # Check if user exists
            stmt = select(UserDB).where(UserDB.user_id == user.user_id, UserDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Update existing user
                existing_user.username = user.username
                existing_user.first_name = user.first_name
                existing_user.last_name = user.last_name
                existing_user.language_code = user.language_code
                existing_user.message_count = user.message_count
                logger.info(f"sqlite_storage|user_updated|user_id={user.user_id}")
            else:
                # Add new user
                user_db = UserDB.from_domain(user)
                session.add(user_db)
                logger.info(
                    f"sqlite_storage|user_added|user_id={user.user_id}|username={user.username}"
                )

            await session.commit()

    async def get_user(self, user_id: int) -> User | None:
        """
        Get user by ID

        Args:
            user_id: Telegram user ID

        Returns:
            User object or None if not found
        """
        async with self._session_maker() as session:
            stmt = select(UserDB).where(UserDB.user_id == user_id, UserDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()

            if user_db:
                logger.info(f"sqlite_storage|get_user|user_id={user_id}|found=True")
                return user_db.to_domain()

            logger.info(f"sqlite_storage|get_user|user_id={user_id}|found=False")
            return None

    async def user_exists(self, user_id: int) -> bool:
        """
        Check if user exists

        Args:
            user_id: Telegram user ID

        Returns:
            True if user exists, False otherwise
        """
        async with self._session_maker() as session:
            stmt = select(UserDB.user_id).where(
                UserDB.user_id == user_id, UserDB.deleted_at.is_(None)
            )
            result = await session.execute(stmt)
            exists = result.scalar_one_or_none() is not None

            logger.info(f"sqlite_storage|user_exists|user_id={user_id}|exists={exists}")
            return exists

    async def get_all_users(self) -> list[User]:
        """
        Get all users

        Returns:
            List of all active users
        """
        async with self._session_maker() as session:
            stmt = select(UserDB).where(UserDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            users_db = result.scalars().all()

            users = [user_db.to_domain() for user_db in users_db]
            logger.info(f"sqlite_storage|get_all_users|count={len(users)}")
            return users

    async def increment_user_message_count(self, user_id: int) -> None:
        """
        Increment user's message count

        Args:
            user_id: Telegram user ID
        """
        async with self._session_maker() as session:
            stmt = select(UserDB).where(UserDB.user_id == user_id, UserDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()

            if user_db:
                user_db.message_count += 1
                await session.commit()
                logger.info(
                    f"sqlite_storage|increment_messages|user_id={user_id}|"
                    f"count={user_db.message_count}"
                )

    # Conversation operations

    async def add_message_to_conversation(self, user_id: int, message: Message) -> None:
        """
        Add message to user's conversation

        Args:
            user_id: Telegram user ID
            message: Message object to add
        """
        async with self._session_maker() as session:
            # Get or create active conversation for user
            stmt = (
                select(ConversationDB)
                .where(
                    ConversationDB.user_id == user_id,
                    ConversationDB.deleted_at.is_(None),
                )
                .order_by(ConversationDB.updated_at.desc())
            )
            result = await session.execute(stmt)
            conversation_db = result.scalar_one_or_none()

            if not conversation_db:
                # Create new conversation
                conversation_db = ConversationDB(user_id=user_id)
                session.add(conversation_db)
                await session.flush()  # Get conversation ID
                logger.info(f"sqlite_storage|new_conversation|user_id={user_id}")

            # Add message
            message_db = MessageDB.from_domain(message, conversation_db.id)
            session.add(message_db)

            # Update conversation timestamp
            conversation_db.updated_at = datetime.now()

            await session.commit()
            logger.info(
                f"sqlite_storage|message_added|user_id={user_id}|role={message.role}|"
                f"conversation_id={conversation_db.id}"
            )

    async def get_conversation(self, user_id: int) -> Conversation | None:
        """
        Get user's active conversation with messages

        Args:
            user_id: Telegram user ID

        Returns:
            Conversation object with messages or None if not found
        """
        async with self._session_maker() as session:
            # Get latest active conversation
            stmt = (
                select(ConversationDB)
                .where(
                    ConversationDB.user_id == user_id,
                    ConversationDB.deleted_at.is_(None),
                )
                .order_by(ConversationDB.updated_at.desc())
            )
            result = await session.execute(stmt)
            conversation_db = result.scalar_one_or_none()

            if not conversation_db:
                logger.info(
                    f"sqlite_storage|get_conversation|user_id={user_id}|found=False|messages=0"
                )
                return None

            # Get active messages for this conversation
            stmt_messages = (
                select(MessageDB)
                .where(
                    MessageDB.conversation_id == conversation_db.id,
                    MessageDB.deleted_at.is_(None),
                )
                .order_by(MessageDB.created_at)
            )
            result_messages = await session.execute(stmt_messages)
            messages_db = result_messages.scalars().all()

            messages = [msg_db.to_domain() for msg_db in messages_db]
            conversation = conversation_db.to_domain(messages)

            logger.info(
                f"sqlite_storage|get_conversation|user_id={user_id}|found=True|"
                f"messages={len(messages)}"
            )
            return conversation

    async def clear_conversation(self, user_id: int) -> None:
        """
        Clear user's conversation using soft delete

        Args:
            user_id: Telegram user ID
        """
        async with self._session_maker() as session:
            # Get active conversation
            stmt = (
                select(ConversationDB)
                .where(
                    ConversationDB.user_id == user_id,
                    ConversationDB.deleted_at.is_(None),
                )
                .order_by(ConversationDB.updated_at.desc())
            )
            result = await session.execute(stmt)
            conversation_db = result.scalar_one_or_none()

            if conversation_db:
                # Soft delete all messages in conversation
                stmt_messages = select(MessageDB).where(
                    MessageDB.conversation_id == conversation_db.id,
                    MessageDB.deleted_at.is_(None),
                )
                result_messages = await session.execute(stmt_messages)
                messages_db = result_messages.scalars().all()

                now = datetime.now()
                message_count = len(messages_db)
                for msg_db in messages_db:
                    msg_db.deleted_at = now

                # Soft delete conversation
                conversation_db.deleted_at = now

                await session.commit()
                logger.info(
                    f"sqlite_storage|conversation_cleared|user_id={user_id}|cleared={message_count}"
                )
            else:
                logger.info(
                    f"sqlite_storage|conversation_cleared|user_id={user_id}|no_conversation"
                )

    # Metrics

    async def get_total_users(self) -> int:
        """
        Get total number of active users

        Returns:
            Number of active users
        """
        async with self._session_maker() as session:
            stmt = select(UserDB.user_id).where(UserDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            count = len(result.all())

            logger.info(f"sqlite_storage|metrics|total_users={count}")
            return count

    async def get_total_messages(self) -> int:
        """
        Get total number of active messages across all users

        Returns:
            Total message count
        """
        async with self._session_maker() as session:
            stmt = select(MessageDB.id).where(MessageDB.deleted_at.is_(None))
            result = await session.execute(stmt)
            total = len(result.all())

            logger.info(f"sqlite_storage|metrics|total_messages={total}")
            return total

    async def get_metrics(self) -> dict[str, int]:
        """
        Get all storage metrics

        Returns:
            Dictionary with metrics
        """
        async with self._session_maker() as session:
            # Count active users
            stmt_users = select(UserDB.user_id).where(UserDB.deleted_at.is_(None))
            result_users = await session.execute(stmt_users)
            total_users = len(result_users.all())

            # Count active conversations
            stmt_convs = select(ConversationDB.id).where(ConversationDB.deleted_at.is_(None))
            result_convs = await session.execute(stmt_convs)
            total_conversations = len(result_convs.all())

            # Count active messages
            stmt_msgs = select(MessageDB.id).where(MessageDB.deleted_at.is_(None))
            result_msgs = await session.execute(stmt_msgs)
            total_messages = len(result_msgs.all())

            # Sum user message counts
            stmt_user_msgs = select(UserDB.message_count).where(UserDB.deleted_at.is_(None))
            result_user_msgs = await session.execute(stmt_user_msgs)
            total_user_messages = sum(result_user_msgs.scalars().all())

            metrics = {
                "total_users": total_users,
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "total_user_messages": total_user_messages,
            }

            logger.info(
                f"sqlite_storage|metrics|users={metrics['total_users']}|"
                f"conversations={metrics['total_conversations']}|"
                f"messages={metrics['total_messages']}|"
                f"user_messages={metrics['total_user_messages']}"
            )

            return metrics
