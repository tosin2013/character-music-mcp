#!/usr/bin/env python3
"""
Wiki Data Models

Data models for wiki integration system to avoid circular imports.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class Genre:
    """Genre data model from wiki"""
    name: str
    description: str
    subgenres: List[str] = field(default_factory=list)
    characteristics: List[str] = field(default_factory=list)
    typical_instruments: List[str] = field(default_factory=list)
    mood_associations: List[str] = field(default_factory=list)
    source_url: str = ""
    download_date: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['download_date'] = self.download_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genre':
        """Create Genre from dictionary"""
        if 'download_date' in data and isinstance(data['download_date'], str):
            data['download_date'] = datetime.fromisoformat(data['download_date'])
        return cls(**data)

@dataclass
class MetaTag:
    """Meta tag data model from wiki"""
    tag: str
    category: str  # structural, emotional, instrumental, vocal, etc.
    description: str
    usage_examples: List[str] = field(default_factory=list)
    compatible_genres: List[str] = field(default_factory=list)
    source_url: str = ""
    download_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['download_date'] = self.download_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetaTag':
        """Create MetaTag from dictionary"""
        if 'download_date' in data and isinstance(data['download_date'], str):
            data['download_date'] = datetime.fromisoformat(data['download_date'])
        return cls(**data)

@dataclass
class Technique:
    """Technique data model from wiki tip pages"""
    name: str
    description: str
    technique_type: str  # prompt_structure, vocal_style, production, etc.
    examples: List[str] = field(default_factory=list)
    applicable_scenarios: List[str] = field(default_factory=list)
    source_url: str = ""
    download_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['download_date'] = self.download_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Technique':
        """Create Technique from dictionary"""
        if 'download_date' in data and isinstance(data['download_date'], str):
            data['download_date'] = datetime.fromisoformat(data['download_date'])
        return cls(**data)

@dataclass
class WikiConfig:
    """Configuration for wiki data integration system"""
    enabled: bool = True
    local_storage_path: str = "./data/wiki"
    refresh_interval_hours: int = 24
    fallback_to_hardcoded: bool = True
    
    genre_pages: List[str] = field(default_factory=lambda: [
        "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
    ])
    
    meta_tag_pages: List[str] = field(default_factory=lambda: [
        "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"
    ])
    
    tip_pages: List[str] = field(default_factory=lambda: [
        "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/",
        "https://sunoaiwiki.com/tips/2024-04-16-how-to-make-suno-ai-sing-with-spoken-word/",
        "https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/",
        "https://sunoaiwiki.com/tips/2024-05-04-how-to-use-meta-tags-in-suno-ai-for-song-creation/",
        "https://sunoaiwiki.com/tips/2024-05-07-how-to-get-specific-vocal-styles-in-suno-ai/",
        "https://sunoaiwiki.com/tips/2024-05-08-how-to-bypass-explicit-lyric-restrictions/",
        "https://sunoaiwiki.com/tips/2024-05-09-how-to-end-a-song-naturally/",
        "https://sunoaiwiki.com/tips/2024-05-18-how-to-optimize-prompts-in-suno-ai-with-letter-case/",
        "https://sunoaiwiki.com/tips/2024-05-22-how-to-prompt-suno-ai-to-use-animal-sounds-and-noises/",
        "https://sunoaiwiki.com/tips/2024-05-22-how-to-solve-suno-ai-sampling-detection-issues/",
        "https://sunoaiwiki.com/tips/2024-05-25-how-to-handle-producer-tags-in-suno-ai/",
        "https://sunoaiwiki.com/tips/2024-07-08-how-to-create-better-lyrics-for-suno/",
        "https://sunoaiwiki.com/tips/2024-07-08-improve-suno-hiphop-rap-trap/"
    ])
    
    # HTTP client settings
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WikiConfig':
        """Create WikiConfig from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate paths
        if not self.local_storage_path:
            errors.append("local_storage_path cannot be empty")
        
        # Validate intervals
        if self.refresh_interval_hours < 1:
            errors.append("refresh_interval_hours must be at least 1")
        
        if self.request_timeout < 1:
            errors.append("request_timeout must be at least 1")
        
        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")
        
        if self.retry_delay < 0:
            errors.append("retry_delay cannot be negative")
        
        # Validate URLs
        all_urls = self.genre_pages + self.meta_tag_pages + self.tip_pages
        for url in all_urls:
            if not self._is_valid_url(url):
                errors.append(f"Invalid URL: {url}")
        
        return errors
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

@dataclass
class RefreshResult:
    """Result of data refresh operation"""
    success: bool
    pages_downloaded: int
    pages_failed: int
    errors: List[str] = field(default_factory=list)
    refresh_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['refresh_time'] = self.refresh_time.isoformat()
        return data