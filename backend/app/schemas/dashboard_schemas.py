"""Pydantic schemas for dashboard analytics."""

from datetime import datetime

from pydantic import BaseModel


class CategoryCount(BaseModel):
    """Count of tests per category."""
    category: str
    count: int


class DashboardStats(BaseModel):
    """Aggregate statistics across all test runs."""
    total_runs: int = 0
    total_tests: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_errors: int = 0
    total_invalid: int = 0
    overall_validity_rate: float = 0.0
    overall_pass_rate: float = 0.0
    recent_runs: list[dict] = []
    category_distribution: list[CategoryCount] = []


class TrendDataPoint(BaseModel):
    """A single data point for historical trend charts."""
    date: str
    run_id: str
    passed: int
    failed: int
    errors: int
    validity_rate: float
    pass_rate: float
