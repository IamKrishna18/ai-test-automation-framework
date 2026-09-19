"""TestCase ORM model.

Represents a single AI-generated test case. Stores the structured test
definition (method, endpoint, headers, body, expected results) and its
validation status.

Important:
    Test cases are structured data, NEVER executable Python code.
    The execution engine interprets these definitions to construct HTTP requests.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TestCase(Base):
    """A structured AI-generated test case definition."""

    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_runs.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now
    )

    # Test definition
    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50))
    method: Mapped[str] = mapped_column(String(10))  # GET, POST, PUT, PATCH, DELETE
    endpoint: Mapped[str] = mapped_column(String(2048))
    headers: Mapped[str] = mapped_column(Text, default="{}")  # JSON dict
    query_params: Mapped[str] = mapped_column(Text, default="{}")  # JSON dict
    path_params: Mapped[str] = mapped_column(Text, default="{}")  # JSON dict
    body: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON dict or null
    expected_status: Mapped[int] = mapped_column(Integer)
    expected_fields: Mapped[str] = mapped_column(Text, default="[]")  # JSON list
    expected_response_schema: Mapped[str | None] = mapped_column(
        Text, nullable=True  # JSON schema dict or null
    )
    priority: Mapped[str] = mapped_column(String(20), default="medium")

    # Validation
    validation_status: Mapped[str] = mapped_column(
        String(20), default="pending"  # pending | valid | invalid
    )
    validation_errors: Mapped[str] = mapped_column(
        Text, default="[]"  # JSON array of error strings
    )

    # Relationships
    run: Mapped["TestRun"] = relationship("TestRun", back_populates="test_cases")
    result: Mapped["TestResult | None"] = relationship(
        "TestResult", back_populates="test_case", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<TestCase(id={self.id!r}, name={self.name!r}, "
            f"method={self.method!r}, endpoint={self.endpoint!r})>"
        )
