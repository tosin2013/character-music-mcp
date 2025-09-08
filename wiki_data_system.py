#!/usr/bin/env python3
"""
Wiki Data System for Dynamic Suno Data Integration

This module provides the core infrastructure for downloading, caching, and managing
wiki data from Suno AI Wiki to enhance music generation capabilities.
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import aiohttp
import aiofiles

from wiki_data_models import WikiConfig, Genre, MetaTag, Technique, RefreshResult
from wiki_downloader import WikiDownloader
from wiki_cache_manager import WikiCacheManager
from wiki_content_parser import ContentParser

# Configure logging
logger = logging.getLogger(__name__)



# ================================================================================================
# WIKI DATA MANAGER
# ================================================================================================

class WikiDataManager:
    """Central coordinator for all wiki data operations"""
    
    def __init__(self):
        self.config: Optional[WikiConfig] = None
        self.storage_path: Optional[Path] = None
        self.initialized: bool = False
        
        # Dynamic configuration management
        self.dynamic_config_manager: Optional['DynamicConfigManager'] = None
        
        # New components
        self.cache_manager: Optional[WikiCacheManager] = None
        self.downloader: Optional[WikiDownloader] = None
        self.parser: Optional[ContentParser] = None
        
        # Data caches
        self._genres: List[Genre] = []
        self._meta_tags: List[MetaTag] = []
        self._techniques: List[Technique] = []
        
        # Cache timestamps
        self._last_refresh: Optional[datetime] = None
        self._cache_valid: bool = False
    
    async def initialize(self, config: WikiConfig) -> None:
        """Initialize the wiki data manager with configuration"""
        logger.info("Initializing WikiDataManager")
        
        # Validate configuration
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        self.config = config
        
        # Set up storage directory
        self.storage_path = Path(config.local_storage_path)
        await self._setup_storage_structure()
        
        # Initialize cache manager and downloader if enabled
        if config.enabled:
            self.cache_manager = WikiCacheManager(config.local_storage_path)
            await self.cache_manager.initialize()
            
            self.downloader = WikiDownloader(
                cache_manager=self.cache_manager,
                request_timeout=config.request_timeout,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay
            )
            
            # Initialize content parser
            self.parser = ContentParser()
        
        # Load existing data from local storage
        await self._load_cached_data()
        
        self.initialized = True
        logger.info(f"WikiDataManager initialized with storage at {self.storage_path}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.downloader:
            await self.downloader.cleanup()
            self.downloader = None
        self.cache_manager = None

    async def clear_cache(self) -> None:
        """Clear all cached data"""
        self._genres = []
        self._meta_tags = []
        self._techniques = []
        self._cache_valid = False
        logger.info("Cache cleared")

    async def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'genres_cached': len(self._genres),
            'meta_tags_cached': len(self._meta_tags),
            'techniques_cached': len(self._techniques),
            'cache_valid': self._cache_valid
        }
    
    async def get_genres(self) -> List[Genre]:
        """Get list of genres from wiki data"""
        if not self.initialized:
            raise RuntimeError("WikiDataManager not initialized")
        
        # Check if refresh is needed
        if self._should_refresh():
            await self.refresh_data()
        
        return self._genres.copy()
    
    async def get_meta_tags(self, category: str = None) -> List[MetaTag]:
        """Get list of meta tags, optionally filtered by category"""
        if not self.initialized:
            raise RuntimeError("WikiDataManager not initialized")
        
        # Check if refresh is needed
        if self._should_refresh():
            await self.refresh_data()
        
        if category:
            return [tag for tag in self._meta_tags if tag.category.lower() == category.lower()]
        return self._meta_tags.copy()
    
    async def get_techniques(self, technique_type: str = None) -> List[Technique]:
        """Get list of techniques, optionally filtered by type"""
        if not self.initialized:
            raise RuntimeError("WikiDataManager not initialized")
        
        # Check if refresh is needed
        if self._should_refresh():
            await self.refresh_data()
        
        if technique_type:
            return [tech for tech in self._techniques if tech.technique_type.lower() == technique_type.lower()]
        return self._techniques.copy()
    
    async def refresh_data(self, force: bool = False) -> RefreshResult:
        """Refresh wiki data from remote sources"""
        if not self.initialized:
            raise RuntimeError("WikiDataManager not initialized")
        
        if not self.config.enabled:
            logger.info("Wiki data integration disabled, skipping refresh")
            return RefreshResult(success=True, pages_downloaded=0, pages_failed=0)
        
        if not force and not self._should_refresh():
            logger.info("Data is still fresh, skipping refresh")
            return RefreshResult(success=True, pages_downloaded=0, pages_failed=0)
        
        logger.info("Starting wiki data refresh")
        
        if not self.downloader:
            logger.error("Downloader not initialized")
            return RefreshResult(
                success=False,
                pages_downloaded=0,
                pages_failed=0,
                errors=["Downloader not initialized"]
            )
        
        # Collect all URLs to download
        all_urls = (
            self.config.genre_pages + 
            self.config.meta_tag_pages + 
            self.config.tip_pages
        )
        
        # Use the new batch download functionality
        async with self.downloader:
            batch_result = await self.downloader.download_with_retry_logic(
                all_urls,
                max_age_hours=self.config.refresh_interval_hours,
                max_concurrent=3,  # Conservative concurrent limit
                max_batch_retries=2
            )
        
        # Parse downloaded HTML files and save as JSON
        await self._parse_and_cache_data()
        
        # Reload cached data after parsing
        await self._load_cached_data()
        
        self._last_refresh = datetime.now()
        self._cache_valid = True
        
        # Convert batch result to refresh result
        errors = [result.error_message for result in batch_result.results 
                 if not result.success and result.error_message]
        
        result = RefreshResult(
            success=batch_result.failed_downloads == 0,
            pages_downloaded=batch_result.successful_downloads,
            pages_failed=batch_result.failed_downloads,
            errors=errors
        )
        
        logger.info(f"Wiki data refresh completed: {batch_result.successful_downloads} downloaded, "
                   f"{batch_result.failed_downloads} failed, {batch_result.skipped_downloads} skipped")
        return result
    
    async def _parse_and_cache_data(self) -> None:
        """Parse downloaded HTML files and cache as structured data"""
        if not self.parser or not self.cache_manager:
            logger.error("Parser or cache manager not initialized")
            return
        
        # Get all cached files
        cached_urls = await self.cache_manager.list_cached_urls()
        cached_files = []
        for url in cached_urls:
            entry = await self.cache_manager.get_cache_entry(url)
            if entry:
                cached_files.append(entry)
        
        # Parse genres
        genres = []
        for file_info in cached_files:
            if any(genre_url in file_info.url for genre_url in self.config.genre_pages):
                try:
                    async with aiofiles.open(file_info.local_path, 'r', encoding='utf-8') as f:
                        html_content = await f.read()
                    
                    parsed_genres = self.parser.parse_genre_page(html_content)
                    for genre in parsed_genres:
                        genre.source_url = file_info.url
                        genre.download_date = file_info.download_date
                    genres.extend(parsed_genres)
                    logger.info(f"Parsed {len(parsed_genres)} genres from {file_info.url}")
                except Exception as e:
                    logger.error(f"Error parsing genre file {file_info.local_path}: {e}")
        
        # Parse meta tags
        meta_tags = []
        for file_info in cached_files:
            if any(meta_url in file_info.url for meta_url in self.config.meta_tag_pages):
                try:
                    async with aiofiles.open(file_info.local_path, 'r', encoding='utf-8') as f:
                        html_content = await f.read()
                    
                    parsed_tags = self.parser.parse_meta_tag_page(html_content)
                    for tag in parsed_tags:
                        tag.source_url = file_info.url
                        tag.download_date = file_info.download_date
                    meta_tags.extend(parsed_tags)
                    logger.info(f"Parsed {len(parsed_tags)} meta tags from {file_info.url}")
                except Exception as e:
                    logger.error(f"Error parsing meta tag file {file_info.local_path}: {e}")
        
        # Parse techniques
        techniques = []
        for file_info in cached_files:
            if any(tip_url in file_info.url for tip_url in self.config.tip_pages):
                try:
                    async with aiofiles.open(file_info.local_path, 'r', encoding='utf-8') as f:
                        html_content = await f.read()
                    
                    parsed_techniques = self.parser.parse_tip_page(html_content)
                    for technique in parsed_techniques:
                        technique.source_url = file_info.url
                        technique.download_date = file_info.download_date
                    techniques.extend(parsed_techniques)
                    logger.info(f"Parsed {len(parsed_techniques)} techniques from {file_info.url}")
                except Exception as e:
                    logger.error(f"Error parsing tip file {file_info.local_path}: {e}")
        
        # Save parsed data to JSON cache files
        cache_dir = self.storage_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        # Save genres
        if genres:
            genres_file = cache_dir / "genres.json"
            try:
                genres_data = [genre.to_dict() for genre in genres]
                async with aiofiles.open(genres_file, 'w') as f:
                    await f.write(json.dumps(genres_data, indent=2))
                logger.info(f"Saved {len(genres)} genres to cache")
            except Exception as e:
                logger.error(f"Error saving genres cache: {e}")
        
        # Save meta tags
        if meta_tags:
            meta_tags_file = cache_dir / "meta_tags.json"
            try:
                meta_tags_data = [tag.to_dict() for tag in meta_tags]
                async with aiofiles.open(meta_tags_file, 'w') as f:
                    await f.write(json.dumps(meta_tags_data, indent=2))
                logger.info(f"Saved {len(meta_tags)} meta tags to cache")
            except Exception as e:
                logger.error(f"Error saving meta tags cache: {e}")
        
        # Save techniques
        if techniques:
            techniques_file = cache_dir / "techniques.json"
            try:
                techniques_data = [technique.to_dict() for technique in techniques]
                async with aiofiles.open(techniques_file, 'w') as f:
                    await f.write(json.dumps(techniques_data, indent=2))
                logger.info(f"Saved {len(techniques)} techniques to cache")
            except Exception as e:
                logger.error(f"Error saving techniques cache: {e}")

    def get_source_urls(self, data_type: str) -> List[str]:
        """Get source URLs for a specific data type"""
        if not self.config:
            return []
        
        data_type_lower = data_type.lower()
        if data_type_lower == "genres":
            return self.config.genre_pages.copy()
        elif data_type_lower == "meta_tags":
            return self.config.meta_tag_pages.copy()
        elif data_type_lower == "techniques":
            return self.config.tip_pages.copy()
        elif data_type_lower == "all":
            # Return all URLs
            return (self.config.genre_pages + 
                   self.config.meta_tag_pages + 
                   self.config.tip_pages)
        else:
            return []
    
    # Private methods
    
    async def _setup_storage_structure(self) -> None:
        """Set up local storage directory structure"""
        if not self.storage_path:
            return
        
        # Create main directories
        directories = [
            self.storage_path,
            self.storage_path / "genres",
            self.storage_path / "meta_tags", 
            self.storage_path / "techniques",
            self.storage_path / "cache"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storage structure created at {self.storage_path}")
    
    async def _load_cached_data(self) -> None:
        """Load existing data from local storage"""
        if not self.storage_path:
            return
        
        # Load cached data files
        cache_dir = self.storage_path / "cache"
        
        # Load genres
        genres_file = cache_dir / "genres.json"
        if genres_file.exists():
            try:
                async with aiofiles.open(genres_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self._genres = [Genre.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self._genres)} genres from cache")
            except Exception as e:
                logger.error(f"Error loading genres cache: {e}")
                self._genres = []
        
        # Load meta tags
        meta_tags_file = cache_dir / "meta_tags.json"
        if meta_tags_file.exists():
            try:
                async with aiofiles.open(meta_tags_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self._meta_tags = [MetaTag.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self._meta_tags)} meta tags from cache")
            except Exception as e:
                logger.error(f"Error loading meta tags cache: {e}")
                self._meta_tags = []
        
        # Load techniques
        techniques_file = cache_dir / "techniques.json"
        if techniques_file.exists():
            try:
                async with aiofiles.open(techniques_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self._techniques = [Technique.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self._techniques)} techniques from cache")
            except Exception as e:
                logger.error(f"Error loading techniques cache: {e}")
                self._techniques = []
        
        # Check if we have any data
        if self._genres or self._meta_tags or self._techniques:
            self._cache_valid = True
    
    def _should_refresh(self) -> bool:
        """Check if data should be refreshed"""
        if not self.config or not self.config.enabled:
            return False
        
        if not self._cache_valid:
            return True
        
        if not self._last_refresh:
            return True
        
        refresh_interval = timedelta(hours=self.config.refresh_interval_hours)
        return datetime.now() - self._last_refresh > refresh_interval
    
    async def enable_dynamic_config(self, config_path: Optional[str] = None) -> None:
        """
        Enable dynamic configuration management with file watching
        
        Args:
            config_path: Optional path to configuration file
        """
        try:
            # Import here to avoid circular imports
            from dynamic_config_manager import DynamicConfigManager
            
            self.dynamic_config_manager = DynamicConfigManager(config_path)
            await self.dynamic_config_manager.initialize()
            
            # Add callback for configuration changes
            self.dynamic_config_manager.add_change_callback(self._handle_config_change)
            
            # Start file watching
            self.dynamic_config_manager.start_watching()
            
            logger.info("Dynamic configuration management enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable dynamic configuration: {e}")
            raise
    
    def disable_dynamic_config(self) -> None:
        """Disable dynamic configuration management"""
        if self.dynamic_config_manager:
            self.dynamic_config_manager.stop_watching()
            self.dynamic_config_manager = None
            logger.info("Dynamic configuration management disabled")
    
    async def _handle_config_change(self, old_config: WikiConfig, new_config: WikiConfig) -> None:
        """
        Handle configuration changes from dynamic config manager
        
        Args:
            old_config: Previous configuration
            new_config: New configuration
        """
        logger.info("Handling configuration change in WikiDataManager")
        
        try:
            # Update our configuration
            self.config = new_config
            
            # Check if storage path changed
            if old_config.local_storage_path != new_config.local_storage_path:
                logger.info("Storage path changed, reinitializing storage")
                self.storage_path = Path(new_config.local_storage_path)
                await self._setup_storage_structure()
            
            # Check if URLs changed
            old_urls = set(old_config.genre_pages + old_config.meta_tag_pages + old_config.tip_pages)
            new_urls = set(new_config.genre_pages + new_config.meta_tag_pages + new_config.tip_pages)
            
            if old_urls != new_urls:
                logger.info("Wiki URLs changed, invalidating cache")
                self._cache_valid = False
            
            # Reinitialize components with new config
            if self.cache_manager:
                self.cache_manager = WikiCacheManager(self.storage_path)
            
            if self.downloader:
                self.downloader = WikiDownloader(
                    cache_manager=self.cache_manager,
                    request_timeout=new_config.request_timeout,
                    max_retries=new_config.max_retries,
                    retry_delay=new_config.retry_delay
                )
            
            logger.info("Configuration change handled successfully")
            
        except Exception as e:
            logger.error(f"Error handling configuration change: {e}")
    
    async def update_config_runtime(self, **settings) -> bool:
        """
        Update configuration settings at runtime
        
        Args:
            **settings: Configuration settings to update
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self.dynamic_config_manager:
            logger.error("Dynamic configuration not enabled")
            return False
        
        try:
            result = await self.dynamic_config_manager.update_settings(**settings)
            return result.is_valid
        except Exception as e:
            logger.error(f"Error updating configuration at runtime: {e}")
            return False
    
    async def add_wiki_urls_runtime(self, url_type: str, urls: List[str], validate_urls: bool = True) -> bool:
        """
        Add wiki URLs at runtime
        
        Args:
            url_type: Type of URLs ('genre_pages', 'meta_tag_pages', 'tip_pages')
            urls: List of URLs to add
            validate_urls: Whether to validate URL accessibility
            
        Returns:
            True if addition was successful, False otherwise
        """
        if not self.dynamic_config_manager:
            logger.error("Dynamic configuration not enabled")
            return False
        
        try:
            result = await self.dynamic_config_manager.add_urls(url_type, urls, validate_urls)
            return result.is_valid
        except Exception as e:
            logger.error(f"Error adding URLs at runtime: {e}")
            return False
    
    async def remove_wiki_urls_runtime(self, url_type: str, urls: List[str]) -> bool:
        """
        Remove wiki URLs at runtime
        
        Args:
            url_type: Type of URLs ('genre_pages', 'meta_tag_pages', 'tip_pages')
            urls: List of URLs to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if not self.dynamic_config_manager:
            logger.error("Dynamic configuration not enabled")
            return False
        
        try:
            result = await self.dynamic_config_manager.remove_urls(url_type, urls)
            return result.is_valid
        except Exception as e:
            logger.error(f"Error removing URLs at runtime: {e}")
            return False
    
    def get_dynamic_config_status(self) -> Dict[str, Any]:
        """
        Get status of dynamic configuration management
        
        Returns:
            Dictionary with status information
        """
        if not self.dynamic_config_manager:
            return {
                'enabled': False,
                'watching': False,
                'last_validation': None
            }
        
        return {
            'enabled': True,
            'watching': self.dynamic_config_manager.is_watching(),
            'last_validation': self.dynamic_config_manager.get_last_validation_result(),
            'config_file': str(self.dynamic_config_manager.config_file)
        }


# ================================================================================================
# CONFIGURATION MANAGEMENT
# ================================================================================================

class ConfigurationManager:
    """Manages wiki configuration loading and validation"""
    
    DEFAULT_CONFIG_PATH = "./config/wiki_config.json"
    
    @classmethod
    async def load_config(cls, config_path: Optional[str] = None) -> WikiConfig:
        """Load configuration from file or create default"""
        path = Path(config_path or cls.DEFAULT_CONFIG_PATH)
        
        if path.exists():
            try:
                async with aiofiles.open(path, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    config = WikiConfig.from_dict(data)
                    logger.info(f"Loaded wiki configuration from {path}")
                    return config
            except Exception as e:
                logger.error(f"Error loading config from {path}: {e}")
                logger.info("Using default configuration")
        
        # Return default configuration
        return WikiConfig()
    
    @classmethod
    async def save_config(cls, config: WikiConfig, config_path: Optional[str] = None) -> None:
        """Save configuration to file"""
        path = Path(config_path or cls.DEFAULT_CONFIG_PATH)
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(path, 'w') as f:
                content = json.dumps(config.to_dict(), indent=2)
                await f.write(content)
            logger.info(f"Saved wiki configuration to {path}")
        except Exception as e:
            logger.error(f"Error saving config to {path}: {e}")
            raise
    
    def _get_fallback_genres(self) -> List[Genre]:
        """Get fallback genres when wiki data is unavailable"""
        fallback_genres = [
            Genre(
                name="Rock",
                description="A broad genre of popular music characterized by amplified instruments and strong rhythms",
                subgenres=["Alternative Rock", "Classic Rock", "Hard Rock", "Punk Rock"],
                characteristics=["electric guitars", "drums", "bass", "strong vocals"],
                typical_instruments=["electric guitar", "drums", "bass guitar"],
                mood_associations=["energetic", "rebellious", "powerful"],
                source_url="hardcoded_fallback",
                confidence_score=0.8
            ),
            Genre(
                name="Pop",
                description="Popular music characterized by catchy melodies and broad appeal",
                subgenres=["Dance Pop", "Synth Pop", "Teen Pop"],
                characteristics=["catchy hooks", "verse-chorus structure", "electronic production"],
                typical_instruments=["synthesizers", "drums", "vocals"],
                mood_associations=["upbeat", "fun", "romantic"],
                source_url="hardcoded_fallback",
                confidence_score=0.9
            ),
            Genre(
                name="Hip Hop",
                description="Music genre consisting of stylized rhythmic music accompanied by rapping",
                subgenres=["Trap", "Drill", "Conscious Hip Hop"],
                characteristics=["beats", "rapping", "sampling"],
                typical_instruments=["drum machine", "sampler", "turntables"],
                mood_associations=["confident", "streetwise", "expressive"],
                source_url="hardcoded_fallback",
                confidence_score=0.85
            )
        ]
        return fallback_genres

    def _get_fallback_meta_tags(self) -> List[MetaTag]:
        """Get fallback meta tags when wiki data is unavailable"""
        fallback_tags = [
            MetaTag(
                tag="verse",
                description="Section of a song typically featuring lyrics and melody",
                category="structure",
                source_url="hardcoded_fallback"
            ),
            MetaTag(
                tag="chorus",
                description="Repeated section of a song with the main hook",
                category="structure",
                source_url="hardcoded_fallback"
            ),
            MetaTag(
                tag="bridge",
                description="Contrasting section that prepares for the return of original material",
                category="structure",
                source_url="hardcoded_fallback"
            ),
            MetaTag(
                tag="intro",
                description="Opening section of a song",
                category="structure",
                source_url="hardcoded_fallback"
            ),
            MetaTag(
                tag="outro",
                description="Closing section of a song",
                category="structure",
                source_url="hardcoded_fallback"
            )
        ]
        return fallback_tags

    def _get_fallback_techniques(self) -> List[Technique]:
        """Get fallback techniques when wiki data is unavailable"""
        fallback_techniques = [
            Technique(
                name="Layering",
                description="Adding multiple instrumental or vocal tracks to create depth",
                technique_type="production",
                difficulty="intermediate",
                source_url="hardcoded_fallback"
            ),
            Technique(
                name="Compression",
                description="Reducing dynamic range to make audio more consistent",
                technique_type="mixing",
                difficulty="advanced",
                source_url="hardcoded_fallback"
            ),
            Technique(
                name="Sampling",
                description="Using portions of existing recordings in new compositions",
                technique_type="production",
                difficulty="beginner",
                source_url="hardcoded_fallback"
            ),
            Technique(
                name="EQ",
                description="Adjusting frequency balance of audio signals",
                technique_type="mixing",
                difficulty="intermediate",
                source_url="hardcoded_fallback"
            ),
            Technique(
                name="Reverb",
                description="Adding artificial space and depth to sounds",
                technique_type="effects",
                difficulty="beginner",
                source_url="hardcoded_fallback"
            )
        ]
        return fallback_techniques

    @classmethod
    def validate_config(cls, config: WikiConfig) -> List[str]:
        """Validate configuration and return errors"""
        return config.validate()