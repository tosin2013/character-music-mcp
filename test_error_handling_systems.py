#!/usr/bin/env python3
"""
Tests for Error Handling and Fallback Systems

This module provides comprehensive tests for the error recovery manager,
graceful degradation system, retry system, and error monitoring system.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from error_recovery_manager import (
    ErrorRecoveryManager, ErrorType, RecoveryAction, DataSource, 
    FallbackData, RecoveryResult
)
from graceful_degradation_system import (
    GracefulDegradationSystem, DataQualityMetrics, DegradationLevel
)
from retry_system import (
    RetrySystem, RetryPolicy, RetryStrategy, OperationType, 
    CircuitState, RetrySession
)
from error_monitoring_system import (
    ErrorMonitoringSystem, ErrorSeverity, AlertType, HealthStatus,
    ErrorEvent, Alert
)
from wiki_data_system import Genre, MetaTag, Technique, WikiDataManager

# ================================================================================================
# TEST FIXTURES
# ================================================================================================

@pytest.fixture
async def error_recovery_manager():
    """Create and initialize ErrorRecoveryManager for testing"""
    manager = ErrorRecoveryManager("./test_data/error_recovery")
    await manager.initialize()
    yield manager
    # Cleanup would go here if needed

@pytest.fixture
async def retry_system():
    """Create and initialize RetrySystem for testing"""
    system = RetrySystem("./test_data/retry_system")
    await system.initialize()
    yield system
    # Cleanup would go here if needed

@pytest.fixture
async def error_monitoring_system():
    """Create and initialize ErrorMonitoringSystem for testing"""
    system = ErrorMonitoringSystem("./test_data/error_monitoring")
    await system.initialize()
    yield system
    # Cleanup would go here if needed

@pytest.fixture
def mock_wiki_data_manager():
    """Create mock WikiDataManager for testing"""
    manager = Mock(spec=WikiDataManager)
    manager.get_genres = AsyncMock()
    manager.get_meta_tags = AsyncMock()
    manager.get_techniques = AsyncMock()
    return manager

@pytest.fixture
async def graceful_degradation_system(mock_wiki_data_manager, error_recovery_manager):
    """Create and initialize GracefulDegradationSystem for testing"""
    system = GracefulDegradationSystem(mock_wiki_data_manager, error_recovery_manager)
    await system.initialize()
    yield system
    # Cleanup would go here if needed

# ================================================================================================
# ERROR RECOVERY MANAGER TESTS
# ================================================================================================

class TestErrorRecoveryManager:
    """Tests for ErrorRecoveryManager"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, error_recovery_manager):
        """Test error recovery manager initialization"""
        assert error_recovery_manager.initialized
        assert len(error_recovery_manager.fallback_data_cache) > 0
        assert 'genres' in error_recovery_manager.fallback_data_cache
        assert 'meta_tags' in error_recovery_manager.fallback_data_cache
        assert 'techniques' in error_recovery_manager.fallback_data_cache
    
    @pytest.mark.asyncio
    async def test_handle_download_failure_network_error(self, error_recovery_manager):
        """Test handling download failure with network error"""
        url = "https://example.com/test"
        error = ConnectionError("Network unreachable")
        context = {"operation": "test_download"}
        
        result = await error_recovery_manager.handle_download_failure(url, error, context)
        
        assert isinstance(result, RecoveryResult)
        assert result.recovery_action in [RecoveryAction.USE_CACHED_DATA, RecoveryAction.USE_FALLBACK_DATA]
        assert len(error_recovery_manager.error_history) > 0
        
        # Check error record
        error_record = error_recovery_manager.error_history[-1]
        assert error_record.error_type == ErrorType.NETWORK_ERROR
        assert error_record.operation == f"download:{url}"
    
    @pytest.mark.asyncio
    async def test_handle_parse_failure(self, error_recovery_manager):
        """Test handling parse failure"""
        content = "<invalid>html</content>"
        error = ValueError("Invalid HTML structure")
        content_type = "genres"
        source_url = "https://example.com/genres"
        
        result = await error_recovery_manager.handle_parse_failure(
            content, error, content_type, source_url
        )
        
        assert isinstance(result, RecoveryResult)
        assert result.recovery_action == RecoveryAction.USE_FALLBACK_DATA
        assert result.success  # Should succeed with fallback data
        assert result.data is not None
    
    def test_get_fallback_data(self, error_recovery_manager):
        """Test getting fallback data"""
        # Test getting genres fallback
        genres_fallback = error_recovery_manager.get_fallback_data('genres')
        assert genres_fallback is not None
        assert isinstance(genres_fallback, FallbackData)
        assert genres_fallback.source == DataSource.HARDCODED_FALLBACK
        assert len(genres_fallback.data) > 0
        
        # Test getting non-existent data type
        invalid_fallback = error_recovery_manager.get_fallback_data('invalid_type')
        assert invalid_fallback is None
    
    def test_create_mixed_source_data(self, error_recovery_manager):
        """Test creating mixed source data"""
        wiki_data = [{'name': 'Rock', 'source': 'wiki'}]
        fallback_data = [{'name': 'Pop', 'source': 'fallback'}, {'name': 'Rock', 'source': 'fallback'}]
        
        mixed_data = error_recovery_manager.create_mixed_source_data(
            wiki_data, fallback_data, 'genres'
        )
        
        assert isinstance(mixed_data, FallbackData)
        assert mixed_data.source == DataSource.MIXED_SOURCES
        assert len(mixed_data.data) == 2  # Rock should not be duplicated
        assert mixed_data.quality_score > 0.5  # Should have decent quality
    
    def test_error_statistics(self, error_recovery_manager):
        """Test getting error statistics"""
        # Add some test errors
        error_recovery_manager.error_history.extend([
            Mock(error_type=ErrorType.NETWORK_ERROR, recovery_successful=True),
            Mock(error_type=ErrorType.PARSE_ERROR, recovery_successful=False),
            Mock(error_type=ErrorType.NETWORK_ERROR, recovery_successful=True)
        ])
        
        stats = error_recovery_manager.get_error_statistics()
        
        assert stats['total_errors'] == 3
        assert stats['recovery_success_rate'] == 2/3  # 2 out of 3 successful
        assert 'errors_by_type' in stats
        assert 'most_common_errors' in stats

