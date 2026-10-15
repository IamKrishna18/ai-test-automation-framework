# Backend Deep Dive

The backend is built with FastAPI and strictly follows a layered architectural pattern to separate API routing, business logic, and database operations.

## 1. API Controllers (`app/api/`)
- **Design Pattern**: Router-based endpoints using FastAPI's `APIRouter`.
- **Functionality**: Endpoints map to HTTP actions. Validation of incoming JSON payloads is handled implicitly by Pydantic models (e.g., `CreateRunRequest`). Controllers rely on Dependency Injection (`Depends(get_db)`) to acquire database sessions and pass them down to repositories and services.

## 2. Orchestration (`app/services/orchestrator.py`)
- **Role**: The centralized coordinator. It handles complex, multi-step operations that span multiple domains (generation + validation + execution).
- **Why it matters**: By keeping the API controllers thin and moving the workflow logic here, the backend remains highly testable. You can instantiate `OrchestratorService` in a unit test without mocking the entire HTTP layer.

## 3. Validation Logic (`app/validators/`)
- **Schema Validation**: Uses Pydantic to ensure the structure of the LLM output is exactly what the framework expects.
- **Semantic Validation**: This is a critical safety mechanism. LLMs are prone to hallucinating APIs (e.g., guessing a `/users/delete_all` endpoint). The `SemanticValidator` parses the actual OpenAPI spec and checks every generated test case against it. If the path or method isn't in the spec, it flags the test as `invalid`, preventing rogue HTTP requests.

## 4. Execution Engine (`app/executors/http_executor.py`)
- **Concurrency**: Built for asynchronous execution. It takes the AI-generated parameters (path, query, body) and fires actual network requests against the target API.
- **Safety Features**: Catches connection timeouts and network errors gracefully, ensuring that a single hanging endpoint doesn't crash the entire test run. Records exact request and response headers/bodies for auditing.

## 5. Result Evaluation (`app/evaluators/result_evaluator.py`)
- **Logic**: It performs the assertion phase of testing. It compares the `actual_status_code` returned by the HTTP Executor against the `expected_status` predicted by the LLM. It also verifies that any `expected_fields` are present in the response body.
- **Outcome Mapping**: Maps the outcome to a deterministic `pass`, `fail`, or `error` state.

## 6. Data Access (`app/repositories/`)
- **Pattern**: Repository pattern using SQLAlchemy 2.0.
- **Benefits**: Isolates the ORM from the rest of the application. The orchestrator doesn't write SQL or know about database constraints; it just calls methods like `run_repo.get_cases_for_run(run_id)`.

## 7. AI Providers (`app/providers/`)
- **Abstraction**: Defines a `BaseLLMProvider` interface. This allows the application to swap between Google Gemini and OpenAI simply by changing a configuration flag, protecting the core logic from SDK-specific breaking changes.
