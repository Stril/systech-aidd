"""Tests for custom exceptions"""

from src.exceptions import (
    LLMAPIError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnknownError,
)


def test_llm_error_base():
    """Test LLMError base exception"""
    error = LLMError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_llm_connection_error():
    """Test LLMConnectionError"""
    error = LLMConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, LLMError)
    assert isinstance(error, Exception)


def test_llm_timeout_error():
    """Test LLMTimeoutError"""
    error = LLMTimeoutError("Request timeout")
    assert str(error) == "Request timeout"
    assert isinstance(error, LLMError)


def test_llm_rate_limit_error():
    """Test LLMRateLimitError"""
    error = LLMRateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, LLMError)


def test_llm_api_error():
    """Test LLMAPIError"""
    error = LLMAPIError("API error")
    assert str(error) == "API error"
    assert isinstance(error, LLMError)


def test_llm_unknown_error():
    """Test LLMUnknownError"""
    error = LLMUnknownError("Unknown error")
    assert str(error) == "Unknown error"
    assert isinstance(error, LLMError)


def test_exception_hierarchy():
    """Test exception hierarchy"""
    # All LLM exceptions should be catchable by LLMError
    exceptions = [
        LLMConnectionError("test"),
        LLMTimeoutError("test"),
        LLMRateLimitError("test"),
        LLMAPIError("test"),
        LLMUnknownError("test"),
    ]

    for exc in exceptions:
        assert isinstance(exc, LLMError)
        assert isinstance(exc, Exception)
