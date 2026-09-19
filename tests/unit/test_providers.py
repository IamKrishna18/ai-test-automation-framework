"""Unit tests for the LLM provider abstraction layer."""

import pytest
from unittest.mock import patch, MagicMock

from app.providers.base_provider import BaseLLMProvider, LLMError, LLMRateLimitError
from app.providers.provider_factory import get_llm_provider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider


class DummyProvider(BaseLLMProvider):
    """A dummy provider for testing the base class retry and parse logic."""
    
    def __init__(self, responses, exceptions=None):
        self.responses = responses
        self.exceptions = exceptions or []
        self.call_count = 0
        
    @property
    def provider_name(self) -> str:
        return "dummy"
        
    def _call_api(self, prompt: str, model: str) -> str:
        self.call_count += 1
        
        if self.exceptions and len(self.exceptions) >= self.call_count:
            exc = self.exceptions[self.call_count - 1]
            if exc:
                raise exc
                
        if self.responses:
            idx = min(self.call_count - 1, len(self.responses) - 1)
            return self.responses[idx]
            
        return ""


class TestBaseProvider:
    
    def test_parse_valid_json_list(self):
        provider = DummyProvider([
            '[{"name": "test1", "endpoint": "/api", "method": "GET"}]'
        ])
        result = provider.generate_test_cases("prompt", "model")
        assert len(result.test_cases) == 1
        assert result.test_cases[0]["name"] == "test1"
        assert len(result.parse_errors) == 0

    def test_parse_json_with_markdown_fences(self):
        raw = '''```json
        {
            "test_cases": [
                {"name": "test1", "endpoint": "/api", "method": "GET"}
            ]
        }
        ```'''
        provider = DummyProvider([raw])
        result = provider.generate_test_cases("prompt", "model")
        assert len(result.test_cases) == 1
        assert result.test_cases[0]["name"] == "test1"

    def test_parse_json_dict_with_test_cases_key(self):
        raw = '{"test_cases": [{"name": "test1", "endpoint": "/api", "method": "GET"}]}'
        provider = DummyProvider([raw])
        result = provider.generate_test_cases("prompt", "model")
        assert len(result.test_cases) == 1

    def test_parse_invalid_json_returns_error(self):
        provider = DummyProvider(["This is not JSON"])
        result = provider.generate_test_cases("prompt", "model")
        assert len(result.test_cases) == 0
        assert len(result.parse_errors) == 1
        assert "Failed to parse LLM response as JSON" in result.parse_errors[0]

    @patch("time.sleep", return_value=None)  # skip actual sleep
    def test_retry_on_rate_limit(self, mock_sleep):
        provider = DummyProvider(
            responses=["", '[{"name": "test"}]'],
            exceptions=[LLMRateLimitError("Too many requests"), None]
        )
        result = provider.generate_test_cases("prompt", "model")
        
        assert provider.call_count == 2
        assert len(result.test_cases) == 1
        assert mock_sleep.called

    @patch("time.sleep", return_value=None)
    def test_fails_after_max_retries(self, mock_sleep):
        provider = DummyProvider(
            responses=[],
            exceptions=[LLMRateLimitError("Too many requests")] * 3
        )
        with pytest.raises(LLMError, match="Failed after 3 attempts"):
            provider.generate_test_cases("prompt", "model")
        
        assert provider.call_count == 3


class TestProviderFactory:
    
    @patch("app.providers.gemini_provider.get_settings")
    @patch("app.providers.gemini_provider.genai.Client")
    def test_get_gemini(self, mock_client, mock_settings):
        mock_settings.return_value.gemini_api_key = "test_key"
        provider = get_llm_provider("gemini")
        assert isinstance(provider, GeminiProvider)
        
    @patch("app.providers.openai_provider.get_settings")
    @patch("app.providers.openai_provider.OpenAI")
    def test_get_openai(self, mock_client, mock_settings):
        mock_settings.return_value.openai_api_key = "test_key"
        provider = get_llm_provider("openai")
        assert isinstance(provider, OpenAIProvider)
        
    def test_get_invalid_provider(self):
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm_provider("claude")
