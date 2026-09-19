"""TestRun ORM model.

Represents a single test-generation-and-execution cycle. A run tracks
the full lifecycle: creation → generation → validation → execution → completion.

Relationships:
    - One TestRun has many TestCases
    - One TestRun has many TestResults (denormalized for query efficiency)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TestRun(Base):
    """Represents a complete test generation and execution run."""

    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Configuration
    target_url: Mapped[str] = mapped_column(String(2048))
    api_spec: Mapped[str] = mapped_column(Text)  # Full spec content
    provider: Mapped[str] = mapped_column(String(50))  # gemini | openai
    model: Mapped[str] = mapped_column(String(100))  # e.g. gemini-2.5-flash
    categories: Mapped[str] = mapped_column(
        Text, default="[]"  # JSON array of selected categories
    )
    requested_test_count: Mapped[int] = mapped_column(Integer, default=10)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default="created"
        # created | generating | validating | executing | completed | failed
    )

    # Metrics (updated as pipeline progresses)
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    valid_tests: Mapped[int] = mapped_column(Integer, default=0)
    invalid_tests: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    validity_rate: Mapped[float] = mapped_column(Float, default=0.0)
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    test_cases: Mapped[list["TestCase"]] = relationship(
        "TestCase", back_populates="run", cascade="all, delete-orphan"
    )
    test_results: Mapped[list["TestResult"]] = relationship(
        "TestResult",
        back_populates="run",
        cascade="all, delete-orphan",
        foreign_keys="TestResult.run_id",
    )

    def __repr__(self) -> str:
        return f"<TestRun(id={self.id!r}, status={self.status!r})>"
