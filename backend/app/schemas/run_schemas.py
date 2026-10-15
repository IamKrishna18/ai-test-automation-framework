"""Pydantic schemas for test run endpoints."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TestCategory(str, Enum):
    """Supported test case categories."""
    FUNCTIONAL = "functional"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    VALIDATION = "validation"
    ERROR_HANDLING = "error_handling"
    EDGE_CASE = "edge_case"
    AUTHENTICATION = "authentication"
    REGRESSION = "regression"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    MOCK = "mock"


class RunStatus(str, Enum):
    """Test run lifecycle states."""
    CREATED = "created"
    GENERATING = "generating"
    VALIDATING = "validating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateRunRequest(BaseModel):
    """Request body for creating a new test run."""
    target_url: str = Field(
        ...,
        description="Base URL of the target API to test.",
        examples=["http://localhost:8001"],
    )
    api_spec: str = Field(
        ...,
        description="API specification content (JSON, YAML, or OpenAPI).",
        min_length=10,
    )
    provider: LLMProvider = Field(
        default=LLMProvider.GEMINI,
        description="LLM provider to use for test generation.",
    )
    model: str = Field(
        default="gemini-2.5-flash",
        description="LLM model name.",
    )
    categories: list[TestCategory] = Field(
        default_factory=lambda: list(TestCategory),
        description="Test categories to generate.",
    )
    test_count: int = Field(
        default=10,
        ge=1,
        le=200,
        description="Number of test cases to generate.",
    )


class TestRunResponse(BaseModel):
    """Response schema for a test run."""
    id: str
    created_at: datetime
    completed_at: datetime | None = None
    target_url: str
    provider: str
    model: str
    status: str
    categories: list[str] = []
    requested_test_count: int = 10
    total_tests: int = 0
    valid_tests: int = 0
    invalid_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    validity_rate: float = 0.0
    pass_rate: float = 0.0

    model_config = {"from_attributes": True}


class TestRunListResponse(BaseModel):
    """Paginated list of test runs."""
    runs: list[TestRunResponse]
    total: int


class GenerateResponse(BaseModel):
    """Response after test generation."""
    run_id: str
    total_generated: int
    valid: int
    invalid: int
    validation_errors: list[str] = []


class ExecuteRunResponse(BaseModel):
    """Response after test execution."""
    run_id: str
    executed: int
    passed: int
    failed: int
    errors: int
    skipped: int
    pass_rate: float
