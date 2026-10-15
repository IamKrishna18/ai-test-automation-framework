"""Pydantic schemas for test result data."""

from datetime import datetime

from pydantic import BaseModel


class TestResultResponse(BaseModel):
    """Detailed response schema for a single test result."""
    id: str
    test_case_id: str
    run_id: str = ""
    status: str  # pass | fail | error | skipped
    actual_status_code: int | None = None
    response_time_ms: float | None = None
    actual_response_body: dict | list | str | None = None
    actual_headers: dict | None = None
    error_message: str | None = None
    evaluation_details: dict | None = None
    executed_at: datetime | None = None

    model_config = {"from_attributes": True}
