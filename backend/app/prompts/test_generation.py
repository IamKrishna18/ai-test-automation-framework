"""Prompt templates for test generation."""

SYSTEM_PROMPT = """
You are a senior software QA engineer specializing in API test automation.
Your task is to analyze an API specification and generate structured test cases.

You must output a JSON object with a single key 'test_cases', which is an array of test case objects.
Each test case object MUST conform to the exact structure requested by the user.

CRITICAL RULES:
1. Only use endpoints and methods explicitly present in the specification. DO NOT invent endpoints.
2. Provide valid, realistic data for path parameters, query parameters, and request bodies.
3. For negative tests, intentionally provide invalid data but valid JSON.
4. Ensure the `expected_status` is an integer (e.g., 200, 400, 404).
5. Output MUST be valid JSON only. No markdown, no explanations, no preamble.
"""

USER_PROMPT_TEMPLATE = """
Generate {test_count} API test cases covering the following categories: {categories}.

API SPECIFICATION (Parsed JSON/YAML):
{api_spec}

INSTRUCTIONS:
1. Distribute the tests across the available endpoints and the requested categories.
2. For each test, provide a descriptive name and a brief explanation of what is being tested.
3. Specify the exact HTTP method (GET, POST, PUT, DELETE, PATCH).
4. Provide the exact endpoint path (e.g., '/users/1'). Replace path templates like {{id}} with actual test values.
5. Provide headers, query_params, path_params, and body as JSON objects.
6. Specify the expected_status code.

OUTPUT SCHEMA:
You must output a JSON object containing a "test_cases" array. Each object in the array MUST have the following structure exactly:
{{
  "name": "string (descriptive test name)",
  "description": "string (brief explanation)",
  "category": "string (one of: {categories})",
  "method": "string (uppercase HTTP method)",
  "endpoint": "string (actual path to call)",
  "headers": {{}},
  "query_params": {{}},
  "path_params": {{}},
  "body": {{}} or null,
  "expected_status": integer,
  "expected_fields": ["list", "of", "string", "keys", "expected", "in", "response"],
  "priority": "string (high, medium, low)"
}}
"""

def build_generation_prompt(
    api_spec: dict,
    test_count: int,
    categories: list[str],
) -> str:
    """Build the complete prompt string for the LLM."""
    import json
    
    # We dump the spec to a formatted string
    spec_str = json.dumps(api_spec, indent=2)
    categories_str = ", ".join(categories)
    
    user_msg = USER_PROMPT_TEMPLATE.format(
        test_count=test_count,
        categories=categories_str,
        api_spec=spec_str
    )
    
    return f"{SYSTEM_PROMPT}\n\n{user_msg}"
