"""SQLAlchemy database models for persistence layer"""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.models import Conversation, Message, User


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class UserDB(Base):
    """User database model"""

    __tablename__ = "users"

    # Primary key - Telegram user_id without AUTOINCREMENT
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    first_name: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    message_count: Mapped[int] = mapped_column(default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    # Indexes
    __table_args__ = (
        Index("idx_users_deleted_at", "deleted_at"),
        CheckConstraint("message_count >= 0", name="check_message_count_positive"),
    )

    def to_domain(self) -> User:
        """Convert database model to domain model"""
        return User(
            user_id=self.user_id,
            username=self.username,
            first_name=self.first_name,
            created_at=self.created_at,
            message_count=self.message_count,
            deleted_at=self.deleted_at,
        )

    @staticmethod
    def from_domain(user: User) -> "UserDB":
        """Convert domain model to database model"""
        return UserDB(
            user_id=user.user_id,
            username=user.username,
            first_name=user.first_name,
            created_at=user.created_at,
            message_count=user.message_count,
            deleted_at=user.deleted_at,
        )


class ConversationDB(Base):
    """Conversation database model"""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    # Indexes - NO UNIQUE on user_id (multiple conversations per user)
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_deleted_at", "deleted_at"),
    )

    def to_domain(self, messages: list[Message]) -> Conversation:
        """Convert database model to domain model"""
        return Conversation(
            user_id=self.user_id,
            messages=messages,
            created_at=self.created_at,
            updated_at=self.updated_at,
            id=self.id,
            deleted_at=self.deleted_at,
        )

    @staticmethod
    def from_domain(conversation: Conversation) -> "ConversationDB":
        """Convert domain model to database model"""
        return ConversationDB(
            id=conversation.id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            deleted_at=conversation.deleted_at,
        )


class MessageDB(Base):
    """Message database model"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_length: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    # Indexes
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_user_id", "user_id"),
        Index("idx_messages_created_at", "created_at"),
        Index("idx_messages_deleted_at", "deleted_at"),
        Index("idx_messages_composite", "conversation_id", "deleted_at", "created_at"),
    )

    def to_domain(self) -> Message:
        """Convert database model to domain model"""
        return Message(
            id=self.id,
            user_id=self.user_id,
            role=self.role,
            content=self.content,
            content_length=self.content_length,
            created_at=self.created_at,
            deleted_at=self.deleted_at,
        )

    @staticmethod
    def from_domain(message: Message, conversation_id: int) -> "MessageDB":
        """Convert domain model to database model"""
        return MessageDB(
            id=message.id,
            conversation_id=conversation_id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
            content_length=message.content_length,
            created_at=message.created_at,
            deleted_at=message.deleted_at,
        )
