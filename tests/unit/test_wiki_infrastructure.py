#!/usr/bin/env python3
"""
Unit tests for wiki data system infrastructure
"""

import sys
import os
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from wiki_data_system import (
    WikiConfig, WikiDataManager, ConfigurationManager,
    Genre, MetaTag, Technique, RefreshResult
)

class TestWikiConfig:
    """Test WikiConfig data model"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = WikiConfig()
        assert config.enabled == True
        assert config.refresh_interval_hours == 24
        assert config.fallback_to_hardcoded == True
        assert len(config.genre_pages) > 0
        assert len(config.meta_tag_pages) > 0
        assert len(config.tip_pages) > 0
    
    def test_config_validation_valid(self):
        """Test validation of valid configuration"""
        config = WikiConfig()
        errors = config.validate()
        assert len(errors) == 0
    
    def test_config_validation_invalid(self):
        """Test validation of invalid configuration"""
        config = WikiConfig(
            refresh_interval_hours=-1,
            request_timeout=0,
            max_retries=-1,
            local_storage_path=""
        )
        errors = config.validate()
        assert len(errors) > 0
        assert any("refresh_interval_hours" in error for error in errors)
        assert any("request_timeout" in error for error in errors)
        assert any("max_retries" in error for error in errors)
        assert any("local_storage_path" in error for error in errors)
    
    def test_config_serialization(self):
        """Test configuration serialization and deserialization"""
        original = WikiConfig(enabled=False, refresh_interval_hours=48)
        config_dict = original.to_dict()
        restored = WikiConfig.from_dict(config_dict)
        
        assert restored.enabled == original.enabled
        assert restored.refresh_interval_hours == original.refresh_interval_hours
        assert restored.local_storage_path == original.local_storage_path

class TestDataModels:
    """Test data models"""
    
    def test_genre_model(self):
        """Test Genre data model"""
        genre = Genre(
            name="Jazz",
            description="A music genre that originated in the African-American communities",
            subgenres=["Bebop", "Cool Jazz"],
            characteristics=["Improvisation", "Swing"],
            source_url="https://example.com"
        )
        
        # Test serialization
        genre_dict = genre.to_dict()
        assert genre_dict['name'] == "Jazz"
        assert isinstance(genre_dict['download_date'], str)
        
        # Test deserialization
        restored = Genre.from_dict(genre_dict)
        assert restored.name == genre.name
        assert isinstance(restored.download_date, datetime)
    
    def test_meta_tag_model(self):
        """Test MetaTag data model"""
        tag = MetaTag(
            tag="upbeat",
            category="emotional",
            description="Creates an uplifting mood",
            usage_examples=["[upbeat]", "[upbeat, energetic]"],
            source_url="https://example.com"
        )
        
        # Test serialization
        tag_dict = tag.to_dict()
        assert tag_dict['tag'] == "upbeat"
        assert tag_dict['category'] == "emotional"
        
        # Test deserialization
        restored = MetaTag.from_dict(tag_dict)
        assert restored.tag == tag.tag
        assert restored.category == tag.category
    
    def test_technique_model(self):
        """Test Technique data model"""
        technique = Technique(
            name="Prompt Structure",
            description="How to structure prompts effectively",
            technique_type="prompt_structure",
            examples=["[verse] lyrics here", "[chorus] lyrics here"],
            source_url="https://example.com"
        )
        
        # Test serialization
        tech_dict = technique.to_dict()
        assert tech_dict['name'] == "Prompt Structure"
        assert tech_dict['technique_type'] == "prompt_structure"
        
        # Test deserialization
        restored = Technique.from_dict(tech_dict)
        assert restored.name == technique.name
        assert restored.technique_type == technique.technique_type

class TestConfigurationManager:
    """Test ConfigurationManager"""
    
    @pytest.mark.asyncio
    async def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            
            # Create and save config
            original_config = WikiConfig(enabled=False, refresh_interval_hours=48)
            await ConfigurationManager.save_config(original_config, str(config_path))
            
            # Verify file exists
            assert config_path.exists()
            
            # Load and verify
            loaded_config = await ConfigurationManager.load_config(str(config_path))
            assert loaded_config.enabled == False
            assert loaded_config.refresh_interval_hours == 48
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_config(self):
        """Test loading non-existent configuration returns default"""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_path = Path(temp_dir) / "non_existent.json"
            config = await ConfigurationManager.load_config(str(non_existent_path))
            
            # Should return default config
            assert config.enabled == True
            assert config.refresh_interval_hours == 24

class TestWikiDataManager:
    """Test WikiDataManager"""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test WikiDataManager initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=True,
                local_storage_path=str(Path(temp_dir) / "wiki_data")
            )
            
            manager = WikiDataManager()
            await manager.initialize(config)
            
            try:
                assert manager.initialized == True
                assert manager.storage_path.exists()
                
                # Check directory structure
                expected_dirs = ["genres", "meta_tags", "techniques", "cache"]
                for dir_name in expected_dirs:
                    dir_path = manager.storage_path / dir_name
                    assert dir_path.exists()
                
            finally:
                await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_disabled_initialization(self):
        """Test initialization with disabled wiki system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=False,
                local_storage_path=str(Path(temp_dir) / "wiki_data")
            )
            
            manager = WikiDataManager()
            await manager.initialize(config)
            
            try:
                assert manager.initialized == True
                assert manager._session is None  # No HTTP session when disabled
                
            finally:
                await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_invalid_config_initialization(self):
        """Test initialization with invalid configuration"""
        invalid_config = WikiConfig(refresh_interval_hours=-1)
        
        manager = WikiDataManager()
        with pytest.raises(ValueError):
            await manager.initialize(invalid_config)
    
    @pytest.mark.asyncio
    async def test_get_empty_data(self):
        """Test getting data when no cache exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=False,  # Disabled to avoid network calls
                local_storage_path=str(Path(temp_dir) / "wiki_data")
            )
            
            manager = WikiDataManager()
            await manager.initialize(config)
            
            try:
                genres = await manager.get_genres()
                meta_tags = await manager.get_meta_tags()
                techniques = await manager.get_techniques()
                
                assert isinstance(genres, list)
                assert isinstance(meta_tags, list)
                assert isinstance(techniques, list)
                assert len(genres) == 0  # No data cached yet
                assert len(meta_tags) == 0
                assert len(techniques) == 0
                
            finally:
                await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_source_urls(self):
        """Test getting source URLs"""
        config = WikiConfig()
        manager = WikiDataManager()
        await manager.initialize(config)
        
        try:
            genre_urls = manager.get_source_urls("genres")
            meta_tag_urls = manager.get_source_urls("meta_tags")
            technique_urls = manager.get_source_urls("techniques")
            invalid_urls = manager.get_source_urls("invalid")
            
            assert len(genre_urls) > 0
            assert len(meta_tag_urls) > 0
            assert len(technique_urls) > 0
            assert len(invalid_urls) == 0
            
        finally:
            await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_refresh_disabled_system(self):
        """Test refresh on disabled system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=False,
                local_storage_path=str(Path(temp_dir) / "wiki_data")
            )
            
            manager = WikiDataManager()
            await manager.initialize(config)
            
            try:
                result = await manager.refresh_data()
                assert result.success == True
                assert result.pages_downloaded == 0
                assert result.pages_failed == 0
                
            finally:
                await manager.cleanup()