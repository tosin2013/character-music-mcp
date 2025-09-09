#!/usr/bin/env python3
"""
Performance Monitoring System for Dynamic Suno Data Integration

This module provides comprehensive performance monitoring including:
- Download times and success rates
- Parsing performance and memory usage
- Generation time metrics with wiki data integration
- Real-time performance dashboards and alerts
"""

import asyncio
import logging
import time

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
import gc
import json
import threading
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    operation: str
    duration: float  # seconds
    success: bool
    memory_usage: float  # MB
    cpu_usage: float  # percentage
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'operation': self.operation,
            'duration': self.duration,
            'success': self.success,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'context': self.context
        }

@dataclass
class OperationStats:
    """Statistics for a specific operation"""
    operation: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_memory_usage: float = 0.0
    avg_cpu_usage: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0.0

    @property
    def average_duration(self) -> float:
        """Calculate average duration"""
        return (self.total_duration / self.successful_calls) if self.successful_calls > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'operation': self.operation,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': self.success_rate,
            'average_duration': self.average_duration,
            'min_duration': self.min_duration if self.min_duration != float('inf') else 0.0,
            'max_duration': self.max_duration,
            'avg_memory_usage': self.avg_memory_usage,
            'avg_cpu_usage': self.avg_cpu_usage,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_failure': self.last_failure.isoformat() if self.last_failure else None
        }

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    active_threads: int
    gc_collections: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_available_mb': self.memory_available_mb,
            'disk_usage_percent': self.disk_usage_percent,
            'active_threads': self.active_threads,
            'gc_collections': self.gc_collections
        }

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    timestamp: datetime
    report_period: str
    system_metrics: SystemMetrics
    operation_stats: Dict[str, OperationStats]
    top_slowest_operations: List[Dict[str, Any]]
    performance_trends: Dict[str, Any]
    alerts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'report_period': self.report_period,
            'system_metrics': self.system_metrics.to_dict(),
            'operation_stats': {op: stats.to_dict() for op, stats in self.operation_stats.items()},
            'top_slowest_operations': self.top_slowest_operations,
            'performance_trends': self.performance_trends,
            'alerts': self.alerts
        }

