"""Test execution engine.

Responsible for sending HTTP requests exactly as specified by the test cases.
Captures the raw response and timing, but does NOT evaluate pass/fail.
"""

import json
import time
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.test_case import TestCase
from app.models.test_result import TestResult

logger = get_logger(__name__)


class HttpExecutor:
    """Executes test cases against a target API."""

    def __init__(self, target_url: str, db: Session):
        """
        Args:
            target_url: Base URL of the target API.
            db: SQLAlchemy session for recording results.
        """
        self.target_url = target_url.rstrip("/")
        self.db = db
        self.settings = get_settings()

    async def execute_case(self, tc: TestCase) -> TestResult:
        """Execute a single test case.
        
        Args:
            tc: The TestCase ORM model to execute.
            
        Returns:
            The created TestResult ORM model (saved to DB).
        """
        logger.info(f"Executing test {tc.id}: {tc.method} {tc.endpoint}")
        
        # Parse fields from the DB (stored as JSON text)
        headers = json.loads(tc.headers) if tc.headers else {}
        query_params = json.loads(tc.query_params) if tc.query_params else {}
        
        body = None
        if tc.body:
            try:
                body = json.loads(tc.body)
            except json.JSONDecodeError:
                body = tc.body  # Could be plain text in some edge cases
        
        # Build full URL
        endpoint = tc.endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = self.target_url + endpoint

        # Prepare for result
        result = TestResult(
            test_case_id=tc.id,
            run_id=tc.run_id,
            status="error", # Default, updated below
        )
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.settings.default_request_timeout) as client:
                req = client.build_request(
                    method=tc.method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    json=body if isinstance(body, (dict, list)) else None,
                    content=body if not isinstance(body, (dict, list)) else None
                )
                
                response = await client.send(req)
                
                # Record success (meaning HTTP call succeeded, not necessarily test pass)
                result.actual_status_code = response.status_code
                result.actual_headers = json.dumps(dict(response.headers))
                
                try:
                    # Try to parse as JSON first
                    result.actual_response_body = json.dumps(response.json())
                except json.JSONDecodeError:
                    # Fallback to text
                    result.actual_response_body = response.text
                    
                result.status = "executed"  # Temporary status before evaluation
                
        except httpx.TimeoutException as e:
            result.status = "error"
            result.error_message = f"Request timed out after {self.settings.default_request_timeout}s"
            logger.warning(f"Test {tc.id} timed out")
            
        except httpx.RequestError as e:
            result.status = "error"
            result.error_message = f"Network error: {str(e)}"
            logger.warning(f"Test {tc.id} network error: {e}")
            
        except Exception as e:
            result.status = "error"
            result.error_message = f"Execution error: {str(e)}"
            logger.error(f"Test {tc.id} failed to execute: {e}")
            
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            result.response_time_ms = round(elapsed_ms, 2)
            
            # Save result
            self.db.add(result)
            self.db.commit()
            
        return result
