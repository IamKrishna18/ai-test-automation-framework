# AI-Driven Test Automation & Evaluation Framework

[![CI/CD Pipeline](https://github.com/IamKrishna18/ai-test-automation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/IamKrishna18/ai-test-automation-framework/actions)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/IamKrishna18/ai-test-automation-framework)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/IamKrishna18/ai-test-automation-framework)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)

A complete web-based platform that uses Large Language Models (LLMs) to automatically generate, validate, execute, and evaluate software tests from OpenAPI specifications.

---

## 🎓 For Faculty & Evaluators: How to Test This Project

You can test this project in **under 2 minutes** without setting up anything on your local machine:

### 🌟 Method 1: Instant 1-Click Cloud Run (GitHub Codespaces)
Click the badge below to launch a full, pre-configured cloud environment directly in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/IamKrishna18/ai-test-automation-framework)

Once the Codespace opens:
1. Run `python -m uvicorn backend.app.main:app --port 8000` (or `python run_demo.py`).
2. GitHub will automatically show a popup to open the web dashboard in your browser.
3. Click **"Try 1-Click Demo"** to generate and execute tests!

---

### ⚡ Method 2: 1-Command Terminal Evaluation
If you have cloned the repository locally:
```bash
# Runs the full generation, semantic validation, execution, and exports an HTML report
python run_demo.py
```

---

### 🧪 Method 3: Automated Test Suite (100% Pass)
```bash
export PYTHONPATH=backend
pytest tests/ -v
```

---

### 💻 Method 4: Local Web Dashboard
1. Open the Web Dashboard at `http://localhost:5173`.
2. Click **"Try 1-Click Demo"** (or **"New Run" -> "Load 1-Click Demo Spec"**).
3. The form automatically fills with the included **Sample Target API** specification and selects the **⚡ Mock / Demo Provider** (zero API keys required).
4. Click **Create Run** -> **Generate Tests** -> **Execute Tests**.
5. Watch the framework validate against hallucinated routes, execute HTTP calls, and generate downloadable HTML & CSV reports!

---

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
