#!/usr/bin/env python3
"""
Test Performance Monitoring System

This module tests the comprehensive performance monitoring system including:
- Download performance tracking
- Parsing performance monitoring
- Generation metrics with wiki data integration
- System health monitoring
"""

import asyncio
import pytest
import pytest_asyncio
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from performance_monitor import (
    PerformanceMonitor, PerformanceMetric, OperationStats, SystemMetrics,
    PerformanceReport, monitor_performance
)
from wiki_downloader import WikiDownloader
from wiki_content_parser import ContentParser
from enhanced_genre_mapper import EnhancedGenreMapper
from wiki_data_models import Genre

# ================================================================================================
# FIXTURES
# ================================================================================================

@pytest_asyncio.fixture
async def performance_monitor():
    """Create and initialize PerformanceMonitor for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        monitor = PerformanceMonitor(storage_path=temp_dir)
        await monitor.initialize()
        try:
            yield monitor
        finally:
            await monitor.save_state()

@pytest.fixture
def mock_wiki_data_manager():
    """Create mock WikiDataManager"""
    manager = Mock()
    manager.get_genres = AsyncMock(return_value=[
        Genre(
            name="Electronic",
            description="Electronic music genre",
            subgenres=["House", "Techno"],
            characteristics=["synthetic", "danceable"],
            typical_instruments=["synthesizer", "drum machine"],
            mood_associations=["energetic", "futuristic"],
            source_url="https://example.com/electronic",
            download_date=datetime.now()
        )
    ])
    return manager

# ================================================================================================
# PERFORMANCE MONITOR TESTS
# ================================================================================================

class TestPerformanceMonitor:
    """Tests for PerformanceMonitor"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, performance_monitor):
        """Test performance monitor initialization"""
        assert performance_monitor.initialized
        assert len(performance_monitor.metrics) == 0
        assert len(performance_monitor.operation_stats) == 0
    
    @pytest.mark.asyncio
    async def test_measure_operation_context_manager(self, performance_monitor):
        """Test operation measurement context manager"""
        async with performance_monitor.measure_operation("test_operation", {"test": "context"}):
            await asyncio.sleep(0.1)  # Simulate work
        
        # Check that metric was recorded
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "test_operation"
        assert metric.success == True
        assert metric.duration >= 0.1
        assert metric.context["test"] == "context"
        
        # Check operation stats
        stats = performance_monitor.operation_stats["test_operation"]
        assert stats.total_calls == 1
        assert stats.successful_calls == 1
        assert stats.success_rate == 100.0
    
    @pytest.mark.asyncio
    async def test_measure_operation_with_exception(self, performance_monitor):
        """Test operation measurement when exception occurs"""
        with pytest.raises(ValueError):
            async with performance_monitor.measure_operation("failing_operation"):
                raise ValueError("Test error")
        
        # Check that metric was recorded as failed
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "failing_operation"
        assert metric.success == False
        
        # Check operation stats
        stats = performance_monitor.operation_stats["failing_operation"]
        assert stats.total_calls == 1
        assert stats.failed_calls == 1
        assert stats.success_rate == 0.0
    
    def test_sync_operation_measurement(self, performance_monitor):
        """Test synchronous operation measurement"""
        with performance_monitor.measure_sync_operation("sync_operation"):
            time.sleep(0.05)  # Simulate work
        
        # Give async task time to complete
        time.sleep(0.1)
        
        # Check that metric was recorded
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "sync_operation"
        assert metric.success == True
        assert metric.duration >= 0.05
    
    @pytest.mark.asyncio
    async def test_record_download_metrics(self, performance_monitor):
        """Test recording download-specific metrics"""
        await performance_monitor.record_download_metrics(
            url="https://example.com/test",
            duration=2.5,
            success=True,
            file_size=1024000,  # 1MB
            status_code=200
        )
        
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "wiki_download"
        assert metric.duration == 2.5
        assert metric.success == True
        assert metric.context["url"] == "https://example.com/test"
        assert metric.context["file_size_bytes"] == 1024000
        assert metric.context["status_code"] == 200
        assert metric.context["download_speed_mbps"] > 0
    
    @pytest.mark.asyncio
    async def test_record_parsing_metrics(self, performance_monitor):
        """Test recording parsing-specific metrics"""
        await performance_monitor.record_parsing_metrics(
            content_type="genre_page",
            content_size=50000,
            duration=1.2,
            success=True,
            items_parsed=25
        )
        
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "content_parsing"
        assert metric.duration == 1.2
        assert metric.success == True
        assert metric.context["content_type"] == "genre_page"
        assert metric.context["items_parsed"] == 25
        assert metric.context["parsing_speed_items_per_sec"] > 0
    
    @pytest.mark.asyncio
    async def test_record_generation_metrics(self, performance_monitor):
        """Test recording generation-specific metrics"""
        await performance_monitor.record_generation_metrics(
            generation_type="album_creation",
            duration=5.0,
            success=True,
            wiki_data_used=True,
            fallback_used=False
        )
        
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "music_generation"
        assert metric.duration == 5.0
        assert metric.success == True
        assert metric.context["generation_type"] == "album_creation"
        assert metric.context["wiki_data_used"] == True
        assert metric.context["data_source"] == "wiki"
    
    def test_get_operation_statistics(self, performance_monitor):
        """Test getting operation statistics"""
        # Add some test metrics by creating a proper OperationStats object
        from performance_monitor import OperationStats
        stats = OperationStats(operation="test_op")
        stats.total_calls = 10
        stats.successful_calls = 8
        stats.failed_calls = 2
        stats.total_duration = 25.0
        stats.min_duration = 1.0
        stats.max_duration = 5.0
        
        performance_monitor.operation_stats["test_op"] = stats
        
        result = performance_monitor.get_operation_statistics("test_op")
        assert result["total_calls"] == 10
        assert result["success_rate"] == 80.0
        assert result["average_duration"] == 3.125  # 25.0 / 8
        assert result["min_duration"] == 1.0
        assert result["max_duration"] == 5.0
    
    @pytest.mark.asyncio
    async def test_download_performance_report(self, performance_monitor):
        """Test download performance report generation"""
        # Add some download metrics
        await performance_monitor.record_download_metrics("https://example.com/1", 1.0, True, 1000, 200)
        await performance_monitor.record_download_metrics("https://example.com/2", 2.0, True, 2000, 200)
        await performance_monitor.record_download_metrics("https://example.com/3", 0.5, False, 0, 404)
        
        report = performance_monitor.get_download_performance_report()
        assert report["total_downloads"] == 3
        assert report["successful_downloads"] == 2
        assert report["failed_downloads"] == 1
        assert report["success_rate"] == pytest.approx(66.67, rel=1e-2)
        assert report["average_duration_seconds"] == 1.5  # (1.0 + 2.0) / 2
    
    @pytest.mark.asyncio
    async def test_parsing_performance_report(self, performance_monitor):
        """Test parsing performance report generation"""
        # Add some parsing metrics
        await performance_monitor.record_parsing_metrics("genre_page", 10000, 1.0, True, 10)
        await performance_monitor.record_parsing_metrics("meta_tag_page", 5000, 0.5, True, 20)
        await performance_monitor.record_parsing_metrics("genre_page", 8000, 2.0, False, 0)
        
        report = performance_monitor.get_parsing_performance_report()
        assert "genre_page" in report
        assert "meta_tag_page" in report
        
        genre_stats = report["genre_page"]
        assert genre_stats["total_operations"] == 2
        assert genre_stats["successful_operations"] == 1
        assert genre_stats["success_rate"] == 50.0
        assert genre_stats["total_items_parsed"] == 10
    
    @pytest.mark.asyncio
    async def test_generation_performance_report(self, performance_monitor):
        """Test generation performance report generation"""
        # Add some generation metrics
        await performance_monitor.record_generation_metrics("album", 3.0, True, True, False)
        await performance_monitor.record_generation_metrics("song", 1.0, True, False, True)
        await performance_monitor.record_generation_metrics("album", 2.0, False, True, False)
        
        report = performance_monitor.get_generation_performance_report()
        assert report["total_generations"] == 3
        assert report["wiki_data_performance"]["count"] == 2
        assert report["fallback_data_performance"]["count"] == 1
        assert report["overall_success_rate"] == pytest.approx(66.67, rel=1e-2)
    
    def test_system_health_report(self, performance_monitor):
        """Test system health report generation"""
        report = performance_monitor.get_system_health_report()
        assert "current_metrics" in report
        assert "recent_averages" in report
        assert "performance_issues" in report
        assert "health_status" in report
        assert report["health_status"] in ["healthy", "degraded", "critical"]
    
    @pytest.mark.asyncio
    async def test_comprehensive_report_generation(self, performance_monitor):
        """Test comprehensive performance report generation"""
        # Add some test data
        await performance_monitor.record_download_metrics("https://example.com", 1.0, True, 1000, 200)
        await performance_monitor.record_parsing_metrics("genre_page", 5000, 0.5, True, 5)
        
        report = await performance_monitor.generate_comprehensive_report()
        assert isinstance(report, PerformanceReport)
        assert report.report_period == "last_24_hours"
        assert isinstance(report.system_metrics, SystemMetrics)
        assert len(report.operation_stats) > 0
        assert isinstance(report.top_slowest_operations, list)
        assert isinstance(report.performance_trends, dict)
        assert isinstance(report.alerts, list)
    
    @pytest.mark.asyncio
    async def test_alert_callback(self, performance_monitor):
        """Test performance alert callbacks"""
        callback_called = False
        received_alert = None
        received_context = None
        
        def test_callback(alert, context):
            nonlocal callback_called, received_alert, received_context
            callback_called = True
            received_alert = alert
            received_context = context
        
        performance_monitor.add_alert_callback(test_callback)
        
        # Trigger a slow operation alert
        await performance_monitor.record_download_metrics(
            "https://slow-example.com", 
            10.0,  # Very slow
            True, 
            1000, 
            200
        )
        
        # Give callback time to execute
        await asyncio.sleep(0.1)
        
        assert callback_called
        assert "Slow operation detected" in received_alert
        assert received_context is not None