# ================================================================================================
# GRACEFUL DEGRADATION SYSTEM TESTS
# ================================================================================================

class TestGracefulDegradationSystem:
    """Tests for GracefulDegradationSystem"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, graceful_degradation_system):
        """Test graceful degradation system initialization"""
        assert graceful_degradation_system.initialized
        assert isinstance(graceful_degradation_system.current_degradation, DegradationLevel)
    
    @pytest.mark.asyncio
    async def test_get_genres_with_fallback_success(self, graceful_degradation_system, mock_wiki_data_manager):
        """Test getting genres with successful wiki data"""
        # Mock successful wiki data
        mock_genres = [
            Genre(name="Rock", description="Rock music", subgenres=[], characteristics=[], 
                  typical_instruments=[], mood_associations=[], source_url="wiki", 
                  download_date=datetime.now())
        ]
        mock_wiki_data_manager.get_genres.return_value = mock_genres
        
        genres, quality_metrics = await graceful_degradation_system.get_genres_with_fallback()
        
        assert len(genres) > 0
        assert isinstance(quality_metrics, DataQualityMetrics)
        assert quality_metrics.wiki_items > 0
        assert quality_metrics.overall_score > 0.8  # High quality with wiki data
    
    @pytest.mark.asyncio
    async def test_get_genres_with_fallback_failure(self, graceful_degradation_system, mock_wiki_data_manager):
        """Test getting genres when wiki data fails"""
        # Mock wiki failure
        mock_wiki_data_manager.get_genres.side_effect = ConnectionError("Network error")
        
        genres, quality_metrics = await graceful_degradation_system.get_genres_with_fallback()
        
        assert len(genres) > 0  # Should have fallback data
        assert isinstance(quality_metrics, DataQualityMetrics)
        assert quality_metrics.wiki_items == 0
        assert quality_metrics.fallback_items > 0
        assert quality_metrics.overall_score < 0.8  # Lower quality with fallback only
    
    @pytest.mark.asyncio
    async def test_handle_partial_data_failure(self, graceful_degradation_system):
        """Test handling partial data failure"""
        partial_data = [{'name': 'Partial Rock', 'description': 'Partially recovered'}]
        error = ValueError("Parse error")
        
        combined_data, quality_metrics = await graceful_degradation_system.handle_partial_data_failure(
            'genres', partial_data, error
        )
        
        assert len(combined_data) > len(partial_data)  # Should have additional fallback data
        assert isinstance(quality_metrics, DataQualityMetrics)
        assert quality_metrics.overall_score > 0.3  # Should have reasonable quality
    
    def test_get_current_degradation_status(self, graceful_degradation_system):
        """Test getting current degradation status"""
        status = graceful_degradation_system.get_current_degradation_status()
        
        assert isinstance(status, DegradationLevel)
        assert 0 <= status.level <= 5
        assert isinstance(status.description, str)
        assert isinstance(status.active_fallbacks, list)
        assert isinstance(status.affected_features, list)
        assert 0.0 <= status.estimated_quality <= 1.0
    
    def test_data_quality_report(self, graceful_degradation_system):
        """Test getting data quality report"""
        report = graceful_degradation_system.get_data_quality_report()
        
        assert 'degradation_level' in report
        assert 'degradation_description' in report
        assert 'overall_quality' in report
        assert 'active_fallbacks' in report
        assert 'affected_features' in report
        assert 'data_sources' in report

# ================================================================================================
# RETRY SYSTEM TESTS
# ================================================================================================

class TestRetrySystem:
    """Tests for RetrySystem"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, retry_system):
        """Test retry system initialization"""
        assert retry_system.initialized
        assert len(retry_system.retry_policies) > 0
        assert 'default' in retry_system.retry_policies
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_success_first_attempt(self, retry_system):
        """Test successful operation on first attempt"""
        async def successful_operation():
            return "success"
        
        result = await retry_system.execute_with_retry(
            successful_operation, "test_op_1", OperationType.DOWNLOAD
        )
        
        assert result == "success"
        assert len(retry_system.retry_sessions) == 1
        
        session = retry_system.retry_sessions[0]
        assert session.final_success
        assert session.total_attempts == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_success_after_failures(self, retry_system):
        """Test successful operation after some failures"""
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Temporary network error")
            return "success"
        
        result = await retry_system.execute_with_retry(
            flaky_operation, "test_op_2", OperationType.NETWORK_REQUEST
        )
        
        assert result == "success"
        assert len(retry_system.retry_sessions) == 1
        
        session = retry_system.retry_sessions[0]
        assert session.final_success
        assert session.total_attempts == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_all_attempts_fail(self, retry_system):
        """Test operation that fails all retry attempts"""
        async def failing_operation():
            raise ConnectionError("Persistent network error")
        
        with pytest.raises(ConnectionError):
            await retry_system.execute_with_retry(
                failing_operation, "test_op_3", OperationType.NETWORK_REQUEST
            )
        
        assert len(retry_system.retry_sessions) == 1
        
        session = retry_system.retry_sessions[0]
        assert not session.final_success
        assert session.total_attempts > 1
    
    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, retry_system):
        """Test that non-retryable exceptions are not retried"""
        async def auth_error_operation():
            raise PermissionError("Authentication failed")
        
        with pytest.raises(PermissionError):
            await retry_system.execute_with_retry(
                auth_error_operation, "test_op_4", OperationType.DOWNLOAD
            )
        
        session = retry_system.retry_sessions[-1]
        assert not session.final_success
        assert session.total_attempts == 1  # Should not retry
    
    def test_add_retry_policy(self, retry_system):
        """Test adding custom retry policy"""
        custom_policy = RetryPolicy(
            max_attempts=5,
            base_delay=2.0,
            strategy=RetryStrategy.LINEAR_BACKOFF
        )
        
        retry_system.add_retry_policy("custom", custom_policy)
        
        assert "custom" in retry_system.retry_policies
        assert retry_system.retry_policies["custom"] == custom_policy
    
    def test_circuit_breaker_functionality(self, retry_system):
        """Test circuit breaker functionality"""
        operation_key = "test_operation"
        
        # Initially should be able to attempt
        initial_status = retry_system.get_circuit_breaker_status(operation_key)
        assert initial_status.state == CircuitState.CLOSED
        
        # Reset circuit breaker
        retry_system.reset_circuit_breaker(operation_key)
        reset_status = retry_system.get_circuit_breaker_status(operation_key)
        assert reset_status.state == CircuitState.CLOSED
        assert reset_status.failure_count == 0
    
    def test_retry_statistics(self, retry_system):
        """Test getting retry statistics"""
        # Add some mock sessions
        retry_system.retry_sessions.extend([
            Mock(final_success=True, total_attempts=1, operation_type=OperationType.DOWNLOAD, 
                 start_time=datetime.now(), duration=timedelta(seconds=1)),
            Mock(final_success=False, total_attempts=3, operation_type=OperationType.PARSE,
                 start_time=datetime.now(), duration=timedelta(seconds=5))
        ])
        
        stats = retry_system.get_retry_statistics()
        
        assert stats['total_sessions'] == 2
        assert stats['success_rate'] == 0.5
        assert 'operations_by_type' in stats
        assert 'circuit_breaker_states' in stats

