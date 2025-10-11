"""Property-based tests for ContextManager using Hypothesis"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.context_manager import ContextManager


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    messages=st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=20),
)
def test_context_never_exceeds_max_messages(user_id, messages):
    """Property: context length never exceeds max_messages"""
    max_messages = 10
    cm = ContextManager(max_messages=max_messages)

    # Add all messages as user messages
    for msg in messages:
        cm.add_message(user_id, "user", msg)

    # Get context
    context = cm.get_context(user_id)

    # Property: context length should never exceed max_messages
    assert len(context) <= max_messages


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    max_messages=st.integers(min_value=1, max_value=50),
    message_count=st.integers(min_value=0, max_value=100),
)
def test_context_respects_configured_limit(user_id, max_messages, message_count):
    """Property: context respects any configured limit"""
    cm = ContextManager(max_messages=max_messages)

    # Add message_count messages
    for i in range(message_count):
        cm.add_message(user_id, "user", f"Message {i}")

    context = cm.get_context(user_id)

    # Property: context should never exceed the configured limit
    assert len(context) <= max_messages


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    messages=st.lists(
        st.tuples(st.sampled_from(["user", "assistant"]), st.text(min_size=1, max_size=100)),
        min_size=1,
        max_size=30,
    ),
)
def test_context_preserves_last_messages(user_id, messages):
    """Property: context always preserves the most recent messages"""
    max_messages = 10
    cm = ContextManager(max_messages=max_messages)

    # Add all messages
    for role, content in messages:
        cm.add_message(user_id, role, content)

    context = cm.get_context(user_id)

    # If we have more messages than max_messages, check that the last ones are preserved
    if len(messages) > max_messages:
        last_messages = messages[-max_messages:]
        assert len(context) == max_messages

        # Verify the last messages are in the context
        for i, (role, content) in enumerate(last_messages):
            assert context[i]["role"] == role
            assert context[i]["content"] == content


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    messages=st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=20),
)
def test_reset_always_clears_context(user_id, messages):
    """Property: reset always clears all context"""
    cm = ContextManager()

    # Add messages
    for msg in messages:
        cm.add_message(user_id, "user", msg)

    # Verify messages were added
    assert len(cm.get_context(user_id)) > 0

    # Reset context
    cm.reset_context(user_id)

    # Property: context should always be empty after reset
    assert len(cm.get_context(user_id)) == 0


@pytest.mark.property
@given(
    user_ids=st.lists(
        st.integers(min_value=1, max_value=100000), min_size=2, max_size=10, unique=True
    ),
    message_content=st.text(min_size=1, max_size=100),
)
def test_users_have_isolated_contexts(user_ids, message_content):
    """Property: different users always have isolated contexts"""
    cm = ContextManager()

    # Add same message for each user
    for user_id in user_ids:
        cm.add_message(user_id, "user", message_content)

    # Property: each user should have exactly one message
    for user_id in user_ids:
        context = cm.get_context(user_id)
        assert len(context) == 1
        assert context[0]["content"] == message_content

    # Modify one user's context
    cm.add_message(user_ids[0], "assistant", "Response")

    # Property: only the first user's context should have 2 messages
    assert len(cm.get_context(user_ids[0])) == 2
    for user_id in user_ids[1:]:
        assert len(cm.get_context(user_id)) == 1


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    messages=st.lists(
        st.tuples(st.sampled_from(["user", "assistant"]), st.text(min_size=1, max_size=100)),
        min_size=1,
        max_size=20,
    ),
)
def test_messages_maintain_order(user_id, messages):
    """Property: messages are always returned in the order they were added"""
    cm = ContextManager(max_messages=100)  # Large enough to not trigger trimming

    # Add messages
    for role, content in messages:
        cm.add_message(user_id, role, content)

    context = cm.get_context(user_id)

    # Property: order should be preserved
    assert len(context) == len(messages)
    for i, (role, content) in enumerate(messages):
        assert context[i]["role"] == role
        assert context[i]["content"] == content


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
)
def test_get_context_for_new_user_returns_empty_list(user_id):
    """Property: getting context for new user always returns empty list"""
    cm = ContextManager()

    # Property: new user should always have empty context
    context = cm.get_context(user_id)
    assert context == []
    assert isinstance(context, list)
