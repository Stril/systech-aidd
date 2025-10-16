"""Tests for MemoryStorage class"""

from datetime import datetime

import pytest

from src.memory_storage import MemoryStorage
from src.models import Message, User


@pytest.mark.unit
def test_memory_storage_initialization():
    """Test MemoryStorage initialization"""
    storage = MemoryStorage()
    assert storage.get_total_users() == 0
    assert storage.get_total_messages() == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_user():
    """Test adding a user"""
    storage = MemoryStorage()
    user = User(
        user_id=123,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        created_at=datetime.now(),
    )

    await storage.add_user(user)
    assert await storage.user_exists(123)
    assert storage.get_total_users() == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user():
    """Test getting a user"""
    storage = MemoryStorage()
    user = User(
        user_id=123,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        created_at=datetime.now(),
    )

    await storage.add_user(user)
    retrieved_user = storage.get_user(123)

    assert retrieved_user is not None
    assert retrieved_user.user_id == 123
    assert retrieved_user.username == "testuser"


@pytest.mark.unit
def test_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    storage = MemoryStorage()
    user = storage.get_user(999)
    assert user is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user():
    """Test updating an existing user"""
    storage = MemoryStorage()
    user = User(
        user_id=123,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        created_at=datetime.now(),
        message_count=5,
    )

    await storage.add_user(user)

    # Update user
    updated_user = User(
        user_id=123,
        username="newusername",
        first_name="Test",
        last_name="UpdatedUser",
        language_code="ru",
        created_at=datetime.now(),
        message_count=10,
    )

    await storage.add_user(updated_user)

    retrieved = storage.get_user(123)
    assert retrieved.username == "newusername"
    assert retrieved.message_count == 10
    assert storage.get_total_users() == 1  # Should not create duplicate


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_users():
    """Test getting all users"""
    storage = MemoryStorage()

    for i in range(3):
        user = User(
            user_id=100 + i,
            username=f"user{i}",
            first_name=f"User {i}",
            last_name=None,
            language_code="en",
            created_at=datetime.now(),
        )
        await storage.add_user(user)

    all_users = storage.get_all_users()
    assert len(all_users) == 3
    assert all(isinstance(u, User) for u in all_users)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_increment_user_message_count():
    """Test incrementing user message count"""
    storage = MemoryStorage()
    user = User(
        user_id=123,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        created_at=datetime.now(),
        message_count=0,
    )

    await storage.add_user(user)

    await storage.increment_user_message_count(123)
    await storage.increment_user_message_count(123)
    await storage.increment_user_message_count(123)

    retrieved = storage.get_user(123)
    assert retrieved.message_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_message_to_conversation():
    """Test adding a message to conversation"""
    storage = MemoryStorage()

    message = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )

    await storage.add_message_to_conversation(123, message)

    conversation = storage.get_conversation(123)
    assert conversation is not None
    assert conversation.get_message_count() == 1
    assert conversation.messages[0].content == "Hello"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_multiple_messages_to_conversation():
    """Test adding multiple messages to conversation"""
    storage = MemoryStorage()

    messages = [
        Message(
            user_id=123,
            role="user",
            content="Hello",
            created_at=datetime.now(),
            content_length=len("Hello"),
        ),
        Message(
            user_id=123,
            role="assistant",
            content="Hi there!",
            created_at=datetime.now(),
            content_length=len("Hi there!"),
        ),
        Message(
            user_id=123,
            role="user",
            content="How are you?",
            created_at=datetime.now(),
            content_length=len("How are you?"),
        ),
    ]

    for msg in messages:
        await storage.add_message_to_conversation(123, msg)

    conversation = storage.get_conversation(123)
    assert conversation.get_message_count() == 3
    assert len(conversation.messages) == 3


@pytest.mark.unit
def test_get_nonexistent_conversation():
    """Test getting a conversation that doesn't exist"""
    storage = MemoryStorage()
    conversation = storage.get_conversation(999)
    assert conversation is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clear_conversation():
    """Test clearing a conversation"""
    storage = MemoryStorage()

    # Add some messages
    for i in range(5):
        content = f"Message {i}"
        message = Message(
            user_id=123,
            role="user",
            content=content,
            created_at=datetime.now(),
            content_length=len(content),
        )
        await storage.add_message_to_conversation(123, message)

    conversation = storage.get_conversation(123)
    assert conversation.get_message_count() == 5

    # Clear conversation
    await storage.clear_conversation(123)

    conversation = storage.get_conversation(123)
    assert conversation.get_message_count() == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clear_nonexistent_conversation():
    """Test clearing a conversation that doesn't exist"""
    storage = MemoryStorage()
    # Should not raise error
    await storage.clear_conversation(999)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_multiple_users_separate_conversations():
    """Test that different users have separate conversations"""
    storage = MemoryStorage()

    await storage.add_message_to_conversation(
        123,
        Message(
            user_id=123,
            role="user",
            content="User 123",
            created_at=datetime.now(),
            content_length=len("User 123"),
        ),
    )
    await storage.add_message_to_conversation(
        456,
        Message(
            user_id=456,
            role="user",
            content="User 456",
            created_at=datetime.now(),
            content_length=len("User 456"),
        ),
    )

    conv_123 = storage.get_conversation(123)
    conv_456 = storage.get_conversation(456)

    assert conv_123.get_message_count() == 1
    assert conv_456.get_message_count() == 1
    assert conv_123.messages[0].content == "User 123"
    assert conv_456.messages[0].content == "User 456"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_total_messages():
    """Test getting total messages across all users"""
    storage = MemoryStorage()

    # User 1: 3 messages
    for i in range(3):
        content = f"Msg {i}"
        await storage.add_message_to_conversation(
            123,
            Message(
                user_id=123,
                role="user",
                content=content,
                created_at=datetime.now(),
                content_length=len(content),
            ),
        )

    # User 2: 2 messages
    for i in range(2):
        content = f"Msg {i}"
        await storage.add_message_to_conversation(
            456,
            Message(
                user_id=456,
                role="user",
                content=content,
                created_at=datetime.now(),
                content_length=len(content),
            ),
        )

    assert storage.get_total_messages() == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_metrics():
    """Test getting all metrics"""
    storage = MemoryStorage()

    # Add users
    for i in range(2):
        user = User(
            user_id=100 + i,
            username=f"user{i}",
            first_name=f"User {i}",
            last_name=None,
            language_code="en",
            created_at=datetime.now(),
            message_count=5,
        )
        await storage.add_user(user)

    # Add messages
    for i in range(3):
        content = f"Msg {i}"
        await storage.add_message_to_conversation(
            100,
            Message(
                user_id=100,
                role="user",
                content=content,
                created_at=datetime.now(),
                content_length=len(content),
            ),
        )

    for i in range(2):
        content = f"Msg {i}"
        await storage.add_message_to_conversation(
            101,
            Message(
                user_id=101,
                role="user",
                content=content,
                created_at=datetime.now(),
                content_length=len(content),
            ),
        )

    metrics = storage.get_metrics()

    assert metrics["total_users"] == 2
    assert metrics["total_conversations"] == 2
    assert metrics["total_messages"] == 5
    assert metrics["total_user_messages"] == 10  # 5 + 5 from user.message_count
