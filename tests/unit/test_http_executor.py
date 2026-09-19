"""Unit tests for the HTTP execution engine."""

import json
from unittest.mock import AsyncMock, patch

import pytest
import httpx
from sqlalchemy.orm import Session

from app.executors.http_executor import HttpExecutor
from app.models.test_case import TestCase
from app.models.test_result import TestResult

@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=Session)


@pytest.fixture
def sample_test_case():
    return TestCase(
        id="test-123",
        run_id="run-456",
        method="POST",
        endpoint="/api/users",
        headers='{"Authorization": "Bearer token"}',
        query_params='{"limit": "10"}',
        body='{"name": "Alice"}',
    )


@pytest.mark.asyncio
@patch("app.executors.http_executor.httpx.AsyncClient")
async def test_execute_case_success(mock_client_class, mock_db_session, sample_test_case):
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status_code = 201
    mock_response.headers = httpx.Headers({"Content-Type": "application/json"})
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    
    mock_client = mock_client_class.return_value.__aenter__.return_value
    mock_client.build_request.return_value = AsyncMock()
    mock_client.send.return_value = mock_response

    executor = HttpExecutor(target_url="http://target", db=mock_db_session)
    result = await executor.execute_case(sample_test_case)

    # Verify HTTP call arguments
    mock_client.build_request.assert_called_once_with(
        method="POST",
        url="http://target/api/users",
        headers={"Authorization": "Bearer token"},
        params={"limit": "10"},
        json={"name": "Alice"},
        content=None
    )
    
    # Verify DB insertion
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    
    # Verify result model
    assert result.status == "executed"
    assert result.actual_status_code == 201
    assert "Content-Type" in json.loads(result.actual_headers)
    assert json.loads(result.actual_response_body) == {"id": 1, "name": "Alice"}
    assert result.response_time_ms is not None


@pytest.mark.asyncio
@patch("app.executors.http_executor.httpx.AsyncClient")
async def test_execute_case_timeout(mock_client_class, mock_db_session, sample_test_case):
    mock_client = mock_client_class.return_value.__aenter__.return_value
    mock_client.send.side_effect = httpx.TimeoutException("Timeout")

    executor = HttpExecutor(target_url="http://target", db=mock_db_session)
    result = await executor.execute_case(sample_test_case)

    assert result.status == "error"
    assert "timed out" in result.error_message
    assert result.actual_status_code is None
