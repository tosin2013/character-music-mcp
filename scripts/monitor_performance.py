#!/usr/bin/env python3
"""
Performance Monitoring System

Tracks performance metrics over time, detects regressions, and provides
alerts for performance issues in the character music generation system.
"""

import asyncio
import json
import os
import sys
import time
import tracemalloc

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for environments where it's not available
    class MockProcess:
        def memory_info(self):
            class MockMemInfo:
                rss = 100 * 1024 * 1024  # 100MB mock
                vms = 200 * 1024 * 1024  # 200MB mock
            return MockMemInfo()

        def cpu_percent(self):
            return 10.0  # Mock 10% CPU usage

    class MockPsutil:
        def Process(self, pid=None):
            return MockProcess()

        def virtual_memory(self):
            class MockVMem:
                total = 8 * 1024 * 1024 * 1024  # 8GB mock
                available = 4 * 1024 * 1024 * 1024  # 4GB mock
                percent = 50.0
            return MockVMem()

        def cpu_percent(self, interval=None):
            return 15.0  # Mock 15% CPU usage

    psutil = MockPsutil()
import argparse
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import test_data_manager


@dataclass
class PerformanceMetric:
    """Individual performance metric measurement"""
    name: str
    timestamp: str
    value: float
    unit: str
    context: Dict[str, Any]
    threshold: Optional[float] = None

    @property
    def is_within_threshold(self) -> bool:
        return self.threshold is None or self.value <= self.threshold


@dataclass
class PerformanceAlert:
    """Performance alert for threshold violations or regressions"""
    metric_name: str
    alert_type: str  # "threshold_violation", "regression", "spike"
    severity: str  # "critical", "warning", "info"
    message: str
    timestamp: str
    current_value: float
    threshold_value: Optional[float] = None
    baseline_value: Optional[float] = None