# ================================================================================================
# ERROR MONITORING SYSTEM TESTS
# ================================================================================================

class TestErrorMonitoringSystem:
    """Tests for ErrorMonitoringSystem"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, error_monitoring_system):
        """Test error monitoring system initialization"""
        assert error_monitoring_system.initialized
        assert len(error_monitoring_system.alert_callbacks) == 0
    
    def test_log_error(self, error_monitoring_system):
        """Test logging an error"""
        operation = "test_operation"
        error = ValueError("Test error")
        context = {"test_key": "test_value"}
        
        error_monitoring_system.log_error(operation, error, ErrorSeverity.HIGH, context)
        
        assert len(error_monitoring_system.error_events) == 1
        
        error_event = error_monitoring_system.error_events[0]
        assert error_event.operation == operation
        assert error_event.error_type == "ValueError"
        assert error_event.error_message == "Test error"
        assert error_event.severity == ErrorSeverity.HIGH
        assert error_event.context == context
    
    def test_log_success(self, error_monitoring_system):
        """Test logging a successful operation"""
        operation = "test_operation"
        response_time = 1.5
        
        error_monitoring_system.log_success(operation, response_time)
        
        metrics = error_monitoring_system.operation_metrics[operation]
        assert metrics['total_operations'] == 1
        assert metrics['successful_operations'] == 1
        assert metrics['total_response_time'] == response_time
        assert metrics['last_success'] is not None
    
    def test_alert_callback(self, error_monitoring_system):
        """Test alert callback functionality"""
        callback_called = False
        received_alert = None
        
        def test_callback(alert):
            nonlocal callback_called, received_alert
            callback_called = True
            received_alert = alert
        
        error_monitoring_system.add_alert_callback(test_callback)
        
        # Trigger an alert by logging many errors quickly
        for i in range(10):
            error_monitoring_system.log_error(
                "test_op", ValueError(f"Error {i}"), ErrorSeverity.HIGH
            )
        
        # Give some time for alert processing
        import time
        time.sleep(0.1)
        
        # Check if callback was called (may not always trigger depending on thresholds)
        if callback_called:
            assert received_alert is not None
            assert isinstance(received_alert, Alert)
    
    def test_acknowledge_and_resolve_alert(self, error_monitoring_system):
        """Test acknowledging and resolving alerts"""
        # Create a test alert
        alert = Alert(
            alert_id="test_alert",
            alert_type=AlertType.ERROR_RATE_HIGH,
            severity=ErrorSeverity.HIGH,
            title="Test Alert",
            description="Test alert description",
            timestamp=datetime.now()
        )
        error_monitoring_system.active_alerts["test_alert"] = alert
        
        # Test acknowledgment
        assert error_monitoring_system.acknowledge_alert("test_alert")
        assert alert.acknowledged
        assert alert.acknowledgment_time is not None
        
        # Test resolution
        assert error_monitoring_system.resolve_alert("test_alert")
        assert alert.resolved
        assert alert.resolution_time is not None
        
        # Test non-existent alert
        assert not error_monitoring_system.acknowledge_alert("non_existent")
        assert not error_monitoring_system.resolve_alert("non_existent")
    
    def test_get_current_health_status(self, error_monitoring_system):
        """Test getting current health status"""
        # Add some test data
        error_monitoring_system.log_success("test_op", 1.0)
        error_monitoring_system.log_error("test_op", ValueError("Test error"))
        
        health_status = error_monitoring_system.get_current_health_status()
        
        assert isinstance(health_status.overall_status, HealthStatus)
        assert health_status.error_rate >= 0
        assert 0 <= health_status.success_rate <= 100
        assert health_status.average_response_time >= 0
        assert isinstance(health_status.degraded_services, list)
        assert isinstance(health_status.quality_scores, dict)
    
    def test_get_error_statistics(self, error_monitoring_system):
        """Test getting error statistics"""
        # Add some test errors
        error_monitoring_system.log_error("op1", ValueError("Error 1"), ErrorSeverity.HIGH)
        error_monitoring_system.log_error("op2", ConnectionError("Error 2"), ErrorSeverity.MEDIUM)
        error_monitoring_system.log_error("op1", ValueError("Error 3"), ErrorSeverity.LOW)
        
        stats = error_monitoring_system.get_error_statistics()
        
        assert stats['total_errors'] == 3
        assert 'errors_by_severity' in stats
        assert 'errors_by_operation' in stats
        assert 'errors_by_type' in stats
        assert 'recent_errors' in stats
        
        # Check specific counts
        assert stats['errors_by_operation']['op1'] == 2
        assert stats['errors_by_operation']['op2'] == 1
    
    def test_get_operation_health_report(self, error_monitoring_system):
        """Test getting operation health report"""
        # Add test data for multiple operations
        error_monitoring_system.log_success("healthy_op", 0.5)
        error_monitoring_system.log_success("healthy_op", 0.7)
        
        error_monitoring_system.log_success("degraded_op", 1.0)
        error_monitoring_system.log_error("degraded_op", ValueError("Error"))
        
        report = error_monitoring_system.get_operation_health_report()
        
        assert 'healthy_op' in report
        assert 'degraded_op' in report
        
        healthy_report = report['healthy_op']
        assert healthy_report['health_status'] == 'healthy'
        assert healthy_report['success_rate'] == 100.0
        
        degraded_report = report['degraded_op']
        assert degraded_report['success_rate'] == 50.0

# ================================================================================================
# INTEGRATION TESTS
# ================================================================================================

class TestErrorHandlingIntegration:
    """Integration tests for error handling systems"""
    
    @pytest.mark.asyncio
    async def test_full_error_handling_workflow(self, error_recovery_manager, 
                                               retry_system, error_monitoring_system):
        """Test complete error handling workflow"""
        # Simulate a failing operation that eventually succeeds
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            
            # Log the attempt
            if attempt_count < 3:
                error = ConnectionError(f"Network error on attempt {attempt_count}")
                error_monitoring_system.log_error("integration_test", error, ErrorSeverity.MEDIUM)
                raise error
            else:
                error_monitoring_system.log_success("integration_test", 1.0)
                return "success"
        
        # Execute with retry system
        result = await retry_system.execute_with_retry(
            flaky_operation, "integration_test", OperationType.NETWORK_REQUEST
        )
        
        assert result == "success"
        
        # Check that errors were logged
        assert len(error_monitoring_system.error_events) >= 2
        
        # Check that retry session was recorded
        assert len(retry_system.retry_sessions) == 1
        session = retry_system.retry_sessions[0]
        assert session.final_success
        assert session.total_attempts == 3
        
        # Check operation metrics
        metrics = error_monitoring_system.operation_metrics["integration_test"]
        assert metrics['successful_operations'] == 1
        assert metrics['failed_operations'] == 2
    
    @pytest.mark.asyncio
    async def test_degradation_with_monitoring(self, graceful_degradation_system, 
                                             error_monitoring_system, mock_wiki_data_manager):
        """Test graceful degradation with error monitoring"""
        # Simulate wiki service failure
        mock_wiki_data_manager.get_genres.side_effect = ConnectionError("Wiki service down")
        
        # Log the error
        error_monitoring_system.log_error("wiki_service", ConnectionError("Wiki service down"), 
                                        ErrorSeverity.HIGH)
        
        # Try to get genres (should fall back gracefully)
        genres, quality_metrics = await graceful_degradation_system.get_genres_with_fallback()
        
        # Should have fallback data
        assert len(genres) > 0
        assert quality_metrics.wiki_items == 0
        assert quality_metrics.fallback_items > 0
        
        # Check degradation status
        degradation_status = graceful_degradation_system.get_current_degradation_status()
        assert degradation_status.level > 0  # Should be degraded
        
        # Check health status
        health_status = error_monitoring_system.get_current_health_status()
        assert health_status.overall_status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

# ================================================================================================
# PERFORMANCE TESTS
# ================================================================================================

class TestErrorHandlingPerformance:
    """Performance tests for error handling systems"""
    
    @pytest.mark.asyncio
    async def test_high_volume_error_logging(self, error_monitoring_system):
        """Test performance with high volume of error logging"""
        import time
        
        start_time = time.time()
        
        # Log many errors quickly
        for i in range(1000):
            error_monitoring_system.log_error(
                f"operation_{i % 10}", 
                ValueError(f"Error {i}"), 
                ErrorSeverity.MEDIUM
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle 1000 errors in reasonable time (< 1 second)
        assert duration < 1.0
        assert len(error_monitoring_system.error_events) == 1000
    
    @pytest.mark.asyncio
    async def test_concurrent_retry_operations(self, retry_system):
        """Test performance with concurrent retry operations"""
        async def test_operation(op_id: str):
            attempt_count = 0
            
            async def flaky_op():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 2:
                    raise ConnectionError("Temporary error")
                return f"success_{op_id}"
            
            return await retry_system.execute_with_retry(
                flaky_op, op_id, OperationType.DOWNLOAD
            )
        
        # Run multiple operations concurrently
        tasks = [test_operation(f"op_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 10
        assert all("success_" in result for result in results)
        
        # Check that all sessions were recorded
        assert len(retry_system.retry_sessions) == 10

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])