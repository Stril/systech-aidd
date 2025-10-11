"""Custom exceptions for the bot"""


class LLMError(Exception):
    """Base exception for LLM-related errors"""

    pass


class LLMConnectionError(LLMError):
    """Raised when cannot connect to LLM service"""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""

    pass


class LLMRateLimitError(LLMError):
    """Raised when rate limit is exceeded"""

    pass


class LLMAPIError(LLMError):
    """Raised when LLM API returns an error"""

    pass


class LLMUnknownError(LLMError):
    """Raised when an unknown error occurs with LLM"""

    pass