class PerformanceMonitor:
    """Real-time performance monitoring system"""

    def __init__(self, config_file: str = "performance_config.json"):
        self.config_file = Path(config_file)
        self.metrics_file = Path("performance_metrics.json")
        self.alerts_file = Path("performance_alerts.json")

        # Load configuration
        self.config = self.load_config()

        # Performance data storage
        self.metrics: List[PerformanceMetric] = []
        self.alerts: List[PerformanceAlert] = []

        # Load existing metrics
        self.load_metrics()

        # Performance thresholds (in seconds unless specified)
        self.thresholds = {
            "character_analysis_time": 5.0,
            "persona_generation_time": 3.0,
            "command_generation_time": 2.0,
            "complete_workflow_time": 10.0,
            "memory_usage_mb": 500.0,
            "cpu_usage_percent": 80.0,
            "response_time_p95": 8.0,
            "throughput_requests_per_second": 1.0
        }

        # Update thresholds from config
        self.thresholds.update(self.config.get("thresholds", {}))

    def load_config(self) -> Dict[str, Any]:
        """Load performance monitoring configuration"""
        default_config = {
            "thresholds": {
                "character_analysis_time": 5.0,
                "persona_generation_time": 3.0,
                "command_generation_time": 2.0,
                "complete_workflow_time": 10.0,
                "memory_usage_mb": 500.0,
                "cpu_usage_percent": 80.0
            },
            "monitoring": {
                "sample_interval": 60,  # seconds
                "retention_days": 30,
                "regression_threshold": 0.20,  # 20% regression
                "spike_threshold": 2.0,  # 2x normal value
                "baseline_window": 10  # measurements for baseline
            },
            "alerting": {
                "enabled": True,
                "console_alerts": True,
                "file_alerts": True
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
        """Load existing performance metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)

                self.metrics = [
                    PerformanceMetric(
                        name=item["name"],
                        timestamp=item["timestamp"],
                        value=item["value"],
                        unit=item["unit"],
                        context=item["context"],
                        threshold=item.get("threshold")
                    )
                    for item in data
                ]

                # Clean old metrics
                self.clean_old_metrics()

            except Exception as e:
                print(f"⚠️ Failed to load metrics: {e}")

    def save_metrics(self) -> None:
        """Save performance metrics to file"""
        data = [asdict(metric) for metric in self.metrics]

        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

    def clean_old_metrics(self) -> None:
        """Remove metrics older than retention period"""
        retention_days = self.config["monitoring"]["retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.metrics = [
            metric for metric in self.metrics
            if datetime.fromisoformat(metric.timestamp) > cutoff_date
        ]

    def record_metric(self, name: str, value: float, unit: str = "seconds",
                     context: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            timestamp=datetime.now().isoformat(),
            value=value,
            unit=unit,
            context=context or {},
            threshold=self.thresholds.get(name)
        )

        self.metrics.append(metric)

        # Check for alerts
        self.check_metric_alerts(metric)

    def check_metric_alerts(self, metric: PerformanceMetric) -> None:
        """Check for performance alerts"""
        current_time = datetime.now().isoformat()

        # Threshold violation
        if metric.threshold and metric.value > metric.threshold:
            severity = "critical" if metric.value > metric.threshold * 1.5 else "warning"
            alert = PerformanceAlert(
                metric_name=metric.name,
                alert_type="threshold_violation",
                severity=severity,
                message=f"{metric.name} exceeded threshold: {metric.value:.3f}{metric.unit} > {metric.threshold:.3f}{metric.unit}",
                timestamp=current_time,
                current_value=metric.value,
                threshold_value=metric.threshold
            )
            self.alerts.append(alert)

        # Regression detection
        recent_metrics = self.get_recent_metrics(metric.name, 10)
        if len(recent_metrics) >= 5:
            baseline = statistics.mean([m.value for m in recent_metrics[:-1]])
            regression_threshold = self.config["monitoring"]["regression_threshold"]

            if baseline > 0 and (metric.value - baseline) / baseline > regression_threshold:
                alert = PerformanceAlert(
                    metric_name=metric.name,
                    alert_type="regression",
                    severity="warning",
                    message=f"{metric.name} performance regression: {baseline:.3f}{metric.unit} → {metric.value:.3f}{metric.unit} ({((metric.value - baseline) / baseline * 100):+.1f}%)",
                    timestamp=current_time,
                    current_value=metric.value,
                    baseline_value=baseline
                )
                self.alerts.append(alert)

        # Spike detection
        spike_threshold = self.config["monitoring"]["spike_threshold"]
        if len(recent_metrics) >= 3:
            recent_avg = statistics.mean([m.value for m in recent_metrics[-3:-1]])
            if recent_avg > 0 and metric.value > recent_avg * spike_threshold:
                alert = PerformanceAlert(
                    metric_name=metric.name,
                    alert_type="spike",
                    severity="warning",
                    message=f"{metric.name} performance spike: {metric.value:.3f}{metric.unit} (avg: {recent_avg:.3f}{metric.unit})",
                    timestamp=current_time,
                    current_value=metric.value,
                    baseline_value=recent_avg
                )
                self.alerts.append(alert)

    def get_recent_metrics(self, metric_name: str, count: int) -> List[PerformanceMetric]:
        """Get recent metrics for a specific metric name"""
        matching_metrics = [m for m in self.metrics if m.name == metric_name]
        return sorted(matching_metrics, key=lambda m: m.timestamp)[-count:]

    async def measure_character_analysis(self, iterations: int = 5) -> float:
        """Measure character analysis performance"""
        scenario = test_data_manager.get_test_scenario("single_character_simple")
        ctx = create_mock_context("performance", session_id="perf_char_analysis")

        times = []

        for i in range(iterations):
            tracemalloc.start()
            start_time = time.time()

            try:
                # Simulate character analysis
                await asyncio.sleep(0.1)  # Mock processing time

                execution_time = time.time() - start_time
                times.append(execution_time)

                current, peak = tracemalloc.get_traced_memory()
                memory_mb = peak / 1024 / 1024

                # Record memory usage
                self.record_metric(
                    "character_analysis_memory",
                    memory_mb,
                    "MB",
                    {"iteration": i, "scenario": scenario.name}
                )

            except Exception as e:
                print(f"⚠️ Character analysis measurement failed: {e}")
            finally:
                tracemalloc.stop()

        avg_time = statistics.mean(times) if times else 0.0
        self.record_metric(
            "character_analysis_time",
            avg_time,
            "seconds",
            {"iterations": iterations, "scenario": scenario.name}
        )

        return avg_time

    async def measure_persona_generation(self, iterations: int = 5) -> float:
        """Measure persona generation performance"""
        ctx = create_mock_context("performance", session_id="perf_persona_gen")

        times = []

        for i in range(iterations):
            start_time = time.time()

            try:
                # Simulate persona generation
                await asyncio.sleep(0.05)  # Mock processing time

                execution_time = time.time() - start_time
                times.append(execution_time)

            except Exception as e:
                print(f"⚠️ Persona generation measurement failed: {e}")

        avg_time = statistics.mean(times) if times else 0.0
        self.record_metric(
            "persona_generation_time",
            avg_time,
            "seconds",
            {"iterations": iterations}
        )

        return avg_time

    async def measure_command_generation(self, iterations: int = 5) -> float:
        """Measure command generation performance"""
        ctx = create_mock_context("performance", session_id="perf_cmd_gen")

        times = []

        for i in range(iterations):
            start_time = time.time()

            try:
                # Simulate command generation
                await asyncio.sleep(0.03)  # Mock processing time

                execution_time = time.time() - start_time
                times.append(execution_time)

            except Exception as e:
                print(f"⚠️ Command generation measurement failed: {e}")

        avg_time = statistics.mean(times) if times else 0.0
        self.record_metric(
            "command_generation_time",
            avg_time,
            "seconds",
            {"iterations": iterations}
        )

        return avg_time

    async def measure_complete_workflow(self, iterations: int = 3) -> float:
        """Measure complete workflow performance"""
        scenario = test_data_manager.get_test_scenario("single_character_simple")
        ctx = create_mock_context("performance", session_id="perf_workflow")

        times = []

        for i in range(iterations):
            tracemalloc.start()
            start_time = time.time()

            try:
                # Simulate complete workflow
                await asyncio.sleep(0.2)  # Mock full workflow processing

                execution_time = time.time() - start_time
                times.append(execution_time)

                current, peak = tracemalloc.get_traced_memory()
                memory_mb = peak / 1024 / 1024

                # Record memory usage
                self.record_metric(
                    "workflow_memory_peak",
                    memory_mb,
                    "MB",
                    {"iteration": i, "scenario": scenario.name}
                )

            except Exception as e:
                print(f"⚠️ Workflow measurement failed: {e}")
            finally:
                tracemalloc.stop()

        avg_time = statistics.mean(times) if times else 0.0
        self.record_metric(
            "complete_workflow_time",
            avg_time,
            "seconds",
            {"iterations": iterations, "scenario": scenario.name}
        )

        return avg_time

    def measure_system_resources(self) -> Dict[str, float]:
        """Measure current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_usage_percent", cpu_percent, "%")

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            memory_percent = memory.percent

            self.record_metric("system_memory_usage_mb", memory_mb, "MB")
            self.record_metric("system_memory_percent", memory_percent, "%")

            # Disk usage
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("disk_usage_percent", disk_percent, "%")

            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }

        except Exception as e:
            print(f"⚠️ System resource measurement failed: {e}")
            return {}

    async def run_performance_measurements(self) -> Dict[str, float]:
        """Run all performance measurements"""
        print("📊 Running performance measurements...")

        results = {}

        # Measure individual components
        measurements = [
            ("character_analysis", self.measure_character_analysis, 5),
            ("persona_generation", self.measure_persona_generation, 5),
            ("command_generation", self.measure_command_generation, 5),
            ("complete_workflow", self.measure_complete_workflow, 3)
        ]

        for name, measure_func, iterations in measurements:
            try:
                result = await measure_func(iterations)
                results[name] = result
                print(f"  ✅ {name}: {result:.3f}s")
            except Exception as e:
                print(f"  ❌ {name} measurement failed: {e}")
                results[name] = 0.0

        # Measure system resources
        system_resources = self.measure_system_resources()
        results.update(system_resources)

        return results

    def process_alerts(self) -> None:
        """Process and display performance alerts"""
        if not self.alerts:
            return

        print(f"\n🚨 Processing {len(self.alerts)} performance alerts...")

        for alert in self.alerts:
            severity_icons = {
                "critical": "🔴",
                "warning": "🟡",
                "info": "🔵"
            }

            icon = severity_icons.get(alert.severity, "📢")
            print(f"{icon} {alert.severity.upper()}: {alert.message}")

        # Save alerts to file
        if self.config["alerting"]["file_alerts"]:
            alerts_data = [asdict(alert) for alert in self.alerts]
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)

        # Clear processed alerts
        self.alerts.clear()

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "metrics": {},
            "trends": {},
            "alerts": len(self.alerts)
        }

        # Group metrics by name
        metric_groups = {}
        for metric in self.metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)

        # Calculate statistics for each metric
        for name, metrics in metric_groups.items():
            if not metrics:
                continue

            values = [m.value for m in metrics]
            recent_values = [m.value for m in metrics[-10:]]  # Last 10 measurements

            report["metrics"][name] = {
                "current": metrics[-1].value if metrics else 0,
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "count": len(values),
                "unit": metrics[-1].unit if metrics else "",
                "threshold": metrics[-1].threshold,
                "within_threshold": metrics[-1].is_within_threshold if metrics else True
            }

            # Calculate trend
            if len(recent_values) >= 5:
                first_half = recent_values[:len(recent_values)//2]
                second_half = recent_values[len(recent_values)//2:]

                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)

                if first_avg > 0:
                    trend_percent = ((second_avg - first_avg) / first_avg) * 100
                    if trend_percent > 5:
                        trend = "degrading"
                    elif trend_percent < -5:
                        trend = "improving"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"

                report["trends"][name] = {
                    "direction": trend,
                    "change_percent": trend_percent if first_avg > 0 else 0
                }

        # Overall summary
        threshold_violations = sum(
            1 for metrics in metric_groups.values()
            for metric in metrics[-1:]  # Only check latest metric
            if metric.threshold and not metric.is_within_threshold
        )

        report["summary"] = {
            "total_metrics": len(metric_groups),
            "threshold_violations": threshold_violations,
            "measurement_count": len(self.metrics),
            "monitoring_period_days": self.config["monitoring"]["retention_days"]
        }

        return report

    def print_performance_summary(self) -> None:
        """Print performance monitoring summary"""
        print("\n" + "=" * 60)
        print("⚡ PERFORMANCE MONITORING SUMMARY")
        print("=" * 60)

        if not self.metrics:
            print("No performance metrics available")
            return

        # Group metrics by name and get latest values
        metric_groups = {}
        for metric in self.metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)

        print("📊 Current Performance Metrics:")
        for name, metrics in sorted(metric_groups.items()):
            if not metrics:
                continue

            latest = metrics[-1]
            status = "✅" if latest.is_within_threshold else "❌"

            print(f"  {status} {name}: {latest.value:.3f}{latest.unit}")
            if latest.threshold:
                print(f"    Threshold: {latest.threshold:.3f}{latest.unit}")

            # Show trend if enough data
            if len(metrics) >= 5:
                recent_avg = statistics.mean([m.value for m in metrics[-5:]])
                older_avg = statistics.mean([m.value for m in metrics[-10:-5]]) if len(metrics) >= 10 else recent_avg

                if older_avg > 0:
                    trend_percent = ((recent_avg - older_avg) / older_avg) * 100
                    trend_icon = "📈" if trend_percent > 5 else "📉" if trend_percent < -5 else "➡️"
                    print(f"    Trend: {trend_icon} {trend_percent:+.1f}%")

        # Alert summary
        if self.alerts:
            print(f"\n🚨 Active Alerts: {len(self.alerts)}")
            for alert in self.alerts[-3:]:  # Show last 3 alerts
                print(f"  • {alert.severity}: {alert.message}")

        print("=" * 60)

    async def run_monitoring_cycle(self) -> bool:
        """Run complete performance monitoring cycle"""
        print("⚡ Starting performance monitoring cycle...")

        # Run measurements
        results = await self.run_performance_measurements()

        # Save metrics
        self.save_metrics()

        # Process alerts
        self.process_alerts()

        # Generate report
        report = self.generate_performance_report()
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        self.print_performance_summary()

        print(f"📄 Performance report saved: {report_file}")

        # Return success if no critical alerts
        critical_alerts = [a for a in self.alerts if a.severity == "critical"]
        return len(critical_alerts) == 0


async def main():
    """Main performance monitoring execution"""
    parser = argparse.ArgumentParser(description="Performance monitoring system")
    parser.add_argument("--config", "-c", default="performance_config.json",
                       help="Configuration file path")
    parser.add_argument("--continuous", action="store_true",
                       help="Run in continuous monitoring mode")
    parser.add_argument("--interval", "-i", type=int, default=300,
                       help="Monitoring interval in seconds")
    parser.add_argument("--iterations", type=int, default=5,
                       help="Number of iterations for each measurement")

    args = parser.parse_args()

    monitor = PerformanceMonitor(args.config)

    if args.continuous:
        print(f"🔄 Starting continuous performance monitoring (interval: {args.interval}s)")
        try:
            while True:
                success = await monitor.run_monitoring_cycle()
                if not success:
                    print("⚠️ Performance issues detected!")

                print(f"💤 Sleeping for {args.interval} seconds...")
                await asyncio.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 Performance monitoring stopped by user")
    else:
        # Single monitoring cycle
        success = await monitor.run_monitoring_cycle()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
