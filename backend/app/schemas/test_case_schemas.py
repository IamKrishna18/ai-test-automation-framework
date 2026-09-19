"""Pydantic schemas for test case data.

GeneratedTestCase is the strict schema that AI-generated test cases
must conform to. This is used during validation to reject malformed output.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class HTTPMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class Priority(str, Enum):
    """Test case priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GeneratedTestCase(BaseModel):
    """Schema for validating AI-generated test cases.

    This is the contract between the LLM output and the execution engine.
    The LLM must return data conforming to this schema.
    """
    name: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="")
    category: str = Field(..., min_length=1)
    method: str = Field(...)
    endpoint: str = Field(..., min_length=1)
    headers: dict[str, str] = Field(default_factory=dict)
    query_params: dict[str, str] = Field(default_factory=dict)
    path_params: dict[str, str] = Field(default_factory=dict)
    body: dict | list | None = Field(default=None)
    expected_status: int = Field(..., ge=100, le=599)
    expected_fields: list[str] = Field(default_factory=list)
    expected_response_schema: dict | None = Field(default=None)
    priority: str = Field(default="medium")

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Ensure HTTP method is valid and uppercase."""
        v = v.upper()
        valid = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if v not in valid:
            raise ValueError(f"Invalid HTTP method: {v}. Must be one of {valid}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Ensure category is valid."""
        v = v.lower().replace(" ", "_").replace("-", "_")
        valid = {
            "functional", "negative", "boundary", "validation",
            "error_handling", "edge_case", "authentication", "regression",
        }
        if v not in valid:
            raise ValueError(f"Invalid category: {v}. Must be one of {valid}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Ensure priority is valid."""
        v = v.lower()
        valid = {"high", "medium", "low"}
        if v not in valid:
            raise ValueError(f"Invalid priority: {v}. Must be one of {valid}")
        return v


class TestCaseResponse(BaseModel):
    """Response schema for a test case with its result."""
    id: str
    run_id: str
    name: str
    description: str
    category: str
    method: str
    endpoint: str
    headers: dict = {}
    query_params: dict = {}
    path_params: dict = {}
    body: dict | list | None = None
    expected_status: int
    expected_fields: list[str] = []
    priority: str = "medium"
    validation_status: str
    validation_errors: list[str] = []
    created_at: datetime

    # Result (populated if test has been executed)
    result_status: str | None = None
    actual_status_code: int | None = None
    response_time_ms: float | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}
