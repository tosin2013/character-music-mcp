#!/usr/bin/env python3
"""
Quality Monitoring System

Monitors test coverage, performance metrics, and overall code quality with
alerting for regressions and threshold violations.
"""

import json
import sys
import os
import time
import smtplib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import argparse


@dataclass
class QualityMetric:
    """Individual quality metric"""
    name: str
    current_value: float
    threshold: float
    trend: str  # "improving", "stable", "declining"
    status: str  # "passing", "warning", "failing"
    last_updated: str
    history: List[float]
    
    @property
    def is_passing(self) -> bool:
        return self.current_value >= self.threshold
    
    @property
    def trend_direction(self) -> str:
        if len(self.history) < 2:
            return "stable"
        
        recent_avg = sum(self.history[-3:]) / min(3, len(self.history))
        older_avg = sum(self.history[-6:-3]) / min(3, len(self.history[-6:-3])) if len(self.history) >= 6 else recent_avg
        
        if recent_avg > older_avg * 1.02:
            return "improving"
        elif recent_avg < older_avg * 0.98:
            return "declining"
        else:
            return "stable"


@dataclass
class QualityAlert:
    """Quality alert for threshold violations"""
    metric_name: str
    alert_type: str  # "threshold_violation", "regression", "improvement"
    severity: str  # "critical", "warning", "info"
    message: str
    timestamp: str
    current_value: float
    threshold_value: Optional[float] = None
    previous_value: Optional[float] = None


