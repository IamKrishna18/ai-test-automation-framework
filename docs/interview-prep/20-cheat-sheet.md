# 20. Master Cheat Sheet (Phase 28, 29, 30)

Review this sheet 30 minutes before your interview.

## 🌟 The Core Value Prop
"I built a system that turns static OpenAPI specs into executable test suites using LLMs. It solves the blank-page problem for QA by guaranteeing structured, hallucination-free JSON test cases."

## 🏗️ Architecture Stack
*   **Backend:** Python, FastAPI (Async), SQLAlchemy 2.0 (ORM)
*   **Database:** SQLite (WAL mode for concurrency)
*   **AI:** `google-genai` (Gemini), prompt engineering, Pydantic (Structured Output)
*   **Frontend:** React, TypeScript, Vite, Tailwind
*   **Execution:** `httpx` (async HTTP client)

## 🚦 The Data Flow (Memorize This)
1. **Intake:** User uploads OpenAPI Spec.
2. **Prompting:** Backend parses spec, constructs prompt ("Act as a QA engineer...").
3. **Generation:** LLM generates test cases.
4. **Schema Validation:** Pydantic ensures output is strictly JSON and has required fields.
5. **Semantic Validation:** App verifies the LLM didn't hallucinate non-existent endpoints.
6. **Execution:** Async `httpx` calls hit the target API.
7. **Evaluation:** App compares actual HTTP status/body to the LLM's expected status/body.
8. **Reporting:** Results saved to DB, served to React UI.

## 🚩 Flagged Complex Code (Review Before Interview)

### 1. `BaseLLMProvider` & Pydantic
Know how you enforced structured output. If using Gemini's structured outputs:
```python
# Know this concept: Passing a Pydantic model to the SDK
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MyTestSchema,
    ),
)
```

### 2. `SemanticValidator`
How do you prove it's not hallucinating?
*Concept:* "I iterate over the LLM tests, extract the `method` and `url`. I then check if `url` exists in the `paths` dictionary of the parsed OpenAPI JSON, and if the `method` exists for that path."

### 3. Async DB Sessions (SQLAlchemy)
*Concept:* "Because it's FastAPI, I used `AsyncSession`. The trickiest part was avoiding `DetachedInstanceError`. I had to make sure I eagerly loaded relationships or accessed necessary attributes before the session closed, especially when passing DB objects to the execution engine."

## 🛡️ Defending Trade-offs
*   **Why SQLite?** Speed of development, zero configuration for users. Acknowledged limitation: write concurrency.
*   **Why JSON instead of Python tests?** Security and determinism. Executing AI-generated code is a massive security risk. Structuring it as data (JSON) is safe.
*   **Why abstraction?** Decoupling the core business logic from the specific LLM vendor (Gemini vs OpenAI) prevents lock-in.

## 📚 Priority Learning Areas (If you have time)
1. **Async Python:** Be able to explain the Event Loop and the difference between CPU-bound and I/O-bound tasks (test execution is I/O-bound, hence async is perfect).
2. **OpenAPI Spec Structure:** Know that it has `info`, `servers`, `paths`, and `components/schemas`.
3. **LLM Hallucinations:** Be able to speak intelligently about why LLMs make things up and how constraining their output space (via Pydantic/Schemas) mitigates it.
