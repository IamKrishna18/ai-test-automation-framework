# Result Evaluation (Phase 12)

The evaluation step acts as the assertion engine. It takes the expected outcomes (defined in the `TestCase`) and compares them against the actual outcomes (recorded in the `TestResult`).

## `ResultEvaluator` Logic
Implemented in `result_evaluator.py`. The logic aggregates a list of failure strings; if the list remains empty, the test passes.

### 1. Status Code Evaluation
The most fundamental assertion. The engine strictly compares the `actual_status_code` from the `TestResult` against the `expected_status` defined by the AI.

### 2. Field Presence Evaluation
The AI can specify a list of `expected_fields` (e.g., `["user.id", "data.0.status"]`) that must exist in the JSON response body.
- The evaluator uses a custom dot-notation parsing algorithm (`_field_exists`) to traverse the nested actual response dictionary/list.
- It robustly handles traversing into nested dictionaries and indexing into arrays. 
- If a defined field is missing, a specific failure message is appended.

### Final Status Determination
- If execution failed previously (e.g., network timeout), the status remains `"error"` and evaluation is skipped.
- If any assertions fail, the result status is set to `"fail"`, and the aggregated failure messages are joined with semicolons into the `error_message` column.
- If all assertions pass, the result status is set to `"pass"`.
