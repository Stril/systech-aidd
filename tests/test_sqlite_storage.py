"""Tests for SQLiteStorage class"""

from datetime import datetime

import pytest
from sqlalchemy import select

from src.database_models import Base, UserDB
from src.models import Message, User
from src.sqlite_storage import SQLiteStorage


@pytest.fixture
async def storage():
    """Create SQLiteStorage with in-memory database"""
    storage = SQLiteStorage("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with storage._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield storage

    await storage.close()


# User tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_user(storage: SQLiteStorage):
    """Test adding a user"""
    user = User(user_id=123, username="testuser", first_name="Test", created_at=datetime.now())

    await storage.add_user(user)
    assert await storage.user_exists(123)
    assert await storage.get_total_users() == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_user(storage: SQLiteStorage):
    """Test getting a user"""
    user = User(user_id=123, username="testuser", first_name="Test", created_at=datetime.now())

    await storage.add_user(user)
    retrieved_user = await storage.get_user(123)

    assert retrieved_user is not None
    assert retrieved_user.user_id == 123
    assert retrieved_user.username == "testuser"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_nonexistent_user(storage: SQLiteStorage):
    """Test getting a user that doesn't exist"""
    user = await storage.get_user(999)
    assert user is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user(storage: SQLiteStorage):
    """Test updating an existing user"""
    user = User(user_id=123, username="testuser", first_name="Test", created_at=datetime.now())
    await storage.add_user(user)

    updated_user = User(
        user_id=123, username="updateduser", first_name="Updated", created_at=datetime.now()
    )
    await storage.add_user(updated_user)

    retrieved_user = await storage.get_user(123)
    assert retrieved_user is not None
    assert retrieved_user.username == "updateduser"
    assert retrieved_user.first_name == "Updated"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_users(storage: SQLiteStorage):
    """Test getting all users"""
    user1 = User(user_id=123, username="user1", first_name="User1", created_at=datetime.now())
    user2 = User(user_id=456, username="user2", first_name="User2", created_at=datetime.now())

    await storage.add_user(user1)
    await storage.add_user(user2)

    users = await storage.get_all_users()
    assert len(users) == 2
    assert any(u.user_id == 123 for u in users)
    assert any(u.user_id == 456 for u in users)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_increment_user_message_count(storage: SQLiteStorage):
    """Test incrementing user message count"""
    user = User(
        user_id=123,
        username="testuser",
        first_name="Test",
        created_at=datetime.now(),
        message_count=0,
    )
    await storage.add_user(user)

    await storage.increment_user_message_count(123)
    await storage.increment_user_message_count(123)

    retrieved_user = await storage.get_user(123)
    assert retrieved_user is not None
    assert retrieved_user.message_count == 2


# Conversation tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_message_to_conversation(storage: SQLiteStorage):
    """Test adding a message to conversation"""
    message = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )

    await storage.add_message_to_conversation(123, message)

    conversation = await storage.get_conversation(123)
    assert conversation is not None
    assert len(conversation.messages) == 1
    assert conversation.messages[0].content == "Hello"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_nonexistent_conversation(storage: SQLiteStorage):
    """Test getting a conversation that doesn't exist"""
    conversation = await storage.get_conversation(999)
    assert conversation is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_multiple_messages(storage: SQLiteStorage):
    """Test adding multiple messages to a conversation"""
    message1 = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )
    message2 = Message(
        user_id=123,
        role="assistant",
        content="Hi there!",
        created_at=datetime.now(),
        content_length=len("Hi there!"),
    )

    await storage.add_message_to_conversation(123, message1)
    await storage.add_message_to_conversation(123, message2)

    conversation = await storage.get_conversation(123)
    assert conversation is not None
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == "user"
    assert conversation.messages[1].role == "assistant"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clear_conversation(storage: SQLiteStorage):
    """Test clearing a conversation (soft delete)"""
    message1 = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )
    message2 = Message(
        user_id=123,
        role="assistant",
        content="Hi!",
        created_at=datetime.now(),
        content_length=len("Hi!"),
    )

    await storage.add_message_to_conversation(123, message1)
    await storage.add_message_to_conversation(123, message2)

    # Verify messages exist
    conversation_before = await storage.get_conversation(123)
    assert conversation_before is not None
    assert len(conversation_before.messages) == 2

    # Clear conversation
    await storage.clear_conversation(123)

    # Verify no active messages
    conversation_after = await storage.get_conversation(123)
    assert conversation_after is None


