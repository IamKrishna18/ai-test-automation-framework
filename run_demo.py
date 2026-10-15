"""
Quick Demo & Evaluation Script for AI-Driven Test Automation Framework.

Run this script directly to experience the full generation, validation, and evaluation pipeline:
    python run_demo.py
"""

import os
import sys
import json
import asyncio

# Ensure backend modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import SessionLocal, init_db
from app.repositories.run_repo import RunRepository, TestCaseRepository, TestResultRepository
from app.services.orchestrator import OrchestratorService
from app.schemas.run_schemas import CreateRunRequest, LLMProvider, TestCategory
from app.reporters.html_reporter import HtmlReporter

SAMPLE_SPEC = {
  "openapi": "3.0.3",
  "info": {
    "title": "Sample Target API",
    "version": "1.0.0",
    "description": "Predictable API for testing"
  },
  "servers": [{"url": "http://localhost:8001"}],
  "paths": {
    "/users": {
      "get": {
        "summary": "List all users",
        "parameters": [{"name": "limit", "in": "query", "schema": {"type": "integer"}}],
        "responses": {"200": {"description": "Success"}}
      },
      "post": {
        "summary": "Create user",
        "requestBody": {
          "required": True,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {"type": "string"},
                  "email": {"type": "string"},
                  "age": {"type": "integer"}
                },
                "required": ["name", "email", "age"]
              }
            }
          }
        },
        "responses": {
          "201": {"description": "Created"},
          "400": {"description": "Bad Request"},
          "422": {"description": "Validation Error"}
        }
      }
    },
    "/users/{user_id}": {
      "get": {
        "summary": "Get user by ID",
        "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {
          "200": {"description": "Found"},
          "400": {"description": "Bad Request"},
          "404": {"description": "Not Found"},
          "500": {"description": "Server Error"}
        }
      }
    }
  }
}

async def main():
    print("=" * 60)
    print("   AI-DRIVEN TEST AUTOMATION FRAMEWORK - QUICK DEMO")
    print("=" * 60)

    # 1. Initialize Database
    print("\n[1/5] Initializing Database...")
    init_db()
    db = SessionLocal()
    run_repo = RunRepository(db)
    orchestrator = OrchestratorService(db)

    # 2. Determine provider (Gemini if key exists, otherwise MockProvider)
    has_gemini = bool(os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY").startswith("your_"))
    provider = LLMProvider.GEMINI if has_gemini else LLMProvider.MOCK
    model = "gemini-3.6-flash" if has_gemini else "mock-standard"
    print(f"Using Provider: {provider.value.upper()} (Model: {model})")

    # 3. Create Run
    print("\n[2/5] Creating Test Run from OpenAPI Blueprint...")
    req = CreateRunRequest(
        target_url="http://localhost:8001",
        api_spec=json.dumps(SAMPLE_SPEC),
        provider=provider,
        model=model,
        categories=[TestCategory.FUNCTIONAL, TestCategory.NEGATIVE, TestCategory.VALIDATION],
        test_count=4
    )
    run = run_repo.create_run(req)
    print(f"-> Test Run created! ID: {run.id}")

    # 4. Generate & Validate Tests
    print("\n[3/5] Generating Tests & Performing Semantic/Schema Validation...")
    gen_result = orchestrator.generate_tests(run.id)
    print(f"-> Total Generated: {gen_result['total']}")
    print(f"-> Valid Tests:     {gen_result['valid']}")
    print(f"-> Invalid Tests:   {gen_result['invalid']} (caught by Anti-Hallucination filter)")

    # 5. Execute Tests
    print("\n[4/5] Executing Tests Against Target API (http://localhost:8001)...")
    exec_result = await orchestrator.execute_run(run.id)
    print(f"-> Passed: {exec_result['passed']}")
    print(f"-> Failed: {exec_result['failed']}")
    print(f"-> Errors: {exec_result['errors']}")

    # 6. Generate HTML Report
    print("\n[5/5] Generating HTML Report...")
    cases = TestCaseRepository(db).get_cases_for_run(run.id)
    results = TestResultRepository(db).get_results_for_run(run.id)
    reporter = HtmlReporter()
    html_content = reporter.generate(run, cases, results)
    
    os.makedirs("reports", exist_ok=True)
    report_file = os.path.join("reports", f"demo_report_{run.id[:8]}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> Report saved to: {report_file}")

    print("\n" + "=" * 60)
    print("   DEMO COMPLETED SUCCESSFULLY!")
    print(f"   View Web Dashboard: http://localhost:5173/runs/{run.id}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
