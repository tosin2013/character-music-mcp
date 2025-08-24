#!/usr/bin/env python3
"""
Demonstration of the configuration management and validation system.

This script shows how to:
1. Validate wiki configurations
2. Use dynamic configuration management
3. Handle runtime configuration updates
4. Integrate with WikiDataManager
"""

import asyncio
import tempfile
import json
from pathlib import Path

from wiki_data_system import WikiDataManager, WikiConfig
from wiki_config_validator import validate_config_full, validate_config_quick
from dynamic_config_manager import DynamicConfigManager


async def demo_basic_validation():
    """Demonstrate basic configuration validation"""
    print("=== Basic Configuration Validation ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid configuration
        valid_config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=24,
            genre_pages=["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"],
            meta_tag_pages=["https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"]
        )
        
        print("Validating valid configuration...")
        result = await validate_config_quick(valid_config)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.errors}")
        print(f"Warnings: {result.warnings}")
        print(f"Storage info: {result.storage_info}")
        
        # Create an invalid configuration
        invalid_config = WikiConfig(
            enabled=True,
            local_storage_path="",  # Invalid - empty path
            refresh_interval_hours=-1,  # Invalid - negative
            request_timeout=0,  # Invalid - zero timeout
            genre_pages=["not-a-url"]  # Invalid URL format
        )
        
        print("\nValidating invalid configuration...")
        result = await validate_config_quick(invalid_config)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.errors}")
        print(f"Warnings: {result.warnings}")


async def demo_dynamic_configuration():
    """Demonstrate dynamic configuration management"""
    print("\n=== Dynamic Configuration Management ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.json"
        
        # Create initial configuration
        initial_config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=24,
            genre_pages=["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"]
        )
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(initial_config.to_dict(), f, indent=2)
        
        print(f"Created configuration file: {config_file}")
        
        # Create dynamic config manager
        async with DynamicConfigManager(str(config_file)) as manager:
            print(f"Initial refresh interval: {manager.get_current_config().refresh_interval_hours}")
            
            # Update settings at runtime
            print("Updating refresh interval to 48 hours...")
            result = await manager.update_settings(refresh_interval_hours=48)
            print(f"Update successful: {result.is_valid}")
            print(f"New refresh interval: {manager.get_current_config().refresh_interval_hours}")
            
            # Add URLs at runtime
            print("Adding new genre page URL...")
            result = await manager.add_urls(
                "genre_pages",
                ["https://example.com/new-genre-page"],
                validate_urls=False
            )
            print(f"URL addition successful: {result.is_valid}")
            print(f"Genre pages: {manager.get_current_config().genre_pages}")
            
            # Remove URLs at runtime
            print("Removing the new URL...")
            result = await manager.remove_urls(
                "genre_pages",
                ["https://example.com/new-genre-page"]
            )
            print(f"URL removal successful: {result.is_valid}")
            print(f"Genre pages: {manager.get_current_config().genre_pages}")


async def demo_wiki_data_manager_integration():
    """Demonstrate integration with WikiDataManager"""
    print("\n=== WikiDataManager Integration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.json"
        
        # Create configuration
        config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=24
        )
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        # Initialize WikiDataManager
        manager = WikiDataManager()
        await manager.initialize(config)
        print("WikiDataManager initialized")
        
        # Enable dynamic configuration
        await manager.enable_dynamic_config(str(config_file))
        print("Dynamic configuration enabled")
        
        # Get status
        status = manager.get_dynamic_config_status()
        print(f"Dynamic config status: {status}")
        
        # Update configuration at runtime
        print("Updating refresh interval via WikiDataManager...")
        success = await manager.update_config_runtime(refresh_interval_hours=72)
        print(f"Update successful: {success}")
        print(f"New refresh interval: {manager.config.refresh_interval_hours}")
        
        # Add URLs at runtime
        print("Adding URLs via WikiDataManager...")
        success = await manager.add_wiki_urls_runtime(
            "tip_pages",
            ["https://example.com/new-tip"],
            validate_urls=False
        )
        print(f"URL addition successful: {success}")
        print(f"Tip pages: {manager.config.tip_pages}")
        
        # Disable dynamic configuration
        manager.disable_dynamic_config()
        print("Dynamic configuration disabled")
        
        status = manager.get_dynamic_config_status()
        print(f"Final status: {status}")


async def demo_url_validation():
    """Demonstrate URL accessibility validation"""
    print("\n=== URL Accessibility Validation ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration with mix of accessible and inaccessible URLs
        config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=24,
            genre_pages=[
                "https://httpbin.org/status/200",  # Should be accessible
                "https://httpbin.org/status/404",  # Should return 404
                "https://invalid-domain-that-does-not-exist.com"  # Should be inaccessible
            ]
        )
        
        print("Performing full validation with URL checks...")
        result = await validate_config_full(config, timeout=5)
        
        print(f"Overall valid: {result.is_valid}")
        print(f"Errors: {result.errors}")
        print(f"Warnings: {result.warnings}")
        print("URL accessibility results:")
        for url, accessible in result.url_checks.items():
            status = "✓ Accessible" if accessible else "✗ Not accessible"
            print(f"  {url}: {status}")


async def main():
    """Run all demonstrations"""
    print("Configuration Management and Validation System Demo")
    print("=" * 60)
    
    try:
        await demo_basic_validation()
        await demo_dynamic_configuration()
        await demo_wiki_data_manager_integration()
        await demo_url_validation()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())