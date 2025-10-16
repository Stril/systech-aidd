"""Message extractor for extracting data from Telegram messages"""

from dataclasses import dataclass

from aiogram.types import Message


@dataclass
class MessageContext:
    """Extracted message context from Telegram message"""

    user_id: int
    username: str
    first_name: str | None
    last_name: str | None
    language_code: str | None
    text: str
    chat_id: int

    def __repr__(self) -> str:
        return f"MessageContext(user_id={self.user_id}, username={self.username})"


class MessageExtractor:
    """Extracts data from Telegram messages"""

    @staticmethod
    def extract(message: Message) -> MessageContext:
        """Extract all relevant data from Telegram message

        Args:
            message: Incoming Telegram message

        Returns:
            MessageContext with extracted data
        """
        username = "Unknown"
        if message.from_user and message.from_user.username:
            username = message.from_user.username

        return MessageContext(
            user_id=message.from_user.id if message.from_user else 0,
            username=username,
            first_name=message.from_user.first_name if message.from_user else None,
            last_name=message.from_user.last_name if message.from_user else None,
            language_code=message.from_user.language_code if message.from_user else None,
            text=message.text or "",
            chat_id=message.chat.id,
        )
