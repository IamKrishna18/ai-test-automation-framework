"""Validates the structure of AI-generated test cases using Pydantic."""

import json

from pydantic import ValidationError
from app.models.test_case import TestCase
from app.schemas.test_case_schemas import GeneratedTestCase

def validate_schema(test_case: TestCase) -> list[str]:
    """Validates that a TestCase ORM model contains structurally valid data.
    
    Returns:
        A list of error strings. Empty list means the schema is valid.
    """
    errors = []
    
    # Reconstruct dictionary from ORM model to validate against Pydantic schema
    try:
        data = {
            "name": test_case.name,
            "description": test_case.description,
            "category": test_case.category,
            "method": test_case.method,
            "endpoint": test_case.endpoint,
            "headers": json.loads(test_case.headers) if test_case.headers else {},
            "query_params": json.loads(test_case.query_params) if test_case.query_params else {},
            "path_params": json.loads(test_case.path_params) if test_case.path_params else {},
            "body": json.loads(test_case.body) if test_case.body else None,
            "expected_status": test_case.expected_status,
            "expected_fields": json.loads(test_case.expected_fields) if test_case.expected_fields else [],
            "priority": test_case.priority,
        }
    except json.JSONDecodeError as e:
        return [f"Failed to decode JSON fields: {e}"]
        
    try:
        # Pydantic validation
        GeneratedTestCase(**data)
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(l) for l in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
            
    return errors
