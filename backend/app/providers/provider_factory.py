"""Factory for instantiating LLM providers."""

from app.providers.base_provider import BaseLLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.run_schemas import LLMProvider


def get_llm_provider(provider_name: str | LLMProvider) -> BaseLLMProvider:
    """Instantiate and return the requested LLM provider.
    
    Args:
        provider_name: The name of the provider ('gemini', 'openai', or 'mock').
        
    Returns:
        An instance of BaseLLMProvider.
        
    Raises:
        ValueError: If the provider_name is not supported.
    """
    if isinstance(provider_name, LLMProvider):
        name = provider_name.value
    else:
        name = provider_name.lower().strip()
    
    if name == "gemini":
        try:
            return GeminiProvider()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Gemini init failed ({e}). Falling back to MockProvider.")
            return MockProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "mock":
        return MockProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: '{provider_name}'. Supported: gemini, openai.")
