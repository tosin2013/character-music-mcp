#!/usr/bin/env python3
"""
Graceful Degradation System for Dynamic Suno Data Integration

This module provides graceful degradation mechanisms that ensure the system
continues to function even when wiki data is unavailable or partially corrupted.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Tuple

from error_recovery_manager import DataSource, ErrorRecoveryManager
from wiki_data_system import Genre, MetaTag, Technique, WikiDataManager

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment"""
    total_items: int
    wiki_items: int
    cached_items: int
    fallback_items: int
    quality_score: float
    freshness_score: float
    completeness_score: float
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def wiki_ratio(self) -> float:
        """Ratio of wiki items to total items"""
        return self.wiki_items / self.total_items if self.total_items > 0 else 0.0

    @property
    def overall_score(self) -> float:
        """Overall data quality score"""
        return (self.quality_score * 0.4 +
                self.freshness_score * 0.3 +
                self.completeness_score * 0.3)

@dataclass
class DegradationLevel:
    """Represents the current degradation level of the system"""
    level: int  # 0 = full functionality, 5 = maximum degradation
    description: str
    active_fallbacks: List[str]
    affected_features: List[str]
    estimated_quality: float

    def is_degraded(self) -> bool:
        """Check if system is in degraded state"""
        return self.level > 0

# ================================================================================================
# GRACEFUL DEGRADATION SYSTEM
# ================================================================================================

