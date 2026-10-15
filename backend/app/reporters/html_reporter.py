"""HTML report generator."""

from jinja2 import BaseLoader, Environment, select_autoescape

from app.models.test_case import TestCase
from app.models.test_result import TestResult
from app.models.test_run import TestRun
from app.reporters.base_reporter import BaseReporter

# Simple inline template for the HTML report
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Run Report - {{ run.id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        h1, h2 { color: #333; }
        .summary { background: #f4f4f4; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .status-pass { color: green; font-weight: bold; }
        .status-fail { color: red; font-weight: bold; }
        .status-error { color: orange; font-weight: bold; }
        .status-invalid { color: gray; }
    </style>
</head>
<body>
    <h1>Test Run Report</h1>
    
    <div class="summary">
        <h2>Run Summary</h2>
        <p><strong>Run ID:</strong> {{ run.id }}</p>
        <p><strong>Target URL:</strong> {{ run.target_url }}</p>
        <p><strong>Provider/Model:</strong> {{ run.provider }} / {{ run.model }}</p>
        <p><strong>Status:</strong> {{ run.status }}</p>
        <p><strong>Total Tests:</strong> {{ run.total_tests }} ({{ run.valid_tests }} valid, {{ run.invalid_tests }} invalid)</p>
        <p><strong>Results:</strong> <span class="status-pass">{{ run.passed }} Passed</span> | <span class="status-fail">{{ run.failed }} Failed</span> | <span class="status-error">{{ run.errors }} Errors</span></p>
    </div>

    <h2>Test Details</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Validation</th>
                <th>Execution</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
            {% for case in cases %}
            {% set result = result_map.get(case.id) %}
            <tr>
                <td>{{ case.name }}</td>
                <td>{{ case.method }}</td>
                <td>{{ case.endpoint }}</td>
                <td>{{ case.expected_status }}</td>
                <td>{{ result.actual_status_code if result else 'N/A' }}</td>
                <td>{{ case.validation_status }}</td>
                <td class="status-{{ result.status if result else 'invalid' }}">
                    {{ result.status if result else 'Not Executed' }}
                </td>
                <td>
                    {% if result and result.error_message %}
                        {{ result.error_message }}
                    {% elif case.validation_errors %}
                        {{ case.validation_errors }}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

class DictLoader(BaseLoader):
    def __init__(self, templates):
        self.templates = templates

    def get_source(self, environment, template):
        if template in self.templates:
            return self.templates[template], template, lambda: True
        raise Exception(f"Template {template} not found")


class HtmlReporter(BaseReporter):
    """Generates HTML reports for test runs using Jinja2."""
    
    def __init__(self):
        self.env = Environment(
            loader=DictLoader({"report.html": HTML_TEMPLATE}),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def generate(self, run: TestRun, cases: list[TestCase], results: list[TestResult]) -> str:
        template = self.env.get_template("report.html")
        
        # Create map for O(1) lookups in template
        result_map = {r.test_case_id: r for r in results}
        
        return template.render(
            run=run,
            cases=cases,
            results=results,
            result_map=result_map
        )
