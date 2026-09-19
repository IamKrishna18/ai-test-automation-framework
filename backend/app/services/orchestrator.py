"""Run execution and validation orchestrator.

Ties together generation, validation, and execution.
"""
import asyncio
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.repositories.run_repo import RunRepository, TestCaseRepository
from app.services.run_service import RunService
from app.executors.http_executor import HttpExecutor
from app.evaluators.result_evaluator import ResultEvaluator
from app.validators.schema_validator import validate_schema
from app.validators.semantic_validator import validate_semantics
from app.services.spec_parser import parse_spec

logger = get_logger(__name__)

class OrchestratorService:
    """Orchestrates the lifecycle of a TestRun."""
    
    def __init__(self, db: Session):
        self.db = db
        self.run_repo = RunRepository(db)
        self.case_repo = TestCaseRepository(db)
        self.run_service = RunService(db)

    def generate_tests(self, run_id: str) -> Dict[str, Any]:
        """Trigger AI test generation and run validation."""
        run = self.run_repo.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")
            
        try:
            # 1. Generate via RunService (uses LLM)
            total, _, _ = self.run_service.generate_tests_for_run(run_id)
            
            # 2. Validate the generated tests
            cases = self.case_repo.get_cases_for_run(run_id)
            parsed_spec = parse_spec(run.api_spec)
            
            valid_count = 0
            invalid_count = 0
            
            for tc in cases:
                schema_errors = validate_schema(tc)
                semantic_errors = validate_semantics(tc, parsed_spec)
                
                all_errors = schema_errors + semantic_errors
                
                if all_errors:
                    tc.validation_status = "invalid"
                    tc.validation_errors = "; ".join(all_errors)
                    invalid_count += 1
                else:
                    tc.validation_status = "valid"
                    valid_count += 1
                    
            run.valid_tests = valid_count
            run.invalid_tests = invalid_count
            self.db.commit()
            
            return {
                "message": "Generation complete",
                "total": total,
                "valid": valid_count,
                "invalid": invalid_count
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self.run_repo.update_status(run_id, "failed", str(e))
            raise

    async def execute_run(self, run_id: str) -> Dict[str, Any]:
        """Execute all VALID tests for a run against the target API."""
        run = self.run_repo.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")
            
        self.run_repo.update_status(run_id, "executing")
        
        executor = HttpExecutor(target_url=run.target_url, db=self.db)
        cases = self.case_repo.get_cases_for_run(run_id)
        
        passed = 0
        failed = 0
        errors = 0
        
        for tc in cases:
            # Only execute valid tests
            if tc.validation_status != "valid":
                continue
                
            # Execute HTTP request
            result = await executor.execute_case(tc)
            
            # Evaluate pass/fail
            evaluated_result = ResultEvaluator.evaluate(tc, result)
            self.db.commit() # Save evaluated status
            
            if evaluated_result.status == "pass":
                passed += 1
            elif evaluated_result.status == "fail":
                failed += 1
            else:
                errors += 1
                
        # Update run stats
        run.passed = passed
        run.failed = failed
        run.errors = errors
        run.status = "completed"
        self.db.commit()
        
        return {
            "message": "Execution complete",
            "passed": passed,
            "failed": failed,
            "errors": errors
        }
