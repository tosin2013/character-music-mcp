#!/usr/bin/env python3
"""
Source Attribution Manager

Manages source URL attribution for LLM context building, ensuring transparent
references to wiki content and proper tracking of content usage.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class ContentSource:
    """Represents a content source with metadata"""
    url: str
    content_type: str  # 'genre', 'meta_tag', 'technique', 'general'
    title: str
    download_date: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'url': self.url,
            'content_type': self.content_type,
            'title': self.title,
            'download_date': self.download_date.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentSource':
        """Create from dictionary"""
        return cls(
            url=data['url'],
            content_type=data['content_type'],
            title=data['title'],
            download_date=datetime.fromisoformat(data['download_date']),
            last_used=datetime.fromisoformat(data['last_used']) if data.get('last_used') else None,
            usage_count=data.get('usage_count', 0)
        )

@dataclass
class AttributedContent:
    """Content with source attribution metadata"""
    content: Any
    sources: List[ContentSource]
    attribution_text: str
    content_id: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'content': self.content if isinstance(self.content, (str, dict, list)) else str(self.content),
            'sources': [source.to_dict() for source in self.sources],
            'attribution_text': self.attribution_text,
            'content_id': self.content_id,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class UsageRecord:
    """Records content usage for tracking and analytics"""
    content_id: str
    source_url: str
    used_at: datetime
    context: str  # Description of how it was used
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'content_id': self.content_id,
            'source_url': self.source_url,
            'used_at': self.used_at.isoformat(),
            'context': self.context
        }

# ================================================================================================
# SOURCE ATTRIBUTION MANAGER
# ================================================================================================

class SourceAttributionManager:
    """Manages source URL attribution for LLM context building"""
    
    def __init__(self, storage_path: str = "./data/attribution"):
        self.storage_path = Path(storage_path)
        self.sources: Dict[str, ContentSource] = {}
        self.usage_records: List[UsageRecord] = []
        self.initialized = False
        
        # Attribution templates for different content types
        self.attribution_templates = {
            'genre': "Genre information sourced from: {sources}",
            'meta_tag': "Meta tag data sourced from: {sources}",
            'technique': "Technique information sourced from: {sources}",
            'general': "Information sourced from: {sources}",
            'mixed': "Information sourced from multiple wiki pages: {sources}"
        }
    
    async def initialize(self) -> None:
        """Initialize the attribution manager"""
        logger.info("Initializing SourceAttributionManager")
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing sources and usage records
        await self._load_sources()
        await self._load_usage_records()
        
        self.initialized = True
        logger.info("SourceAttributionManager initialized successfully")
    
    def build_attributed_context(self, content: Any, sources: List[str]) -> AttributedContent:
        """Build attributed content with source references
        
        Args:
            content: The content to attribute
            sources: List of source URLs
            
        Returns:
            AttributedContent with proper attribution
        """
        if not self.initialized:
            raise RuntimeError("SourceAttributionManager not initialized")
        
        # Convert URLs to ContentSource objects
        content_sources = []
        for url in sources:
            if url in self.sources:
                content_sources.append(self.sources[url])
            else:
                # Create a basic source entry if not found
                source = ContentSource(
                    url=url,
                    content_type='general',
                    title=self._extract_title_from_url(url),
                    download_date=datetime.now()
                )
                self.sources[url] = source
                content_sources.append(source)
        
        # Generate content ID
        content_id = self._generate_content_id(content, sources)
        
        # Format attribution text
        attribution_text = self.format_source_references(sources)
        
        # Create attributed content
        attributed_content = AttributedContent(
            content=content,
            sources=content_sources,
            attribution_text=attribution_text,
            content_id=content_id
        )
        
        return attributed_content
    
    def format_source_references(self, sources: List[str]) -> str:
        """Format source URLs for LLM context
        
        Args:
            sources: List of source URLs
            
        Returns:
            Formatted source reference string
        """
        if not sources:
            return ""
        
        # Determine content type for appropriate template
        content_types = set()
        for url in sources:
            if url in self.sources:
                content_types.add(self.sources[url].content_type)
        
        # Choose appropriate template
        if len(content_types) == 1:
            template_key = list(content_types)[0]
        else:
            template_key = 'mixed'
        
        template = self.attribution_templates.get(template_key, self.attribution_templates['general'])
        
        # Format sources for display
        formatted_sources = []
        for url in sources:
            if url in self.sources:
                source = self.sources[url]
                formatted_sources.append(f"{source.title} ({url})")
            else:
                formatted_sources.append(url)
        
        return template.format(sources=", ".join(formatted_sources))
    
    def track_content_usage(self, content_id: str, source_url: str, context: str = "") -> None:
        """Track usage of attributed content
        
        Args:
            content_id: ID of the content being used
            source_url: URL of the source being used
            context: Description of how the content is being used
        """
        if not self.initialized:
            logger.warning("SourceAttributionManager not initialized, skipping usage tracking")
            return
        
        # Update source usage statistics
        if source_url in self.sources:
            source = self.sources[source_url]
            source.usage_count += 1
            source.last_used = datetime.now()
        
        # Record usage
        usage_record = UsageRecord(
            content_id=content_id,
            source_url=source_url,
            used_at=datetime.now(),
            context=context
        )
        self.usage_records.append(usage_record)
        
        logger.debug(f"Tracked usage of content {content_id} from {source_url}")
    
    def register_source(self, url: str, content_type: str, title: str, download_date: datetime) -> None:
        """Register a new content source
        
        Args:
            url: Source URL
            content_type: Type of content ('genre', 'meta_tag', 'technique', 'general')
            title: Human-readable title
            download_date: When the content was downloaded
        """
        source = ContentSource(
            url=url,
            content_type=content_type,
            title=title,
            download_date=download_date
        )
        self.sources[url] = source
        logger.debug(f"Registered source: {title} ({url})")
    
    def get_source_urls(self, content_type: Optional[str] = None) -> List[str]:
        """Get source URLs, optionally filtered by content type
        
        Args:
            content_type: Optional content type filter
            
        Returns:
            List of source URLs
        """
        if content_type:
            return [url for url, source in self.sources.items() 
                   if source.content_type == content_type]
        return list(self.sources.keys())
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all sources
        
        Returns:
            Dictionary with usage statistics
        """
        stats = {
            'total_sources': len(self.sources),
            'total_usage_records': len(self.usage_records),
            'sources_by_type': {},
            'most_used_sources': [],
            'recent_usage': []
        }
        
        # Count sources by type
        for source in self.sources.values():
            content_type = source.content_type
            if content_type not in stats['sources_by_type']:
                stats['sources_by_type'][content_type] = 0
            stats['sources_by_type'][content_type] += 1
        
        # Most used sources
        sorted_sources = sorted(self.sources.values(), 
                              key=lambda s: s.usage_count, reverse=True)
        stats['most_used_sources'] = [
            {'url': s.url, 'title': s.title, 'usage_count': s.usage_count}
            for s in sorted_sources[:10]
        ]
        
        # Recent usage
        recent_usage = sorted(self.usage_records, 
                            key=lambda r: r.used_at, reverse=True)
        stats['recent_usage'] = [
            {'content_id': r.content_id, 'source_url': r.source_url, 
             'used_at': r.used_at.isoformat(), 'context': r.context}
            for r in recent_usage[:20]
        ]
        
        return stats
    
    async def save_state(self) -> None:
        """Save current state to disk"""
        if not self.initialized:
            return
        
        # Save sources
        sources_file = self.storage_path / "sources.json"
        sources_data = {url: source.to_dict() for url, source in self.sources.items()}
        with open(sources_file, 'w') as f:
            json.dump(sources_data, f, indent=2)
        
        # Save usage records
        usage_file = self.storage_path / "usage_records.json"
        usage_data = [record.to_dict() for record in self.usage_records]
        with open(usage_file, 'w') as f:
            json.dump(usage_data, f, indent=2)
        
        logger.debug("Saved attribution state to disk")
    
    async def _load_sources(self) -> None:
        """Load sources from disk"""
        sources_file = self.storage_path / "sources.json"
        if sources_file.exists():
            try:
                with open(sources_file, 'r') as f:
                    sources_data = json.load(f)
                
                for url, data in sources_data.items():
                    self.sources[url] = ContentSource.from_dict(data)
                
                logger.debug(f"Loaded {len(self.sources)} sources from disk")
            except Exception as e:
                logger.warning(f"Failed to load sources: {e}")
    
    async def _load_usage_records(self) -> None:
        """Load usage records from disk"""
        usage_file = self.storage_path / "usage_records.json"
        if usage_file.exists():
            try:
                with open(usage_file, 'r') as f:
                    usage_data = json.load(f)
                
                for record_data in usage_data:
                    record = UsageRecord(
                        content_id=record_data['content_id'],
                        source_url=record_data['source_url'],
                        used_at=datetime.fromisoformat(record_data['used_at']),
                        context=record_data['context']
                    )
                    self.usage_records.append(record)
                
                logger.debug(f"Loaded {len(self.usage_records)} usage records from disk")
            except Exception as e:
                logger.warning(f"Failed to load usage records: {e}")
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a human-readable title from URL"""
        # Simple title extraction from URL path
        try:
            path_parts = url.rstrip('/').split('/')
            if path_parts:
                title = path_parts[-1]
                # Clean up common URL patterns
                title = title.replace('-', ' ').replace('_', ' ')
                title = title.replace('.html', '').replace('.php', '')
                return title.title()
        except Exception:
            pass
        
        return url
    
    def _generate_content_id(self, content: Any, sources: List[str]) -> str:
        """Generate a unique content ID"""
        import hashlib
        
        # Create a hash from content and sources
        content_str = str(content)[:1000]  # Limit content length for hashing
        sources_str = "|".join(sorted(sources))
        combined = f"{content_str}|{sources_str}"
        
        return hashlib.md5(combined.encode()).hexdigest()[:16]