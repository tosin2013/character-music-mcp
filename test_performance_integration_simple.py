#!/usr/bin/env python3
"""
Simple Performance Monitoring Integration Test

This test verifies that performance monitoring is working correctly
with the wiki system components.
"""

import asyncio
import tempfile
import time
from datetime import datetime

from performance_monitor import PerformanceMonitor

async def test_performance_monitoring():
    """Test basic performance monitoring functionality"""
    print("Testing Performance Monitoring System...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize performance monitor
        monitor = PerformanceMonitor(storage_path=temp_dir)
        await monitor.initialize()
        print(f"✓ Performance monitor initialized: {monitor.initialized}")
        
        # Test operation measurement
        async with monitor.measure_operation("test_download", {"url": "https://example.com"}):
            await asyncio.sleep(0.1)  # Simulate download
        
        print(f"✓ Operation measured, metrics count: {len(monitor.metrics)}")
        
        # Test download metrics recording
        await monitor.record_download_metrics(
            url="https://sunoaiwiki.com/test",
            duration=2.5,
            success=True,
            file_size=1024000,
            status_code=200
        )
        print("✓ Download metrics recorded")
        
        # Test parsing metrics recording
        await monitor.record_parsing_metrics(
            content_type="genre_page",
            content_size=50000,
            duration=1.2,
            success=True,
            items_parsed=25
        )
        print("✓ Parsing metrics recorded")
        
        # Test generation metrics recording
        await monitor.record_generation_metrics(
            generation_type="album_creation",
            duration=5.0,
            success=True,
            wiki_data_used=True,
            fallback_used=False
        )
        print("✓ Generation metrics recorded")
        
        # Get performance reports
        download_report = monitor.get_download_performance_report()
        parsing_report = monitor.get_parsing_performance_report()
        generation_report = monitor.get_generation_performance_report()
        system_health = monitor.get_system_health_report()
        
        print(f"✓ Download report: {download_report['total_downloads']} downloads, {download_report['success_rate']:.1f}% success rate")
        print(f"✓ Parsing report: {len(parsing_report)} content types processed")
        print(f"✓ Generation report: {generation_report['total_generations']} generations")
        print(f"✓ System health: {system_health['health_status']}")
        
        # Generate comprehensive report
        comprehensive_report = await monitor.generate_comprehensive_report()
        print(f"✓ Comprehensive report generated for {comprehensive_report.report_period}")
        
        # Test operation statistics
        stats = monitor.get_operation_statistics()
        print(f"✓ Operation statistics: {len(stats)} operations tracked")
        
        # Save state
        await monitor.save_state()
        print("✓ State saved successfully")
        
        print(f"\nTotal metrics recorded: {len(monitor.metrics)}")
        print("Performance monitoring test completed successfully! ✅")

if __name__ == "__main__":
    asyncio.run(test_performance_monitoring())