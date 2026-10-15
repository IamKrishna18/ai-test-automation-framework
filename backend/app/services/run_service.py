"""Service orchestrating the test run lifecycle.

This service ties together the spec parser, prompt builder, LLM providers,
validators, and executors to move a TestRun through its states.
"""

import json

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.test_case import TestCase
from app.models.test_run import TestRun
from app.prompts.test_generation import build_generation_prompt
from app.providers.provider_factory import get_llm_provider
from app.services.spec_parser import parse_spec

logger = get_logger(__name__)

class RunService:
    def __init__(self, db: Session):
        self.db = db

    def generate_tests_for_run(self, run_id: str) -> tuple[int, int, int]:
        """Generate test cases for a run using the LLM.
        
        Returns:
            Tuple of (total_generated, valid_count, invalid_count).
        """
        run = self.db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
            
        run.status = "generating"
        self.db.commit()
        
        try:
            # 1. Parse spec
            parsed_spec = parse_spec(run.api_spec)
            
            # 2. Build prompt
            categories = json.loads(run.categories)
            prompt = build_generation_prompt(
                api_spec=parsed_spec.raw_spec, 
                test_count=run.requested_test_count,
                categories=categories
            )
            
            # 3. Call LLM
            provider = get_llm_provider(run.provider)
            result = provider.generate_test_cases(prompt, run.model)
            
            # 4. Store raw generated cases (validation happens in next stage)
            # For now, we'll do a simple schema dump. Full validation in Stage 7.
            valid_count = 0
            invalid_count = 0
            
            for raw_tc in result.test_cases:
                tc = TestCase(
                    run_id=run.id,
                    name=raw_tc.get("name", "Unknown Test"),
                    description=raw_tc.get("description", ""),
                    category=raw_tc.get("category", "functional"),
                    method=str(raw_tc.get("method", "GET")).upper(),
                    endpoint=raw_tc.get("endpoint", "/"),
                    headers=json.dumps(raw_tc.get("headers", {})),
                    query_params=json.dumps(raw_tc.get("query_params", {})),
                    path_params=json.dumps(raw_tc.get("path_params", {})),
                    body=json.dumps(raw_tc.get("body")) if raw_tc.get("body") is not None else None,
                    expected_status=int(raw_tc.get("expected_status", 200)),
                    expected_fields=json.dumps(raw_tc.get("expected_fields", [])),
                    priority=raw_tc.get("priority", "medium"),
                    validation_status="pending",
                )
                self.db.add(tc)
                
            run.total_tests = len(result.test_cases)
            run.status = "generated"
            self.db.commit()
            
            logger.info(f"Generated {run.total_tests} tests for run {run_id}")
            return run.total_tests, 0, 0
            
        except Exception as e:
            run.status = "failed"
            self.db.commit()
            logger.error(f"Test generation failed for run {run_id}: {e}")
            raise
