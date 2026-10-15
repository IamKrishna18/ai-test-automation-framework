# Testing (Phase 19)

## Overview
The AI Test Automation Framework relies on a comprehensive testing strategy combining unit and integration tests using `pytest` for the Python backend.

## Types of Tests Used
- **Unit Tests (`tests/unit/`)**: Isolate and test individual functions, especially parsing, matching, and generation algorithms.
- **Integration Tests (`tests/integration/`)**: Test how the backend routes and controllers interact with the database and external AI models/services.
- **Fixtures (`tests/fixtures/`)**: We rely heavily on Pytest fixtures to provide reusable mock data, mocked AI responses, and initialized test databases to avoid repetitive setup code.

## Key Testing Practices
1. **Mocking External APIs**: We use `unittest.mock` to patch calls to LLMs (like OpenAI or Anthropic). This ensures tests are deterministic, fast, and don't incur API costs.
2. **Database Rollbacks**: Using transaction fixtures, each test starts with a clean database state and rolls back after execution.
3. **Assertions on AI Outputs**: Since AI output is non-deterministic, tests often use regex or semantic matching assertions rather than strict equality checks.
