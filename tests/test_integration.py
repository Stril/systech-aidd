"""Integration tests for full workflow scenarios"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.context_manager import ContextManager
from src.memory_storage import MemoryStorage
from src.message_handler import MessageHandler
from src.openai_client import OpenAIClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_message_flow():
    """Test complete flow: message → handler → llm → storage → response"""
    # Setup real components
    context_manager = ContextManager(max_messages=10)
    storage = MemoryStorage()

    # Mock OpenAI client
    mock_openai = Mock(spec=OpenAIClient)
    mock_openai.send_message = AsyncMock(return_value="Hello! How can I help you?")

    # Create handler
    handler = MessageHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        context_manager=context_manager,
        storage=storage,
    )

    # Mock Telegram message
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.text = "Hello bot"
    message.chat.id = 12345
    message.bot = None  # No bot for simplicity

    # Execute full flow
    await handler.handle_text_message(message)

    # Verify context manager has both user and assistant messages
    context = context_manager.get_context(12345)
    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello bot"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Hello! How can I help you?"

    # Verify storage has both messages
    conversation = await storage.get_conversation(12345)
    assert conversation is not None
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Hello bot"
    assert conversation.messages[1].role == "assistant"
    assert conversation.messages[1].content == "Hello! How can I help you?"

    # Verify message was sent
    message.answer.assert_called_once_with("Hello! How can I help you?")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reset_clears_all_components():
    """Test /reset command clears context and storage"""
    # Setup real components
    context_manager = ContextManager(max_messages=10)
    storage = MemoryStorage()

    handler = MessageHandler(
        openai_client=None,
        system_prompt="",
        context_manager=context_manager,
        storage=storage,
    )

    # Add some data first
    user_id = 12345
    context_manager.add_message(user_id, "user", "Hello")
    context_manager.add_message(user_id, "assistant", "Hi")

    from src.models import Message as StorageMessage

    await storage.add_message_to_conversation(
        user_id,
        StorageMessage(
            user_id=user_id,
            role="user",
            content="Hello",
            created_at=datetime.now(),
            content_length=len("Hello"),
        ),
    )
    await storage.add_message_to_conversation(
        user_id,
        StorageMessage(
            user_id=user_id,
            role="assistant",
            content="Hi",
            created_at=datetime.now(),
            content_length=len("Hi"),
        ),
    )

    # Verify data exists
    assert len(context_manager.get_context(user_id)) == 2
    conv = await storage.get_conversation(user_id)
    assert conv is not None
    assert len(conv.messages) == 2

    # Mock Telegram message for /reset
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.text = "/reset"
    message.chat.id = user_id

    # Execute reset
    await handler.handle_reset(message)

    # Verify everything is cleared
    assert len(context_manager.get_context(user_id)) == 0
    conv = await storage.get_conversation(user_id)
    assert conv is not None
    assert len(conv.messages) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_error_flow():
    """Test error handling across components when LLM fails"""
    # Setup real components
    context_manager = ContextManager(max_messages=10)
    storage = MemoryStorage()

    # Mock OpenAI client that raises error
    from src.exceptions import LLMConnectionError

    mock_openai = Mock(spec=OpenAIClient)
    mock_openai.send_message = AsyncMock(side_effect=LLMConnectionError("Connection failed"))

    handler = MessageHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        context_manager=context_manager,
        storage=storage,
    )

    # Mock Telegram message
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.text = "Hello bot"
    message.chat.id = 12345
    message.bot = None

    # Execute flow (should handle error gracefully)
    await handler.handle_text_message(message)

    # Verify user message was added to context and storage
    context = context_manager.get_context(12345)
    assert len(context) == 1
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello bot"

    conversation = await storage.get_conversation(12345)
    assert conversation is not None
    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "user"

    # Verify error message was sent to user
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "подключиться" in call_args.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_messages_conversation():
    """Test full conversation with multiple back-and-forth messages"""
    # Setup real components
    context_manager = ContextManager(max_messages=10)
    storage = MemoryStorage()

    # Mock OpenAI client with different responses
    mock_openai = Mock(spec=OpenAIClient)
    responses = ["Hi there!", "I'm doing great, thanks!", "Goodbye!"]
    mock_openai.send_message = AsyncMock(side_effect=responses)

    handler = MessageHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        context_manager=context_manager,
        storage=storage,
    )

    user_id = 12345

    # Simulate conversation
    messages_to_send = ["Hello", "How are you?", "Bye"]

    for user_msg in messages_to_send:
        message = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = user_id
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.text = user_msg
        message.chat.id = user_id
        message.bot = None

        await handler.handle_text_message(message)

    # Verify context has all messages in order
    context = context_manager.get_context(user_id)
    assert len(context) == 6  # 3 user + 3 assistant messages

    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Hi there!"

    assert context[2]["role"] == "user"
    assert context[2]["content"] == "How are you?"
    assert context[3]["role"] == "assistant"
    assert context[3]["content"] == "I'm doing great, thanks!"

    assert context[4]["role"] == "user"
    assert context[4]["content"] == "Bye"
    assert context[5]["role"] == "assistant"
    assert context[5]["content"] == "Goodbye!"

    # Verify storage has all messages
    conversation = await storage.get_conversation(user_id)
    assert conversation is not None
    assert len(conversation.messages) == 6


@pytest.mark.integration
@pytest.mark.asyncio
async def test_start_command_creates_user_in_storage():
    """Test /start command creates user record in storage"""
    storage = MemoryStorage()

    handler = MessageHandler(
        openai_client=None,
        system_prompt="",
        context_manager=None,
        storage=storage,
    )

    user_id = 12345

    # Mock Telegram message for /start
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.text = "/start"
    message.chat.id = user_id

    # Execute start command
    await handler.handle_start(message)

    # Verify user was created in storage
    assert await storage.user_exists(user_id)
    user = storage.get_user(user_id)
    assert user is not None
    assert user.user_id == user_id
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.message_count == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_recovery_after_restart():
    """Test context is restored from database after restart simulation"""
    # Setup real components
    context_manager = ContextManager(max_messages=10)
    storage = MemoryStorage()

    # Mock OpenAI client
    mock_openai = Mock(spec=OpenAIClient)
    mock_openai.send_message = AsyncMock(
        side_effect=[
            "Response 1",
            "Response 2",
            "Response 3 (with restored context)",
        ]
    )

    handler = MessageHandler(
        openai_client=mock_openai,
        system_prompt="You are a helpful assistant",
        context_manager=context_manager,
        storage=storage,
    )

    user_id = 12345

    # Step 1: Send a few messages before "restart"
    messages_before_restart = ["Message 1", "Message 2"]

    for user_msg in messages_before_restart:
        message = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = user_id
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.text = user_msg
        message.chat.id = user_id
        message.bot = None

        await handler.handle_text_message(message)

    # Verify context has 4 messages (2 user + 2 assistant)
    context_before = context_manager.get_context(user_id)
    assert len(context_before) == 4

    # Verify storage has all messages
    conversation_before = await storage.get_conversation(user_id)
    assert conversation_before is not None
    assert len(conversation_before.messages) == 4

    # Step 2: Simulate app restart by clearing in-memory context
    context_manager.reset_context(user_id)

    # Verify context is empty (simulates restart)
    assert len(context_manager.get_context(user_id)) == 0

    # But storage still has messages
    conversation_after_reset = await storage.get_conversation(user_id)
    assert conversation_after_reset is not None
    assert len(conversation_after_reset.messages) == 4

    # Step 3: Send a new message after "restart"
    message_after_restart = AsyncMock()
    message_after_restart.from_user = MagicMock()
    message_after_restart.from_user.id = user_id
    message_after_restart.from_user.username = "testuser"
    message_after_restart.from_user.first_name = "Test"
    message_after_restart.text = "Message 3 after restart"
    message_after_restart.chat.id = user_id
    message_after_restart.bot = None

    await handler.handle_text_message(message_after_restart)

    # Step 4: Verify context was restored from database
    context_after = context_manager.get_context(user_id)

    # Should have 6 messages: 4 restored + 1 new user + 1 new assistant
    assert len(context_after) == 6

    # Verify restored messages
    assert context_after[0]["role"] == "user"
    assert context_after[0]["content"] == "Message 1"
    assert context_after[1]["role"] == "assistant"
    assert context_after[1]["content"] == "Response 1"
    assert context_after[2]["role"] == "user"
    assert context_after[2]["content"] == "Message 2"
    assert context_after[3]["role"] == "assistant"
    assert context_after[3]["content"] == "Response 2"

    # Verify new messages
    assert context_after[4]["role"] == "user"
    assert context_after[4]["content"] == "Message 3 after restart"
    assert context_after[5]["role"] == "assistant"
    assert context_after[5]["content"] == "Response 3 (with restored context)"

    # Verify storage also has all 6 messages
    final_conversation = await storage.get_conversation(user_id)
    assert final_conversation is not None
    assert len(final_conversation.messages) == 6
