"""CSV report generator."""

import csv
import io

from app.models.test_case import TestCase
from app.models.test_result import TestResult
from app.models.test_run import TestRun
from app.reporters.base_reporter import BaseReporter


class CsvReporter(BaseReporter):
    """Generates CSV reports for test runs."""
    
    def generate(self, run: TestRun, cases: list[TestCase], results: list[TestResult]) -> str:
        # Create a mapping of case ID to result for easy lookup
        result_map = {r.test_case_id: r for r in results}
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Test ID", "Name", "Category", "Method", "Endpoint", 
            "Expected Status", "Validation Status", "Execution Status", 
            "Actual Status Code", "Response Time (ms)", "Error Message"
        ])
        
        # Write rows
        for tc in cases:
            res = result_map.get(tc.id)
            writer.writerow([
                tc.id,
                tc.name,
                tc.category,
                tc.method,
                tc.endpoint,
                tc.expected_status,
                tc.validation_status,
                res.status if res else "Not executed",
                res.actual_status_code if res else "",
                res.response_time_ms if res else "",
                res.error_message if res else (tc.validation_errors or "")
            ])
            
        return output.getvalue()
