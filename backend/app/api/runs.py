"""API endpoints for Test Run management."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.run_schemas import (
    CreateRunRequest,
    ExecuteRunResponse,
    GenerateResponse,
    TestRunListResponse,
    TestRunResponse,
)
from app.schemas.test_case_schemas import TestCaseResponse
from app.schemas.result_schemas import TestResultResponse
from app.repositories.run_repo import RunRepository, TestCaseRepository, TestResultRepository
from app.services.orchestrator import OrchestratorService

logger = get_logger(__name__)
router = APIRouter(prefix="/api/runs", tags=["Runs"])


@router.post("", response_model=TestRunResponse, status_code=201)
def create_run(req: CreateRunRequest, db: Session = Depends(get_db)) -> Any:
    """Create a new test run."""
    try:
        repo = RunRepository(db)
        run = repo.create_run(req)
        
        # Convert ORM to Pydantic
        return TestRunResponse(
            id=run.id,
            target_url=run.target_url,
            provider=run.provider,
            model=run.model,
            status=run.status,
            requested_test_count=run.requested_test_count,
            categories=json.loads(run.categories) if run.categories else [],
            total_tests=run.total_tests,
            valid_tests=run.valid_tests,
            invalid_tests=run.invalid_tests,
            passed=run.passed,
            failed=run.failed,
            errors=run.errors,
            created_at=run.created_at,
        )
    except Exception as e:
        logger.error(f"Failed to create run: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=TestRunListResponse)
def list_runs(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> Any:
    """List test runs with pagination."""
    repo = RunRepository(db)
    runs = repo.list_runs(limit=limit, skip=skip)
    total = repo.count_runs()
    
    response_runs = []
    for run in runs:
        response_runs.append(TestRunResponse(
            id=run.id,
            target_url=run.target_url,
            provider=run.provider,
            model=run.model,
            status=run.status,
            requested_test_count=run.requested_test_count,
            categories=json.loads(run.categories),
            total_tests=run.total_tests,
            valid_tests=run.valid_tests,
            invalid_tests=run.invalid_tests,
            passed=run.passed,
            failed=run.failed,
            errors=run.errors,
            created_at=run.created_at,
        ))
        
    return TestRunListResponse(runs=response_runs, total=total)


@router.get("/{run_id}", response_model=TestRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)) -> Any:
    """Get a specific test run."""
    repo = RunRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return TestRunResponse(
        id=run.id,
        target_url=run.target_url,
        provider=run.provider,
        model=run.model,
        status=run.status,
        requested_test_count=run.requested_test_count,
        categories=json.loads(run.categories),
        total_tests=run.total_tests,
        valid_tests=run.valid_tests,
        invalid_tests=run.invalid_tests,
        passed=run.passed,
        failed=run.failed,
        errors=run.errors,
        created_at=run.created_at,
    )


@router.post("/{run_id}/generate", response_model=GenerateResponse)
def generate_tests(run_id: str, db: Session = Depends(get_db)) -> Any:
    """Trigger AI test generation and validation for a run."""
    orchestrator = OrchestratorService(db)
    try:
        result = orchestrator.generate_tests(run_id)
        return GenerateResponse(
            run_id=run_id,
            total_generated=result["total"],
            valid=result["valid"],
            invalid=result["invalid"],
            validation_errors=[]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{run_id}/execute", response_model=ExecuteRunResponse)
async def execute_run(run_id: str, db: Session = Depends(get_db)) -> Any:
    """Execute the valid tests in a run against the target API."""
    orchestrator = OrchestratorService(db)
    try:
        result = await orchestrator.execute_run(run_id)
        executed = result["passed"] + result["failed"] + result["errors"]
        pass_rate = (result["passed"] / executed * 100) if executed > 0 else 0.0
        
        # We need to know how many were skipped.
        repo = RunRepository(db)
        run = repo.get_run(run_id)
        skipped = run.total_tests - executed if run else 0

        return ExecuteRunResponse(
            run_id=run_id,
            executed=executed,
            passed=result["passed"],
            failed=result["failed"],
            errors=result["errors"],
            skipped=skipped,
            pass_rate=pass_rate
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}/cases", response_model=list[TestCaseResponse])
def get_run_cases(run_id: str, db: Session = Depends(get_db)) -> Any:
    """Get all test cases for a run."""
    repo = TestCaseRepository(db)
    cases = repo.get_cases_for_run(run_id)
    
    result = []
    for tc in cases:
        result.append(TestCaseResponse(
            id=tc.id,
            name=tc.name,
            description=tc.description,
            category=tc.category,
            method=tc.method,
            endpoint=tc.endpoint,
            headers=json.loads(tc.headers) if tc.headers else {},
            query_params=json.loads(tc.query_params) if tc.query_params else {},
            path_params=json.loads(tc.path_params) if tc.path_params else {},
            body=json.loads(tc.body) if tc.body else None,
            expected_status=tc.expected_status,
            expected_fields=json.loads(tc.expected_fields) if tc.expected_fields else [],
            priority=tc.priority,
            validation_status=tc.validation_status,
            validation_errors=tc.validation_errors,
        ))
    return result

@router.get("/{run_id}/results", response_model=list[TestResultResponse])
def get_run_results(run_id: str, db: Session = Depends(get_db)) -> Any:
    """Get all test results for a run."""
    repo = TestResultRepository(db)
    results = repo.get_results_for_run(run_id)
    
    res_list = []
    for r in results:
        actual_headers = {}
        if r.actual_headers:
            try:
                actual_headers = json.loads(r.actual_headers)
            except:
                pass
                
        res_list.append(TestResultResponse(
            id=r.id,
            test_case_id=r.test_case_id,
            status=r.status,
            actual_status_code=r.actual_status_code,
            actual_response_body=r.actual_response_body,
            actual_headers=actual_headers,
            response_time_ms=r.response_time_ms,
            error_message=r.error_message,
        ))
    return res_list
