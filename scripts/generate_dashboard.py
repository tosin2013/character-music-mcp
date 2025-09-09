#!/usr/bin/env python3
"""
Quality Dashboard Generator

Generates an HTML dashboard from test results, benchmark data, and validation
reports for continuous monitoring of code quality and performance.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Template


class QualityDashboardGenerator:
    """Generates quality dashboard from CI artifacts"""

    def __init__(self, artifacts_dir: str = "."):
        self.artifacts_dir = Path(artifacts_dir)
        self.dashboard_dir = Path("dashboard")
        self.dashboard_dir.mkdir(exist_ok=True)

        # Dashboard template
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Character Music MCP - Quality Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #f5f7fa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                      gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 10px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #666; font-size: 0.9em; text-transform: uppercase;
                        letter-spacing: 1px; margin-bottom: 10px; }
        .stat-value { font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }
        .stat-value.success { color: #27ae60; }
        .stat-value.warning { color: #f39c12; }
        .stat-value.error { color: #e74c3c; }
        .stat-subtitle { color: #888; font-size: 0.9em; }
        .section { background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section h2 { color: #333; margin-bottom: 20px; padding-bottom: 10px;
                      border-bottom: 2px solid #eee; }
        .test-results { display: grid; gap: 15px; }
        .test-suite { border: 1px solid #eee; border-radius: 8px; padding: 20px; }
        .test-suite h4 { color: #555; margin-bottom: 15px; }
        .test-progress { background: #f8f9fa; height: 8px; border-radius: 4px;
                         overflow: hidden; margin-bottom: 10px; }
        .test-progress-bar { height: 100%; transition: width 0.3s ease; }
        .test-progress-bar.success { background: #27ae60; }
        .test-progress-bar.partial { background: linear-gradient(to right, #27ae60 0%, #f39c12 100%); }
        .benchmark-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .benchmark-item { border: 1px solid #eee; border-radius: 8px; padding: 20px; }
        .benchmark-item h4 { color: #555; margin-bottom: 10px; }
        .benchmark-metric { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .benchmark-metric span:first-child { color: #666; }
        .benchmark-metric span:last-child { font-weight: bold; }
        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8em;
                        font-weight: bold; text-transform: uppercase; }
        .status-badge.passed { background: #d4edda; color: #155724; }
        .status-badge.failed { background: #f8d7da; color: #721c24; }
        .status-badge.warning { background: #fff3cd; color: #856404; }
        .timestamp { color: #888; font-size: 0.9em; text-align: center; margin-top: 30px; }
        .chart-container { height: 300px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #555; }
        .trend-up { color: #27ae60; }
        .trend-down { color: #e74c3c; }
        .trend-stable { color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Character Music MCP</h1>
            <p>Quality Dashboard - Continuous Integration Results</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Overall Test Success</h3>
                <div class="stat-value {{ 'success' if overall_success_rate >= 0.9 else 'warning' if overall_success_rate >= 0.7 else 'error' }}">
                    {{ "%.1f" | format(overall_success_rate * 100) }}%
                </div>
                <div class="stat-subtitle">{{ total_tests }} total tests</div>
            </div>

            <div class="stat-card">
                <h3>Code Coverage</h3>
                <div class="stat-value {{ 'success' if coverage_percentage >= 80 else 'warning' if coverage_percentage >= 60 else 'error' }}">
                    {{ "%.1f" | format(coverage_percentage) }}%
                </div>
                <div class="stat-subtitle">Line coverage</div>
            </div>

            <div class="stat-card">
                <h3>Performance Score</h3>
                <div class="stat-value {{ 'success' if performance_score >= 0.8 else 'warning' if performance_score >= 0.6 else 'error' }}">
                    {{ "%.1f" | format(performance_score * 100) }}%
                </div>
                <div class="stat-subtitle">Benchmarks passed</div>
            </div>

            <div class="stat-card">
                <h3>Documentation Quality</h3>
                <div class="stat-value {{ 'success' if documentation_score >= 0.9 else 'warning' if documentation_score >= 0.7 else 'error' }}">
                    {{ "%.1f" | format(documentation_score * 100) }}%
                </div>
                <div class="stat-subtitle">Examples validated</div>
            </div>
        </div>

        <div class="section">
            <h2>📋 Test Results</h2>
            <div class="test-results">
                {% for suite in test_suites %}
                <div class="test-suite">
                    <h4>{{ suite.name }}</h4>
                    <div class="test-progress">
                        <div class="test-progress-bar {{ 'success' if suite.success_rate >= 0.9 else 'partial' }}"
                             style="width: {{ suite.success_rate * 100 }}%"></div>
                    </div>
                    <div class="benchmark-metric">
                        <span>Passed:</span>
                        <span class="status-badge passed">{{ suite.passed }}/{{ suite.total }}</span>
                    </div>
                    {% if suite.failed > 0 %}
                    <div class="benchmark-metric">
                        <span>Failed:</span>
                        <span class="status-badge failed">{{ suite.failed }}</span>
                    </div>
                    {% endif %}
                    <div class="benchmark-metric">
                        <span>Execution Time:</span>
                        <span>{{ "%.2f" | format(suite.execution_time) }}s</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>🚀 Performance Benchmarks</h2>
            <div class="benchmark-grid">
                {% for benchmark in benchmarks %}
                <div class="benchmark-item">
                    <h4>{{ benchmark.name | title | replace('_', ' ') }}</h4>
                    <div class="benchmark-metric">
                        <span>Execution Time:</span>
                        <span class="{{ 'trend-up' if benchmark.threshold_met else 'trend-down' }}">
                            {{ "%.3f" | format(benchmark.execution_time) }}s
                        </span>
                    </div>
                    <div class="benchmark-metric">
                        <span>Memory Usage:</span>
                        <span>{{ "%.1f" | format(benchmark.memory_usage_mb) }}MB</span>
                    </div>
                    <div class="benchmark-metric">
                        <span>Success Rate:</span>
                        <span>{{ "%.1f" | format(benchmark.success_rate * 100) }}%</span>
                    </div>
                    <div class="benchmark-metric">
                        <span>Status:</span>
                        <span class="status-badge {{ 'passed' if benchmark.threshold_met else 'failed' }}">
                            {{ 'Passed' if benchmark.threshold_met else 'Failed' }}
                        </span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        {% if validation_results %}
        <div class="section">
            <h2>📚 Documentation Validation</h2>
            <table>
                <thead>
                    <tr>
                        <th>Validation Type</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for validation in validation_results %}
                    <tr>
                        <td>{{ validation.type | title }}</td>
                        <td>
                            <span class="status-badge {{ 'passed' if validation.passed else 'failed' }}">
                                {{ 'Passed' if validation.passed else 'Failed' }}
                            </span>
                        </td>
                        <td>{{ "%.1f" | format(validation.score * 100) }}%</td>
                        <td>{{ validation.details }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        {% if security_results %}
        <div class="section">
            <h2>🔒 Security Scan Results</h2>
            <div class="benchmark-grid">
                {% for scan in security_results %}
                <div class="benchmark-item">
                    <h4>{{ scan.tool | title }}</h4>
                    <div class="benchmark-metric">
                        <span>Issues Found:</span>
                        <span class="status-badge {{ 'passed' if scan.issues == 0 else 'warning' if scan.issues < 5 else 'failed' }}">
                            {{ scan.issues }}
                        </span>
                    </div>
                    <div class="benchmark-metric">
                        <span>Severity:</span>
                        <span>{{ scan.max_severity | title }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div class="timestamp">
            Last updated: {{ timestamp }}
        </div>
    </div>
</body>
</html>
        """

    def collect_test_results(self) -> Dict[str, Any]:
        """Collect test results from artifacts"""
        test_data = {
            "overall_success_rate": 0.0,
            "total_tests": 0,
            "test_suites": []
        }

        # Look for test result files
        test_files = list(self.artifacts_dir.glob("**/test_report_*.json"))

        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "suite_results" in data:
                    for suite in data["suite_results"]:
                        test_data["test_suites"].append({
                            "name": suite["suite_name"],
                            "total": suite["total_tests"],
                            "passed": suite["passed"],
                            "failed": suite["failed"],
                            "success_rate": suite.get("success_rate", 0.0),
                            "execution_time": suite["total_time"]
                        })

                test_data["overall_success_rate"] = data.get("overall_success_rate", 0.0)
                test_data["total_tests"] = data.get("total_tests", 0)

            except Exception as e:
                print(f"⚠️ Failed to load test results from {test_file}: {e}")

        return test_data

    def collect_benchmark_results(self) -> List[Dict[str, Any]]:
        """Collect benchmark results from artifacts"""
        benchmarks = []

        # Look for benchmark result files
        benchmark_files = list(self.artifacts_dir.glob("**/benchmark_results.json"))

        for benchmark_file in benchmark_files:
            try:
                with open(benchmark_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "results" in data:
                    for result in data["results"]:
                        benchmarks.append({
                            "name": result["name"],
                            "execution_time": result["execution_time"],
                            "memory_usage_mb": result["memory_usage_mb"],
                            "success_rate": result["success_rate"],
                            "threshold_met": result["threshold_met"]
                        })

            except Exception as e:
                print(f"⚠️ Failed to load benchmark results from {benchmark_file}: {e}")

        return benchmarks

    def collect_validation_results(self) -> List[Dict[str, Any]]:
        """Collect documentation validation results"""
        validations = []

        # Look for validation report files
        validation_files = list(self.artifacts_dir.glob("**/validation_report*.json"))

        for validation_file in validation_files:
            try:
                with open(validation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract validation results
                if "documentation_validation" in data:
                    validations.append({
                        "type": "documentation",
                        "passed": data["documentation_validation"].get("passed", False),
                        "score": data["documentation_validation"].get("score", 0.0),
                        "details": data["documentation_validation"].get("summary", "")
                    })

                if "template_validation" in data:
                    validations.append({
                        "type": "templates",
                        "passed": data["template_validation"].get("passed", False),
                        "score": data["template_validation"].get("score", 0.0),
                        "details": data["template_validation"].get("summary", "")
                    })

                if "example_validation" in data:
                    validations.append({
                        "type": "examples",
                        "passed": data["example_validation"].get("passed", False),
                        "score": data["example_validation"].get("score", 0.0),
                        "details": data["example_validation"].get("summary", "")
                    })

            except Exception as e:
                print(f"⚠️ Failed to load validation results from {validation_file}: {e}")

        return validations

    def collect_security_results(self) -> List[Dict[str, Any]]:
        """Collect security scan results"""
        security_results = []

        # Look for security report files
        security_files = list(self.artifacts_dir.glob("**/*security*.json")) + \
                         list(self.artifacts_dir.glob("**/safety_report.json")) + \
                         list(self.artifacts_dir.glob("**/bandit_report.json"))

        for security_file in security_files:
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "safety" in security_file.name.lower():
                    # Safety report format
                    issues = len(data.get("vulnerabilities", []))
                    max_severity = "low"
                    if issues > 0:
                        severities = [v.get("severity", "low") for v in data.get("vulnerabilities", [])]
                        if "high" in severities:
                            max_severity = "high"
                        elif "medium" in severities:
                            max_severity = "medium"

                    security_results.append({
                        "tool": "safety",
                        "issues": issues,
                        "max_severity": max_severity
                    })

                elif "bandit" in security_file.name.lower():
                    # Bandit report format
                    issues = len(data.get("results", []))
                    max_severity = "low"
                    if issues > 0:
                        severities = [r.get("issue_severity", "low") for r in data.get("results", [])]
                        if "HIGH" in severities:
                            max_severity = "high"
                        elif "MEDIUM" in severities:
                            max_severity = "medium"

                    security_results.append({
                        "tool": "bandit",
                        "issues": issues,
                        "max_severity": max_severity.lower()
                    })

            except Exception as e:
                print(f"⚠️ Failed to load security results from {security_file}: {e}")

        return security_results

    def calculate_coverage_percentage(self) -> float:
        """Calculate code coverage percentage from artifacts"""
        coverage_files = list(self.artifacts_dir.glob("**/coverage.xml"))

        for coverage_file in coverage_files:
            try:
                # Simple XML parsing for coverage percentage
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for line-rate attribute in coverage tag
                import re
                match = re.search(r'line-rate="([0-9.]+)"', content)
                if match:
                    return float(match.group(1)) * 100

            except Exception as e:
                print(f"⚠️ Failed to parse coverage from {coverage_file}: {e}")

        return 75.0  # Default fallback

    def generate_dashboard(self) -> None:
        """Generate complete quality dashboard"""
        print("📊 Generating quality dashboard...")

        # Collect all data
        test_data = self.collect_test_results()
        benchmarks = self.collect_benchmark_results()
        validations = self.collect_validation_results()
        security_results = self.collect_security_results()
        coverage_percentage = self.calculate_coverage_percentage()

        # Calculate performance score
        performance_score = 0.0
        if benchmarks:
            passed_benchmarks = len([b for b in benchmarks if b["threshold_met"]])
            performance_score = passed_benchmarks / len(benchmarks)

        # Calculate documentation score
        documentation_score = 0.0
        if validations:
            passed_validations = len([v for v in validations if v["passed"]])
            documentation_score = passed_validations / len(validations)

        # Prepare template data
        template_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "overall_success_rate": test_data["overall_success_rate"],
            "total_tests": test_data["total_tests"],
            "coverage_percentage": coverage_percentage,
            "performance_score": performance_score,
            "documentation_score": documentation_score,
            "test_suites": test_data["test_suites"],
            "benchmarks": benchmarks,
            "validation_results": validations,
            "security_results": security_results
        }

        # Generate HTML
        template = Template(self.html_template)
        html_content = template.render(**template_data)

        # Save dashboard
        dashboard_file = self.dashboard_dir / "index.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Quality dashboard generated: {dashboard_file}")

        # Generate summary JSON for API access
        summary_data = {
            "timestamp": template_data["timestamp"],
            "summary": {
                "overall_success_rate": template_data["overall_success_rate"],
                "total_tests": template_data["total_tests"],
                "coverage_percentage": template_data["coverage_percentage"],
                "performance_score": template_data["performance_score"],
                "documentation_score": template_data["documentation_score"]
            },
            "counts": {
                "test_suites": len(template_data["test_suites"]),
                "benchmarks": len(template_data["benchmarks"]),
                "validations": len(template_data["validation_results"]),
                "security_scans": len(template_data["security_results"])
            }
        }

        summary_file = self.dashboard_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2)

        print(f"📄 Dashboard summary saved: {summary_file}")


def main():
    """Main dashboard generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate quality dashboard")
    parser.add_argument("--artifacts-dir", "-a", default=".",
                       help="Directory containing CI artifacts")
    parser.add_argument("--output-dir", "-o", default="dashboard",
                       help="Output directory for dashboard")

    args = parser.parse_args()

    generator = QualityDashboardGenerator(args.artifacts_dir)
    generator.dashboard_dir = Path(args.output_dir)
    generator.dashboard_dir.mkdir(exist_ok=True)

    generator.generate_dashboard()

    print("🎉 Quality dashboard generation complete!")


if __name__ == "__main__":
    main()
