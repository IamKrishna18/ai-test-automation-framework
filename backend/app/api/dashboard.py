"""API endpoints for Dashboard analytics."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.run_repo import TestResultRepository
from app.schemas.dashboard_schemas import DashboardStats, TrendDataPoint

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)) -> Any:
    """Get high-level statistics for the dashboard."""
    repo = TestResultRepository(db)
    stats = repo.get_dashboard_stats()
    
    return DashboardStats(
        total_runs=stats["total_runs"],
        total_tests_generated=stats["total_tests_generated"],
        overall_pass_rate=stats["overall_pass_rate"],
        top_failing_endpoints=[] # Placeholder for MVP
    )


@router.get("/trends", response_model=list[TrendDataPoint])
def get_execution_trends(db: Session = Depends(get_db)) -> Any:
    """Get test execution trends over time."""
    # Placeholder for trend data
    return [
        TrendDataPoint(date="2024-01-01", pass_rate=85.5, total_tests=120),
        TrendDataPoint(date="2024-01-02", pass_rate=92.0, total_tests=150),
    ]