class GracefulDegradationSystem:
    """Manages graceful degradation of wiki data integration system"""

    def __init__(self, wiki_data_manager: WikiDataManager,
                 error_recovery_manager: ErrorRecoveryManager):
        self.wiki_data_manager = wiki_data_manager
        self.error_recovery_manager = error_recovery_manager
        self.current_degradation = DegradationLevel(0, "Full functionality", [], [], 1.0)
        self.data_quality_cache: Dict[str, DataQualityMetrics] = {}
        self.fallback_strategies: Dict[str, List[str]] = {}
        self.initialized = False

        # Setup fallback strategies
        self._setup_fallback_strategies()

    async def initialize(self) -> None:
        """Initialize the graceful degradation system"""
        logger.info("Initializing GracefulDegradationSystem")

        # Ensure dependencies are initialized
        if not self.error_recovery_manager.initialized:
            await self.error_recovery_manager.initialize()

        # Assess initial system state
        await self._assess_system_state()

        self.initialized = True
        logger.info(f"GracefulDegradationSystem initialized (degradation level: {self.current_degradation.level})")

    async def get_genres_with_fallback(self, max_age_hours: int = 24) -> Tuple[List[Genre], DataQualityMetrics]:
        """
        Get genres with graceful fallback to cached and hardcoded data

        Args:
            max_age_hours: Maximum age for cached data

        Returns:
            Tuple of (genres_list, quality_metrics)
        """
        logger.debug("Getting genres with fallback support")

        wiki_genres = []
        cached_genres = []
        fallback_genres = []

        # Try to get fresh wiki data
        try:
            wiki_genres = await self.wiki_data_manager.get_genres()
            logger.info(f"Retrieved {len(wiki_genres)} genres from wiki")
        except Exception as e:
            logger.warning(f"Failed to get wiki genres: {e}")

            # Handle the failure through error recovery
            recovery_result = await self.error_recovery_manager.handle_download_failure(
                "genres", e, {"operation": "get_genres"}
            )

            if recovery_result.success and recovery_result.data:
                if recovery_result.source == DataSource.WIKI_CACHED:
                    cached_genres = recovery_result.data
                elif recovery_result.source == DataSource.HARDCODED_FALLBACK:
                    fallback_genres = recovery_result.data

        # If we have no wiki data, try to get cached data
        if not wiki_genres and not cached_genres:
            cached_genres = await self._get_cached_genres(max_age_hours)

        # If we still have no data, use hardcoded fallbacks
        if not wiki_genres and not cached_genres:
            fallback_data = self.error_recovery_manager.get_fallback_data('genres')
            if fallback_data:
                fallback_genres = self._convert_to_genre_objects(fallback_data.data)

        # Combine data sources intelligently
        combined_genres, quality_metrics = self._combine_genre_sources(
            wiki_genres, cached_genres, fallback_genres
        )

        # Update degradation level based on data quality
        await self._update_degradation_level('genres', quality_metrics)

        logger.info(f"Returning {len(combined_genres)} genres (quality: {quality_metrics.overall_score:.2f})")
        return combined_genres, quality_metrics

    async def get_meta_tags_with_fallback(self, category: str = None,
                                        max_age_hours: int = 24) -> Tuple[List[MetaTag], DataQualityMetrics]:
        """
        Get meta tags with graceful fallback to cached and hardcoded data

        Args:
            category: Optional category filter
            max_age_hours: Maximum age for cached data

        Returns:
            Tuple of (meta_tags_list, quality_metrics)
        """
        logger.debug(f"Getting meta tags with fallback support (category: {category})")

        wiki_meta_tags = []
        cached_meta_tags = []
        fallback_meta_tags = []

        # Try to get fresh wiki data
        try:
            wiki_meta_tags = await self.wiki_data_manager.get_meta_tags(category)
            logger.info(f"Retrieved {len(wiki_meta_tags)} meta tags from wiki")
        except Exception as e:
            logger.warning(f"Failed to get wiki meta tags: {e}")

            # Handle the failure through error recovery
            recovery_result = await self.error_recovery_manager.handle_download_failure(
                "meta_tags", e, {"operation": "get_meta_tags", "category": category}
            )

            if recovery_result.success and recovery_result.data:
                if recovery_result.source == DataSource.WIKI_CACHED:
                    cached_meta_tags = recovery_result.data
                elif recovery_result.source == DataSource.HARDCODED_FALLBACK:
                    fallback_meta_tags = recovery_result.data

        # If we have no wiki data, try to get cached data
        if not wiki_meta_tags and not cached_meta_tags:
            cached_meta_tags = await self._get_cached_meta_tags(category, max_age_hours)

        # If we still have no data, use hardcoded fallbacks
        if not wiki_meta_tags and not cached_meta_tags:
            fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
            if fallback_data:
                fallback_meta_tags = self._convert_to_meta_tag_objects(fallback_data.data)

                # Filter by category if specified
                if category:
                    fallback_meta_tags = [tag for tag in fallback_meta_tags
                                        if tag.category.lower() == category.lower()]

        # Combine data sources intelligently
        combined_meta_tags, quality_metrics = self._combine_meta_tag_sources(
            wiki_meta_tags, cached_meta_tags, fallback_meta_tags
        )

        # Update degradation level based on data quality
        await self._update_degradation_level('meta_tags', quality_metrics)

        logger.info(f"Returning {len(combined_meta_tags)} meta tags (quality: {quality_metrics.overall_score:.2f})")
        return combined_meta_tags, quality_metrics

    async def get_techniques_with_fallback(self, technique_type: str = None,
                                         max_age_hours: int = 24) -> Tuple[List[Technique], DataQualityMetrics]:
        """
        Get techniques with graceful fallback to cached and hardcoded data

        Args:
            technique_type: Optional technique type filter
            max_age_hours: Maximum age for cached data

        Returns:
            Tuple of (techniques_list, quality_metrics)
        """
        logger.debug(f"Getting techniques with fallback support (type: {technique_type})")

        wiki_techniques = []
        cached_techniques = []
        fallback_techniques = []

        # Try to get fresh wiki data
        try:
            wiki_techniques = await self.wiki_data_manager.get_techniques(technique_type)
            logger.info(f"Retrieved {len(wiki_techniques)} techniques from wiki")
        except Exception as e:
            logger.warning(f"Failed to get wiki techniques: {e}")

            # Handle the failure through error recovery
            recovery_result = await self.error_recovery_manager.handle_download_failure(
                "techniques", e, {"operation": "get_techniques", "technique_type": technique_type}
            )

            if recovery_result.success and recovery_result.data:
                if recovery_result.source == DataSource.WIKI_CACHED:
                    cached_techniques = recovery_result.data
                elif recovery_result.source == DataSource.HARDCODED_FALLBACK:
                    fallback_techniques = recovery_result.data

        # If we have no wiki data, try to get cached data
        if not wiki_techniques and not cached_techniques:
            cached_techniques = await self._get_cached_techniques(technique_type, max_age_hours)

        # If we still have no data, use hardcoded fallbacks
        if not wiki_techniques and not cached_techniques:
            fallback_data = self.error_recovery_manager.get_fallback_data('techniques')
            if fallback_data:
                fallback_techniques = self._convert_to_technique_objects(fallback_data.data)

        # Combine data sources intelligently
        combined_techniques, quality_metrics = self._combine_technique_sources(
            wiki_techniques, cached_techniques, fallback_techniques
        )

        # Update degradation level based on data quality
        await self._update_degradation_level('techniques', quality_metrics)

        logger.info(f"Returning {len(combined_techniques)} techniques (quality: {quality_metrics.overall_score:.2f})")
        return combined_techniques, quality_metrics

    async def handle_partial_data_failure(self, data_type: str, partial_data: Any,
                                        error: Exception) -> Tuple[Any, DataQualityMetrics]:
        """
        Handle partial data failure by mixing partial data with fallbacks

        Args:
            data_type: Type of data ('genres', 'meta_tags', 'techniques')
            partial_data: Partially recovered data
            error: Original error that caused partial failure

        Returns:
            Tuple of (combined_data, quality_metrics)
        """
        logger.info(f"Handling partial data failure for {data_type}")

        # Get fallback data
        fallback_data = self.error_recovery_manager.get_fallback_data(data_type)

        if not fallback_data:
            # No fallback available, return partial data with low quality score
            quality_metrics = DataQualityMetrics(
                total_items=len(partial_data) if partial_data else 0,
                wiki_items=len(partial_data) if partial_data else 0,
                cached_items=0,
                fallback_items=0,
                quality_score=0.3,  # Low quality due to partial failure
                freshness_score=0.5,
                completeness_score=0.2
            )
            return partial_data, quality_metrics

        # Combine partial data with fallback data
        if data_type == 'genres':
            combined_data, quality_metrics = self._combine_genre_sources(
                partial_data or [], [], self._convert_to_genre_objects(fallback_data.data)
            )
        elif data_type == 'meta_tags':
            combined_data, quality_metrics = self._combine_meta_tag_sources(
                partial_data or [], [], self._convert_to_meta_tag_objects(fallback_data.data)
            )
        elif data_type == 'techniques':
            combined_data, quality_metrics = self._combine_technique_sources(
                partial_data or [], [], self._convert_to_technique_objects(fallback_data.data)
            )
        else:
            # Unknown data type, return partial data
            quality_metrics = DataQualityMetrics(
                total_items=len(partial_data) if partial_data else 0,
                wiki_items=len(partial_data) if partial_data else 0,
                cached_items=0,
                fallback_items=0,
                quality_score=0.3,
                freshness_score=0.5,
                completeness_score=0.2
            )
            combined_data = partial_data

        # Update degradation level
        await self._update_degradation_level(data_type, quality_metrics)

        logger.info(f"Combined partial {data_type} data with fallbacks (quality: {quality_metrics.overall_score:.2f})")
        return combined_data, quality_metrics

    def get_current_degradation_status(self) -> DegradationLevel:
        """Get current system degradation status"""
        return self.current_degradation

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive data quality report"""
        report = {
            'degradation_level': self.current_degradation.level,
            'degradation_description': self.current_degradation.description,
            'overall_quality': self.current_degradation.estimated_quality,
            'active_fallbacks': self.current_degradation.active_fallbacks,
            'affected_features': self.current_degradation.affected_features,
            'data_sources': {}
        }

        # Add quality metrics for each data type
        for data_type, metrics in self.data_quality_cache.items():
            report['data_sources'][data_type] = {
                'total_items': metrics.total_items,
                'wiki_ratio': metrics.wiki_ratio,
                'quality_score': metrics.quality_score,
                'freshness_score': metrics.freshness_score,
                'completeness_score': metrics.completeness_score,
                'overall_score': metrics.overall_score,
                'last_updated': metrics.last_updated.isoformat()
            }

        return report

    # Private methods

    async def _assess_system_state(self) -> None:
        """Assess current system state and set initial degradation level"""
        degradation_factors = []

        # Test wiki data availability
        try:
            genres = await self.wiki_data_manager.get_genres()
            if not genres:
                degradation_factors.append("No wiki genres available")
        except Exception as e:
            degradation_factors.append(f"Wiki genres unavailable: {str(e)[:100]}")

        try:
            meta_tags = await self.wiki_data_manager.get_meta_tags()
            if not meta_tags:
                degradation_factors.append("No wiki meta tags available")
        except Exception as e:
            degradation_factors.append(f"Wiki meta tags unavailable: {str(e)[:100]}")

        try:
            techniques = await self.wiki_data_manager.get_techniques()
            if not techniques:
                degradation_factors.append("No wiki techniques available")
        except Exception as e:
            degradation_factors.append(f"Wiki techniques unavailable: {str(e)[:100]}")

        # Determine initial degradation level
        degradation_level = min(len(degradation_factors), 5)

        if degradation_level == 0:
            description = "Full functionality - all wiki data available"
            estimated_quality = 1.0
        elif degradation_level == 1:
            description = "Minor degradation - one data source unavailable"
            estimated_quality = 0.8
        elif degradation_level == 2:
            description = "Moderate degradation - two data sources unavailable"
            estimated_quality = 0.6
        elif degradation_level == 3:
            description = "Significant degradation - all wiki data unavailable"
            estimated_quality = 0.4
        else:
            description = "Maximum degradation - system running on fallbacks only"
            estimated_quality = 0.3

        self.current_degradation = DegradationLevel(
            level=degradation_level,
            description=description,
            active_fallbacks=degradation_factors,
            affected_features=self._get_affected_features(degradation_level),
            estimated_quality=estimated_quality
        )

    def _get_affected_features(self, degradation_level: int) -> List[str]:
        """Get list of features affected by degradation level"""
        if degradation_level == 0:
            return []
        elif degradation_level == 1:
            return ["Reduced genre variety or meta tag options"]
        elif degradation_level == 2:
            return ["Limited genre mapping", "Reduced meta tag variety"]
        elif degradation_level == 3:
            return ["Basic genre mapping only", "Limited meta tags", "No advanced techniques"]
        else:
            return ["Minimal functionality", "Hardcoded data only", "No wiki-based features"]

    async def _update_degradation_level(self, data_type: str, quality_metrics: DataQualityMetrics) -> None:
        """Update system degradation level based on data quality"""
        self.data_quality_cache[data_type] = quality_metrics

        # Calculate overall system quality
        if self.data_quality_cache:
            avg_quality = sum(m.overall_score for m in self.data_quality_cache.values()) / len(self.data_quality_cache)

            # Update degradation level based on average quality
            if avg_quality >= 0.9:
                new_level = 0
                description = "Full functionality"
            elif avg_quality >= 0.7:
                new_level = 1
                description = "Minor degradation"
            elif avg_quality >= 0.5:
                new_level = 2
                description = "Moderate degradation"
            elif avg_quality >= 0.3:
                new_level = 3
                description = "Significant degradation"
            else:
                new_level = 4
                description = "Maximum degradation"

            # Update if degradation level changed
            if new_level != self.current_degradation.level:
                active_fallbacks = [f"{dt}: {m.wiki_ratio:.1%} wiki data"
                                  for dt, m in self.data_quality_cache.items()]

                self.current_degradation = DegradationLevel(
                    level=new_level,
                    description=description,
                    active_fallbacks=active_fallbacks,
                    affected_features=self._get_affected_features(new_level),
                    estimated_quality=avg_quality
                )

                logger.info(f"Degradation level updated to {new_level}: {description}")

    def _combine_genre_sources(self, wiki_genres: List[Genre], cached_genres: List[Genre],
                             fallback_genres: List[Genre]) -> Tuple[List[Genre], DataQualityMetrics]:
        """Combine genre data from multiple sources"""
        combined = []
        seen_names = set()

        # Add wiki genres first (highest priority)
        for genre in wiki_genres:
            if genre.name.lower() not in seen_names:
                combined.append(genre)
                seen_names.add(genre.name.lower())

        # Add cached genres that aren't in wiki data
        for genre in cached_genres:
            if genre.name.lower() not in seen_names:
                combined.append(genre)
                seen_names.add(genre.name.lower())

        # Add fallback genres that aren't in other sources
        for genre in fallback_genres:
            if genre.name.lower() not in seen_names:
                combined.append(genre)
                seen_names.add(genre.name.lower())

        # Calculate quality metrics
        quality_metrics = DataQualityMetrics(
            total_items=len(combined),
            wiki_items=len(wiki_genres),
            cached_items=len(cached_genres),
            fallback_items=len(fallback_genres),
            quality_score=self._calculate_quality_score(len(wiki_genres), len(cached_genres), len(fallback_genres)),
            freshness_score=self._calculate_freshness_score(wiki_genres, cached_genres),
            completeness_score=self._calculate_completeness_score(len(combined))
        )

        return combined, quality_metrics

    def _combine_meta_tag_sources(self, wiki_tags: List[MetaTag], cached_tags: List[MetaTag],
                                fallback_tags: List[MetaTag]) -> Tuple[List[MetaTag], DataQualityMetrics]:
        """Combine meta tag data from multiple sources"""
        combined = []
        seen_tags = set()

        # Add wiki tags first (highest priority)
        for tag in wiki_tags:
            if tag.tag.lower() not in seen_tags:
                combined.append(tag)
                seen_tags.add(tag.tag.lower())

        # Add cached tags that aren't in wiki data
        for tag in cached_tags:
            if tag.tag.lower() not in seen_tags:
                combined.append(tag)
                seen_tags.add(tag.tag.lower())

        # Add fallback tags that aren't in other sources
        for tag in fallback_tags:
            if tag.tag.lower() not in seen_tags:
                combined.append(tag)
                seen_tags.add(tag.tag.lower())

        # Calculate quality metrics
        quality_metrics = DataQualityMetrics(
            total_items=len(combined),
            wiki_items=len(wiki_tags),
            cached_items=len(cached_tags),
            fallback_items=len(fallback_tags),
            quality_score=self._calculate_quality_score(len(wiki_tags), len(cached_tags), len(fallback_tags)),
            freshness_score=self._calculate_freshness_score(wiki_tags, cached_tags),
            completeness_score=self._calculate_completeness_score(len(combined))
        )

        return combined, quality_metrics

    def _combine_technique_sources(self, wiki_techniques: List[Technique], cached_techniques: List[Technique],
                                 fallback_techniques: List[Technique]) -> Tuple[List[Technique], DataQualityMetrics]:
        """Combine technique data from multiple sources"""
        combined = []
        seen_names = set()

        # Add wiki techniques first (highest priority)
        for technique in wiki_techniques:
            if technique.name.lower() not in seen_names:
                combined.append(technique)
                seen_names.add(technique.name.lower())

        # Add cached techniques that aren't in wiki data
        for technique in cached_techniques:
            if technique.name.lower() not in seen_names:
                combined.append(technique)
                seen_names.add(technique.name.lower())

        # Add fallback techniques that aren't in other sources
        for technique in fallback_techniques:
            if technique.name.lower() not in seen_names:
                combined.append(technique)
                seen_names.add(technique.name.lower())

        # Calculate quality metrics
        quality_metrics = DataQualityMetrics(
            total_items=len(combined),
            wiki_items=len(wiki_techniques),
            cached_items=len(cached_techniques),
            fallback_items=len(fallback_techniques),
            quality_score=self._calculate_quality_score(len(wiki_techniques), len(cached_techniques), len(fallback_techniques)),
            freshness_score=self._calculate_freshness_score(wiki_techniques, cached_techniques),
            completeness_score=self._calculate_completeness_score(len(combined))
        )

        return combined, quality_metrics

    def _calculate_quality_score(self, wiki_count: int, cached_count: int, fallback_count: int) -> float:
        """Calculate quality score based on data source distribution"""
        total = wiki_count + cached_count + fallback_count
        if total == 0:
            return 0.0

        # Wiki data is highest quality (1.0), cached is medium (0.7), fallback is lowest (0.4)
        weighted_score = (wiki_count * 1.0 + cached_count * 0.7 + fallback_count * 0.4) / total
        return weighted_score

    def _calculate_freshness_score(self, wiki_items: List[Any], cached_items: List[Any]) -> float:
        """Calculate freshness score based on data recency"""
        if not wiki_items and not cached_items:
            return 0.0

        total_items = len(wiki_items) + len(cached_items)
        wiki_ratio = len(wiki_items) / total_items

        # Wiki data is always fresh (1.0), cached data freshness depends on age
        # For simplicity, assume cached data has 0.6 freshness
        freshness = wiki_ratio * 1.0 + (1 - wiki_ratio) * 0.6
        return freshness

    def _calculate_completeness_score(self, total_items: int) -> float:
        """Calculate completeness score based on total items available"""
        # Define expected minimum items for each data type

        # Use a reasonable default if we can't determine the type
        expected_minimum = 20

        if total_items >= expected_minimum:
            return 1.0
        elif total_items >= expected_minimum * 0.5:
            return 0.8
        elif total_items >= expected_minimum * 0.25:
            return 0.6
        elif total_items > 0:
            return 0.4
        else:
            return 0.0

    async def _get_cached_genres(self, max_age_hours: int) -> List[Genre]:
        """Get cached genre data if available and fresh"""
        # This would integrate with the cache manager
        # For now, return empty list (would be implemented with actual cache)
        return []

    async def _get_cached_meta_tags(self, category: str, max_age_hours: int) -> List[MetaTag]:
        """Get cached meta tag data if available and fresh"""
        # This would integrate with the cache manager
        # For now, return empty list (would be implemented with actual cache)
        return []

    async def _get_cached_techniques(self, technique_type: str, max_age_hours: int) -> List[Technique]:
        """Get cached technique data if available and fresh"""
        # This would integrate with the cache manager
        # For now, return empty list (would be implemented with actual cache)
        return []

    def _convert_to_genre_objects(self, data: List[Any]) -> List[Genre]:
        """Convert fallback data to Genre objects"""
        genres = []
        for item in data:
            if isinstance(item, Genre):
                genres.append(item)
            elif isinstance(item, dict):
                genre = Genre(
                    name=item.get('name', 'Unknown'),
                    description=item.get('description', ''),
                    subgenres=item.get('subgenres', []),
                    characteristics=item.get('characteristics', []),
                    typical_instruments=item.get('typical_instruments', []),
                    mood_associations=item.get('mood_associations', []),
                    source_url='fallback',
                    download_date=datetime.now(),
                    confidence_score=0.6
                )
                genres.append(genre)
        return genres

    def _convert_to_meta_tag_objects(self, data: List[Any]) -> List[MetaTag]:
        """Convert fallback data to MetaTag objects"""
        meta_tags = []
        for item in data:
            if isinstance(item, MetaTag):
                meta_tags.append(item)
            elif isinstance(item, dict):
                meta_tag = MetaTag(
                    tag=item.get('tag', ''),
                    category=item.get('category', 'general'),
                    description=item.get('description', ''),
                    usage_examples=item.get('usage_examples', []),
                    compatible_genres=item.get('compatible_genres', []),
                    source_url='fallback',
                    download_date=datetime.now()
                )
                meta_tags.append(meta_tag)
        return meta_tags

    def _convert_to_technique_objects(self, data: List[Any]) -> List[Technique]:
        """Convert fallback data to Technique objects"""
        techniques = []
        for item in data:
            if isinstance(item, Technique):
                techniques.append(item)
            elif isinstance(item, dict):
                technique = Technique(
                    name=item.get('name', 'Unknown'),
                    description=item.get('description', ''),
                    technique_type=item.get('technique_type', 'general'),
                    examples=item.get('examples', []),
                    applicable_scenarios=item.get('applicable_scenarios', []),
                    source_url='fallback',
                    download_date=datetime.now()
                )
                techniques.append(technique)
        return techniques

    def _setup_fallback_strategies(self) -> None:
        """Setup fallback strategies for different scenarios"""
        self.fallback_strategies = {
            'network_failure': [
                'use_cached_data',
                'use_hardcoded_fallback',
                'partial_functionality'
            ],
            'parse_failure': [
                'use_cached_data',
                'attempt_partial_parse',
                'use_hardcoded_fallback'
            ],
            'data_corruption': [
                'validate_and_filter',
                'use_cached_data',
                'use_hardcoded_fallback'
            ],
            'partial_failure': [
                'combine_with_fallback',
                'supplement_missing_data',
                'continue_with_reduced_quality'
            ]
        }
