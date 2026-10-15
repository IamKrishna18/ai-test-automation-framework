# Database & ORM Models (Phase 13)

The application uses SQLAlchemy to model a highly relational SQLite database that tracks the full lifecycle of test generation and execution.

## Core Models & Relationships

### `TestRun`
Represents a single automated test generation and execution cycle.
- **Fields**: Stores configuration (API spec, target URL, chosen LLM provider/model) and aggregate metrics (total, valid, passed, failed counts).
- **Relationships**: A 1-to-Many relationship with `TestCase`. For optimized querying (e.g., fetching all results for a dashboard), it also maintains a denormalized 1-to-Many relationship directly with `TestResult`.

### `TestCase`
Represents a single AI-generated test definition.
- **Fields**: Stores the structured definition (`method`, `endpoint`, `expected_status`). Complex nested structures like `headers`, `query_params`, and `body` are serialized and stored as JSON Text strings.
- **Relationships**: Belongs to one `TestRun`. Has a 1-to-1 relationship with a `TestResult`.
- **State**: Tracks `validation_status` ("pending", "valid", "invalid") to prevent malformed or hallucinated tests from executing.

### `TestResult`
Represents the actual outcome of executing a `TestCase`.
- **Fields**: Stores raw execution data (`actual_status_code`, `response_time_ms`, `actual_response_body`).
- **State**: Tracks the evaluation `status` ("pass", "fail", "error", "skipped"). 
- **Design Note**: A "fail" indicates an assertion failure (e.g., 404 instead of 200), whereas an "error" indicates a catastrophic execution failure (e.g., DNS resolution failed, timeout).