# ================================================================================================
# PERFORMANCE MONITOR
# ================================================================================================

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""

    def __init__(self, storage_path: str = "./data/performance"):
        self.storage_path = Path(storage_path)
        self.metrics: deque = deque(maxlen=50000)  # Keep last 50k metrics
        self.operation_stats: Dict[str, OperationStats] = defaultdict(lambda: OperationStats(operation="default"))
        self.system_metrics_history: deque = deque(maxlen=1440)  # 24 hours of minute data
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self.initialized = False

        # Performance thresholds
        self.slow_operation_threshold = 5.0  # seconds
        self.high_memory_threshold = 80.0  # percentage
        self.high_cpu_threshold = 80.0  # percentage
        self.low_success_rate_threshold = 90.0  # percentage

        # Monitoring configuration
        self.system_metrics_interval = 60  # seconds
        self.cleanup_interval = 3600  # seconds
        self.report_interval = 300  # seconds (5 minutes)

        # Process monitoring
        self.process = psutil.Process() if PSUTIL_AVAILABLE else None
        self._lock = threading.Lock()

    async def initialize(self) -> None:
        """Initialize the performance monitoring system"""
        logger.info("Initializing PerformanceMonitor")

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load previous state
        await self._load_state()

        # Start background monitoring tasks
        asyncio.create_task(self._system_metrics_collector())
        asyncio.create_task(self._performance_analyzer())
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._generate_reports())

        self.initialized = True
        logger.info("PerformanceMonitor initialized successfully")

    @asynccontextmanager
    async def measure_operation(self, operation: str, context: Dict[str, Any] = None):
        """
        Context manager to measure operation performance

        Usage:
            async with performance_monitor.measure_operation("download_page"):
                await download_page(url)
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = self._get_cpu_usage()
        success = False

        try:
            yield
            success = True
        except Exception:
            success = False
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            end_memory = self._get_memory_usage()
            end_cpu = self._get_cpu_usage()

            # Record the metric
            await self._record_metric(
                operation=operation,
                duration=duration,
                success=success,
                memory_usage=(start_memory + end_memory) / 2,
                cpu_usage=(start_cpu + end_cpu) / 2,
                context=context or {}
            )

    def measure_sync_operation(self, operation: str, context: Dict[str, Any] = None):
        """
        Context manager for synchronous operations

        Usage:
            with performance_monitor.measure_sync_operation("parse_html"):
                parse_html_content(html)
        """
        class SyncMeasureContext:
            def __init__(self, monitor, operation, context):
                self.monitor = monitor
                self.operation = operation
                self.context = context or {}
                self.start_time = None
                self.start_memory = None
                self.start_cpu = None

            def __enter__(self):
                self.start_time = time.time()
                self.start_memory = self.monitor._get_memory_usage()
                self.start_cpu = self.monitor._get_cpu_usage()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                duration = end_time - self.start_time
                end_memory = self.monitor._get_memory_usage()
                end_cpu = self.monitor._get_cpu_usage()
                success = exc_type is None

                # Record the metric (synchronous)
                try:
                    asyncio.get_running_loop()
                    asyncio.create_task(self.monitor._record_metric(
                        operation=self.operation,
                        duration=duration,
                        success=success,
                        memory_usage=(self.start_memory + end_memory) / 2,
                        cpu_usage=(self.start_cpu + end_cpu) / 2,
                        context=self.context
                    ))
                except RuntimeError:
                    # No event loop running, schedule for later
                    import threading
                    def record_later():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.monitor._record_metric(
                                operation=self.operation,
                                duration=duration,
                                success=success,
                                memory_usage=(self.start_memory + end_memory) / 2,
                                cpu_usage=(self.start_cpu + end_cpu) / 2,
                                context=self.context
                            ))
                            loop.close()
                        except Exception as e:
                            logger.error(f"Error recording sync metric: {e}")

                    thread = threading.Thread(target=record_later)
                    thread.daemon = True
                    thread.start()

        return SyncMeasureContext(self, operation, context)

    async def record_download_metrics(self, url: str, duration: float, success: bool,
                                    file_size: int = 0, status_code: int = None) -> None:
        """Record specific download performance metrics"""
        context = {
            'url': url,
            'file_size_bytes': file_size,
            'status_code': status_code,
            'download_speed_mbps': (file_size / (1024 * 1024)) / duration if duration > 0 and file_size > 0 else 0
        }

        await self._record_metric(
            operation="wiki_download",
            duration=duration,
            success=success,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
            context=context
        )

    async def record_parsing_metrics(self, content_type: str, content_size: int,
                                   duration: float, success: bool, items_parsed: int = 0) -> None:
        """Record specific parsing performance metrics"""
        context = {
            'content_type': content_type,
            'content_size_bytes': content_size,
            'items_parsed': items_parsed,
            'parsing_speed_items_per_sec': items_parsed / duration if duration > 0 else 0
        }

        await self._record_metric(
            operation="content_parsing",
            duration=duration,
            success=success,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
            context=context
        )

    async def record_generation_metrics(self, generation_type: str, duration: float,
                                      success: bool, wiki_data_used: bool = False,
                                      fallback_used: bool = False) -> None:
        """Record music generation performance metrics"""
        context = {
            'generation_type': generation_type,
            'wiki_data_used': wiki_data_used,
            'fallback_used': fallback_used,
            'data_source': 'wiki' if wiki_data_used else 'fallback' if fallback_used else 'hardcoded'
        }

        await self._record_metric(
            operation="music_generation",
            duration=duration,
            success=success,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
            context=context
        )

    def get_operation_statistics(self, operation: str = None) -> Dict[str, Any]:
        """Get performance statistics for operations"""
        if operation:
            if operation in self.operation_stats:
                return self.operation_stats[operation].to_dict()
            else:
                return {}
        else:
            return {op: stats.to_dict() for op, stats in self.operation_stats.items()}

    def get_download_performance_report(self) -> Dict[str, Any]:
        """Get specific report for download performance"""
        download_metrics = [m for m in self.metrics if m.operation == "wiki_download"]

        if not download_metrics:
            return {"message": "No download metrics available"}

        # Calculate statistics
        total_downloads = len(download_metrics)
        successful_downloads = len([m for m in download_metrics if m.success])
        failed_downloads = total_downloads - successful_downloads

        success_rate = (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0

        # Download speeds
        speeds = [m.context.get('download_speed_mbps', 0) for m in download_metrics if m.success and m.context.get('download_speed_mbps', 0) > 0]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0

        # Response times
        durations = [m.duration for m in download_metrics if m.success]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Recent performance (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in download_metrics if m.timestamp >= recent_cutoff]
        recent_success_rate = (len([m for m in recent_metrics if m.success]) / len(recent_metrics) * 100) if recent_metrics else 0

        return {
            'total_downloads': total_downloads,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'success_rate': success_rate,
            'recent_success_rate': recent_success_rate,
            'average_download_speed_mbps': avg_speed,
            'average_duration_seconds': avg_duration,
            'fastest_download': min(durations) if durations else 0,
            'slowest_download': max(durations) if durations else 0
        }

    def get_parsing_performance_report(self) -> Dict[str, Any]:
        """Get specific report for parsing performance"""
        parsing_metrics = [m for m in self.metrics if m.operation == "content_parsing"]

        if not parsing_metrics:
            return {"message": "No parsing metrics available"}

        # Group by content type
        by_content_type = defaultdict(list)
        for metric in parsing_metrics:
            content_type = metric.context.get('content_type', 'unknown')
            by_content_type[content_type].append(metric)

        report = {}
        for content_type, metrics in by_content_type.items():
            successful_metrics = [m for m in metrics if m.success]

            total_items = sum(m.context.get('items_parsed', 0) for m in successful_metrics)
            total_duration = sum(m.duration for m in successful_metrics)
            avg_parsing_speed = total_items / total_duration if total_duration > 0 else 0

            report[content_type] = {
                'total_operations': len(metrics),
                'successful_operations': len(successful_metrics),
                'success_rate': (len(successful_metrics) / len(metrics) * 100) if metrics else 0,
                'total_items_parsed': total_items,
                'average_parsing_speed_items_per_sec': avg_parsing_speed,
                'average_duration': sum(m.duration for m in successful_metrics) / len(successful_metrics) if successful_metrics else 0
            }

        return report

    def get_generation_performance_report(self) -> Dict[str, Any]:
        """Get specific report for generation performance"""
        generation_metrics = [m for m in self.metrics if m.operation == "music_generation"]

        if not generation_metrics:
            return {"message": "No generation metrics available"}

        # Performance by data source
        wiki_metrics = [m for m in generation_metrics if m.context.get('wiki_data_used', False)]
        fallback_metrics = [m for m in generation_metrics if m.context.get('fallback_used', False)]
        hardcoded_metrics = [m for m in generation_metrics if not m.context.get('wiki_data_used', False) and not m.context.get('fallback_used', False)]

        def calculate_stats(metrics):
            if not metrics:
                return {'count': 0, 'success_rate': 0, 'avg_duration': 0}

            successful = [m for m in metrics if m.success]
            return {
                'count': len(metrics),
                'success_rate': (len(successful) / len(metrics) * 100),
                'avg_duration': sum(m.duration for m in successful) / len(successful) if successful else 0
            }

        return {
            'total_generations': len(generation_metrics),
            'wiki_data_performance': calculate_stats(wiki_metrics),
            'fallback_data_performance': calculate_stats(fallback_metrics),
            'hardcoded_data_performance': calculate_stats(hardcoded_metrics),
            'overall_success_rate': (len([m for m in generation_metrics if m.success]) / len(generation_metrics) * 100) if generation_metrics else 0
        }

    def get_system_health_report(self) -> Dict[str, Any]:
        """Get current system health and resource usage"""
        current_metrics = self._get_current_system_metrics()

        # Get recent system metrics for trends
        recent_metrics = list(self.system_metrics_history)[-60:]  # Last hour

        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            max_cpu = max(m.cpu_percent for m in recent_metrics)
            max_memory = max(m.memory_percent for m in recent_metrics)
        else:
            avg_cpu = avg_memory = max_cpu = max_memory = 0

        # Identify performance issues
        issues = []
        if current_metrics.cpu_percent > self.high_cpu_threshold:
            issues.append(f"High CPU usage: {current_metrics.cpu_percent:.1f}%")
        if current_metrics.memory_percent > self.high_memory_threshold:
            issues.append(f"High memory usage: {current_metrics.memory_percent:.1f}%")
        if current_metrics.disk_usage_percent > 90:
            issues.append(f"High disk usage: {current_metrics.disk_usage_percent:.1f}%")

        return {
            'current_metrics': current_metrics.to_dict(),
            'recent_averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory
            },
            'recent_peaks': {
                'cpu_percent': max_cpu,
                'memory_percent': max_memory
            },
            'performance_issues': issues,
            'health_status': 'healthy' if not issues else 'degraded' if len(issues) < 3 else 'critical'
        }

    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for performance alerts"""
        self.alert_callbacks.append(callback)

    async def generate_comprehensive_report(self) -> PerformanceReport:
        """Generate comprehensive performance report"""
        current_time = datetime.now()
        system_metrics = self._get_current_system_metrics()

        # Get slowest operations
        slowest_ops = []
        for op, stats in self.operation_stats.items():
            if stats.total_calls > 0:
                slowest_ops.append({
                    'operation': op,
                    'average_duration': stats.average_duration,
                    'max_duration': stats.max_duration,
                    'success_rate': stats.success_rate
                })

        slowest_ops.sort(key=lambda x: x['average_duration'], reverse=True)
        slowest_ops = slowest_ops[:10]  # Top 10 slowest

        # Calculate performance trends
        trends = self._calculate_performance_trends()

        # Generate alerts
        alerts = self._generate_performance_alerts()

        return PerformanceReport(
            timestamp=current_time,
            report_period="last_24_hours",
            system_metrics=system_metrics,
            operation_stats=dict(self.operation_stats),
            top_slowest_operations=slowest_ops,
            performance_trends=trends,
            alerts=alerts
        )

    # Private methods

    async def _record_metric(self, operation: str, duration: float, success: bool,
                           memory_usage: float, cpu_usage: float, context: Dict[str, Any]) -> None:
        """Record a performance metric"""
        if not self.initialized:
            return

        metric = PerformanceMetric(
            timestamp=datetime.now(),
            operation=operation,
            duration=duration,
            success=success,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            context=context
        )

        with self._lock:
            self.metrics.append(metric)

            # Update operation statistics
            if operation not in self.operation_stats:
                self.operation_stats[operation] = OperationStats(operation=operation)

            stats = self.operation_stats[operation]
            stats.total_calls += 1

            if success:
                stats.successful_calls += 1
                stats.total_duration += duration
                stats.min_duration = min(stats.min_duration, duration)
                stats.max_duration = max(stats.max_duration, duration)
                stats.last_success = metric.timestamp
            else:
                stats.failed_calls += 1
                stats.last_failure = metric.timestamp

            # Update averages
            if stats.total_calls > 0:
                stats.avg_memory_usage = ((stats.avg_memory_usage * (stats.total_calls - 1)) + memory_usage) / stats.total_calls
                stats.avg_cpu_usage = ((stats.avg_cpu_usage * (stats.total_calls - 1)) + cpu_usage) / stats.total_calls

        # Check for performance alerts
        await self._check_performance_alerts(metric, stats)

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return self.process.cpu_percent()
        except:
            return 0.0

    def _get_current_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # System-wide metrics
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
            else:
                cpu_percent = 15.0  # Mock value
                class MockMemory:
                    total = 8 * 1024 * 1024 * 1024  # 8GB
                    available = 4 * 1024 * 1024 * 1024  # 4GB
                    percent = 50.0
                memory = MockMemory()
                class MockDisk:
                    total = 100 * 1024 * 1024 * 1024  # 100GB
                    free = 50 * 1024 * 1024 * 1024  # 50GB
                    used = 50 * 1024 * 1024 * 1024  # 50GB
                disk = MockDisk()

            # Process-specific metrics
            active_threads = threading.active_count()

            # Garbage collection stats
            gc_stats = {}
            for i in range(3):
                gc_stats[f'generation_{i}'] = gc.get_count()[i]

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                active_threads=active_threads,
                gc_collections=gc_stats
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                active_threads=0,
                gc_collections={}
            )

    async def _check_performance_alerts(self, metric: PerformanceMetric, stats: OperationStats) -> None:
        """Check if performance metric should trigger alerts"""
        alerts = []

        # Slow operation alert
        if metric.success and metric.duration > self.slow_operation_threshold:
            alerts.append(f"Slow operation detected: {metric.operation} took {metric.duration:.2f}s")

        # Low success rate alert
        if stats.total_calls >= 10 and stats.success_rate < self.low_success_rate_threshold:
            alerts.append(f"Low success rate for {metric.operation}: {stats.success_rate:.1f}%")

        # High memory usage alert
        if metric.memory_usage > 1000:  # 1GB
            alerts.append(f"High memory usage in {metric.operation}: {metric.memory_usage:.1f}MB")

        # Send alerts
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metric.to_dict())
                except Exception as e:
                    logger.error(f"Error in performance alert callback: {e}")

    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        now = datetime.now()

        # Get metrics from different time periods
        last_hour = [m for m in self.metrics if now - m.timestamp <= timedelta(hours=1)]
        last_day = [m for m in self.metrics if now - m.timestamp <= timedelta(days=1)]

        trends = {}

        # Overall success rate trend
        if last_hour and last_day:
            hour_success_rate = len([m for m in last_hour if m.success]) / len(last_hour) * 100
            day_success_rate = len([m for m in last_day if m.success]) / len(last_day) * 100
            trends['success_rate_trend'] = hour_success_rate - day_success_rate

        # Average response time trend
        if last_hour and last_day:
            hour_avg_duration = sum(m.duration for m in last_hour if m.success) / len([m for m in last_hour if m.success]) if any(m.success for m in last_hour) else 0
            day_avg_duration = sum(m.duration for m in last_day if m.success) / len([m for m in last_day if m.success]) if any(m.success for m in last_day) else 0
            trends['response_time_trend'] = hour_avg_duration - day_avg_duration

        return trends

    def _generate_performance_alerts(self) -> List[str]:
        """Generate performance alerts based on current metrics"""
        alerts = []

        # Check operation statistics
        for op, stats in self.operation_stats.items():
            if stats.total_calls >= 10:
                if stats.success_rate < self.low_success_rate_threshold:
                    alerts.append(f"Low success rate for {op}: {stats.success_rate:.1f}%")

                if stats.average_duration > self.slow_operation_threshold:
                    alerts.append(f"Slow average response time for {op}: {stats.average_duration:.2f}s")

        # Check system metrics
        if self.system_metrics_history:
            latest_system = self.system_metrics_history[-1]
            if latest_system.cpu_percent > self.high_cpu_threshold:
                alerts.append(f"High CPU usage: {latest_system.cpu_percent:.1f}%")
            if latest_system.memory_percent > self.high_memory_threshold:
                alerts.append(f"High memory usage: {latest_system.memory_percent:.1f}%")

        return alerts

    async def _system_metrics_collector(self) -> None:
        """Background task to collect system metrics"""
        while True:
            try:
                await asyncio.sleep(self.system_metrics_interval)

                system_metrics = self._get_current_system_metrics()
                self.system_metrics_history.append(system_metrics)

            except Exception as e:
                logger.error(f"Error in system metrics collector: {e}")

    async def _performance_analyzer(self) -> None:
        """Background task to analyze performance patterns"""
        while True:
            try:
                await asyncio.sleep(self.report_interval)

                # Analyze recent performance
                now = datetime.now()
                recent_metrics = [m for m in self.metrics if now - m.timestamp <= timedelta(minutes=5)]

                if recent_metrics:
                    # Check for performance degradation
                    failed_metrics = [m for m in recent_metrics if not m.success]
                    if len(failed_metrics) / len(recent_metrics) > 0.1:  # More than 10% failures
                        logger.warning(f"High failure rate detected: {len(failed_metrics)}/{len(recent_metrics)} operations failed")

                logger.debug(f"Performance analyzer: processed {len(recent_metrics)} recent metrics")

            except Exception as e:
                logger.error(f"Error in performance analyzer: {e}")

    async def _cleanup_old_data(self) -> None:
        """Background task to cleanup old performance data"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)

                # Clean up old operation stats for operations that haven't been used recently
                cutoff_time = datetime.now() - timedelta(days=7)
                ops_to_remove = []

                for op, stats in self.operation_stats.items():
                    if (stats.last_success and stats.last_success < cutoff_time and
                        stats.last_failure and stats.last_failure < cutoff_time):
                        ops_to_remove.append(op)

                for op in ops_to_remove:
                    del self.operation_stats[op]

                logger.debug(f"Cleanup: removed {len(ops_to_remove)} old operation stats")

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def _generate_reports(self) -> None:
        """Background task to generate periodic reports"""
        while True:
            try:
                await asyncio.sleep(self.report_interval)

                # Generate and save performance report
                report = await self.generate_comprehensive_report()

                # Save report to file
                report_file = self.storage_path / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                with open(report_file, 'w') as f:
                    json.dump(report.to_dict(), f, indent=2)

                logger.debug(f"Generated performance report: {report_file}")

            except Exception as e:
                logger.error(f"Error generating performance report: {e}")

    async def _load_state(self) -> None:
        """Load previous performance state"""
        # Load operation statistics
        stats_file = self.storage_path / "operation_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)

                for op, data in stats_data.items():
                    stats = OperationStats(operation=op)
                    stats.total_calls = data.get('total_calls', 0)
                    stats.successful_calls = data.get('successful_calls', 0)
                    stats.failed_calls = data.get('failed_calls', 0)
                    stats.total_duration = data.get('total_duration', 0.0)
                    stats.min_duration = data.get('min_duration', float('inf'))
                    stats.max_duration = data.get('max_duration', 0.0)
                    stats.avg_memory_usage = data.get('avg_memory_usage', 0.0)
                    stats.avg_cpu_usage = data.get('avg_cpu_usage', 0.0)

                    if data.get('last_success'):
                        stats.last_success = datetime.fromisoformat(data['last_success'])
                    if data.get('last_failure'):
                        stats.last_failure = datetime.fromisoformat(data['last_failure'])

                    self.operation_stats[op] = stats

                logger.debug(f"Loaded {len(self.operation_stats)} operation statistics")
            except Exception as e:
                logger.warning(f"Failed to load operation statistics: {e}")

    async def save_state(self) -> None:
        """Save current performance state"""
        if not self.initialized:
            return

        # Save operation statistics
        stats_file = self.storage_path / "operation_stats.json"
        stats_data = {op: stats.to_dict() for op, stats in self.operation_stats.items()}
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, indent=2)

        logger.debug("Saved performance monitoring state to disk")

# ================================================================================================
# PERFORMANCE DECORATORS
# ================================================================================================

def monitor_performance(operation: str, monitor: PerformanceMonitor):
    """Decorator to monitor function performance"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with monitor.measure_operation(operation):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                with monitor.measure_sync_operation(operation):
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator
