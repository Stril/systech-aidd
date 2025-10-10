"""In-memory storage for users and conversations"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.models import User, Message, Conversation

logger = logging.getLogger(__name__)


class MemoryStorage:
    """In-memory storage for users, conversations and metrics"""
    
    def __init__(self):
        """Initialize empty storage"""
        self._users: Dict[int, User] = {}
        self._conversations: Dict[int, Conversation] = {}
        logger.info("memory_storage|status=initialized")
    
    # User operations
    
    def add_user(self, user: User) -> None:
        """
        Add or update user
        
        Args:
            user: User object to store
        """
        is_new = user.user_id not in self._users
        self._users[user.user_id] = user
        
        if is_new:
            logger.info(f"memory_storage|user_added|user_id={user.user_id}|username={user.username}")
        else:
            logger.info(f"memory_storage|user_updated|user_id={user.user_id}")
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User object or None if not found
        """
        user = self._users.get(user_id)
        logger.info(f"memory_storage|get_user|user_id={user_id}|found={user is not None}")
        return user
    
    def user_exists(self, user_id: int) -> bool:
        """
        Check if user exists
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user exists, False otherwise
        """
        exists = user_id in self._users
        logger.info(f"memory_storage|user_exists|user_id={user_id}|exists={exists}")
        return exists
    
    def get_all_users(self) -> List[User]:
        """
        Get all users
        
        Returns:
            List of all users
        """
        users = list(self._users.values())
        logger.info(f"memory_storage|get_all_users|count={len(users)}")
        return users
    
    def increment_user_message_count(self, user_id: int) -> None:
        """
        Increment user's message count
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self._users:
            self._users[user_id].message_count += 1
            logger.info(
                f"memory_storage|increment_messages|user_id={user_id}|"
                f"count={self._users[user_id].message_count}"
            )
    
    # Conversation operations
    
    def add_message_to_conversation(self, user_id: int, message: Message) -> None:
        """
        Add message to user's conversation
        
        Args:
            user_id: Telegram user ID
            message: Message object to add
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = Conversation(user_id=user_id)
            logger.info(f"memory_storage|new_conversation|user_id={user_id}")
        
        self._conversations[user_id].add_message(message)
        
        logger.info(
            f"memory_storage|message_added|user_id={user_id}|role={message.role}|"
            f"total_messages={self._conversations[user_id].get_message_count()}"
        )
    
    def get_conversation(self, user_id: int) -> Optional[Conversation]:
        """
        Get user's conversation
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Conversation object or None if not found
        """
        conversation = self._conversations.get(user_id)
        message_count = conversation.get_message_count() if conversation else 0
        
        logger.info(
            f"memory_storage|get_conversation|user_id={user_id}|"
            f"found={conversation is not None}|messages={message_count}"
        )
        return conversation
    
    def clear_conversation(self, user_id: int) -> None:
        """
        Clear user's conversation
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self._conversations:
            cleared_count = self._conversations[user_id].clear_messages()
            logger.info(f"memory_storage|conversation_cleared|user_id={user_id}|cleared={cleared_count}")
        else:
            logger.info(f"memory_storage|conversation_cleared|user_id={user_id}|no_conversation")
    
    # Metrics
    
    def get_total_users(self) -> int:
        """
        Get total number of users
        
        Returns:
            Number of users
        """
        count = len(self._users)
        logger.info(f"memory_storage|metrics|total_users={count}")
        return count
    
    def get_total_messages(self) -> int:
        """
        Get total number of messages across all users
        
        Returns:
            Total message count
        """
        total = sum(conv.get_message_count() for conv in self._conversations.values())
        logger.info(f"memory_storage|metrics|total_messages={total}")
        return total
    
    def get_metrics(self) -> dict:
        """
        Get all storage metrics
        
        Returns:
            Dictionary with metrics
        """
        metrics = {
            "total_users": len(self._users),
            "total_conversations": len(self._conversations),
            "total_messages": sum(conv.get_message_count() for conv in self._conversations.values()),
            "total_user_messages": sum(user.message_count for user in self._users.values())
        }
        
        logger.info(
            f"memory_storage|metrics|users={metrics['total_users']}|"
            f"conversations={metrics['total_conversations']}|"
            f"messages={metrics['total_messages']}|"
            f"user_messages={metrics['total_user_messages']}"
        )
        
        return metrics

