# AI-Driven Test Automation & Evaluation Framework

A complete web-based platform that uses Large Language Models (LLMs) to automatically generate, validate, execute, and evaluate software tests from OpenAPI specifications.

## What it does

1. **Intakes API Specifications:** Upload or paste OpenAPI/Swagger JSON/YAML specs.
2. **AI Generation:** Uses Google Gemini (or OpenAI) to generate structured test cases covering functional, negative, and edge-case scenarios.
3. **Validation:** Validates that AI-generated tests are syntactically and semantically correct (preventing hallucinated endpoints).
4. **Execution:** Automatically executes the valid tests against the target API.
5. **Evaluation:** Evaluates the test results to determine if the target API behaved correctly (Pass/Fail) based on expected HTTP status codes and JSON response bodies.
6. **Reporting:** Generates downloadable CSV and HTML reports and displays metrics on a React dashboard.

## Key Features

- **Strict Schema Enforcement:** Uses `google-genai` and `pydantic` to ensure LLMs return structured, deterministic JSON.
- **Provider Abstraction:** Easily swap between Gemini and OpenAI models.
- **Validation Pipeline:** Distinguishes between "Invalid AI Tests" (hallucinated endpoints/methods) and "Failing API Tests" (the API itself has a bug).
- **FastAPI Backend:** Fully asynchronous, clean architecture, SQLAlchemy 2.0 ORM.
- **React/Vite Frontend:** Responsive UI powered by TailwindCSS.
- **Sample Target API:** Included mock API for testing the framework itself.

## Setup Instructions

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Copy env and add your GEMINI_API_KEY
cp ../.env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Sample Target API (for testing)

```bash
# In a new terminal
cd sample_target_api
pip install -r requirements.txt
uvicorn app:app --port 8001
```

Then visit `http://localhost:5173` (Frontend) and create a test run pointing to `http://localhost:8001`.

## Interview Preparation & Architecture

This project is built to demonstrate production engineering practices. If discussing this in an interview, emphasize:

- **What/Why:** It solves the "blank page" problem in QA by bootstrapping test suites. It proves LLMs can do structured logic, not just chat.
- **Data Flow:** UI -> FastAPI -> Spec Parser -> Prompt Builder -> LLM SDK -> Schema Validator -> Semantic Validator -> HTTP Executor -> Evaluator -> UI/Report.
- **Important Classes:** `BaseLLMProvider` (abstraction & retries), `OrchestratorService` (ties the lifecycle together), `ResultEvaluator` (the core pass/fail logic).
- **What can go wrong (and how it's handled):**
  - *LLM Hallucinates Endpoints:* Caught by `SemanticValidator`.
  - *LLM Returns Invalid JSON:* Caught by `BaseLLMProvider` parsing logic and retried.
  - *LLM Returns Wrong Fields:* Caught by `SchemaValidator` (Pydantic).
  - *Target API Hangs:* Caught by `HttpExecutor` timeouts.

## Tech Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, SQLite (WAL mode), Pydantic v2, pytest
- **Frontend:** React, Vite, TypeScript, TailwindCSS, Axios
- **AI Integration:** Google GenAI SDK (`google-genai`), OpenAI SDK
- **CI/CD:** GitHub Actions
