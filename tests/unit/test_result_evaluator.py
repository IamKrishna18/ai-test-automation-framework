"""Unit tests for the result evaluator."""

import json

from app.evaluators.result_evaluator import ResultEvaluator
from app.models.test_case import TestCase
from app.models.test_result import TestResult

def test_evaluate_pass():
    tc = TestCase(
        id="tc1",
        expected_status=200,
        expected_fields='["id", "name"]'
    )
    result = TestResult(
        test_case_id="tc1",
        status="executed",
        actual_status_code=200,
        actual_response_body='{"id": 1, "name": "Alice"}'
    )
    
    evaluated = ResultEvaluator.evaluate(tc, result)
    
    assert evaluated.status == "pass"
    assert evaluated.error_message is None

def test_evaluate_fail_status_code():
    tc = TestCase(
        id="tc2",
        expected_status=200,
    )
    result = TestResult(
        test_case_id="tc2",
        status="executed",
        actual_status_code=404,
        actual_response_body='{"error": "Not found"}'
    )
    
    evaluated = ResultEvaluator.evaluate(tc, result)
    
    assert evaluated.status == "fail"
    assert "Status code mismatch" in evaluated.error_message

def test_evaluate_fail_missing_field():
    tc = TestCase(
        id="tc3",
        expected_status=200,
        expected_fields='["id", "email"]'
    )
    result = TestResult(
        test_case_id="tc3",
        status="executed",
        actual_status_code=200,
        actual_response_body='{"id": 1, "name": "Alice"}'
    )
    
    evaluated = ResultEvaluator.evaluate(tc, result)
    
    assert evaluated.status == "fail"
    assert "Expected field 'email' not found" in evaluated.error_message

def test_evaluate_ignores_already_error():
    tc = TestCase(id="tc4", expected_status=200)
    result = TestResult(
        test_case_id="tc4",
        status="error",
        error_message="Network timeout"
    )
    
    evaluated = ResultEvaluator.evaluate(tc, result)
    
    assert evaluated.status == "error"
    assert evaluated.error_message == "Network timeout"

def test_field_exists_nested():
    data = {"user": {"profile": {"id": 123}}}
    assert ResultEvaluator._field_exists(data, "user.profile.id") is True
    assert ResultEvaluator._field_exists(data, "user.profile.email") is False
