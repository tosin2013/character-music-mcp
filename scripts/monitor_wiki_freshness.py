#!/usr/bin/env python3
"""
Wiki Data Freshness Monitoring Script

This script monitors the freshness of wiki data and provides alerts
when data becomes stale or when refresh operations fail.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from wiki_data_models import WikiConfig
from wiki_data_system import WikiDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WikiFreshnessMonitor:
    """Monitor wiki data freshness and health"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = WikiConfig()
        self.wiki_manager = None
        self.alerts = []

    async def initialize(self):
        """Initialize the wiki data manager"""
        try:
            self.wiki_manager = WikiDataManager()
            await self.wiki_manager.initialize(self.config)
            logger.info("Wiki data manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize wiki data manager: {e}")
            self.alerts.append(f"CRITICAL: Wiki data manager initialization failed: {e}")
            return False

    async def check_data_freshness(self) -> Dict[str, any]:
        """Check the freshness of all wiki data"""
        freshness_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'categories': {},
            'alerts': [],
            'recommendations': []
        }

        if not self.wiki_manager:
            freshness_report['overall_status'] = 'critical'
            freshness_report['alerts'].append('Wiki data manager not available')
            return freshness_report

        # Check each data category
        categories = ['genres', 'meta_tags', 'techniques']

        for category in categories:
            category_status = await self._check_category_freshness(category)
            freshness_report['categories'][category] = category_status

            if category_status['status'] == 'stale':
                freshness_report['alerts'].append(
                    f"{category.title()} data is stale (last updated: {category_status['last_updated']})"
                )
            elif category_status['status'] == 'missing':
                freshness_report['alerts'].append(f"{category.title()} data is missing")
                freshness_report['overall_status'] = 'degraded'

        # Determine overall status
        if any(cat['status'] == 'missing' for cat in freshness_report['categories'].values()):
            freshness_report['overall_status'] = 'degraded'
        elif any(cat['status'] == 'stale' for cat in freshness_report['categories'].values()):
            freshness_report['overall_status'] = 'warning'

        # Add recommendations
        if freshness_report['overall_status'] != 'healthy':
            freshness_report['recommendations'].append('Consider running manual wiki data refresh')

        return freshness_report

    async def _check_category_freshness(self, category: str) -> Dict[str, any]:
        """Check freshness of a specific data category"""
        try:
            if category == 'genres':
                data = await self.wiki_manager.get_genres()
            elif category == 'meta_tags':
                data = await self.wiki_manager.get_meta_tags()
            elif category == 'techniques':
                data = await self.wiki_manager.get_techniques()
            else:
                return {'status': 'unknown', 'error': f'Unknown category: {category}'}

            if not data:
                return {
                    'status': 'missing',
                    'count': 0,
                    'last_updated': None,
                    'age_hours': None
                }

            # Get the most recent update time from the data
            last_updated = None
            if hasattr(data[0], 'download_date') and data[0].download_date:
                last_updated = data[0].download_date
                for item in data:
                    if hasattr(item, 'download_date') and item.download_date:
                        if item.download_date > last_updated:
                            last_updated = item.download_date

            if last_updated:
                age_hours = (datetime.now() - last_updated).total_seconds() / 3600
                status = 'healthy'

                # Check if data is stale based on refresh interval
                if age_hours > (self.config.refresh_interval_hours * 1.5):
                    status = 'stale'

                return {
                    'status': status,
                    'count': len(data),
                    'last_updated': last_updated.isoformat(),
                    'age_hours': round(age_hours, 2)
                }
            else:
                return {
                    'status': 'unknown',
                    'count': len(data),
                    'last_updated': None,
                    'age_hours': None,
                    'note': 'No timestamp information available'
                }

        except Exception as e:
            logger.error(f"Error checking {category} freshness: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'count': 0
            }

    async def check_wiki_connectivity(self) -> Dict[str, any]:
        """Check connectivity to wiki sources"""
        connectivity_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'sources': {},
            'alerts': []
        }

        # Collect all configured URLs
        all_urls = []
        all_urls.extend(self.config.genre_pages)
        all_urls.extend(self.config.meta_tag_pages)
        all_urls.extend(self.config.tip_pages)

        for url in all_urls:
            source_status = await self._check_url_connectivity(url)
            connectivity_report['sources'][url] = source_status

            if source_status['status'] != 'accessible':
                connectivity_report['alerts'].append(
                    f"Source not accessible: {url} ({source_status.get('error', 'Unknown error')})"
                )
                connectivity_report['overall_status'] = 'degraded'

        return connectivity_report

    async def _check_url_connectivity(self, url: str) -> Dict[str, any]:
        """Check if a specific URL is accessible"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=10) as response:
                    return {
                        'status': 'accessible' if response.status == 200 else 'error',
                        'status_code': response.status,
                        'response_time_ms': None  # Could add timing if needed
                    }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def perform_health_check(self) -> Dict[str, any]:
        """Perform comprehensive health check"""
        logger.info("Starting comprehensive wiki health check...")

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        # Check data freshness
        logger.info("Checking data freshness...")
        freshness_report = await self.check_data_freshness()
        health_report['checks']['data_freshness'] = freshness_report

        # Check connectivity
        logger.info("Checking wiki connectivity...")
        connectivity_report = await self.check_wiki_connectivity()
        health_report['checks']['connectivity'] = connectivity_report

        # Check local storage
        logger.info("Checking local storage...")
        storage_report = self._check_local_storage()
        health_report['checks']['storage'] = storage_report

        # Determine overall status
        statuses = [
            freshness_report['overall_status'],
            connectivity_report['overall_status'],
            storage_report['status']
        ]

        if 'critical' in statuses:
            health_report['overall_status'] = 'critical'
        elif 'degraded' in statuses:
            health_report['overall_status'] = 'degraded'
        elif 'warning' in statuses:
            health_report['overall_status'] = 'warning'

        # Collect all alerts
        all_alerts = []
        all_alerts.extend(freshness_report.get('alerts', []))
        all_alerts.extend(connectivity_report.get('alerts', []))
        all_alerts.extend(storage_report.get('alerts', []))

        health_report['alerts'] = all_alerts

        logger.info(f"Health check complete. Overall status: {health_report['overall_status']}")

        return health_report

    def _check_local_storage(self) -> Dict[str, any]:
        """Check local storage health"""
        storage_path = Path(self.config.local_storage_path)

        try:
            if not storage_path.exists():
                return {
                    'status': 'critical',
                    'alerts': ['Storage directory does not exist'],
                    'path': str(storage_path)
                }

            if not storage_path.is_dir():
                return {
                    'status': 'critical',
                    'alerts': ['Storage path is not a directory'],
                    'path': str(storage_path)
                }

            # Check permissions
            test_file = storage_path / '.write_test'
            try:
                test_file.write_text('test')
                test_file.unlink()
            except Exception as e:
                return {
                    'status': 'critical',
                    'alerts': [f'Storage directory not writable: {e}'],
                    'path': str(storage_path)
                }

            # Check disk usage
            import shutil
            total, used, free = shutil.disk_usage(storage_path)

            # Calculate storage directory size
            dir_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())

            storage_report = {
                'status': 'healthy',
                'path': str(storage_path),
                'directory_size_mb': round(dir_size / (1024 * 1024), 2),
                'free_space_mb': round(free / (1024 * 1024), 2),
                'alerts': []
            }

            # Check if running low on space
            if free < (100 * 1024 * 1024):  # Less than 100MB free
                storage_report['status'] = 'warning'
                storage_report['alerts'].append('Low disk space (< 100MB free)')

            # Check if cache is getting too large
            if dir_size > (1024 * 1024 * 1024):  # More than 1GB
                storage_report['status'] = 'warning'
                storage_report['alerts'].append('Wiki cache is large (> 1GB)')

            return storage_report

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'path': str(storage_path)
            }

    async def force_refresh(self) -> Dict[str, any]:
        """Force a refresh of all wiki data"""
        logger.info("Starting forced wiki data refresh...")

        if not self.wiki_manager:
            return {
                'status': 'error',
                'error': 'Wiki data manager not available'
            }

        try:
            refresh_result = await self.wiki_manager.refresh_data(force=True)

            logger.info("Forced refresh completed successfully")
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'refresh_result': refresh_result
            }

        except Exception as e:
            logger.error(f"Forced refresh failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

async def main():
    """Main monitoring function"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor wiki data freshness')
    parser.add_argument('--check', action='store_true', help='Perform health check')
    parser.add_argument('--refresh', action='store_true', help='Force data refresh')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--alert-threshold', type=int, default=48,
                       help='Alert threshold in hours (default: 48)')

    args = parser.parse_args()

    monitor = WikiFreshnessMonitor()

    if not await monitor.initialize():
        print("Failed to initialize monitor")
        sys.exit(1)

    if args.refresh:
        result = await monitor.force_refresh()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Refresh {result['status']}")
            if result['status'] == 'error':
                print(f"Error: {result['error']}")
        sys.exit(0 if result['status'] == 'success' else 1)

    if args.check:
        health_report = await monitor.perform_health_check()

        if args.json:
            print(json.dumps(health_report, indent=2))
        else:
            print(f"Overall Status: {health_report['overall_status'].upper()}")

            if health_report['alerts']:
                print("\nAlerts:")
                for alert in health_report['alerts']:
                    print(f"  - {alert}")

            print("\nData Freshness:")
            for category, status in health_report['checks']['data_freshness']['categories'].items():
                print(f"  {category}: {status['status']} ({status['count']} items)")
                if status.get('age_hours'):
                    print(f"    Last updated: {status['age_hours']:.1f} hours ago")

        # Exit with appropriate code
        if health_report['overall_status'] in ['critical', 'degraded']:
            sys.exit(1)
        elif health_report['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)

    # Default: just check freshness
    freshness_report = await monitor.check_data_freshness()

    if args.json:
        print(json.dumps(freshness_report, indent=2))
    else:
        print(f"Data Freshness: {freshness_report['overall_status'].upper()}")

        for category, status in freshness_report['categories'].items():
            print(f"  {category}: {status['status']} ({status['count']} items)")
            if status.get('age_hours'):
                print(f"    Age: {status['age_hours']:.1f} hours")

if __name__ == "__main__":
    asyncio.run(main())