# Metrics tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_total_users(storage: SQLiteStorage):
    """Test getting total number of users"""
    user1 = User(user_id=123, username="user1", first_name="User1", created_at=datetime.now())
    user2 = User(user_id=456, username="user2", first_name="User2", created_at=datetime.now())

    await storage.add_user(user1)
    await storage.add_user(user2)

    total = await storage.get_total_users()
    assert total == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_total_messages(storage: SQLiteStorage):
    """Test getting total number of messages"""
    message1 = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )
    message2 = Message(
        user_id=123,
        role="assistant",
        content="Hi!",
        created_at=datetime.now(),
        content_length=len("Hi!"),
    )
    message3 = Message(
        user_id=456,
        role="user",
        content="Test",
        created_at=datetime.now(),
        content_length=len("Test"),
    )

    await storage.add_message_to_conversation(123, message1)
    await storage.add_message_to_conversation(123, message2)
    await storage.add_message_to_conversation(456, message3)

    total = await storage.get_total_messages()
    assert total == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_metrics(storage: SQLiteStorage):
    """Test getting all storage metrics"""
    user = User(user_id=123, username="user1", first_name="User1", created_at=datetime.now())
    await storage.add_user(user)

    message = Message(
        user_id=123,
        role="user",
        content="Hello",
        created_at=datetime.now(),
        content_length=len("Hello"),
    )
    await storage.add_message_to_conversation(123, message)
    await storage.increment_user_message_count(123)

    metrics = await storage.get_metrics()
    assert metrics["total_users"] == 1
    assert metrics["total_conversations"] == 1
    assert metrics["total_messages"] == 1
    assert metrics["total_user_messages"] == 1


# Soft delete tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soft_delete_user(storage: SQLiteStorage):
    """Test that soft deleted users are not returned"""
    user = User(user_id=123, username="user1", first_name="User1", created_at=datetime.now())
    await storage.add_user(user)

    # Soft delete user directly in DB
    async with storage._session_maker() as session:
        stmt = select(UserDB).where(UserDB.user_id == 123)
        result = await session.execute(stmt)
        user_db = result.scalar_one()
        user_db.deleted_at = datetime.now()
        await session.commit()

    # Verify user is not returned
    assert not await storage.user_exists(123)
    assert await storage.get_user(123) is None
    assert len(await storage.get_all_users()) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soft_delete_messages_in_cleared_conversation(storage: SQLiteStorage):
    """Test that messages in cleared conversation are soft deleted"""
    message = Message(
        user_id=123,
        role="user",
        content="Test",
        created_at=datetime.now(),
        content_length=len("Test"),
    )
    await storage.add_message_to_conversation(123, message)

    await storage.clear_conversation(123)

    # Verify no active messages returned
    conversation = await storage.get_conversation(123)
    assert conversation is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_conversations_per_user(storage: SQLiteStorage):
    """Test that user can have multiple conversations"""
    # Add messages to create first conversation
    message1 = Message(
        user_id=123,
        role="user",
        content="First conversation",
        created_at=datetime.now(),
        content_length=len("First conversation"),
    )
    await storage.add_message_to_conversation(123, message1)

    # Clear first conversation
    await storage.clear_conversation(123)

    # Add messages to create second conversation
    message2 = Message(
        user_id=123,
        role="user",
        content="Second conversation",
        created_at=datetime.now(),
        content_length=len("Second conversation"),
    )
    await storage.add_message_to_conversation(123, message2)

    # Verify only second conversation is active
    conversation = await storage.get_conversation(123)
    assert conversation is not None
    assert len(conversation.messages) == 1
    assert conversation.messages[0].content == "Second conversation"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_exclude_soft_deleted(storage: SQLiteStorage):
    """Test that metrics exclude soft deleted entities"""
    user = User(user_id=123, username="user1", first_name="User1", created_at=datetime.now())
    await storage.add_user(user)

    message = Message(
        user_id=123,
        role="user",
        content="Test",
        created_at=datetime.now(),
        content_length=len("Test"),
    )
    await storage.add_message_to_conversation(123, message)

    # Check metrics before delete
    metrics_before = await storage.get_metrics()
    assert metrics_before["total_messages"] == 1
    assert metrics_before["total_conversations"] == 1

    # Clear conversation
    await storage.clear_conversation(123)

    # Check metrics after delete
    metrics_after = await storage.get_metrics()
    assert metrics_after["total_messages"] == 0
    assert metrics_after["total_conversations"] == 0
