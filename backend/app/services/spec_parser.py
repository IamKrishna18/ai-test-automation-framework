"""API specification parser.

Parses JSON, YAML, and OpenAPI specifications into a structured
format that the prompt builder can use to generate accurate test cases.

Inputs:
    Raw specification string (JSON or YAML format)

Outputs:
    ParsedSpec containing extracted endpoints with their methods,
    parameters, request bodies, and response definitions.

Important:
    The parser extracts metadata from the spec but does NOT validate
    that the target API actually implements these endpoints. That's
    the execution engine's job.
"""

import json
import logging
from dataclasses import dataclass, field

import yaml

logger = logging.getLogger(__name__)


@dataclass
class EndpointParam:
    """A single parameter for an API endpoint."""
    name: str
    location: str  # path, query, header, cookie
    required: bool = False
    param_type: str = "string"
    description: str = ""


@dataclass
class EndpointBody:
    """Request body definition for an API endpoint."""
    content_type: str = "application/json"
    schema: dict = field(default_factory=dict)
    required: bool = False
    example: dict | None = None


@dataclass
class EndpointResponse:
    """Expected response definition for a status code."""
    status_code: int
    description: str = ""
    schema: dict = field(default_factory=dict)


@dataclass 
class EndpointInfo:
    """Complete information about a single API endpoint."""
    path: str
    method: str  # GET, POST, PUT, PATCH, DELETE
    summary: str = ""
    description: str = ""
    parameters: list[EndpointParam] = field(default_factory=list)
    request_body: EndpointBody | None = None
    responses: list[EndpointResponse] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ParsedSpec:
    """Complete parsed API specification."""
    title: str = ""
    description: str = ""
    version: str = ""
    base_url: str = ""
    endpoints: list[EndpointInfo] = field(default_factory=list)
    raw_spec: dict = field(default_factory=dict)

    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)

    @property 
    def available_methods(self) -> set[str]:
        return {ep.method.upper() for ep in self.endpoints}

    @property
    def available_paths(self) -> set[str]:
        return {ep.path for ep in self.endpoints}


class SpecParserError(Exception):
    """Raised when specification parsing fails."""
    pass


def parse_spec(raw_spec: str) -> ParsedSpec:
    """Parse an API specification string into structured data.
    
    Auto-detects JSON vs YAML format, then extracts OpenAPI structure
    if present, otherwise returns the raw parsed dict.
    
    Args:
        raw_spec: Raw specification string (JSON or YAML).
        
    Returns:
        ParsedSpec with extracted endpoint information.
        
    Raises:
        SpecParserError: If the specification cannot be parsed.
    """
    if not raw_spec or not raw_spec.strip():
        raise SpecParserError("Empty specification provided")
    
    # Try parsing as JSON first, then YAML
    spec_dict = _parse_raw(raw_spec)
    
    # Check if it's an OpenAPI spec
    if _is_openapi_spec(spec_dict):
        return _parse_openapi(spec_dict)
    
    # Fall back to generic spec interpretation
    return _parse_generic(spec_dict)


def _parse_raw(raw: str) -> dict:
    """Parse raw string as JSON or YAML."""
    # Try JSON first (stricter, faster)
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
        raise SpecParserError("Specification must be a JSON/YAML object, not an array or scalar")
    except json.JSONDecodeError:
        pass
    
    # Try YAML
    try:
        result = yaml.safe_load(raw)
        if isinstance(result, dict):
            return result
        raise SpecParserError("Specification must be a JSON/YAML object")
    except yaml.YAMLError as e:
        raise SpecParserError(f"Failed to parse specification as JSON or YAML: {e}") from e


def _is_openapi_spec(spec: dict) -> bool:
    """Check if the dict looks like an OpenAPI specification."""
    return (
        "openapi" in spec 
        or "swagger" in spec 
        or ("paths" in spec and "info" in spec)
    )


