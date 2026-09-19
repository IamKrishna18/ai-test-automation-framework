"""Base reporter interface."""

from abc import ABC, abstractmethod
from typing import Any

from app.models.test_run import TestRun
from app.models.test_case import TestCase
from app.models.test_result import TestResult

class BaseReporter(ABC):
    """Abstract base class for all report generators."""
    
    @abstractmethod
    def generate(self, run: TestRun, cases: list[TestCase], results: list[TestResult]) -> Any:
        """Generate a report.
        
        Returns:
            The generated report data (string, bytes, or dict).
        """
        ...
