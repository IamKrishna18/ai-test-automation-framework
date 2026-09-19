from app.validators.schema_validator import validate_schema
from app.models.test_case import TestCase

def test_valid_schema():
    tc = TestCase(
        name="Valid test",
        category="functional",
        method="GET",
        endpoint="/api",
        expected_status=200,
        headers="{}",
        query_params="{}",
        path_params="{}",
        expected_fields="[]"
    )
    errors = validate_schema(tc)
    assert len(errors) == 0

def test_invalid_http_method():
    tc = TestCase(
        name="Invalid method",
        category="functional",
        method="INVALID",
        endpoint="/api",
        expected_status=200,
    )
    errors = validate_schema(tc)
    assert len(errors) > 0
    assert "method" in errors[0]

def test_invalid_category():
    tc = TestCase(
        name="Invalid category",
        category="not_a_real_category",
        method="GET",
        endpoint="/api",
        expected_status=200,
    )
    errors = validate_schema(tc)
    assert len(errors) > 0
    assert "category" in errors[0]
