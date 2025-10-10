"""OpenAI client for LLM interactions via OpenRouter"""
import logging
from typing import List
from openai import OpenAI

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
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self._model = model
        
        logger.info(f"openai_client|status=initialized|model={model}")
    
    def send_message(self, messages: List[dict], system_prompt: str) -> str:
        """Send message to LLM and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt for the conversation
            
        Returns:
            Response text from LLM
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Prepend system prompt to messages
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"llm_request|model={self._model}|messages_count={len(all_messages)}")
            
            # Make API call
            response = self._client.chat.completions.create(
                model=self._model,
                messages=all_messages
            )
            
            content = response.choices[0].message.content
            logger.info(f"llm_response|response_length={len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"llm_error|error={str(e)}")
            raise