class QualityMonitor:
    """Comprehensive quality monitoring system"""
    
    def __init__(self, config_file: str = "quality_config.json"):
        self.config_file = Path(config_file)
        self.metrics_file = Path("quality_metrics.json")
        self.alerts_file = Path("quality_alerts.json")
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize metrics
        self.metrics: Dict[str, QualityMetric] = {}
        self.alerts: List[QualityAlert] = []
        
        # Load existing metrics
        self.load_metrics()
    
    def load_config(self) -> Dict[str, Any]:
        """Load quality monitoring configuration"""
        default_config = {
            "thresholds": {
                "test_coverage": 80.0,
                "test_success_rate": 95.0,
                "performance_score": 80.0,
                "documentation_score": 90.0,
                "security_score": 95.0,
                "code_quality_score": 85.0
            },
            "alerting": {
                "enabled": True,
                "email_notifications": False,
                "slack_notifications": False,
                "console_alerts": True
            },
            "monitoring": {
                "history_length": 30,  # Keep 30 data points
                "regression_threshold": 0.05,  # 5% regression triggers alert
                "improvement_threshold": 0.10,  # 10% improvement triggers notification
                "check_interval": 3600  # Check every hour
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_emails": []
            },
            "slack": {
                "webhook_url": "",
                "channel": "#quality-alerts"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
            except Exception as e:
                print(f"⚠️ Failed to load config, using defaults: {e}")
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def load_metrics(self) -> None:
        """Load existing quality metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                for name, metric_data in data.items():
                    self.metrics[name] = QualityMetric(
                        name=metric_data["name"],
                        current_value=metric_data["current_value"],
                        threshold=metric_data["threshold"],
                        trend=metric_data["trend"],
                        status=metric_data["status"],
                        last_updated=metric_data["last_updated"],
                        history=metric_data["history"]
                    )
            except Exception as e:
                print(f"⚠️ Failed to load metrics: {e}")
    
    def save_metrics(self) -> None:
        """Save quality metrics to file"""
        data = {name: asdict(metric) for name, metric in self.metrics.items()}
        
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_metric(self, name: str, value: float, threshold: Optional[float] = None) -> None:
        """Update a quality metric"""
        current_time = datetime.now().isoformat()
        
        if name in self.metrics:
            metric = self.metrics[name]
            previous_value = metric.current_value
            
            # Update history
            metric.history.append(value)
            if len(metric.history) > self.config["monitoring"]["history_length"]:
                metric.history = metric.history[-self.config["monitoring"]["history_length"]:]
            
            # Update values
            metric.current_value = value
            if threshold is not None:
                metric.threshold = threshold
            metric.last_updated = current_time
            metric.trend = metric.trend_direction
            metric.status = "passing" if metric.is_passing else "failing"
            
            # Check for alerts
            self.check_metric_alerts(metric, previous_value)
            
        else:
            # Create new metric
            threshold = threshold or self.config["thresholds"].get(name, 80.0)
            metric = QualityMetric(
                name=name,
                current_value=value,
                threshold=threshold,
                trend="stable",
                status="passing" if value >= threshold else "failing",
                last_updated=current_time,
                history=[value]
            )
            self.metrics[name] = metric
    
    def check_metric_alerts(self, metric: QualityMetric, previous_value: float) -> None:
        """Check for metric alerts and create notifications"""
        current_time = datetime.now().isoformat()
        
        # Threshold violation alert
        if not metric.is_passing:
            alert = QualityAlert(
                metric_name=metric.name,
                alert_type="threshold_violation",
                severity="critical" if metric.current_value < metric.threshold * 0.8 else "warning",
                message=f"{metric.name} is below threshold: {metric.current_value:.1f}% < {metric.threshold:.1f}%",
                timestamp=current_time,
                current_value=metric.current_value,
                threshold_value=metric.threshold
            )
            self.alerts.append(alert)
        
        # Regression alert
        regression_threshold = self.config["monitoring"]["regression_threshold"]
        if previous_value > 0 and (previous_value - metric.current_value) / previous_value > regression_threshold:
            alert = QualityAlert(
                metric_name=metric.name,
                alert_type="regression",
                severity="warning",
                message=f"{metric.name} regressed: {previous_value:.1f}% → {metric.current_value:.1f}% ({((metric.current_value - previous_value) / previous_value * 100):+.1f}%)",
                timestamp=current_time,
                current_value=metric.current_value,
                previous_value=previous_value
            )
            self.alerts.append(alert)
        
        # Improvement notification
        improvement_threshold = self.config["monitoring"]["improvement_threshold"]
        if previous_value > 0 and (metric.current_value - previous_value) / previous_value > improvement_threshold:
            alert = QualityAlert(
                metric_name=metric.name,
                alert_type="improvement",
                severity="info",
                message=f"{metric.name} improved: {previous_value:.1f}% → {metric.current_value:.1f}% ({((metric.current_value - previous_value) / previous_value * 100):+.1f}%)",
                timestamp=current_time,
                current_value=metric.current_value,
                previous_value=previous_value
            )
            self.alerts.append(alert)
    
    def collect_test_coverage(self) -> float:
        """Collect current test coverage percentage"""
        coverage_files = [
            Path("coverage.xml"),
            Path("htmlcov/index.html"),
            Path(".coverage")
        ]
        
        # Try to parse coverage.xml first
        coverage_file = Path("coverage.xml")
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                coverage_elem = root.find(".")
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get("line-rate", 0))
                    return line_rate * 100
            except Exception as e:
                print(f"⚠️ Failed to parse coverage.xml: {e}")
        
        # Fallback to coverage command
        try:
            import subprocess
            result = subprocess.run(
                ["python", "-m", "coverage", "report", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return coverage_data.get("totals", {}).get("percent_covered", 0.0)
        except Exception as e:
            print(f"⚠️ Failed to get coverage from command: {e}")
        
        return 0.0
    
    def collect_test_success_rate(self) -> float:
        """Collect current test success rate"""
        # Look for recent test reports
        test_reports = list(Path(".").glob("*test_report*.json"))
        
        if test_reports:
            # Use most recent report
            latest_report = max(test_reports, key=lambda p: p.stat().st_mtime)
            
            try:
                with open(latest_report, 'r') as f:
                    data = json.load(f)
                
                return data.get("overall_success_rate", 0.0) * 100
            except Exception as e:
                print(f"⚠️ Failed to parse test report: {e}")
        
        return 0.0
    
    def collect_performance_score(self) -> float:
        """Collect current performance benchmark score"""
        benchmark_files = list(Path(".").glob("benchmark_results*.json"))
        
        if benchmark_files:
            latest_benchmark = max(benchmark_files, key=lambda p: p.stat().st_mtime)
            
            try:
                with open(latest_benchmark, 'r') as f:
                    data = json.load(f)
                
                if "results" in data:
                    total_benchmarks = len(data["results"])
                    passed_benchmarks = len([r for r in data["results"] if r.get("threshold_met", False)])
                    return (passed_benchmarks / total_benchmarks * 100) if total_benchmarks > 0 else 0.0
            except Exception as e:
                print(f"⚠️ Failed to parse benchmark results: {e}")
        
        return 0.0
    
    def collect_documentation_score(self) -> float:
        """Collect current documentation validation score"""
        validation_reports = list(Path(".").glob("validation_report*.json"))
        
        if validation_reports:
            latest_report = max(validation_reports, key=lambda p: p.stat().st_mtime)
            
            try:
                with open(latest_report, 'r') as f:
                    data = json.load(f)
                
                return data.get("overall_score", 0.0) * 100
            except Exception as e:
                print(f"⚠️ Failed to parse validation report: {e}")
        
        return 0.0
    
    def collect_security_score(self) -> float:
        """Collect current security scan score"""
        security_files = ["safety_report.json", "bandit_report.json"]
        
        total_issues = 0
        critical_issues = 0
        
        for security_file in security_files:
            if Path(security_file).exists():
                try:
                    with open(security_file, 'r') as f:
                        data = json.load(f)
                    
                    if "safety" in security_file:
                        vulnerabilities = data.get("vulnerabilities", [])
                        total_issues += len(vulnerabilities)
                        critical_issues += len([v for v in vulnerabilities if v.get("severity") == "high"])
                    
                    elif "bandit" in security_file:
                        results = data.get("results", [])
                        total_issues += len(results)
                        critical_issues += len([r for r in results if r.get("issue_severity") == "HIGH"])
                
                except Exception as e:
                    print(f"⚠️ Failed to parse {security_file}: {e}")
        
        # Calculate score based on issues found
        if total_issues == 0:
            return 100.0
        elif critical_issues == 0:
            return max(80.0, 100.0 - total_issues * 5)  # Deduct 5% per non-critical issue
        else:
            return max(50.0, 100.0 - critical_issues * 20 - (total_issues - critical_issues) * 5)
    
    def collect_code_quality_score(self) -> float:
        """Collect current code quality score from linting"""
        try:
            import subprocess
            
            # Run ruff check
            result = subprocess.run(
                ["python", "-m", "ruff", "check", ".", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                total_issues = len(issues)
                
                # Calculate score based on issues
                if total_issues == 0:
                    return 100.0
                else:
                    # Deduct points based on issue severity
                    score = 100.0
                    for issue in issues:
                        severity = issue.get("severity", "low")
                        if severity == "error":
                            score -= 5
                        elif severity == "warning":
                            score -= 2
                        else:
                            score -= 1
                    
                    return max(0.0, score)
            
        except Exception as e:
            print(f"⚠️ Failed to get code quality score: {e}")
        
        return 85.0  # Default score
    
    def collect_all_metrics(self) -> None:
        """Collect all quality metrics"""
        print("📊 Collecting quality metrics...")
        
        metrics_to_collect = [
            ("test_coverage", self.collect_test_coverage),
            ("test_success_rate", self.collect_test_success_rate),
            ("performance_score", self.collect_performance_score),
            ("documentation_score", self.collect_documentation_score),
            ("security_score", self.collect_security_score),
            ("code_quality_score", self.collect_code_quality_score)
        ]
        
        for metric_name, collector_func in metrics_to_collect:
            try:
                value = collector_func()
                threshold = self.config["thresholds"].get(metric_name, 80.0)
                self.update_metric(metric_name, value, threshold)
                
                status = "✅" if value >= threshold else "❌"
                print(f"  {status} {metric_name}: {value:.1f}% (threshold: {threshold:.1f}%)")
                
            except Exception as e:
                print(f"  ❌ Failed to collect {metric_name}: {e}")
    
    def send_email_alert(self, alert: QualityAlert) -> bool:
        """Send email alert notification"""
        if not self.config["alerting"]["email_notifications"]:
            return False
        
        email_config = self.config["email"]
        if not email_config["sender_email"] or not email_config["recipient_emails"]:
            return False
        
        try:
            # Create message
            msg = MimeMultipart()
            msg["From"] = email_config["sender_email"]
            msg["To"] = ", ".join(email_config["recipient_emails"])
            msg["Subject"] = f"Quality Alert: {alert.metric_name} - {alert.alert_type}"
            
            # Email body
            body = f"""
Quality Alert Notification

Metric: {alert.metric_name}
Alert Type: {alert.alert_type}
Severity: {alert.severity}
Timestamp: {alert.timestamp}

Message: {alert.message}

Current Value: {alert.current_value:.1f}%
"""
            
            if alert.threshold_value:
                body += f"Threshold: {alert.threshold_value:.1f}%\n"
            
            if alert.previous_value:
                body += f"Previous Value: {alert.previous_value:.1f}%\n"
            
            body += "\nPlease investigate and take appropriate action."
            
            msg.attach(MimeText(body, "plain"))
            
            # Send email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["sender_email"], email_config["sender_password"])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to send email alert: {e}")
            return False
    
    def send_console_alert(self, alert: QualityAlert) -> None:
        """Send console alert notification"""
        severity_icons = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon = severity_icons.get(alert.severity, "📢")
        print(f"\n{icon} QUALITY ALERT - {alert.severity.upper()}")
        print(f"Metric: {alert.metric_name}")
        print(f"Type: {alert.alert_type}")
        print(f"Message: {alert.message}")
        print(f"Time: {alert.timestamp}")
        print("-" * 50)
    
    def process_alerts(self) -> None:
        """Process and send all pending alerts"""
        if not self.alerts:
            return
        
        print(f"\n📢 Processing {len(self.alerts)} quality alerts...")
        
        for alert in self.alerts:
            # Console alerts
            if self.config["alerting"]["console_alerts"]:
                self.send_console_alert(alert)
            
            # Email alerts
            if self.config["alerting"]["email_notifications"]:
                if self.send_email_alert(alert):
                    print(f"✅ Email alert sent for {alert.metric_name}")
                else:
                    print(f"❌ Failed to send email alert for {alert.metric_name}")
        
        # Save alerts to file
        alerts_data = [asdict(alert) for alert in self.alerts]
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        # Clear processed alerts
        self.alerts.clear()
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "passing",
            "metrics": {},
            "summary": {
                "total_metrics": len(self.metrics),
                "passing_metrics": 0,
                "failing_metrics": 0,
                "average_score": 0.0
            },
            "trends": {
                "improving": 0,
                "stable": 0,
                "declining": 0
            }
        }
        
        total_score = 0.0
        
        for name, metric in self.metrics.items():
            report["metrics"][name] = asdict(metric)
            
            if metric.is_passing:
                report["summary"]["passing_metrics"] += 1
            else:
                report["summary"]["failing_metrics"] += 1
                report["overall_status"] = "failing"
            
            total_score += metric.current_value
            
            # Count trends
            if metric.trend == "improving":
                report["trends"]["improving"] += 1
            elif metric.trend == "declining":
                report["trends"]["declining"] += 1
            else:
                report["trends"]["stable"] += 1
        
        if self.metrics:
            report["summary"]["average_score"] = total_score / len(self.metrics)
        
        return report
    
    def print_quality_summary(self) -> None:
        """Print quality monitoring summary"""
        print("\n" + "=" * 60)
        print("📊 QUALITY MONITORING SUMMARY")
        print("=" * 60)
        
        if not self.metrics:
            print("No metrics available")
            return
        
        # Overall status
        failing_metrics = [m for m in self.metrics.values() if not m.is_passing]
        overall_status = "✅ PASSING" if not failing_metrics else "❌ FAILING"
        print(f"Overall Status: {overall_status}")
        
        # Metrics summary
        total_score = sum(m.current_value for m in self.metrics.values())
        average_score = total_score / len(self.metrics)
        print(f"Average Score: {average_score:.1f}%")
        print(f"Metrics: {len(self.metrics) - len(failing_metrics)}/{len(self.metrics)} passing")
        
        print("\n📋 Metric Details:")
        for name, metric in sorted(self.metrics.items()):
            status = "✅" if metric.is_passing else "❌"
            trend_icon = {"improving": "📈", "stable": "➡️", "declining": "📉"}.get(metric.trend, "➡️")
            
            print(f"  {status} {name}: {metric.current_value:.1f}% {trend_icon}")
            if not metric.is_passing:
                print(f"    Threshold: {metric.threshold:.1f}% (deficit: {metric.threshold - metric.current_value:.1f}%)")
        
        # Trends
        trends = {"improving": 0, "stable": 0, "declining": 0}
        for metric in self.metrics.values():
            trends[metric.trend] += 1
        
        print(f"\n📈 Trends:")
        print(f"  Improving: {trends['improving']}")
        print(f"  Stable: {trends['stable']}")
        print(f"  Declining: {trends['declining']}")
        
        print("=" * 60)
    
    def run_monitoring_cycle(self) -> bool:
        """Run complete monitoring cycle"""
        print("🔍 Starting quality monitoring cycle...")
        
        # Collect all metrics
        self.collect_all_metrics()
        
        # Save metrics
        self.save_metrics()
        
        # Process alerts
        self.process_alerts()
        
        # Generate and save report
        report = self.generate_quality_report()
        report_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_quality_summary()
        
        print(f"📄 Quality report saved: {report_file}")
        
        return report["overall_status"] == "passing"


def main():
    """Main monitoring execution"""
    parser = argparse.ArgumentParser(description="Quality monitoring system")
    parser.add_argument("--config", "-c", default="quality_config.json",
                       help="Configuration file path")
    parser.add_argument("--continuous", action="store_true",
                       help="Run in continuous monitoring mode")
    parser.add_argument("--interval", "-i", type=int, default=3600,
                       help="Monitoring interval in seconds (for continuous mode)")
    parser.add_argument("--alert-threshold", type=float, default=80.0,
                       help="Global alert threshold percentage")
    
    args = parser.parse_args()
    
    monitor = QualityMonitor(args.config)
    
    # Update thresholds if specified
    if args.alert_threshold:
        for key in monitor.config["thresholds"]:
            monitor.config["thresholds"][key] = args.alert_threshold
    
    if args.continuous:
        print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
        try:
            while True:
                success = monitor.run_monitoring_cycle()
                if not success:
                    print("⚠️ Quality issues detected!")
                
                print(f"💤 Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    else:
        # Single monitoring cycle
        success = monitor.run_monitoring_cycle()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()