"""SQLAlchemy ORM models.

Importing this package registers all models with Base.metadata,
which is required for create_all() to work.
"""

from app.models.test_case import TestCase
from app.models.test_result import TestResult
from app.models.test_run import TestRun

__all__ = ["TestCase", "TestResult", "TestRun"]
