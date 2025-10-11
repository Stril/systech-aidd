"""OpenAI client for LLM interactions via OpenRouter"""

import asyncio
import logging
from functools import partial
from typing import Any

import openai
from openai import OpenAI

from src.exceptions import (
    LLMAPIError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnknownError,
)

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with LLM through OpenAI-compatible API"""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize OpenAI client

        Args:
            api_key: API key for OpenRouter
            base_url: Base URL for API (e.g., https://openrouter.ai/api/v1)
            model: Model identifier (e.g., openai/gpt-3.5-turbo)
        """
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

        logger.info(f"openai_client|status=initialized|model={model}")

    def _sync_send_message(self, messages: list[dict[str, Any]], system_prompt: str) -> str:
        """Synchronous implementation of send_message

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt for the conversation

        Returns:
            Response text from LLM

        Raises:
            LLMConnectionError: If cannot connect to LLM service
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
            LLMAPIError: If API returns an error
            LLMUnknownError: If unknown error occurs
        """
        try:
            # Prepend system prompt to messages
            all_messages = [{"role": "system", "content": system_prompt}] + messages

            logger.info(f"llm_request|model={self._model}|messages_count={len(all_messages)}")

            # Make API call
            response = self._client.chat.completions.create(
                model=self._model, messages=all_messages
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMAPIError("LLM returned empty response")
            logger.info(f"llm_response|response_length={len(content)}")

            return content

        except openai.APITimeoutError as e:
            logger.error(f"llm_error|type=timeout|error={str(e)}")
            raise LLMTimeoutError("Превышено время ожидания ответа от LLM") from e

        except openai.RateLimitError as e:
            logger.error(f"llm_error|type=rate_limit|error={str(e)}")
            raise LLMRateLimitError("Превышен лимит запросов к LLM") from e

        except openai.APIConnectionError as e:
            logger.error(f"llm_error|type=connection_error|error={str(e)}")
            raise LLMConnectionError("Не удалось подключиться к сервису LLM") from e

        except openai.APIError as e:
            logger.error(f"llm_error|type=api_error|error={str(e)}")
            raise LLMAPIError(f"Ошибка API LLM: {str(e)}") from e

        except Exception as e:
            logger.error(f"llm_error|type=unknown|error={str(e)}")
            raise LLMUnknownError(f"Неизвестная ошибка LLM: {str(e)}") from e

    async def send_message(self, messages: list[dict[str, Any]], system_prompt: str) -> str:
        """Send message to LLM and get response (async version)

        Executes synchronous OpenAI API call in a thread pool to avoid blocking event loop.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt for the conversation

        Returns:
            Response text from LLM

        Raises:
            LLMConnectionError: If cannot connect to LLM service
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
            LLMAPIError: If API returns an error
            LLMUnknownError: If unknown error occurs
        """
        loop = asyncio.get_event_loop()
        # Execute synchronous operation in thread pool to avoid blocking event loop
        return await loop.run_in_executor(
            None, partial(self._sync_send_message, messages, system_prompt)
        )
