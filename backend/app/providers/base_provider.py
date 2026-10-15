"""Abstract base class for LLM providers.

Defines the contract that all LLM provider implementations must follow.
The rest of the application interacts with this interface only, enabling
provider swapping without touching any other code.

Key design decisions:
    - generate_test_cases() is the single public API.
    - Retries with exponential backoff are handled in the base class.
    - Each provider only needs to implement _call_api().
    - Error handling is standardized across providers.

What can go wrong:
    - API key missing or invalid → LLMAuthenticationError
    - Rate limit exceeded → LLMRateLimitError (retried automatically)
    - Network/timeout errors → LLMConnectionError (retried automatically)
    - Malformed response → LLMResponseError
    - Model not found → LLMModelError
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Maximum retry attempts for transient errors
MAX_RETRIES = 3
# Base delay for exponential backoff (seconds)
BASE_RETRY_DELAY = 2.0


# ---- Custom Exceptions ----

class LLMError(Exception):
    """Base exception for all LLM provider errors."""


class LLMAuthenticationError(LLMError):
    """API key is missing, invalid, or expired."""


class LLMRateLimitError(LLMError):
    """Rate limit exceeded. Transient — can be retried."""


class LLMConnectionError(LLMError):
    """Network error, timeout, or service unavailable. Transient."""


class LLMResponseError(LLMError):
    """LLM returned a response that could not be parsed."""


class LLMModelError(LLMError):
    """Requested model is not available or not found."""


# ---- Data Classes ----

@dataclass
class GenerationResult:
    """Result of an LLM test-case generation call.

    Attributes:
        raw_response: The raw text returned by the LLM.
        test_cases: Parsed list of test case dictionaries.
        parse_errors: Errors encountered during response parsing.
        provider: Name of the provider used (e.g., "gemini").
        model: Model name used (e.g., "gemini-2.5-flash").
        generation_time_ms: Wall-clock time of the API call in milliseconds.
    """
    raw_response: str
    test_cases: list[dict] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    generation_time_ms: float = 0.0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Subclasses must implement:
        - provider_name (property): unique identifier for the provider
        - _call_api(prompt, model): make the actual API call and return raw text

    The base class handles:
        - Retry logic with exponential backoff
        - Response parsing (JSON extraction)
        - Error classification and logging
        - Timing measurement
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider (e.g., 'gemini', 'openai')."""
        ...

    @abstractmethod
    def _call_api(self, prompt: str, model: str) -> str:
        """Make the actual API call and return the raw response text.

        Args:
            prompt: The fully constructed prompt to send.
            model: The model name to use.

        Returns:
            Raw response text from the LLM.

        Raises:
            LLMAuthenticationError: Invalid or missing API key.
            LLMRateLimitError: Rate limit exceeded.
            LLMConnectionError: Network/timeout error.
            LLMModelError: Model not found.
            LLMResponseError: Empty or unparseable response.
        """
        ...

    def generate_test_cases(
        self, prompt: str, model: str
    ) -> GenerationResult:
        """Generate test cases by calling the LLM with retry logic.

        This is the public API. It handles:
        1. Calling the provider-specific _call_api() method
        2. Retrying on transient errors (rate limit, network)
        3. Parsing the JSON response
        4. Measuring generation time
        5. Logging the outcome

        Args:
            prompt: The fully constructed prompt including spec and instructions.
            model: The model name to use for generation.

        Returns:
            GenerationResult containing parsed test cases and metadata.

        Raises:
            LLMAuthenticationError: If the API key is invalid (not retried).
            LLMModelError: If the model is not found (not retried).
            LLMError: If all retries are exhausted.
        """
        start_time = time.time()
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    "LLM API call attempt %d/%d (provider=%s, model=%s)",
                    attempt, MAX_RETRIES, self.provider_name, model,
                )
                raw_response = self._call_api(prompt, model)

                elapsed_ms = (time.time() - start_time) * 1000

                # Parse the response
                test_cases, parse_errors = self._parse_response(raw_response)

                result = GenerationResult(
                    raw_response=raw_response,
                    test_cases=test_cases,
                    parse_errors=parse_errors,
                    provider=self.provider_name,
                    model=model,
                    generation_time_ms=round(elapsed_ms, 2),
                )

                logger.info(
                    "LLM generation completed: %d test cases, %d parse errors (%.0fms)",
                    len(test_cases), len(parse_errors), elapsed_ms,
                )
                return result

            except (LLMAuthenticationError, LLMModelError):
                # Non-retryable errors — fail immediately
                raise

            except (LLMRateLimitError, LLMConnectionError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        "Transient LLM error (attempt %d/%d), retrying in %.1fs: %s",
                        attempt, MAX_RETRIES, delay, str(e),
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "All %d LLM retry attempts exhausted: %s",
                        MAX_RETRIES, str(e),
                    )

            except Exception as e:
                # Unexpected errors — wrap and raise
                logger.error("Unexpected LLM error: %s", str(e))
                raise LLMError(f"Unexpected error from {self.provider_name}: {e}") from e

        # All retries exhausted
        raise LLMError(
            f"Failed after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    def _parse_response(self, raw: str) -> tuple[list[dict], list[str]]:
        """Parse the raw LLM response into a list of test case dicts.

        Handles common response patterns:
        1. A JSON array directly: [{"name": "...", ...}, ...]
        2. A JSON object with a key containing the array: {"test_cases": [...]}
        3. JSON embedded in markdown code blocks: ```json [...] ```

        Args:
            raw: Raw text response from the LLM.

        Returns:
            Tuple of (parsed test cases list, parse error messages list).
        """
        errors: list[str] = []

        if not raw or not raw.strip():
            return [], ["Empty response from LLM"]

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove opening fence (with optional language tag)
            first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
            cleaned = cleaned[first_newline + 1:]
            # Remove closing fence
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3].rstrip()

        # Try to parse as JSON
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            errors.append(f"Failed to parse LLM response as JSON: {e}")
            return [], errors

        # If it's directly a list, use it
        if isinstance(parsed, list):
            return parsed, errors

        # If it's a dict, look for common keys containing the array
        if isinstance(parsed, dict):
            for key in ("test_cases", "tests", "testCases", "data", "results"):
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key], errors

            # Maybe it's a single test case
            if "method" in parsed and "endpoint" in parsed:
                return [parsed], errors

            errors.append(
                "JSON response is a dict but doesn't contain a recognizable "
                "test case array. Expected a key like 'test_cases' or 'tests'."
            )
            return [], errors

        errors.append(f"Unexpected JSON type: {type(parsed).__name__}")
        return [], errors
"""
    Description="Base class for LLM providers with retry logic, response parsing, and error handling"
    TargetFile="C:\\Users\\Krishna Chaitanya\\.gemini\\antigravity\\scratch\\ai-test-automation-framework\\backend\\app\\providers\\base_provider.py"
"""
