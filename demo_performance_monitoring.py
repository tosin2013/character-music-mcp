#!/usr/bin/env python3
"""
Performance Monitoring Demo

This script demonstrates the performance monitoring system working
with the wiki data integration components.
"""

import asyncio
import tempfile
import time
from pathlib import Path

from performance_monitor import PerformanceMonitor
from wiki_content_parser import ContentParser


async def demo_performance_monitoring():
    """Demonstrate performance monitoring with wiki components"""
    print("🚀 Performance Monitoring Demo")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize performance monitor
        monitor = PerformanceMonitor(storage_path=temp_dir)
        await monitor.initialize()
        print("✅ Performance monitor initialized")

        # Demo 1: Content Parser with Performance Monitoring
        print("\n📊 Demo 1: Content Parser Performance Monitoring")
        parser = ContentParser(performance_monitor=monitor)

        sample_html = """
        <html>
            <body>
                <h3>Electronic Music</h3>
                <ul>
                    <li>House - Four-on-the-floor beats with synthesized basslines</li>
                    <li>Techno - Repetitive electronic beats with futuristic sounds</li>
                    <li>Ambient - Atmospheric electronic music for relaxation</li>
                    <li>Drum and Bass - Fast breakbeats with heavy bass</li>
                    <li>Dubstep - Syncopated drum patterns with prominent bass</li>
                </ul>
                <h3>Rock Music</h3>
                <ul>
                    <li>Classic Rock - Guitar-driven rock from the 60s-80s</li>
                    <li>Progressive Rock - Complex compositions and virtuosic playing</li>
                    <li>Alternative Rock - Non-mainstream rock with diverse influences</li>
                </ul>
            </body>
        </html>
        """

        # Parse content (this will record performance metrics)
        start_time = time.time()
        genres = parser.parse_genre_page(sample_html, "https://demo.com/genres")
        parse_duration = time.time() - start_time

        print(f"   Parsed {len(genres)} genres in {parse_duration:.3f} seconds")

        # Wait for async metrics recording to complete
        await asyncio.sleep(0.1)

        # Demo 2: Manual Performance Measurement
        print("\n⏱️  Demo 2: Manual Performance Measurement")

        async with monitor.measure_operation("demo_download", {"url": "https://sunoaiwiki.com/demo"}):
            print("   Simulating wiki page download...")
            await asyncio.sleep(0.5)  # Simulate download time
            print("   Download completed")

        # Record specific metrics
        await monitor.record_download_metrics(
            url="https://sunoaiwiki.com/genres",
            duration=1.2,
            success=True,
            file_size=45000,
            status_code=200
        )

        await monitor.record_parsing_metrics(
            content_type="meta_tag_page",
            content_size=30000,
            duration=0.8,
            success=True,
            items_parsed=50
        )

        await monitor.record_generation_metrics(
            generation_type="character_album",
            duration=3.5,
            success=True,
            wiki_data_used=True,
            fallback_used=False
        )

        print("   Manual metrics recorded")

        # Demo 3: Performance Reports
        print("\n📈 Demo 3: Performance Reports")

        # Download performance report
        download_report = monitor.get_download_performance_report()
        print("   Download Performance:")
        print(f"     - Total downloads: {download_report['total_downloads']}")
        print(f"     - Success rate: {download_report['success_rate']:.1f}%")
        print(f"     - Average duration: {download_report['average_duration_seconds']:.2f}s")
        print(f"     - Average speed: {download_report['average_download_speed_mbps']:.2f} MB/s")

        # Parsing performance report
        parsing_report = monitor.get_parsing_performance_report()
        print("   Parsing Performance:")
        for content_type, stats in parsing_report.items():
            if isinstance(stats, dict):
                print(f"     - {content_type}: {stats['total_operations']} ops, {stats['success_rate']:.1f}% success")
                print(f"       Average speed: {stats['average_parsing_speed_items_per_sec']:.1f} items/sec")

        # Generation performance report
        generation_report = monitor.get_generation_performance_report()
        print("   Generation Performance:")
        print(f"     - Total generations: {generation_report['total_generations']}")
        print(f"     - Overall success rate: {generation_report['overall_success_rate']:.1f}%")
        print(f"     - Wiki data usage: {generation_report['wiki_data_performance']['count']} operations")

        # System health report
        health_report = monitor.get_system_health_report()
        print(f"   System Health: {health_report['health_status'].upper()}")
        print(f"     - CPU: {health_report['current_metrics']['cpu_percent']:.1f}%")
        print(f"     - Memory: {health_report['current_metrics']['memory_percent']:.1f}%")

        # Demo 4: Operation Statistics
        print("\n📊 Demo 4: Operation Statistics")
        stats = monitor.get_operation_statistics()

        for operation, op_stats in stats.items():
            print(f"   {operation}:")
            print(f"     - Total calls: {op_stats['total_calls']}")
            print(f"     - Success rate: {op_stats['success_rate']:.1f}%")
            print(f"     - Average duration: {op_stats['average_duration']:.3f}s")
            if op_stats['max_duration'] > 0:
                print(f"     - Duration range: {op_stats['min_duration']:.3f}s - {op_stats['max_duration']:.3f}s")

        # Demo 5: Comprehensive Report
        print("\n📋 Demo 5: Comprehensive Performance Report")
        comprehensive_report = await monitor.generate_comprehensive_report()

        print(f"   Report Period: {comprehensive_report.report_period}")
        print(f"   System Status: {health_report['health_status'].upper()}")
        print(f"   Operations Tracked: {len(comprehensive_report.operation_stats)}")
        print(f"   Performance Alerts: {len(comprehensive_report.alerts)}")

        if comprehensive_report.alerts:
            print("   Active Alerts:")
            for alert in comprehensive_report.alerts:
                print(f"     - {alert}")

        if comprehensive_report.top_slowest_operations:
            print("   Slowest Operations:")
            for i, op in enumerate(comprehensive_report.top_slowest_operations[:3], 1):
                print(f"     {i}. {op['operation']}: {op['average_duration']:.3f}s avg")

        # Save performance data
        await monitor.save_state()

        # Save comprehensive report to file
        report_file = Path(temp_dir) / "performance_report.json"
        with open(report_file, 'w') as f:
            import json
            json.dump(comprehensive_report.to_dict(), f, indent=2)

        print(f"\n💾 Performance data saved to: {temp_dir}")
        print(f"📄 Comprehensive report saved to: {report_file}")

        print("\n🎉 Performance monitoring demo completed successfully!")
        print(f"Total metrics recorded: {len(monitor.metrics)}")

if __name__ == "__main__":
    asyncio.run(demo_performance_monitoring())
