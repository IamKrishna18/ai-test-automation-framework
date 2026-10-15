# Execution Engine (Phase 11)

The Execution engine is purely responsible for firing the requests exactly as defined by the generated test cases and capturing the raw reality of the API's response. It explicitly **does not** determine if a test passed or failed.

## `HttpExecutor` Implementation
Implemented in `http_executor.py`, leveraging the asynchronous HTTP client library `httpx`.

- **Request Construction**: 
  - Parses JSON strings from the database (headers, query_params, path_params, body) into native Python dictionaries.
  - Assembles the full URL dynamically based on the target API URL.
  - Sends the request using `httpx.AsyncClient` with a timeout configured from application settings.

- **Response Capture**:
  - Automatically records the exact time taken (`response_time_ms`).
  - Captures the `actual_status_code` and raw `actual_headers`.
  - Attempts to gracefully parse the `actual_response_body` as JSON. If the API returns XML, HTML, or raw text, it falls back to capturing the raw string without crashing.

- **Error Handling**:
  - Differentiates between test failures and execution errors.
  - `httpx.TimeoutException`: Flags the result status as "error" with a timeout message.
  - `httpx.RequestError`: Flags as a network/DNS error.
  - These "error" statuses prevent the evaluation step from attempting to parse a non-existent response.