# ================================================================================================
# INTEGRATION TESTS
# ================================================================================================

class TestPerformanceIntegration:
    """Tests for performance monitoring integration with other components"""
    
    @pytest.mark.asyncio
    async def test_wiki_downloader_integration(self, performance_monitor):
        """Test performance monitoring integration with WikiDownloader"""
        from wiki_cache_manager import WikiCacheManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = WikiCacheManager(temp_dir)
            downloader = WikiDownloader(
                cache_manager=cache_manager,
                performance_monitor=performance_monitor
            )
            
            # Mock the HTTP session to avoid actual network calls
            with patch('aiohttp.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value="<html><body>Test content</body></html>")
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)
                
                mock_session.get.return_value = mock_response
                mock_session.close = AsyncMock()
                mock_session_class.return_value = mock_session
                
                async with downloader:
                    result = await downloader.download_page("https://example.com/test")
                
                # Check that performance metrics were recorded
                assert len(performance_monitor.metrics) > 0
                download_metrics = [m for m in performance_monitor.metrics if m.operation == "wiki_download"]
                assert len(download_metrics) > 0
                
                metric = download_metrics[0]
                assert metric.success == result.success
                assert metric.context["url"] == "https://example.com/test"
    
    @pytest.mark.asyncio
    async def test_content_parser_integration(self, performance_monitor):
        """Test performance monitoring integration with ContentParser"""
        parser = ContentParser(performance_monitor=performance_monitor)
        
        html_content = """
        <html>
            <body>
                <h3>Electronic Music</h3>
                <ul>
                    <li>House - Danceable electronic music</li>
                    <li>Techno - Repetitive electronic beats</li>
                </ul>
            </body>
        </html>
        """
        
        genres = parser.parse_genre_page(html_content, "https://example.com/genres")
        
        # Give async task time to complete
        await asyncio.sleep(0.1)
        
        # Check that performance metrics were recorded
        parsing_metrics = [m for m in performance_monitor.metrics if m.operation == "content_parsing"]
        assert len(parsing_metrics) > 0
        
        metric = parsing_metrics[0]
        assert metric.context["content_type"] == "genre_page"
        assert metric.context["items_parsed"] == len(genres)
    
    @pytest.mark.asyncio
    async def test_genre_mapper_integration(self, performance_monitor, mock_wiki_data_manager):
        """Test performance monitoring integration with EnhancedGenreMapper"""
        mapper = EnhancedGenreMapper(
            wiki_data_manager=mock_wiki_data_manager,
            performance_monitor=performance_monitor
        )
        
        traits = ["energetic", "modern", "danceable"]
        matches = await mapper.map_traits_to_genres(traits)
        
        # Check that performance metrics were recorded
        mapping_metrics = [m for m in performance_monitor.metrics if m.operation == "genre_mapping"]
        assert len(mapping_metrics) > 0
        
        metric = mapping_metrics[0]
        assert metric.context["traits_count"] == len(traits)
        assert metric.success == True

