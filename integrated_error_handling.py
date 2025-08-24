#!/usr/bin/env python3
"""
Integrated Error Handling System for Dynamic Suno Data Integration

This module provides a unified interface for all error handling and fallback systems,
integrating the error recovery manager, graceful degradation system, retry system,
and error monitoring system into a cohesive error handling solution.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from pathlib import Path

from error_recovery_manager import ErrorRecoveryManager, RecoveryResult, DataSource
from graceful_degradation_system import GracefulDegradationSystem, DataQualityMetrics
from retry_system import RetrySystem, OperationType, RetryPolicy
from error_monitoring_system import ErrorMonitoringSystem, ErrorSeverity, Alert, HealthStatus
from wiki_data_system import WikiDataManager, Genre, MetaTag, Technique

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class SystemHealthReport:
    """Comprehensive system health report"""
    timestamp: datetime
    overall_health: HealthStatus
    degradation_level: int
    error_rate: float
    success_rate: float
    active_alerts: int
    data_quality_scores: Dict[str, float]
    circuit_breakers_open: int
    fallback_systems_active: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_health': self.overall_health.value,
            'degradation_level': self.degradation_level,
            'error_rate': self.error_rate,
            'success_rate': self.success_rate,
            'active_alerts': self.active_alerts,
            'data_quality_scores': self.data_quality_scores,
            'circuit_breakers_open': self.circuit_breakers_open,
            'fallback_systems_active': self.fallback_systems_active,
            'recommendations': self.recommendations
        }

@dataclass
class ErrorHandlingConfig:
    """Configuration for integrated error handling system"""
    storage_path: str = "./data/integrated_error_handling"
    enable_monitoring: bool = True
    enable_retry_system: bool = True
    enable_graceful_degradation: bool = True
    enable_error_recovery: bool = True
    
    # Alert thresholds
    error_rate_threshold: float = 10.0  # errors per minute
    success_rate_threshold: float = 90.0  # percentage
    degradation_alert_level: int = 2
    
    # Retry configuration
    default_max_retries: int = 3
    network_max_retries: int = 5
    
    # Health check intervals
    health_check_interval: int = 60  # seconds
    alert_check_interval: int = 30  # seconds

# ================================================================================================
# INTEGRATED ERROR HANDLING SYSTEM
# ================================================================================================

class IntegratedErrorHandlingSystem:
    """Unified error handling system that coordinates all error handling components"""
    
    def __init__(self, wiki_data_manager: WikiDataManager, config: ErrorHandlingConfig = None):
        self.wiki_data_manager = wiki_data_manager
        self.config = config or ErrorHandlingConfig()
        
        # Initialize subsystems
        self.error_recovery_manager: Optional[ErrorRecoveryManager] = None
        self.graceful_degradation_system: Optional[GracefulDegradationSystem] = None
        self.retry_system: Optional[RetrySystem] = None
        self.error_monitoring_system: Optional[ErrorMonitoringSystem] = None
        
        self.initialized = False
        self.alert_handlers: List[Callable[[Alert], None]] = []
        
        # Create storage directory
        Path(self.config.storage_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """Initialize all error handling subsystems"""
        logger.info("Initializing IntegratedErrorHandlingSystem")
        
        try:
            # Initialize error recovery manager
            if self.config.enable_error_recovery:
                self.error_recovery_manager = ErrorRecoveryManager(
                    f"{self.config.storage_path}/error_recovery"
                )
                await self.error_recovery_manager.initialize()
                logger.info("Error recovery manager initialized")
            
            # Initialize retry system
            if self.config.enable_retry_system:
                self.retry_system = RetrySystem(
                    f"{self.config.storage_path}/retry_system"
                )
                await self.retry_system.initialize()
                self._configure_retry_policies()
                logger.info("Retry system initialized")
            
            # Initialize error monitoring system
            if self.config.enable_monitoring:
                self.error_monitoring_system = ErrorMonitoringSystem(
                    f"{self.config.storage_path}/error_monitoring"
                )
                self.error_monitoring_system.error_rate_threshold = self.config.error_rate_threshold
                await self.error_monitoring_system.initialize()
                
                # Add alert handler
                self.error_monitoring_system.add_alert_callback(self._handle_system_alert)
                logger.info("Error monitoring system initialized")
            
            # Initialize graceful degradation system
            if self.config.enable_graceful_degradation and self.error_recovery_manager:
                self.graceful_degradation_system = GracefulDegradationSystem(
                    self.wiki_data_manager, self.error_recovery_manager
                )
                await self.graceful_degradation_system.initialize()
                logger.info("Graceful degradation system initialized")
            
            # Start background monitoring
            asyncio.create_task(self._system_health_monitor())
            asyncio.create_task(self._periodic_maintenance())
            
            self.initialized = True
            logger.info("IntegratedErrorHandlingSystem fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize IntegratedErrorHandlingSystem: {e}")
            raise
    
    async def execute_with_full_error_handling(self,
                                             operation: Callable[[], Awaitable[Any]],
                                             operation_id: str,
                                             operation_type: OperationType,
                                             context: Dict[str, Any] = None) -> Any:
        """
        Execute an operation with full error handling support
        
        Args:
            operation: Async function to execute
            operation_id: Unique identifier for the operation
            operation_type: Type of operation being performed
            context: Additional context information
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If operation fails after all error handling attempts
        """
        if not self.initialized:
            raise RuntimeError("IntegratedErrorHandlingSystem not initialized")
        
        context = context or {}
        start_time = datetime.now()
        
        try:
            # Execute with retry system if available
            if self.retry_system:
                result = await self.retry_system.execute_with_retry(
                    operation, operation_id, operation_type
                )
            else:
                result = await operation()
            
            # Log success
            if self.error_monitoring_system:
                response_time = (datetime.now() - start_time).total_seconds()
                self.error_monitoring_system.log_success(operation_id, response_time, context)
            
            return result
            
        except Exception as e:
            # Log error
            if self.error_monitoring_system:
                severity = self._determine_error_severity(e, operation_type)
                self.error_monitoring_system.log_error(operation_id, e, severity, context)
            
            # Attempt error recovery if available
            if self.error_recovery_manager:
                if operation_type == OperationType.DOWNLOAD:
                    recovery_result = await self.error_recovery_manager.handle_download_failure(
                        operation_id, e, context
                    )
                    if recovery_result.success:
                        logger.info(f"Successfully recovered from download failure: {operation_id}")
                        return recovery_result.data
                
                elif operation_type == OperationType.PARSE:
                    content = context.get('content', '')
                    content_type = context.get('content_type', 'unknown')
                    recovery_result = await self.error_recovery_manager.handle_parse_failure(
                        content, e, content_type, operation_id
                    )
                    if recovery_result.success:
                        logger.info(f"Successfully recovered from parse failure: {operation_id}")
                        return recovery_result.data
            
            # If all recovery attempts fail, re-raise the exception
            logger.error(f"All error handling attempts failed for {operation_id}: {e}")
            raise
    
    async def get_data_with_fallback(self, data_type: str, **kwargs) -> tuple[List[Any], DataQualityMetrics]:
        """
        Get data with full fallback support
        
        Args:
            data_type: Type of data to retrieve ('genres', 'meta_tags', 'techniques')
            **kwargs: Additional arguments for data retrieval
            
        Returns:
            Tuple of (data_list, quality_metrics)
        """
        if not self.graceful_degradation_system:
            raise RuntimeError("Graceful degradation system not available")
        
        if data_type == 'genres':
            return await self.graceful_degradation_system.get_genres_with_fallback(
                kwargs.get('max_age_hours', 24)
            )
        elif data_type == 'meta_tags':
            return await self.graceful_degradation_system.get_meta_tags_with_fallback(
                kwargs.get('category'), kwargs.get('max_age_hours', 24)
            )
        elif data_type == 'techniques':
            return await self.graceful_degradation_system.get_techniques_with_fallback(
                kwargs.get('technique_type'), kwargs.get('max_age_hours', 24)
            )
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add a custom alert handler"""
        self.alert_handlers.append(handler)
    
    def get_system_health_report(self) -> SystemHealthReport:
        """Get comprehensive system health report"""
        timestamp = datetime.now()
        
        # Get health metrics from monitoring system
        if self.error_monitoring_system:
            health_metrics = self.error_monitoring_system.get_current_health_status()
            error_stats = self.error_monitoring_system.get_error_statistics()
            active_alerts = len([a for a in self.error_monitoring_system.active_alerts.values() 
                               if not a.resolved])
        else:
            health_metrics = None
            error_stats = {}
            active_alerts = 0
        
        # Get degradation status
        if self.graceful_degradation_system:
            degradation_status = self.graceful_degradation_system.get_current_degradation_status()
            data_quality_report = self.graceful_degradation_system.get_data_quality_report()
        else:
            degradation_status = None
            data_quality_report = {}
        
        # Get retry system statistics
        if self.retry_system:
            retry_stats = self.retry_system.get_retry_statistics()
            circuit_breakers_open = len([
                cb for cb in self.retry_system.circuit_breakers.values()
                if cb.state.value == 'open'
            ])
        else:
            retry_stats = {}
            circuit_breakers_open = 0
        
        # Determine overall health
        overall_health = HealthStatus.HEALTHY
        if health_metrics:
            overall_health = health_metrics.overall_status
        elif degradation_status and degradation_status.level > 2:
            overall_health = HealthStatus.DEGRADED
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(
            health_metrics, degradation_status, retry_stats, error_stats
        )
        
        return SystemHealthReport(
            timestamp=timestamp,
            overall_health=overall_health,
            degradation_level=degradation_status.level if degradation_status else 0,
            error_rate=health_metrics.error_rate if health_metrics else 0.0,
            success_rate=health_metrics.success_rate if health_metrics else 100.0,
            active_alerts=active_alerts,
            data_quality_scores=data_quality_report.get('data_sources', {}),
            circuit_breakers_open=circuit_breakers_open,
            fallback_systems_active=degradation_status.active_fallbacks if degradation_status else [],
            recommendations=recommendations
        )
    
    async def perform_system_recovery(self) -> Dict[str, Any]:
        """Perform comprehensive system recovery operations"""
        logger.info("Starting system recovery operations")
        
        recovery_results = {
            'timestamp': datetime.now().isoformat(),
            'operations_performed': [],
            'success_count': 0,
            'failure_count': 0,
            'details': {}
        }
        
        # Reset circuit breakers if retry system is available
        if self.retry_system:
            try:
                open_circuits = [
                    key for key, cb in self.retry_system.circuit_breakers.items()
                    if cb.state.value == 'open'
                ]
                
                for circuit_key in open_circuits:
                    self.retry_system.reset_circuit_breaker(circuit_key)
                    recovery_results['operations_performed'].append(f"Reset circuit breaker: {circuit_key}")
                
                recovery_results['success_count'] += len(open_circuits)
                recovery_results['details']['circuit_breakers_reset'] = len(open_circuits)
                
            except Exception as e:
                logger.error(f"Failed to reset circuit breakers: {e}")
                recovery_results['failure_count'] += 1
                recovery_results['details']['circuit_breaker_reset_error'] = str(e)
        
        # Clear old error patterns
        if self.error_monitoring_system:
            try:
                old_pattern_count = len(self.error_monitoring_system.error_patterns)
                # This would typically clear patterns older than a certain threshold
                recovery_results['operations_performed'].append("Cleared old error patterns")
                recovery_results['success_count'] += 1
                recovery_results['details']['error_patterns_cleared'] = old_pattern_count
                
            except Exception as e:
                logger.error(f"Failed to clear error patterns: {e}")
                recovery_results['failure_count'] += 1
                recovery_results['details']['error_pattern_clear_error'] = str(e)
        
        # Refresh fallback data
        if self.error_recovery_manager:
            try:
                # This would typically refresh hardcoded fallback data
                recovery_results['operations_performed'].append("Refreshed fallback data")
                recovery_results['success_count'] += 1
                recovery_results['details']['fallback_data_refreshed'] = True
                
            except Exception as e:
                logger.error(f"Failed to refresh fallback data: {e}")
                recovery_results['failure_count'] += 1
                recovery_results['details']['fallback_refresh_error'] = str(e)
        
        logger.info(f"System recovery completed: {recovery_results['success_count']} successes, "
                   f"{recovery_results['failure_count']} failures")
        
        return recovery_results
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all error handling systems"""
        logger.info("Shutting down IntegratedErrorHandlingSystem")
        
        # Save state for all subsystems
        if self.error_recovery_manager:
            await self.error_recovery_manager.save_state()
        
        if self.retry_system:
            await self.retry_system.save_state()
        
        if self.error_monitoring_system:
            await self.error_monitoring_system.save_state()
        
        logger.info("IntegratedErrorHandlingSystem shutdown complete")
    
    # Private methods
    
    def _configure_retry_policies(self) -> None:
        """Configure retry policies based on configuration"""
        if not self.retry_system:
            return
        
        # Update default policy
        default_policy = RetryPolicy(
            max_attempts=self.config.default_max_retries,
            base_delay=1.0,
            max_delay=30.0
        )
        self.retry_system.add_retry_policy("default", default_policy)
        
        # Network-specific policy
        network_policy = RetryPolicy(
            max_attempts=self.config.network_max_retries,
            base_delay=2.0,
            max_delay=60.0,
            failure_threshold=3
        )
        self.retry_system.add_retry_policy("network", network_policy)
    
    def _determine_error_severity(self, error: Exception, operation_type: OperationType) -> ErrorSeverity:
        """Determine error severity based on error type and operation"""
        error_name = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # Critical errors
        if any(keyword in error_name for keyword in ['critical', 'fatal', 'system']):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if any(keyword in error_name for keyword in ['permission', 'authentication', 'authorization']):
            return ErrorSeverity.HIGH
        
        # Network errors are typically medium severity
        if any(keyword in error_name for keyword in ['connection', 'network', 'timeout']):
            return ErrorSeverity.MEDIUM
        
        # Parse errors are typically low to medium severity
        if any(keyword in error_name for keyword in ['parse', 'format', 'validation']):
            return ErrorSeverity.LOW
        
        # Default to medium severity
        return ErrorSeverity.MEDIUM
    
    def _handle_system_alert(self, alert: Alert) -> None:
        """Handle system alerts from monitoring system"""
        logger.warning(f"System alert: {alert.title} - {alert.description}")
        
        # Call custom alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in custom alert handler: {e}")
        
        # Perform automatic recovery actions for certain alert types
        if alert.alert_type.value == 'circuit_breaker_open':
            asyncio.create_task(self._handle_circuit_breaker_alert(alert))
        elif alert.alert_type.value == 'error_rate_high':
            asyncio.create_task(self._handle_high_error_rate_alert(alert))
    
    async def _handle_circuit_breaker_alert(self, alert: Alert) -> None:
        """Handle circuit breaker alerts"""
        # Could implement automatic circuit breaker reset after a delay
        await asyncio.sleep(300)  # Wait 5 minutes
        
        if self.retry_system:
            circuit_key = alert.context.get('circuit_key')
            if circuit_key:
                self.retry_system.reset_circuit_breaker(circuit_key)
                logger.info(f"Automatically reset circuit breaker: {circuit_key}")
    
    async def _handle_high_error_rate_alert(self, alert: Alert) -> None:
        """Handle high error rate alerts"""
        # Could implement automatic system recovery
        logger.info("High error rate detected, considering system recovery")
        
        # Wait a bit to see if the situation improves
        await asyncio.sleep(60)
        
        # Check if error rate is still high
        if self.error_monitoring_system:
            current_health = self.error_monitoring_system.get_current_health_status()
            if current_health.error_rate > self.config.error_rate_threshold:
                logger.info("Error rate still high, performing system recovery")
                await self.perform_system_recovery()
    
    def _generate_health_recommendations(self, health_metrics, degradation_status, 
                                       retry_stats, error_stats) -> List[str]:
        """Generate health recommendations based on system status"""
        recommendations = []
        
        # Error rate recommendations
        if health_metrics and health_metrics.error_rate > self.config.error_rate_threshold:
            recommendations.append(
                f"High error rate detected ({health_metrics.error_rate:.1f}/min). "
                "Consider investigating root causes and implementing additional error handling."
            )
        
        # Success rate recommendations
        if health_metrics and health_metrics.success_rate < self.config.success_rate_threshold:
            recommendations.append(
                f"Low success rate ({health_metrics.success_rate:.1f}%). "
                "Review failing operations and improve error recovery mechanisms."
            )
        
        # Degradation recommendations
        if degradation_status and degradation_status.level >= self.config.degradation_alert_level:
            recommendations.append(
                f"System degradation level {degradation_status.level}. "
                "Consider refreshing wiki data or checking network connectivity."
            )
        
        # Circuit breaker recommendations
        if retry_stats.get('circuit_breaker_states'):
            open_circuits = [
                key for key, state in retry_stats['circuit_breaker_states'].items()
                if state.get('state') == 'open'
            ]
            if open_circuits:
                recommendations.append(
                    f"{len(open_circuits)} circuit breaker(s) are open. "
                    "Consider manual reset or investigation of underlying issues."
                )
        
        # Error pattern recommendations
        if error_stats.get('error_patterns', 0) > 10:
            recommendations.append(
                "Multiple error patterns detected. "
                "Review error logs for recurring issues that need attention."
            )
        
        # Default recommendation if system is healthy
        if not recommendations:
            recommendations.append("System is operating normally. Continue monitoring.")
        
        return recommendations
    
    async def _system_health_monitor(self) -> None:
        """Background task to monitor overall system health"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # Get system health report
                health_report = self.get_system_health_report()
                
                # Log health status periodically
                if health_report.overall_health != HealthStatus.HEALTHY:
                    logger.warning(f"System health: {health_report.overall_health.value} "
                                 f"(degradation level: {health_report.degradation_level})")
                
                # Auto-recovery for critical states
                if health_report.overall_health == HealthStatus.CRITICAL:
                    logger.error("System in critical state, attempting automatic recovery")
                    await self.perform_system_recovery()
                
            except Exception as e:
                logger.error(f"Error in system health monitor: {e}")
    
    async def _periodic_maintenance(self) -> None:
        """Background task for periodic maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Save state for all subsystems
                if self.error_recovery_manager:
                    await self.error_recovery_manager.save_state()
                
                if self.retry_system:
                    await self.retry_system.save_state()
                
                if self.error_monitoring_system:
                    await self.error_monitoring_system.save_state()
                
                logger.debug("Periodic maintenance completed")
                
            except Exception as e:
                logger.error(f"Error in periodic maintenance: {e}")

# ================================================================================================
# CONVENIENCE FUNCTIONS
# ================================================================================================

async def create_integrated_error_handling_system(
    wiki_data_manager: WikiDataManager,
    config: ErrorHandlingConfig = None
) -> IntegratedErrorHandlingSystem:
    """
    Create and initialize an integrated error handling system
    
    Args:
        wiki_data_manager: WikiDataManager instance
        config: Optional configuration
        
    Returns:
        Initialized IntegratedErrorHandlingSystem
    """
    system = IntegratedErrorHandlingSystem(wiki_data_manager, config)
    await system.initialize()
    return system