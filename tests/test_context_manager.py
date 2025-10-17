import pytest

from src.context_manager import ContextManager


@pytest.mark.unit
def test_context_manager_initialization():
    """Test ContextManager initialization with default and custom values"""
    cm = ContextManager()
    assert cm._max_messages == 10

    cm_custom = ContextManager(max_messages=5)
    assert cm_custom._max_messages == 5


@pytest.mark.unit
def test_add_message_to_new_user():
    """Test adding first message to a new user"""
    cm = ContextManager()
    cm.add_message(123, "user", "Hello")

    context = cm.get_context(123)
    assert len(context) == 1
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"


@pytest.mark.unit
def test_add_multiple_messages():
    """Test adding multiple messages to context"""
    cm = ContextManager()
    cm.add_message(123, "user", "Hello")
    cm.add_message(123, "assistant", "Hi there!")
    cm.add_message(123, "user", "How are you?")

    context = cm.get_context(123)
    assert len(context) == 3
    assert context[0]["role"] == "user"
    assert context[1]["role"] == "assistant"
    assert context[2]["role"] == "user"


@pytest.mark.unit
def test_context_trimming():
    """Test that context is trimmed to max_messages"""
    cm = ContextManager(max_messages=3)

    # Add 5 messages
    for i in range(5):
        cm.add_message(123, "user", f"Message {i}")

    context = cm.get_context(123)
    assert len(context) == 3
    # Should keep last 3 messages
    assert context[0]["content"] == "Message 2"
    assert context[1]["content"] == "Message 3"
    assert context[2]["content"] == "Message 4"


@pytest.mark.unit
def test_reset_context():
    """Test resetting user's context"""
    cm = ContextManager()
    cm.add_message(123, "user", "Hello")
    cm.add_message(123, "assistant", "Hi!")

    assert len(cm.get_context(123)) == 2

    cm.reset_context(123)
    assert len(cm.get_context(123)) == 0


@pytest.mark.unit
def test_reset_context_for_nonexistent_user():
    """Test resetting context for user without context"""
    cm = ContextManager()
    # Should not raise error
    cm.reset_context(999)
    assert len(cm.get_context(999)) == 0


@pytest.mark.unit
def test_multiple_users_separate_contexts():
    """Test that different users have separate contexts"""
    cm = ContextManager()

    cm.add_message(123, "user", "User 123 message")
    cm.add_message(456, "user", "User 456 message")

    context_123 = cm.get_context(123)
    context_456 = cm.get_context(456)

    assert len(context_123) == 1
    assert len(context_456) == 1
    assert context_123[0]["content"] == "User 123 message"
    assert context_456[0]["content"] == "User 456 message"


@pytest.mark.unit
def test_get_context_for_new_user():
    """Test getting context for user without any messages"""
    cm = ContextManager()
    context = cm.get_context(999)
    assert context == []


@pytest.mark.unit
def test_context_preserves_order():
    """Test that context preserves message order"""
    cm = ContextManager()

    messages = [
        ("user", "First"),
        ("assistant", "Second"),
        ("user", "Third"),
        ("assistant", "Fourth"),
    ]

    for role, content in messages:
        cm.add_message(123, role, content)

    context = cm.get_context(123)
    assert len(context) == 4

    for i, (role, content) in enumerate(messages):
        assert context[i]["role"] == role
        assert context[i]["content"] == content


@pytest.mark.unit
def test_load_context_empty_list():
    """Test loading context with empty message list"""
    cm = ContextManager()
    cm.load_context(123, [])

    context = cm.get_context(123)
    assert len(context) == 0


@pytest.mark.unit
def test_load_context_with_messages():
    """Test loading context with several messages"""
    cm = ContextManager()

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
    ]

    cm.load_context(123, messages)

    context = cm.get_context(123)
    assert len(context) == 3
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Hi there!"
    assert context[2]["role"] == "user"
    assert context[2]["content"] == "How are you?"


@pytest.mark.unit
def test_load_context_exceeds_max_messages():
    """Test that load_context trims to max_messages limit"""
    cm = ContextManager(max_messages=3)

    # Create 5 messages
    messages = [
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Message 2"},
        {"role": "user", "content": "Message 3"},
        {"role": "assistant", "content": "Message 4"},
        {"role": "user", "content": "Message 5"},
    ]

    cm.load_context(123, messages)

    context = cm.get_context(123)
    assert len(context) == 3
    # Should keep last 3 messages
    assert context[0]["content"] == "Message 3"
    assert context[1]["content"] == "Message 4"
    assert context[2]["content"] == "Message 5"


@pytest.mark.unit
def test_load_context_for_new_user():
    """Test loading context for a user without existing context"""
    cm = ContextManager()

    messages = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "Response"},
    ]

    # User 999 has no prior context
    assert len(cm.get_context(999)) == 0

    cm.load_context(999, messages)

    context = cm.get_context(999)
    assert len(context) == 2
    assert context[0]["content"] == "First message"
    assert context[1]["content"] == "Response"


@pytest.mark.unit
def test_load_context_overwrites_existing():
    """Test that load_context overwrites existing context"""
    cm = ContextManager()

    # Add some messages manually
    cm.add_message(123, "user", "Old message 1")
    cm.add_message(123, "assistant", "Old message 2")

    assert len(cm.get_context(123)) == 2

    # Load new context - should replace old one
    new_messages = [
        {"role": "user", "content": "New message 1"},
        {"role": "assistant", "content": "New message 2"},
        {"role": "user", "content": "New message 3"},
    ]

    cm.load_context(123, new_messages)

    context = cm.get_context(123)
    assert len(context) == 3
    assert context[0]["content"] == "New message 1"
    assert context[1]["content"] == "New message 2"
    assert context[2]["content"] == "New message 3"