# ================================================================================================
# DECORATOR TESTS
# ================================================================================================

class TestPerformanceDecorators:
    """Tests for performance monitoring decorators"""
    
    @pytest.mark.asyncio
    async def test_async_function_decorator(self, performance_monitor):
        """Test performance decorator on async function"""
        @monitor_performance("test_async_function", performance_monitor)
        async def test_async_function(duration):
            await asyncio.sleep(duration)
            return "success"
        
        result = await test_async_function(0.1)
        assert result == "success"
        
        # Check that performance was monitored
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "test_async_function"
        assert metric.success == True
        assert metric.duration >= 0.1
    
    @pytest.mark.asyncio
    async def test_sync_function_decorator(self, performance_monitor):
        """Test performance decorator on sync function"""
        @monitor_performance("test_sync_function", performance_monitor)
        def test_sync_function(duration):
            time.sleep(duration)
            return "success"
        
        result = test_sync_function(0.05)
        assert result == "success"
        
        # Give async task time to complete
        await asyncio.sleep(0.1)
        
        # Check that performance was monitored
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "test_sync_function"
        assert metric.success == True
        assert metric.duration >= 0.05
    
    @pytest.mark.asyncio
    async def test_decorator_with_exception(self, performance_monitor):
        """Test performance decorator when function raises exception"""
        @monitor_performance("failing_function", performance_monitor)
        async def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await failing_function()
        
        # Check that failure was recorded
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.operation == "failing_function"
        assert metric.success == False

if __name__ == "__main__":
    pytest.main([__file__])