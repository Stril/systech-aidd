"""Data models for the bot"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User model"""

    user_id: int
    username: str | None
    first_name: str | None
    created_at: datetime
    message_count: int = 0
    deleted_at: datetime | None = None

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, username={self.username}, messages={self.message_count})"


@dataclass
class Message:
    """Message model"""

    user_id: int
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime
    content_length: int
    id: int | None = None
    deleted_at: datetime | None = None

    def __repr__(self) -> str:
        return f"Message(user_id={self.user_id}, role={self.role}, length={len(self.content)})"


@dataclass
class Conversation:
    """Conversation model - holds all messages for a user"""

    user_id: int
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: int | None = None
    deleted_at: datetime | None = None

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def clear_messages(self) -> int:
        """Clear all messages and return count of cleared messages"""
        count = len(self.messages)
        self.messages.clear()
        self.updated_at = datetime.now()
        return count

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.messages)

    def __repr__(self) -> str:
        return f"Conversation(user_id={self.user_id}, messages={len(self.messages)})"
