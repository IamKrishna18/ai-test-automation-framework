"""API endpoints for exporting reports."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.reporters.csv_reporter import CsvReporter
from app.reporters.html_reporter import HtmlReporter
from app.repositories.run_repo import (
    RunRepository,
    TestCaseRepository,
    TestResultRepository,
)

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{run_id}")
def download_report(run_id: str, format: str = "html", db: Session = Depends(get_db)) -> Any:
    """Download a test run report in the specified format (csv or html)."""
    
    run_repo = RunRepository(db)
    case_repo = TestCaseRepository(db)
    result_repo = TestResultRepository(db)
    
    run = run_repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    cases = case_repo.get_cases_for_run(run_id)
    results = result_repo.get_results_for_run(run_id)
    
    if format.lower() == "csv":
        csv_reporter = CsvReporter()
        content = csv_reporter.generate(run, cases, results)
        return PlainTextResponse(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{run_id}.csv"}
        )
        
    elif format.lower() == "html":
        html_reporter = HtmlReporter()
        content = html_reporter.generate(run, cases, results)
        return HTMLResponse(
            content=content,
            headers={"Content-Disposition": f"attachment; filename=report_{run_id}.html"}
        )
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'html'.")
