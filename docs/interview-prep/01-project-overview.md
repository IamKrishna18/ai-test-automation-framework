# Project Overview: AI-Driven Test Automation Framework

## 1. High-Level Summary
This project is an automated testing platform that reads OpenAPI specifications and leverages Large Language Models (LLMs) to automatically generate, validate, execute, and evaluate test cases. By taking a specification file and automatically verifying real-world API behavior against it, the framework solves the "blank page" problem for QA engineers and provides rapid, extensive API test coverage.

### Key Value Propositions
- **Automated Bootstrapping**: Generates structured HTTP test suites covering functional, negative, and edge-case scenarios without manual intervention.
- **Smart Validation Pipeline**: Protects against LLM hallucinations by deeply validating generated tests against the OpenAPI schema prior to execution.
- **Deterministic AI Control**: Relies on robust prompting and `pydantic`-enforced output schemas to guarantee the model returns valid, parseable JSON representing test cases.

---

## 2. File-by-File Audit

### Backend (`backend/app/`)
- `main.py`: The FastAPI application entry point. Handles app lifecycle, CORS middleware configuration, and router registration.
- `api/runs.py`: Defines REST endpoints for test run management (`POST /api/runs`, `POST /{run_id}/generate`, `POST /{run_id}/execute`). Connects HTTP requests to repository and service layers.
- `core/`: Contains core application setups such as database connection handling (`database.py`), settings mapping (`config.py`), and logging utilities (`logging.py`).
- `services/orchestrator.py`: The core workflow controller. Coordinates the pipeline: invoking AI generation (`RunService`), schema/semantic validation, test execution (`HttpExecutor`), and outcome evaluation (`ResultEvaluator`).
- `services/run_service.py`: Responsible for delegating to AI providers (like Gemini) via structured prompts to generate test cases.
- `services/spec_parser.py`: Parses the raw OpenAPI/Swagger definition to feed contextual data into the LLM prompt and validation engine.
- `executors/http_executor.py`: Executes the validated test cases asynchronously against the target API.
- `evaluators/result_evaluator.py`: Compares the actual HTTP response (status code, body) against the LLM's expected outcomes to declare a test passed or failed.
- `validators/schema_validator.py` & `semantic_validator.py`: Ensures the AI-generated tests conform to our internal schema and logically match the provided OpenAPI specification (preventing hallucinated paths/methods).
- `repositories/run_repo.py`: Encapsulates SQLAlchemy database interactions for `TestRun`, `TestCase`, and `TestResult` models.
- `models/`: SQLAlchemy 2.0 ORM models defining the database schema.
- `schemas/`: Pydantic v2 models defining data structures for API request/response and internal data transfer.
- `providers/`: Abstract layer for LLM integrations, allowing swapping between models (e.g., Google Gemini, OpenAI).

### Frontend (`frontend/`)
- `package.json`: Defines dependencies including React, Vite, React Router, Axios, and TailwindCSS.
- `src/App.tsx`: The main React component setting up the application layout, navigation shell, and `react-router-dom` routing definitions.
- `src/views/Dashboard.tsx`: Displays high-level analytics and historical test run metrics.
- `src/views/RunCreator.tsx`: The UI form for initializing a new test run, uploading/pasting the API spec, and selecting configurations.
- `src/views/RunDetails.tsx`: Displays detailed results of a specific test run, showing generated tests, valid/invalid breakdown, and execution passes/fails.
