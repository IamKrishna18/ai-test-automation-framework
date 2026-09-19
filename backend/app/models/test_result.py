"""TestResult ORM model.

Represents the outcome of executing a single test case against the target API.

Status semantics:
    - PASS:    API responded and behavior matched expectations.
    - FAIL:    API responded but behavior didn't match expectations.
    - ERROR:   Framework could not execute the test (e.g., timeout, DNS failure).
    - SKIPPED: Test was not executed (e.g., invalid test case).

Important:
    A FAIL does NOT automatically mean the AI was wrong. It means
    expected != actual, which could indicate a real API bug.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TestResult(Base):
    """Execution result for a single test case."""

    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    test_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_cases.id", ondelete="CASCADE")
    )
    # Denormalized for efficient queries (e.g., all results for a run)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_runs.id", ondelete="CASCADE")
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now
    )

    # Result
    status: Mapped[str] = mapped_column(
        String(20)  # pass | fail | error | skipped
    )
    actual_status_code: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    response_time_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    actual_response_body: Mapped[str | None] = mapped_column(
        Text, nullable=True  # JSON string
    )
    actual_headers: Mapped[str | None] = mapped_column(
        Text, nullable=True  # JSON dict
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    evaluation_details: Mapped[str | None] = mapped_column(
        Text, nullable=True  # JSON: field-by-field comparison
    )

    # Relationships
    test_case: Mapped["TestCase"] = relationship(
        "TestCase", back_populates="result"
    )
    run: Mapped["TestRun"] = relationship(
        "TestRun", back_populates="test_results", foreign_keys=[run_id]
    )

    def __repr__(self) -> str:
        return f"<TestResult(id={self.id!r}, status={self.status!r})>"
