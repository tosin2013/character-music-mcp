#!/usr/bin/env python3
"""
Error Monitoring System for Dynamic Suno Data Integration

This module provides comprehensive error logging and monitoring for wiki operations,
including real-time alerting, error pattern analysis, and health metrics.
"""

import asyncio
import hashlib
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# ENUMS AND DATA MODELS
# ================================================================================================

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    ERROR_RATE_HIGH = "error_rate_high"
    REPEATED_FAILURES = "repeated_failures"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    DATA_QUALITY_LOW = "data_quality_low"
    SYSTEM_DEGRADED = "system_degraded"
    RECOVERY_FAILED = "recovery_failed"

class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class ErrorEvent:
    """Represents a single error event"""
    timestamp: datetime
    operation: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None

    @property
    def error_hash(self) -> str:
        """Generate hash for error deduplication"""
        content = f"{self.operation}:{self.error_type}:{self.error_message[:200]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'operation': self.operation,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'severity': self.severity.value,
            'context': self.context,
            'stack_trace': self.stack_trace,
            'resolved': self.resolved,
            'resolution_time': self.resolution_time.isoformat() if self.resolution_time else None,
            'error_hash': self.error_hash
        }

@dataclass
class ErrorPattern:
    """Represents a pattern of recurring errors"""
    error_hash: str
    first_occurrence: datetime
    last_occurrence: datetime
    occurrence_count: int
    operation: str
    error_type: str
    sample_message: str
    severity: ErrorSeverity

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'error_hash': self.error_hash,
            'first_occurrence': self.first_occurrence.isoformat(),
            'last_occurrence': self.last_occurrence.isoformat(),
            'occurrence_count': self.occurrence_count,
            'operation': self.operation,
            'error_type': self.error_type,
            'sample_message': self.sample_message,
            'severity': self.severity.value
        }

@dataclass
class Alert:
    """Represents a system alert"""
    alert_id: str
    alert_type: AlertType
    severity: ErrorSeverity
    title: str
    description: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    acknowledgment_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'acknowledgment_time': self.acknowledgment_time.isoformat() if self.acknowledgment_time else None,
            'resolution_time': self.resolution_time.isoformat() if self.resolution_time else None,
            'context': self.context
        }

@dataclass
class HealthMetrics:
    """System health metrics"""
    timestamp: datetime
    overall_status: HealthStatus
    error_rate: float  # Errors per minute
    success_rate: float  # Success percentage
    average_response_time: float  # Average response time in seconds
    active_circuits_open: int
    degraded_services: List[str]
    quality_scores: Dict[str, float]  # Quality scores by service

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_status': self.overall_status.value,
            'error_rate': self.error_rate,
            'success_rate': self.success_rate,
            'average_response_time': self.average_response_time,
            'active_circuits_open': self.active_circuits_open,
            'degraded_services': self.degraded_services,
            'quality_scores': self.quality_scores
        }

# ================================================================================================
# ERROR MONITORING SYSTEM
# ================================================================================================

