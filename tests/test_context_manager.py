from src.context_manager import ContextManager


def test_context_manager_initialization():
    """Test ContextManager initialization with default and custom values"""
    cm = ContextManager()
    assert cm._max_messages == 10

    cm_custom = ContextManager(max_messages=5)
    assert cm_custom._max_messages == 5


def test_add_message_to_new_user():
    """Test adding first message to a new user"""
    cm = ContextManager()
    cm.add_message(123, "user", "Hello")

    context = cm.get_context(123)
    assert len(context) == 1
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"


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


def test_reset_context():
    """Test resetting user's context"""
    cm = ContextManager()
    cm.add_message(123, "user", "Hello")
    cm.add_message(123, "assistant", "Hi!")

    assert len(cm.get_context(123)) == 2

    cm.reset_context(123)
    assert len(cm.get_context(123)) == 0


def test_reset_context_for_nonexistent_user():
    """Test resetting context for user without context"""
    cm = ContextManager()
    # Should not raise error
    cm.reset_context(999)
    assert len(cm.get_context(999)) == 0


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


def test_get_context_for_new_user():
    """Test getting context for user without any messages"""
    cm = ContextManager()
    context = cm.get_context(999)
    assert context == []


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
