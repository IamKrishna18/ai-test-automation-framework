"""Database repositories for data access.

Abstracts the SQLAlchemy session logic away from the API endpoints.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.test_run import TestRun
from app.models.test_case import TestCase
from app.models.test_result import TestResult
from app.schemas.run_schemas import CreateRunRequest, RunStatus

class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_run(self, run_id: str) -> Optional[TestRun]:
        return self.db.query(TestRun).filter(TestRun.id == run_id).first()

    def list_runs(self, limit: int = 100, skip: int = 0) -> List[TestRun]:
        return self.db.query(TestRun).order_by(TestRun.created_at.desc()).offset(skip).limit(limit).all()

    def count_runs(self) -> int:
        return self.db.query(func.count(TestRun.id)).scalar() or 0

    def create_run(self, req: CreateRunRequest) -> TestRun:
        import json
        run = TestRun(
            target_url=str(req.target_url),
            api_spec=req.api_spec,
            provider=req.provider.value if hasattr(req.provider, 'value') else req.provider,
            model=req.model,
            categories=json.dumps([c.value if hasattr(c, 'value') else c for c in req.categories]),
            requested_test_count=req.test_count,
            status=RunStatus.CREATED.value if hasattr(RunStatus.CREATED, 'value') else "created",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_status(self, run_id: str, status: RunStatus, error_message: str = None) -> Optional[TestRun]:
        run = self.get_run(run_id)
        if run:
            run.status = status
            if error_message:
                run.error_message = error_message
            self.db.commit()
            self.db.refresh(run)
        return run

class TestCaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cases_for_run(self, run_id: str) -> List[TestCase]:
        return self.db.query(TestCase).filter(TestCase.run_id == run_id).all()

class TestResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_results_for_run(self, run_id: str) -> List[TestResult]:
        return self.db.query(TestResult).filter(TestResult.run_id == run_id).all()
        
    def get_dashboard_stats(self) -> dict:
        """Calculate high-level stats for the dashboard."""
        total_runs = self.db.query(func.count(TestRun.id)).scalar() or 0
        total_tests = self.db.query(func.count(TestCase.id)).scalar() or 0
        
        # Count passes
        passed = self.db.query(func.count(TestResult.id)).filter(TestResult.status == "pass").scalar() or 0
        
        pass_rate = 0.0
        if total_tests > 0:
            pass_rate = round((passed / total_tests) * 100, 1)
            
        return {
            "total_runs": total_runs,
            "total_tests_generated": total_tests,
            "overall_pass_rate": pass_rate
        }