def _parse_openapi(spec: dict) -> ParsedSpec:
    """Parse an OpenAPI 3.x specification."""
    info = spec.get("info", {})
    
    # Extract base URL from servers
    servers = spec.get("servers", [])
    base_url = servers[0].get("url", "") if servers else ""
    
    endpoints = []
    paths = spec.get("paths", {})
    
    http_methods = {"get", "post", "put", "patch", "delete", "head", "options"}
    
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
            
        # Path-level parameters (shared by all methods)
        path_params = _parse_parameters(path_item.get("parameters", []))
        
        for method in http_methods:
            if method not in path_item:
                continue
                
            operation = path_item[method]
            if not isinstance(operation, dict):
                continue
            
            # Merge path-level and operation-level parameters
            op_params = _parse_parameters(operation.get("parameters", []))
            all_params = path_params + op_params
            
            # Parse request body
            request_body = _parse_request_body(operation.get("requestBody", {}))
            
            # Parse responses
            responses = _parse_responses(operation.get("responses", {}))
            
            endpoint = EndpointInfo(
                path=path,
                method=method.upper(),
                summary=operation.get("summary", ""),
                description=operation.get("description", ""),
                parameters=all_params,
                request_body=request_body,
                responses=responses,
                tags=operation.get("tags", []),
            )
            endpoints.append(endpoint)
    
    logger.info(
        "Parsed OpenAPI spec: %s endpoints from %s paths",
        len(endpoints), len(paths)
    )
    
    return ParsedSpec(
        title=info.get("title", ""),
        description=info.get("description", ""),
        version=info.get("version", ""),
        base_url=base_url,
        endpoints=endpoints,
        raw_spec=spec,
    )


def _parse_parameters(params: list) -> list[EndpointParam]:
    """Parse OpenAPI parameter definitions."""
    result = []
    for param in params:
        if not isinstance(param, dict):
            continue
        schema = param.get("schema", {})
        result.append(EndpointParam(
            name=param.get("name", ""),
            location=param.get("in", "query"),
            required=param.get("required", False),
            param_type=schema.get("type", "string") if isinstance(schema, dict) else "string",
            description=param.get("description", ""),
        ))
    return result


def _parse_request_body(body: dict | None) -> EndpointBody | None:
    """Parse OpenAPI request body definition."""
    if not body or not isinstance(body, dict):
        return None
    
    content = body.get("content", {})
    # Prefer application/json
    json_content = content.get("application/json", {})
    if not json_content:
        # Try any content type
        if content:
            first_key = next(iter(content))
            json_content = content[first_key]
        else:
            return None
    
    schema = json_content.get("schema", {})
    example = json_content.get("example")
    
    return EndpointBody(
        content_type="application/json",
        schema=schema if isinstance(schema, dict) else {},
        required=body.get("required", False),
        example=example,
    )


def _parse_responses(responses: dict) -> list[EndpointResponse]:
    """Parse OpenAPI response definitions."""
    result = []
    for status_code_str, response_def in responses.items():
        if not isinstance(response_def, dict):
            continue
        try:
            status_code = int(status_code_str)
        except (ValueError, TypeError):
            continue  # Skip 'default' or other non-numeric keys
        
        content = response_def.get("content", {})
        schema = {}
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
        
        result.append(EndpointResponse(
            status_code=status_code,
            description=response_def.get("description", ""),
            schema=schema if isinstance(schema, dict) else {},
        ))
    return result


def _parse_generic(spec: dict) -> ParsedSpec:
    """Parse a non-OpenAPI specification.
    
    Tries to extract endpoint information from common patterns.
    Falls back to storing the raw spec for prompt context.
    """
    logger.info("Spec is not OpenAPI format, treating as generic")
    
    endpoints = []
    
    # Try to find paths-like structure
    paths = spec.get("paths", spec.get("endpoints", {}))
    if isinstance(paths, dict):
        for path, methods in paths.items():
            if isinstance(methods, dict):
                for method, _ in methods.items():
                    if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                        endpoints.append(EndpointInfo(
                            path=path,
                            method=method.upper(),
                        ))
    
    return ParsedSpec(
        title=spec.get("title", spec.get("name", "")),
        description=spec.get("description", ""),
        version=spec.get("version", ""),
        endpoints=endpoints,
        raw_spec=spec,
    )
