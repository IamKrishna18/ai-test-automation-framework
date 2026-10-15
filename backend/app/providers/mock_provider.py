"""Mock LLM Provider for demonstration purposes."""

import json

from app.providers.base_provider import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    """Returns hardcoded test cases without needing an API key."""

    @property
    def provider_name(self) -> str:
        return "mock"

    def _call_api(self, prompt: str, model: str) -> str:
        """Return a hardcoded JSON string of test cases."""
        mock_cases = {
            "test_cases": [
                {
                    "name": "Create user with missing email",
                    "description": "Verifies that the API rejects user creation when email is omitted.",
                    "category": "negative",
                    "method": "POST",
                    "endpoint": "/users",
                    "headers": {"Content-Type": "application/json"},
                    "query_params": {},
                    "path_params": {},
                    "body": {"name": "Test User", "age": 25},
                    "expected_status": 422,
                    "expected_fields": [],
                    "priority": "high"
                },
                {
                    "name": "Fetch non-existent user",
                    "description": "Verifies that fetching user ID 9999 returns 404.",
                    "category": "functional",
                    "method": "GET",
                    "endpoint": "/users/9999",
                    "headers": {},
                    "query_params": {},
                    "path_params": {"user_id": 9999},
                    "body": None,
                    "expected_status": 404,
                    "expected_fields": [],
                    "priority": "medium"
                },
                {
                    "name": "Create valid user",
                    "description": "Verifies that a well-formed user is created.",
                    "category": "functional",
                    "method": "POST",
                    "endpoint": "/users",
                    "headers": {"Content-Type": "application/json"},
                    "query_params": {},
                    "path_params": {},
                    "body": {"name": "Test User", "email": "test@example.com", "age": 25},
                    "expected_status": 201,
                    "expected_fields": ["id", "name", "email", "age"],
                    "priority": "high"
                },
                {
                    "name": "Hallucinated endpoint test",
                    "description": "This is an intentionally broken test that hallucinates a non-existent endpoint to prove the semantic validator catches it.",
                    "category": "edge_case",
                    "method": "GET",
                    "endpoint": "/users/search/invalid/endpoint",
                    "headers": {},
                    "query_params": {},
                    "path_params": {},
                    "body": None,
                    "expected_status": 200,
                    "expected_fields": [],
                    "priority": "low"
                }
            ]
        }
        return json.dumps(mock_cases)
