"""Test result evaluator.

Responsible for comparing actual API responses against expected outcomes
and determining pass/fail status.
"""

import json

from app.core.logging import get_logger
from app.models.test_case import TestCase
from app.models.test_result import TestResult

logger = get_logger(__name__)

class ResultEvaluator:
    """Evaluates test results against expected outcomes."""

    @staticmethod
    def evaluate(tc: TestCase, result: TestResult) -> TestResult:
        """Evaluate a test result and update its status.
        
        Args:
            tc: The TestCase containing expected outcomes.
            result: The TestResult containing actual outcomes.
            
        Returns:
            The updated TestResult.
        """
        # If execution already failed (network error, timeout, etc.), leave it
        if result.status == "error":
            return result
            
        logger.info(f"Evaluating result for test {tc.id}")
        
        failures: list[str] = []
        
        # 1. Check status code
        if result.actual_status_code != tc.expected_status:
            failures.append(
                f"Status code mismatch: expected {tc.expected_status}, "
                f"got {result.actual_status_code}"
            )
            
        # 2. Check expected fields if present
        expected_fields = []
        if tc.expected_fields:
            try:
                expected_fields = json.loads(tc.expected_fields)
            except json.JSONDecodeError:
                pass
                
        if expected_fields and result.actual_response_body:
            try:
                # Try to parse response as JSON
                resp_json = json.loads(result.actual_response_body)
                
                # Check for each field
                for field in expected_fields:
                    if not ResultEvaluator._field_exists(resp_json, field):
                        failures.append(f"Expected field '{field}' not found in response")
                        
            except json.JSONDecodeError:
                failures.append("Response is not valid JSON, cannot check expected fields")
                
        # Finalize status
        if failures:
            result.status = "fail"
            result.error_message = "; ".join(failures)
        else:
            result.status = "pass"
            
        return result

    @staticmethod
    def _field_exists(data: dict | list, field_path: str) -> bool:
        """Check if a nested field exists using dot notation (e.g. 'user.id').
        
        This is a simple implementation. A more robust one might use JSONPath.
        """
        if not isinstance(data, (dict, list)):
            return False
            
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list):
                # If current is list and we're looking for a field, check if ANY item has it
                # For simplicity, we just check the first item or assume false if complex
                if not current:
                    return False
                # If the part is an integer, it's an index
                if part.isdigit():
                    idx = int(part)
                    if idx >= len(current):
                        return False
                    current = current[idx]
                else:
                    # Look inside the first object in the list
                    if isinstance(current[0], dict) and part in current[0]:
                        current = current[0][part]
                    else:
                        return False
            else:
                return False
                
        return True
