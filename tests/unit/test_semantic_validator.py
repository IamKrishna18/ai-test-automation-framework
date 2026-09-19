from app.validators.semantic_validator import validate_semantics
from app.models.test_case import TestCase
from app.services.spec_parser import ParsedSpec, EndpointInfo

def test_valid_semantics():
    spec = ParsedSpec(
        endpoints=[
            EndpointInfo(path="/users/{id}", method="GET")
        ]
    )
    tc = TestCase(method="GET", endpoint="/users/123")
    
    errors = validate_semantics(tc, spec)
    assert len(errors) == 0

def test_endpoint_not_found():
    spec = ParsedSpec(endpoints=[EndpointInfo(path="/users", method="GET")])
    tc = TestCase(method="GET", endpoint="/products")
    
    errors = validate_semantics(tc, spec)
    assert len(errors) == 1
    assert "does not exist in API specification" in errors[0]

def test_method_not_supported():
    spec = ParsedSpec(endpoints=[EndpointInfo(path="/users", method="GET")])
    tc = TestCase(method="POST", endpoint="/users")
    
    errors = validate_semantics(tc, spec)
    assert len(errors) == 1
    assert "HTTP method 'POST' is not supported" in errors[0]
