# 18. Interview Questions (Phase 23, 25, 26, 27)

This document contains a bank of questions you might be asked regarding this project, broken down by difficulty and type.

## Part 1: Pitches

### The 30-Second Pitch (Elevator)
"I built an AI-driven test automation framework that solves the 'blank page' problem in QA. It takes an OpenAPI specification, uses Google Gemini to dynamically generate structured test cases, validates them to prevent LLM hallucinations, and automatically executes them against a target API. It’s built with a FastAPI backend and a React frontend, proving that LLMs can be harnessed for deterministic, structural engineering tasks, not just chatbots."

### The 60-Second Pitch (Context + Tech)
*Start with the 30-second pitch, then add:*
"The biggest challenge was dealing with AI unreliability. To solve this, I built a pipeline that enforces Pydantic schema validation on the LLM output, ensuring we only get executable JSON. I also implemented a semantic validator that compares the AI's generated tests against the original OpenAPI spec to filter out hallucinated endpoints before execution. The backend is fully async using SQLAlchemy 2.0 and httpx to handle parallel test execution, and the results are surfaced on a React dashboard."

### The 120-Second Pitch (The Journey & Impact)
*Start with the 60-second pitch, then add:*
"I designed it with a clean architecture so the LLM provider is abstracted—I can swap Gemini for OpenAI seamlessly. While it handles REST APIs beautifully right now, I had to make tough trade-offs, like restricting it from executing dynamic Python scripts for security reasons, sticking to JSON-driven tests instead. Ultimately, this project drastically reduces the time needed to achieve baseline test coverage for new microservices."

---

## Part 2: Question Bank (L1 to L4)

### L1: The Basics (Junior/General)
*   **Q:** What is the overall architecture of your application?
*   **Q:** Why did you choose FastAPI over Flask or Django?
*   **Q:** How does the React frontend communicate with the backend?
*   **Q:** Explain what an OpenAPI specification is.

### L2: Implementation Details (Mid-Level)
*   **Q:** How exactly do you force the LLM to return JSON instead of free text?
*   **Q:** Your resume mentions "preventing hallucinations." How exactly did you implement that?
    *   *A:* Semantic Validator class. It parses the parsed OpenAPI spec and ensures the `method` + `path` combination proposed by the AI actually exists in the spec.
*   **Q:** How does your `HttpExecutor` handle timeouts or server crashes during test execution?
*   **Q:** Explain your database schema. How do you link a Test Run to individual Test Cases and their Results?

### L3: Architecture & Trade-offs (Senior)
*   **Q:** If I uploaded a 10MB OpenAPI spec with 10,000 endpoints, your app would likely crash or the LLM would reject it. How would you redesign the system to handle enterprise-scale specs?
*   **Q:** You chose SQLite. If we wanted to deploy this as a SaaS for hundreds of users, what breaks first, and how do you migrate to PostgreSQL?
*   **Q:** Let's talk about test isolation. What happens if the AI generates a test that deletes a user, and the next test tries to fetch that user? How would you solve this state dependency?
*   **Q:** Why abstract the LLM provider? Isn't that premature optimization?

### L4: Deep Dives & System Design (Staff/Principal)
*   **Q:** LLMs are inherently non-deterministic. How do you guarantee the reliability of your CI/CD pipeline if you integrate this tool? Will tests randomly fail between runs?
    *   *A:* The framework is for *generating* the static test suite once (or on spec change), not generating tests dynamically on every PR. The generated tests are saved and run deterministically.
*   **Q:** Suppose we want to test a complex workflow: Create User -> Extract Token -> Create Order (using token) -> Assert Order Created. How would you evolve your current static JSON test model to support dynamic chaining and variable passing?
*   **Q:** Walk me through the memory profile of your asynchronous execution engine. If I run 5,000 tests concurrently, what happens to the FastAPI event loop and the database connection pool?

---

## Part 3: Resume Defense & "Why" Questions

*   **"Why Python instead of Node.js or Go for the backend?"**
    *   *Defense:* Python is the undisputed king of AI/ML ecosystems. Libraries like Pydantic, the official GenAI/OpenAI SDKs, and Langchain/LlamaIndex make integrating and validating LLM outputs significantly faster and more robust than in Node or Go.
*   **"Why use an LLM for this at all? Can't we just generate property-based tests randomly?"**
    *   *Defense:* Fuzzing and property-based testing are great for finding crashes, but they don't understand *business logic*. An LLM can read the description of an endpoint (e.g., "Returns 400 if user is under 18") and generate a semantic test case specifically targeting that business rule, which a random fuzzer cannot do.
*   **"Why did you use standard HTTP requests instead of a framework like Pytest for execution?"**
    *   *Defense:* We are storing tests as data (JSON in a database), not as code files on a disk. Executing HTTP requests dynamically via `httpx` based on database records is much safer and easier to orchestrate than generating `.py` files and sub-processing Pytest.
