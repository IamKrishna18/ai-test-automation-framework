# AI & LLM Integration (Phases 8 & 9)

## LLM Provider Architecture
The AI integration is built on an abstract base class `BaseLLMProvider`, which defines the standard interface for any LLM we want to plug in. 

- **Retry Logic & Resiliency**: The base class handles retries with exponential backoff for transient errors (rate limits, timeouts) using custom exceptions (`LLMRateLimitError`, `LLMConnectionError`).
- **Response Parsing**: The base class cleans the raw text response, removing Markdown fences and parsing the underlying JSON, gracefully falling back to extract embedded arrays or objects depending on the model's output structure.
- **Provider Implementation**: The primary implementation is `GeminiProvider`, which uses the official `google-genai` SDK. It forces structured output using JSON schemas and a low temperature (`0.2`) to ensure determinism. 

## Prompt Engineering
Prompts are built via the `build_generation_prompt` function, injecting the parsed API spec (`ParsedSpec`), the requested number of tests, and targeted categories (functional, edge-case, security, etc.). The prompt heavily emphasizes returning the data conforming precisely to our `GeneratedTestCase` schema.

## Hallucination Detection
LLMs can occasionally invent non-existent parameters, paths, or methods. We detect and handle these hallucinations defensively:
1. **Pydantic Schema Enforcement**: We inject a JSON schema derived from our models, instructing the model to adhere strictly to the schema.
2. **Deterministic Configuration**: The model temperature is minimized, significantly reducing randomness.
3. **Post-generation Semantic Validation (Phase 10)**: We cross-reference every generated endpoint, path, and method against the original parsed OpenAPI specification to filter out hallucinated endpoints entirely before they can be executed.
