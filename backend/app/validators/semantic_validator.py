"""Validates the semantics of test cases against the API specification."""

import re

from app.models.test_case import TestCase
from app.services.spec_parser import ParsedSpec


def validate_semantics(test_case: TestCase, spec: ParsedSpec) -> list[str]:
    """Validates that a test case makes sense given the API specification.
    
    Checks:
    1. The endpoint path exists (accounting for path parameters).
    2. The HTTP method is supported for that endpoint.
    
    Returns:
        A list of error strings. Empty list means semantically valid.
    """
    errors: list[str] = []
    
    if not spec or not spec.endpoints:
        # If spec parsing failed or is empty, we can't do semantic validation
        return errors
        
    # Standardize the requested endpoint for matching (e.g. /users/1 -> /users/{id})
    requested_path = test_case.endpoint.split("?")[0] # strip query string
    method = test_case.method.upper()
    
    # We need to see if requested_path matches any spec path template
    # Convert OpenAPI /users/{id} to a regex ^/users/[^/]+$
    match_found = False
    method_supported = False
    
    for ep in spec.endpoints:
        # Convert path variables e.g., {user_id} -> [^/]+
        pattern = re.sub(r'\{[^}]+\}', r'[^/]+', ep.path)
        pattern = f"^{pattern}$"
        
        if re.match(pattern, requested_path):
            match_found = True
            if ep.method.upper() == method:
                method_supported = True
                break
                
    if not match_found:
        errors.append(f"Endpoint '{requested_path}' does not exist in API specification")
    elif not method_supported:
        errors.append(f"HTTP method '{method}' is not supported for endpoint '{requested_path}'")
        
    return errors