class ErrorMonitoringSystem:
    """Comprehensive error monitoring and alerting system"""

    def __init__(self, storage_path: str = "./data/error_monitoring"):
        self.storage_path = Path(storage_path)
        self.error_events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.health_history: deque = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.initialized = False

        # Monitoring configuration
        self.error_rate_threshold = 10.0  # Errors per minute
        self.pattern_threshold = 5  # Occurrences before creating pattern
        self.health_check_interval = 60  # Seconds between health checks

        # Metrics tracking
        self.operation_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_response_time': 0.0,
            'last_success': None,
            'last_failure': None
        })

    async def initialize(self) -> None:
        """Initialize the error monitoring system"""
        logger.info("Initializing ErrorMonitoringSystem")

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load previous state
        await self._load_state()

        # Start background monitoring tasks
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._pattern_analyzer())
        asyncio.create_task(self._alert_processor())
        asyncio.create_task(self._cleanup_old_data())

        self.initialized = True
        logger.info("ErrorMonitoringSystem initialized successfully")

    def log_error(self, operation: str, error: Exception,
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  context: Dict[str, Any] = None) -> None:
        """
        Log an error event
        
        Args:
            operation: Operation that failed
            error: Exception that occurred
            severity: Severity level of the error
            context: Additional context information
        """
        if not self.initialized:
            logger.warning("ErrorMonitoringSystem not initialized, logging to standard logger")
            logger.error(f"Error in {operation}: {error}")
            return

        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            context=context or {},
            stack_trace=self._get_stack_trace(error)
        )

        # Add to event queue
        self.error_events.append(error_event)

        # Update operation metrics
        self.operation_metrics[operation]['failed_operations'] += 1
        self.operation_metrics[operation]['last_failure'] = datetime.now()

        # Check for patterns and alerts
        self._check_error_patterns(error_event)
        self._check_alert_conditions(error_event)

        logger.error(f"Logged error: {operation} - {error}")

    def log_success(self, operation: str, response_time: float = 0.0,
                   context: Dict[str, Any] = None) -> None:
        """
        Log a successful operation
        
        Args:
            operation: Operation that succeeded
            response_time: Response time in seconds
            context: Additional context information
        """
        if not self.initialized:
            return

        # Update operation metrics
        metrics = self.operation_metrics[operation]
        metrics['total_operations'] += 1
        metrics['successful_operations'] += 1
        metrics['total_response_time'] += response_time
        metrics['last_success'] = datetime.now()

    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add a callback function to be called when alerts are generated"""
        self.alert_callbacks.append(callback)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledgment_time = datetime.now()
            logger.info(f"Alert {alert_id} acknowledged")
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            logger.info(f"Alert {alert_id} resolved")
            return True
        return False

    def get_current_health_status(self) -> HealthMetrics:
        """Get current system health status"""
        now = datetime.now()

        # Calculate error rate (last 5 minutes)
        recent_errors = [
            event for event in self.error_events
            if now - event.timestamp <= timedelta(minutes=5)
        ]
        error_rate = len(recent_errors) / 5.0  # Errors per minute

        # Calculate success rate
        total_ops = sum(metrics['total_operations'] for metrics in self.operation_metrics.values())
        successful_ops = sum(metrics['successful_operations'] for metrics in self.operation_metrics.values())
        success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 100.0

        # Calculate average response time
        total_response_time = sum(metrics['total_response_time'] for metrics in self.operation_metrics.values())
        avg_response_time = (total_response_time / successful_ops) if successful_ops > 0 else 0.0

        # Determine overall status
        if error_rate > self.error_rate_threshold or success_rate < 50:
            overall_status = HealthStatus.CRITICAL
        elif error_rate > self.error_rate_threshold / 2 or success_rate < 80:
            overall_status = HealthStatus.UNHEALTHY
        elif error_rate > self.error_rate_threshold / 4 or success_rate < 95:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Get degraded services
        degraded_services = []
        for operation, metrics in self.operation_metrics.items():
            if metrics['total_operations'] > 0:
                op_success_rate = (metrics['successful_operations'] / metrics['total_operations']) * 100
                if op_success_rate < 90:
                    degraded_services.append(operation)

        # Create health metrics
        health_metrics = HealthMetrics(
            timestamp=now,
            overall_status=overall_status,
            error_rate=error_rate,
            success_rate=success_rate,
            average_response_time=avg_response_time,
            active_circuits_open=0,  # Would be populated from circuit breaker system
            degraded_services=degraded_services,
            quality_scores=self._calculate_quality_scores()
        )

        return health_metrics

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        now = datetime.now()

        # Time-based statistics
        last_hour_errors = [e for e in self.error_events if now - e.timestamp <= timedelta(hours=1)]
        last_day_errors = [e for e in self.error_events if now - e.timestamp <= timedelta(days=1)]

        stats = {
            'total_errors': len(self.error_events),
            'last_hour_errors': len(last_hour_errors),
            'last_day_errors': len(last_day_errors),
            'error_patterns': len(self.error_patterns),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'errors_by_severity': {},
            'errors_by_operation': {},
            'errors_by_type': {},
            'top_error_patterns': [],
            'recent_errors': []
        }

        # Errors by severity
        for event in self.error_events:
            severity = event.severity.value
            if severity not in stats['errors_by_severity']:
                stats['errors_by_severity'][severity] = 0
            stats['errors_by_severity'][severity] += 1

        # Errors by operation
        for event in self.error_events:
            operation = event.operation
            if operation not in stats['errors_by_operation']:
                stats['errors_by_operation'][operation] = 0
            stats['errors_by_operation'][operation] += 1

        # Errors by type
        for event in self.error_events:
            error_type = event.error_type
            if error_type not in stats['errors_by_type']:
                stats['errors_by_type'][error_type] = 0
            stats['errors_by_type'][error_type] += 1

        # Top error patterns
        sorted_patterns = sorted(self.error_patterns.values(),
                               key=lambda p: p.occurrence_count, reverse=True)
        stats['top_error_patterns'] = [pattern.to_dict() for pattern in sorted_patterns[:10]]

        # Recent errors
        recent_errors = sorted(self.error_events, key=lambda e: e.timestamp, reverse=True)
        stats['recent_errors'] = [error.to_dict() for error in list(recent_errors)[:20]]

        return stats

    def get_operation_health_report(self) -> Dict[str, Any]:
        """Get health report for all operations"""
        report = {}

        for operation, metrics in self.operation_metrics.items():
            total_ops = metrics['total_operations']
            successful_ops = metrics['successful_operations']
            failed_ops = metrics['failed_operations']

            success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0.0
            avg_response_time = (metrics['total_response_time'] / successful_ops) if successful_ops > 0 else 0.0

            # Determine health status
            if success_rate >= 95:
                health_status = "healthy"
            elif success_rate >= 80:
                health_status = "degraded"
            else:
                health_status = "unhealthy"

            report[operation] = {
                'health_status': health_status,
                'total_operations': total_ops,
                'success_rate': success_rate,
                'failure_rate': (failed_ops / total_ops * 100) if total_ops > 0 else 0.0,
                'average_response_time': avg_response_time,
                'last_success': metrics['last_success'].isoformat() if metrics['last_success'] else None,
                'last_failure': metrics['last_failure'].isoformat() if metrics['last_failure'] else None
            }

        return report

    # Private methods

    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """Get stack trace from exception"""
        import traceback
        try:
            return traceback.format_exc()
        except:
            return None

    def _check_error_patterns(self, error_event: ErrorEvent) -> None:
        """Check for recurring error patterns"""
        error_hash = error_event.error_hash

        if error_hash in self.error_patterns:
            # Update existing pattern
            pattern = self.error_patterns[error_hash]
            pattern.occurrence_count += 1
            pattern.last_occurrence = error_event.timestamp

            # Update severity if this error is more severe
            if error_event.severity.value > pattern.severity.value:
                pattern.severity = error_event.severity
        else:
            # Create new pattern
            pattern = ErrorPattern(
                error_hash=error_hash,
                first_occurrence=error_event.timestamp,
                last_occurrence=error_event.timestamp,
                occurrence_count=1,
                operation=error_event.operation,
                error_type=error_event.error_type,
                sample_message=error_event.error_message[:200],
                severity=error_event.severity
            )
            self.error_patterns[error_hash] = pattern

    def _check_alert_conditions(self, error_event: ErrorEvent) -> None:
        """Check if error event should trigger alerts"""
        now = datetime.now()

        # Check for repeated failures
        error_hash = error_event.error_hash
        if error_hash in self.error_patterns:
            pattern = self.error_patterns[error_hash]
            if pattern.occurrence_count >= self.pattern_threshold:
                self._create_alert(
                    AlertType.REPEATED_FAILURES,
                    ErrorSeverity.HIGH,
                    f"Repeated failures in {pattern.operation}",
                    f"Error pattern detected: {pattern.sample_message} (occurred {pattern.occurrence_count} times)",
                    {'error_hash': error_hash, 'pattern': pattern.to_dict()}
                )

        # Check error rate
        recent_errors = [
            event for event in self.error_events
            if now - event.timestamp <= timedelta(minutes=5)
        ]
        error_rate = len(recent_errors) / 5.0

        if error_rate > self.error_rate_threshold:
            self._create_alert(
                AlertType.ERROR_RATE_HIGH,
                ErrorSeverity.CRITICAL,
                "High error rate detected",
                f"Error rate is {error_rate:.1f} errors/minute (threshold: {self.error_rate_threshold})",
                {'error_rate': error_rate, 'threshold': self.error_rate_threshold}
            )

    def _create_alert(self, alert_type: AlertType, severity: ErrorSeverity,
                     title: str, description: str, context: Dict[str, Any] = None) -> None:
        """Create a new alert"""
        alert_id = f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Check if similar alert already exists
        for existing_alert in self.active_alerts.values():
            if (existing_alert.alert_type == alert_type and
                not existing_alert.resolved and
                datetime.now() - existing_alert.timestamp < timedelta(minutes=30)):
                # Don't create duplicate alerts within 30 minutes
                return

        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            timestamp=datetime.now(),
            context=context or {}
        )

        self.active_alerts[alert_id] = alert

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        logger.warning(f"Created alert: {title}")

    def _calculate_quality_scores(self) -> Dict[str, float]:
        """Calculate quality scores for different services"""
        quality_scores = {}

        for operation, metrics in self.operation_metrics.items():
            if metrics['total_operations'] > 0:
                success_rate = metrics['successful_operations'] / metrics['total_operations']

                # Factor in response time (penalize slow operations)
                avg_response_time = metrics['total_response_time'] / metrics['successful_operations'] if metrics['successful_operations'] > 0 else 0
                response_penalty = min(0.2, avg_response_time / 10.0)  # Max 20% penalty for slow responses

                quality_score = success_rate - response_penalty
                quality_scores[operation] = max(0.0, min(1.0, quality_score))
            else:
                quality_scores[operation] = 1.0  # No data means no problems

        return quality_scores

    async def _health_monitor(self) -> None:
        """Background task to monitor system health"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                # Get current health metrics
                health_metrics = self.get_current_health_status()
                self.health_history.append(health_metrics)

                # Check for health-based alerts
                if health_metrics.overall_status == HealthStatus.CRITICAL:
                    self._create_alert(
                        AlertType.SYSTEM_DEGRADED,
                        ErrorSeverity.CRITICAL,
                        "System in critical state",
                        f"Error rate: {health_metrics.error_rate:.1f}/min, Success rate: {health_metrics.success_rate:.1f}%",
                        {'health_metrics': health_metrics.to_dict()}
                    )
                elif health_metrics.overall_status == HealthStatus.UNHEALTHY:
                    self._create_alert(
                        AlertType.SYSTEM_DEGRADED,
                        ErrorSeverity.HIGH,
                        "System unhealthy",
                        f"Error rate: {health_metrics.error_rate:.1f}/min, Success rate: {health_metrics.success_rate:.1f}%",
                        {'health_metrics': health_metrics.to_dict()}
                    )

            except Exception as e:
                logger.error(f"Error in health monitor: {e}")

    async def _pattern_analyzer(self) -> None:
        """Background task to analyze error patterns"""
        while True:
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes

                # Clean up old patterns
                cutoff_time = datetime.now() - timedelta(hours=24)
                patterns_to_remove = [
                    hash_key for hash_key, pattern in self.error_patterns.items()
                    if pattern.last_occurrence < cutoff_time
                ]

                for hash_key in patterns_to_remove:
                    del self.error_patterns[hash_key]

                logger.debug(f"Pattern analyzer: {len(self.error_patterns)} active patterns")

            except Exception as e:
                logger.error(f"Error in pattern analyzer: {e}")

    async def _alert_processor(self) -> None:
        """Background task to process and manage alerts"""
        while True:
            try:
                await asyncio.sleep(60)  # Process every minute

                # Auto-resolve old alerts
                cutoff_time = datetime.now() - timedelta(hours=24)
                for alert in self.active_alerts.values():
                    if not alert.resolved and alert.timestamp < cutoff_time:
                        alert.resolved = True
                        alert.resolution_time = datetime.now()
                        logger.info(f"Auto-resolved old alert: {alert.alert_id}")

            except Exception as e:
                logger.error(f"Error in alert processor: {e}")

    async def _cleanup_old_data(self) -> None:
        """Background task to cleanup old data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour

                # The deque automatically handles size limits, but we can do additional cleanup here
                # Remove resolved alerts older than 7 days
                cutoff_time = datetime.now() - timedelta(days=7)
                alerts_to_remove = [
                    alert_id for alert_id, alert in self.active_alerts.items()
                    if alert.resolved and alert.resolution_time and alert.resolution_time < cutoff_time
                ]

                for alert_id in alerts_to_remove:
                    del self.active_alerts[alert_id]

                logger.debug(f"Cleanup: removed {len(alerts_to_remove)} old alerts")

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def _load_state(self) -> None:
        """Load previous state from disk"""
        # Load error patterns
        patterns_file = self.storage_path / "error_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)

                for hash_key, data in patterns_data.items():
                    pattern = ErrorPattern(
                        error_hash=data['error_hash'],
                        first_occurrence=datetime.fromisoformat(data['first_occurrence']),
                        last_occurrence=datetime.fromisoformat(data['last_occurrence']),
                        occurrence_count=data['occurrence_count'],
                        operation=data['operation'],
                        error_type=data['error_type'],
                        sample_message=data['sample_message'],
                        severity=ErrorSeverity(data['severity'])
                    )
                    self.error_patterns[hash_key] = pattern

                logger.debug(f"Loaded {len(self.error_patterns)} error patterns")
            except Exception as e:
                logger.warning(f"Failed to load error patterns: {e}")

        # Load active alerts
        alerts_file = self.storage_path / "active_alerts.json"
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)

                for alert_id, data in alerts_data.items():
                    alert = Alert(
                        alert_id=data['alert_id'],
                        alert_type=AlertType(data['alert_type']),
                        severity=ErrorSeverity(data['severity']),
                        title=data['title'],
                        description=data['description'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        acknowledged=data['acknowledged'],
                        resolved=data['resolved'],
                        acknowledgment_time=datetime.fromisoformat(data['acknowledgment_time']) if data.get('acknowledgment_time') else None,
                        resolution_time=datetime.fromisoformat(data['resolution_time']) if data.get('resolution_time') else None,
                        context=data.get('context', {})
                    )
                    self.active_alerts[alert_id] = alert

                logger.debug(f"Loaded {len(self.active_alerts)} active alerts")
            except Exception as e:
                logger.warning(f"Failed to load active alerts: {e}")

    async def save_state(self) -> None:
        """Save current state to disk"""
        if not self.initialized:
            return

        # Save error patterns
        patterns_file = self.storage_path / "error_patterns.json"
        patterns_data = {hash_key: pattern.to_dict() for hash_key, pattern in self.error_patterns.items()}
        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)

        # Save active alerts
        alerts_file = self.storage_path / "active_alerts.json"
        alerts_data = {alert_id: alert.to_dict() for alert_id, alert in self.active_alerts.items()}
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)

        logger.debug("Saved error monitoring state to disk")
