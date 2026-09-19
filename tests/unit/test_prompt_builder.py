"""Unit tests for test generation prompts."""

from app.prompts.test_generation import build_generation_prompt, SYSTEM_PROMPT

def test_build_generation_prompt():
    api_spec = {"openapi": "3.0.0", "paths": {"/users": {"get": {}}}}
    categories = ["functional", "negative"]
    test_count = 5
    
    prompt = build_generation_prompt(api_spec, test_count, categories)
    
    # Check that system prompt is included
    assert SYSTEM_PROMPT in prompt
    
    # Check that user variables are injected
    assert "5 API test cases" in prompt
    assert "functional, negative" in prompt
    
    # Check that spec is included
    assert '"/users"' in prompt
    assert '"get"' in prompt
