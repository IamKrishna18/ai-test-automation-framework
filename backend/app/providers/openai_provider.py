"""OpenAI LLM Provider implementation.

Uses the official openai Python SDK.
Configures structured JSON output using response_format={"type": "json_object"}.
"""

from typing import Any

import openai
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

from app.core.config import get_settings
from app.providers.base_provider import (
    BaseLLMProvider,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMModelError,
    LLMRateLimitError,
)


class OpenAIProvider(BaseLLMProvider):
    """Implementation of BaseLLMProvider for OpenAI."""

    def __init__(self):
        settings = get_settings()
        api_key = settings.openai_api_key
        if not api_key:
            raise LLMAuthenticationError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    def _call_api(self, prompt: str, model: str) -> str:
        """Make the API call to OpenAI.
        
        Args:
            prompt: The full prompt string.
            model: The OpenAI model name (e.g., 'gpt-4o').
            
        Returns:
            Raw JSON string from the model.
        """
        try:
            # We append an explicit instruction to return JSON object containing 'test_cases'
            # because JSON mode requires the word 'json' in the prompt and an object output.
            system_instruction = (
                "You are an expert QA engineer. Always return your response as a valid JSON object "
                "with a single key 'test_cases' containing a list of test cases."
            )
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("OpenAI returned an empty response")
                
            return content

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"Authentication failed: {e}") from e
        except RateLimitError as e:
            raise LLMRateLimitError(f"Rate limit exceeded: {e}") from e
        except APIConnectionError as e:
            raise LLMConnectionError(f"Network error calling OpenAI: {e}") from e
        except APIError as e:
            error_msg = str(e).lower()
            if "model" in error_msg and "not found" in error_msg:
                raise LLMModelError(f"Model {model} not found: {e}") from e
            raise LLMConnectionError(f"OpenAI API error: {e}") from e
        except Exception as e:
            raise LLMError(f"Unexpected error calling OpenAI: {e}") from e
