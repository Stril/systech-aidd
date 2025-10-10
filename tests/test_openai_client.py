"""Tests for OpenAIClient class"""
import pytest
from unittest.mock import Mock, MagicMock
from src.openai_client import OpenAIClient


@pytest.fixture
def mock_openai_response():
    """Fixture for mock OpenAI API response"""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "This is a test response from LLM"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    return mock_response


def test_openai_client_initialization():
    """Test OpenAIClient initializes correctly"""
    client = OpenAIClient(
        api_key="test_key",
        base_url="https://test.com/api/v1",
        model="test-model"
    )
    
    assert client._model == "test-model"
    assert client._client is not None


def test_send_message_success(mock_openai_response):
    """Test successful message sending"""
    client = OpenAIClient("test_key", "https://test.com", "test-model")
    
    # Mock the API call
    client._client.chat.completions.create = Mock(return_value=mock_openai_response)
    
    messages = [{"role": "user", "content": "Hello"}]
    system_prompt = "You are a helpful assistant"
    
    result = client.send_message(messages, system_prompt)
    
    assert result == "This is a test response from LLM"
    
    # Verify API was called with correct parameters
    client._client.chat.completions.create.assert_called_once()
    call_args = client._client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "test-model"
    assert len(call_args.kwargs["messages"]) == 2  # system + user message
    assert call_args.kwargs["messages"][0]["role"] == "system"
    assert call_args.kwargs["messages"][1]["role"] == "user"


def test_send_message_with_multiple_messages(mock_openai_response):
    """Test sending multiple messages"""
    client = OpenAIClient("test_key", "https://test.com", "test-model")
    client._client.chat.completions.create = Mock(return_value=mock_openai_response)
    
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]
    system_prompt = "You are a helpful assistant"
    
    result = client.send_message(messages, system_prompt)
    
    assert result == "This is a test response from LLM"
    
    # Verify all messages were sent
    call_args = client._client.chat.completions.create.call_args
    assert len(call_args.kwargs["messages"]) == 4  # system + 3 messages


def test_send_message_api_error():
    """Test handling of API errors"""
    client = OpenAIClient("test_key", "https://test.com", "test-model")
    
    # Mock API to raise exception
    client._client.chat.completions.create = Mock(side_effect=Exception("API Error"))
    
    messages = [{"role": "user", "content": "Hello"}]
    system_prompt = "You are a helpful assistant"
    
    with pytest.raises(Exception) as exc_info:
        client.send_message(messages, system_prompt)
    
    assert "API Error" in str(exc_info.value)


def test_send_message_empty_messages(mock_openai_response):
    """Test sending with empty message list"""
    client = OpenAIClient("test_key", "https://test.com", "test-model")
    client._client.chat.completions.create = Mock(return_value=mock_openai_response)
    
    messages = []
    system_prompt = "You are a helpful assistant"
    
    result = client.send_message(messages, system_prompt)
    
    assert result == "This is a test response from LLM"
    
    # Should still have system prompt
    call_args = client._client.chat.completions.create.call_args
    assert len(call_args.kwargs["messages"]) == 1
    assert call_args.kwargs["messages"][0]["role"] == "system"

