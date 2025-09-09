#!/usr/bin/env python3
"""
Enhanced Genre Mapper for Dynamic Suno Data Integration

This module provides the EnhancedGenreMapper class that replaces hardcoded genre mappings
with wiki-sourced data, implementing intelligent trait-to-genre matching using semantic analysis.
"""

import logging
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple

from performance_monitor import PerformanceMonitor
from wiki_data_models import Genre
from wiki_data_system import WikiDataManager

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class GenreMatch:
    """Represents a genre match with confidence scoring"""
    genre: Genre
    confidence: float
    matching_traits: List[str] = field(default_factory=list)
    matching_reasons: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Ensure confidence is between 0 and 1
        self.confidence = max(0.0, min(1.0, self.confidence))

@dataclass
class GenreHierarchy:
    """Represents genre hierarchy and relationships"""
    main_genre: str
    subgenres: List[str] = field(default_factory=list)
    parent_genres: List[str] = field(default_factory=list)
    related_genres: List[str] = field(default_factory=list)

# ================================================================================================
# ENHANCED GENRE MAPPER
# ================================================================================================

class EnhancedGenreMapper:
    """Enhanced genre mapper using wiki-sourced data with semantic analysis"""

    def __init__(self, wiki_data_manager: WikiDataManager, performance_monitor: Optional[PerformanceMonitor] = None):
        """
        Initialize EnhancedGenreMapper

        Args:
            wiki_data_manager: WikiDataManager instance for accessing genre data
            performance_monitor: PerformanceMonitor instance for tracking metrics
        """
        self.wiki_data_manager = wiki_data_manager
        self.performance_monitor = performance_monitor
        self._genres_cache: Optional[List[Genre]] = None
        self._trait_keywords_cache: Optional[Dict[str, Set[str]]] = None
        self._fallback_mappings = self._get_fallback_mappings()

    async def map_traits_to_genres(self, traits: List[str], max_results: int = 5,
                                  use_hierarchical: bool = True) -> List[GenreMatch]:
        """
        Map character traits to wiki-sourced genres using intelligent semantic analysis

        Args:
            traits: List of character traits to match
            max_results: Maximum number of genre matches to return
            use_hierarchical: Whether to consider genre hierarchies in matching

        Returns:
            List of GenreMatch objects sorted by confidence
        """
        logger.info(f"Mapping traits to genres: {traits} (hierarchical: {use_hierarchical})")

        # Start performance monitoring
        if self.performance_monitor:
            async with self.performance_monitor.measure_operation("genre_mapping", {
                'traits_count': len(traits),
                'max_results': max_results,
                'use_hierarchical': use_hierarchical
            }):
                return await self._perform_genre_mapping(traits, max_results, use_hierarchical)
        else:
            return await self._perform_genre_mapping(traits, max_results, use_hierarchical)

    async def _perform_genre_mapping(self, traits: List[str], max_results: int, use_hierarchical: bool) -> List[GenreMatch]:

        try:
            # Get wiki genres
            genres = await self._get_genres()

            if not genres:
                logger.warning("No wiki genres available, using fallback mappings")
                return await self._fallback_trait_mapping(traits, max_results)

            # Calculate matches for each genre
            genre_matches = []

            for genre in genres:
                confidence = self.calculate_genre_confidence(traits, genre)

                # Apply hierarchical boost if enabled
                if use_hierarchical and confidence > 0.05:
                    hierarchical_boost = self._calculate_hierarchical_boost(traits, genre)
                    confidence = min(1.0, confidence + hierarchical_boost)

                if confidence > 0.1:  # Only include genres with reasonable confidence
                    matching_traits, reasons = self._analyze_trait_match(traits, genre)

                    match = GenreMatch(
                        genre=genre,
                        confidence=confidence,
                        matching_traits=matching_traits,
                        matching_reasons=reasons
                    )
                    genre_matches.append(match)

            # Sort by confidence and return top results
            genre_matches.sort(key=lambda x: x.confidence, reverse=True)
            result = genre_matches[:max_results]

            # If we don't have enough high-confidence matches, use intelligent fallback
            if len(result) < max_results or (result and result[0].confidence < 0.5):
                logger.info("Using intelligent fallback matching to supplement results")
                fallback_matches = await self.find_fallback_matches(traits, max_results - len(result))

                # Merge results, avoiding duplicates
                existing_genres = {match.genre.name.lower() for match in result}
                for fallback_match in fallback_matches:
                    if fallback_match.genre.name.lower() not in existing_genres:
                        result.append(fallback_match)

                # Re-sort combined results
                result.sort(key=lambda x: x.confidence, reverse=True)
                result = result[:max_results]

            logger.info(f"Found {len(result)} genre matches (top confidence: {result[0].confidence:.3f})")
            return result

        except Exception as e:
            logger.error(f"Error mapping traits to genres: {e}")
            return await self._fallback_trait_mapping(traits, max_results)

    def calculate_genre_confidence(self, traits: List[str], genre: Genre) -> float:
        """
        Calculate confidence score for a trait-genre match

        Args:
            traits: List of character traits
            genre: Genre to match against

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not traits:
            return 0.0

        total_score = 0.0
        max_possible_score = len(traits)

        # Prepare genre text for matching
        genre_text = self._prepare_genre_text(genre)

        for trait in traits:
            trait_score = self._calculate_trait_genre_score(trait, genre, genre_text)
            total_score += trait_score

        # Normalize to 0-1 range
        confidence = total_score / max_possible_score if max_possible_score > 0 else 0.0

        # Apply genre popularity boost (more common genres get slight boost)
        popularity_boost = self._get_genre_popularity_boost(genre)
        confidence = min(1.0, confidence * popularity_boost)

        return confidence

    async def get_genre_hierarchy(self, genre_name: str) -> Optional[GenreHierarchy]:
        """
        Get comprehensive genre hierarchy information with intelligent analysis

        Args:
            genre_name: Name of the genre

        Returns:
            GenreHierarchy object or None if not found
        """
        try:
            # Find the genre (with fuzzy matching if needed)
            genre = self._find_genre_by_name(genre_name)
            if not genre:
                genre = await self._fuzzy_find_genre(genre_name)
                if not genre:
                    logger.warning(f"Genre '{genre_name}' not found in hierarchy analysis")
                    return None

            # Extract direct hierarchy information
            subgenres = genre.subgenres if genre.subgenres else []

            # Infer parent genres from name patterns and wiki data
            parent_genres = await self._infer_parent_genres_enhanced(genre)

            # Find related genres using similarity algorithms
            related_genres = await self._find_related_genres_enhanced(genre)

            return GenreHierarchy(
                main_genre=genre.name,
                subgenres=subgenres,
                parent_genres=parent_genres,
                related_genres=related_genres
            )

        except Exception as e:
            logger.error(f"Error getting genre hierarchy for {genre_name}: {e}")
            return None

    async def find_similar_genres(self, target_genre: str, max_results: int = 5,
                                 similarity_threshold: float = 0.2) -> List[Tuple[Genre, float]]:
        """
        Find genres similar to the target genre using multiple similarity algorithms

        Args:
            target_genre: Target genre name
            max_results: Maximum number of similar genres to return
            similarity_threshold: Minimum similarity score to include

        Returns:
            List of tuples (Genre, similarity_score) sorted by similarity
        """
        try:
            genres = await self._get_genres()
            if not genres:
                return []

            target_genre_obj = self._find_genre_by_name(target_genre)
            if not target_genre_obj:
                # Try fuzzy matching to find the target genre
                target_genre_obj = await self._fuzzy_find_genre(target_genre)
                if not target_genre_obj:
                    logger.warning(f"Target genre '{target_genre}' not found")
                    return []

            # Calculate similarity scores using multiple algorithms
            similarities = []

            for genre in genres:
                if genre.name.lower() == target_genre_obj.name.lower():
                    continue  # Skip the target genre itself

                # Combine multiple similarity measures
                content_similarity = self._calculate_content_similarity(target_genre_obj, genre)
                structural_similarity = self._calculate_structural_similarity(target_genre_obj, genre)
                semantic_similarity = self._calculate_genre_semantic_similarity(target_genre_obj, genre)
                hierarchical_similarity = self._calculate_hierarchical_similarity(target_genre_obj, genre)

                # Weighted combination of similarity measures
                combined_similarity = (
                    content_similarity * 0.3 +
                    structural_similarity * 0.25 +
                    semantic_similarity * 0.25 +
                    hierarchical_similarity * 0.2
                )

                if combined_similarity >= similarity_threshold:
                    similarities.append((genre, combined_similarity))

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:max_results]

        except Exception as e:
            logger.error(f"Error finding similar genres to {target_genre}: {e}")
            return []

    # Private methods

    async def _get_genres(self) -> List[Genre]:
        """Get genres from wiki data manager with caching"""
        if self._genres_cache is None:
            try:
                self._genres_cache = await self.wiki_data_manager.get_genres()
            except Exception as e:
                logger.error(f"Error getting genres from wiki data manager: {e}")
                self._genres_cache = []

        return self._genres_cache or []

    def _prepare_genre_text(self, genre: Genre) -> str:
        """Prepare genre text for matching analysis"""
        text_parts = [
            genre.name,
            genre.description,
            ' '.join(genre.characteristics),
            ' '.join(genre.mood_associations),
            ' '.join(genre.typical_instruments)
        ]
        return ' '.join(text_parts).lower()

    def _calculate_trait_genre_score(self, trait: str, genre: Genre, genre_text: str) -> float:
        """Calculate score for a single trait against a genre"""
        trait_lower = trait.lower()
        score = 0.0

        # Direct name match (highest score)
        if trait_lower in genre.name.lower():
            score += 0.8

        # Description match
        if trait_lower in genre.description.lower():
            score += 0.6

        # Characteristics match
        for characteristic in genre.characteristics:
            if trait_lower in characteristic.lower():
                score += 0.5
                break

        # Mood associations match
        for mood in genre.mood_associations:
            if trait_lower in mood.lower():
                score += 0.4
                break

        # Semantic similarity using keywords
        semantic_score = self._calculate_semantic_similarity(trait_lower, genre_text)
        score += semantic_score * 0.3

        # Fuzzy string matching for partial matches
        fuzzy_score = self._calculate_fuzzy_match(trait_lower, genre_text)
        score += fuzzy_score * 0.2

        return min(1.0, score)  # Cap at 1.0

    def _calculate_semantic_similarity(self, trait: str, genre_text: str) -> float:
        """Calculate semantic similarity between trait and genre text"""
        # Define semantic keyword groups
        semantic_groups = {
            'melancholic': ['sad', 'melancholy', 'blues', 'sorrow', 'emotional', 'introspective'],
            'mysterious': ['dark', 'gothic', 'ambient', 'atmospheric', 'haunting', 'enigmatic'],
            'brave': ['powerful', 'strong', 'metal', 'rock', 'aggressive', 'bold'],
            'rebellious': ['punk', 'alternative', 'grunge', 'rebellious', 'anti-establishment'],
            'intellectual': ['progressive', 'complex', 'art', 'experimental', 'sophisticated'],
            'emotional': ['soul', 'blues', 'passionate', 'heartfelt', 'expressive'],
            'energetic': ['electronic', 'dance', 'upbeat', 'dynamic', 'high-energy'],
            'peaceful': ['ambient', 'chill', 'relaxing', 'meditative', 'calm'],
            'traditional': ['folk', 'country', 'acoustic', 'roots', 'heritage'],
            'spiritual': ['gospel', 'sacred', 'religious', 'devotional', 'transcendent']
        }

        # Find semantic matches
        max_similarity = 0.0

        for group_trait, keywords in semantic_groups.items():
            if trait in group_trait or any(keyword in trait for keyword in keywords):
                for keyword in keywords:
                    if keyword in genre_text:
                        similarity = SequenceMatcher(None, trait, keyword).ratio()
                        max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_fuzzy_match(self, trait: str, genre_text: str) -> float:
        """Calculate fuzzy string matching score"""
        words = genre_text.split()
        max_ratio = 0.0

        for word in words:
            if len(word) > 3:  # Only consider meaningful words
                ratio = SequenceMatcher(None, trait, word).ratio()
                max_ratio = max(max_ratio, ratio)

        return max_ratio

    def _get_genre_popularity_boost(self, genre: Genre) -> float:
        """Get popularity boost for common genres"""
        popular_genres = {
            'pop', 'rock', 'hip hop', 'electronic', 'jazz', 'blues', 'folk', 'country',
            'alternative', 'indie', 'metal', 'punk', 'soul', 'r&b'
        }

        genre_name_lower = genre.name.lower()
        for popular in popular_genres:
            if popular in genre_name_lower:
                return 1.1  # 10% boost for popular genres

        return 1.0  # No boost

    def _analyze_trait_match(self, traits: List[str], genre: Genre) -> Tuple[List[str], List[str]]:
        """Analyze which traits match and why"""
        matching_traits = []
        reasons = []

        for trait in traits:
            trait_lower = trait.lower()

            # Check direct matches
            if trait_lower in genre.name.lower():
                matching_traits.append(trait)
                reasons.append("Direct match in genre name")
            elif trait_lower in genre.description.lower():
                matching_traits.append(trait)
                reasons.append("Match in genre description")
            elif any(trait_lower in char.lower() for char in genre.characteristics):
                matching_traits.append(trait)
                reasons.append("Match in genre characteristics")
            elif any(trait_lower in mood.lower() for mood in genre.mood_associations):
                matching_traits.append(trait)
                reasons.append("Match in mood associations")

        return matching_traits, reasons

    def _find_genre_by_name(self, genre_name: str) -> Optional[Genre]:
        """Find a genre by name"""
        if not self._genres_cache:
            return None

        genre_name_lower = genre_name.lower()
        for genre in self._genres_cache:
            if genre.name.lower() == genre_name_lower:
                return genre

        return None

    async def _infer_parent_genres_enhanced(self, genre: Genre) -> List[str]:
        """Enhanced parent genre inference using wiki data and pattern analysis"""
        parent_genres = []
        genre_lower = genre.name.lower()

        # Get all available genres for cross-referencing
        all_genres = await self._get_genres()
        genre_names = [g.name.lower() for g in all_genres]

        # Enhanced parent-child patterns with more comprehensive mapping
        hierarchical_patterns = {
            'metal': ['heavy metal', 'death metal', 'black metal', 'thrash metal', 'doom metal',
                     'power metal', 'progressive metal', 'symphonic metal', 'folk metal'],
            'rock': ['alternative rock', 'indie rock', 'hard rock', 'soft rock', 'progressive rock',
                    'art rock', 'classic rock', 'punk rock', 'garage rock', 'psychedelic rock'],
            'jazz': ['smooth jazz', 'bebop', 'swing', 'fusion', 'free jazz', 'cool jazz',
                    'hard bop', 'modal jazz', 'latin jazz', 'contemporary jazz'],
            'electronic': ['techno', 'house', 'trance', 'dubstep', 'drum and bass', 'ambient',
                          'synthwave', 'electro', 'breakbeat', 'downtempo'],
            'folk': ['folk rock', 'indie folk', 'acoustic folk', 'traditional folk', 'contemporary folk',
                    'celtic folk', 'american folk', 'world folk'],
            'pop': ['indie pop', 'art pop', 'electropop', 'synthpop', 'dance pop', 'teen pop',
                   'baroque pop', 'chamber pop'],
            'hip hop': ['old school hip hop', 'conscious rap', 'gangsta rap', 'trap', 'boom bap',
                       'alternative hip hop', 'experimental hip hop'],
            'country': ['country rock', 'alt-country', 'bluegrass', 'honky-tonk', 'outlaw country',
                       'contemporary country', 'country pop'],
            'blues': ['delta blues', 'chicago blues', 'electric blues', 'acoustic blues',
                     'country blues', 'rhythm and blues'],
            'punk': ['hardcore punk', 'pop punk', 'post-punk', 'street punk', 'anarcho-punk',
                    'ska punk', 'celtic punk'],
            'classical': ['baroque', 'romantic', 'contemporary classical', 'minimalist',
                         'orchestral', 'chamber music', 'opera']
        }

        # Check for direct parent-child relationships
        for parent, children in hierarchical_patterns.items():
            if any(child in genre_lower for child in children):
                # Verify parent genre exists in our data
                if parent in genre_names:
                    parent_genres.append(parent)

        # Check if this genre appears as a subgenre of others
        for other_genre in all_genres:
            if (other_genre.subgenres and
                genre.name in other_genre.subgenres and
                other_genre.name not in parent_genres):
                parent_genres.append(other_genre.name)

        # Infer from compound genre names (e.g., "folk rock" -> ["folk", "rock"])
        compound_parts = self._extract_compound_genre_parts(genre.name)
        for part in compound_parts:
            if part in genre_names and part not in parent_genres:
                parent_genres.append(part)

        return parent_genres

    def _extract_compound_genre_parts(self, genre_name: str) -> List[str]:
        """Extract base genre parts from compound genre names"""
        genre_lower = genre_name.lower()

        # Common base genres that appear in compound names
        base_genres = [
            'rock', 'pop', 'jazz', 'blues', 'folk', 'country', 'electronic', 'metal',
            'punk', 'hip hop', 'classical', 'ambient', 'house', 'techno', 'soul',
            'funk', 'reggae', 'ska', 'gospel', 'world'
        ]

        found_parts = []
        for base in base_genres:
            if base in genre_lower and base != genre_lower:
                found_parts.append(base)

        return found_parts

    async def _find_related_genres_enhanced(self, genre: Genre) -> List[str]:
        """Find related genres using multiple similarity algorithms"""
        all_genres = await self._get_genres()
        if not all_genres:
            return []

        related_scores = []

        # Find genres with similar characteristics using multiple measures
        for other_genre in all_genres:
            if other_genre.name == genre.name:
                continue

            # Calculate multiple similarity measures
            content_sim = self._calculate_content_similarity(genre, other_genre)
            semantic_sim = self._calculate_genre_semantic_similarity(genre, other_genre)
            hierarchical_sim = self._calculate_hierarchical_similarity(genre, other_genre)

            # Combined similarity score
            combined_score = (content_sim * 0.4 + semantic_sim * 0.4 + hierarchical_sim * 0.2)

            if combined_score > 0.3:  # Threshold for relatedness
                related_scores.append((other_genre.name, combined_score))

        # Sort by similarity and return top related genres
        related_scores.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in related_scores[:8]]  # Return up to 8 related genres

    def _calculate_content_similarity(self, genre1: Genre, genre2: Genre) -> float:
        """Calculate content-based similarity between two genres"""
        # Compare characteristics
        chars1 = set(genre1.characteristics)
        chars2 = set(genre2.characteristics)
        char_similarity = len(chars1 & chars2) / len(chars1 | chars2) if chars1 | chars2 else 0

        # Compare mood associations
        moods1 = set(genre1.mood_associations)
        moods2 = set(genre2.mood_associations)
        mood_similarity = len(moods1 & moods2) / len(moods1 | moods2) if moods1 | moods2 else 0

        # Compare instruments
        instr1 = set(genre1.typical_instruments)
        instr2 = set(genre2.typical_instruments)
        instr_similarity = len(instr1 & instr2) / len(instr1 | instr2) if instr1 | instr2 else 0

        # Weighted average
        similarity = (char_similarity * 0.4 + mood_similarity * 0.4 + instr_similarity * 0.2)

        return similarity

    def _calculate_structural_similarity(self, genre1: Genre, genre2: Genre) -> float:
        """Calculate structural similarity based on genre names and descriptions"""
        # Name similarity using sequence matching
        name_similarity = SequenceMatcher(None, genre1.name.lower(), genre2.name.lower()).ratio()

        # Description similarity using word overlap
        desc1_words = set(genre1.description.lower().split())
        desc2_words = set(genre2.description.lower().split())
        desc_similarity = len(desc1_words & desc2_words) / len(desc1_words | desc2_words) if desc1_words | desc2_words else 0

        # Combined structural similarity
        return (name_similarity * 0.6 + desc_similarity * 0.4)

    def _calculate_genre_semantic_similarity(self, genre1: Genre, genre2: Genre) -> float:
        """Calculate semantic similarity using genre family relationships"""
        # Define genre families for semantic grouping
        genre_families = {
            'electronic': ['electronic', 'techno', 'house', 'trance', 'dubstep', 'edm', 'synthwave', 'ambient electronic'],
            'rock': ['rock', 'alternative rock', 'indie rock', 'hard rock', 'soft rock', 'progressive rock', 'art rock'],
            'metal': ['metal', 'heavy metal', 'death metal', 'black metal', 'thrash metal', 'doom metal', 'power metal'],
            'jazz': ['jazz', 'smooth jazz', 'bebop', 'swing', 'fusion', 'free jazz', 'cool jazz'],
            'blues': ['blues', 'delta blues', 'chicago blues', 'electric blues', 'acoustic blues'],
            'folk': ['folk', 'folk rock', 'indie folk', 'acoustic folk', 'traditional folk'],
            'pop': ['pop', 'indie pop', 'art pop', 'electropop', 'synthpop', 'dance pop'],
            'hip_hop': ['hip hop', 'rap', 'trap', 'old school hip hop', 'conscious rap'],
            'country': ['country', 'country rock', 'bluegrass', 'americana', 'alt-country'],
            'classical': ['classical', 'baroque', 'romantic', 'contemporary classical', 'orchestral'],
            'ambient': ['ambient', 'dark ambient', 'drone', 'atmospheric', 'soundscape'],
            'punk': ['punk', 'punk rock', 'hardcore punk', 'pop punk', 'post-punk']
        }

        # Find which families each genre belongs to
        genre1_families = []
        genre2_families = []

        for family, genres in genre_families.items():
            if any(g in genre1.name.lower() for g in genres):
                genre1_families.append(family)
            if any(g in genre2.name.lower() for g in genres):
                genre2_families.append(family)

        # Calculate family overlap
        if not genre1_families or not genre2_families:
            return 0.0

        family_overlap = len(set(genre1_families) & set(genre2_families))
        max_families = max(len(genre1_families), len(genre2_families))

        return family_overlap / max_families if max_families > 0 else 0.0

    def _calculate_hierarchical_similarity(self, genre1: Genre, genre2: Genre) -> float:
        """Calculate similarity based on genre hierarchies and subgenre relationships"""
        # Check if one genre is a subgenre of another
        if genre1.subgenres and genre2.name in genre1.subgenres:
            return 0.8  # High similarity for parent-child relationship
        if genre2.subgenres and genre1.name in genre2.subgenres:
            return 0.8  # High similarity for parent-child relationship

        # Check for shared subgenres
        if genre1.subgenres and genre2.subgenres:
            shared_subgenres = set(genre1.subgenres) & set(genre2.subgenres)
            if shared_subgenres:
                overlap_ratio = len(shared_subgenres) / len(set(genre1.subgenres) | set(genre2.subgenres))
                return overlap_ratio * 0.6  # Moderate similarity for shared subgenres

        # Check for hierarchical patterns in names
        hierarchy_similarity = self._check_name_hierarchy(genre1.name, genre2.name)

        return hierarchy_similarity

    def _check_name_hierarchy(self, name1: str, name2: str) -> float:
        """Check for hierarchical relationships in genre names"""
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        # Common hierarchical patterns
        hierarchical_patterns = [
            ('rock', ['alternative rock', 'indie rock', 'hard rock', 'soft rock', 'progressive rock']),
            ('metal', ['heavy metal', 'death metal', 'black metal', 'thrash metal', 'doom metal']),
            ('jazz', ['smooth jazz', 'bebop', 'swing', 'fusion', 'free jazz']),
            ('electronic', ['techno', 'house', 'trance', 'dubstep', 'synthwave']),
            ('folk', ['folk rock', 'indie folk', 'acoustic folk', 'traditional folk']),
            ('pop', ['indie pop', 'art pop', 'electropop', 'synthpop', 'dance pop'])
        ]

        for parent, children in hierarchical_patterns:
            # Check if one is parent and other is child
            if parent in name1_lower and any(child in name2_lower for child in children):
                return 0.7
            if parent in name2_lower and any(child in name1_lower for child in children):
                return 0.7

            # Check if both are children of same parent
            if (any(child in name1_lower for child in children) and
                any(child in name2_lower for child in children)):
                return 0.5

        return 0.0

    async def _fuzzy_find_genre(self, genre_name: str, threshold: float = 0.6) -> Optional[Genre]:
        """Find a genre using fuzzy string matching"""
        genres = await self._get_genres()
        if not genres:
            return None

        best_match = None
        best_ratio = 0.0

        for genre in genres:
            ratio = SequenceMatcher(None, genre_name.lower(), genre.name.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = genre

        return best_match

    async def find_fallback_matches(self, traits: List[str], max_results: int = 5) -> List[GenreMatch]:
        """
        Find genre matches using intelligent fallback algorithms when direct matches fail

        Args:
            traits: List of character traits
            max_results: Maximum number of matches to return

        Returns:
            List of GenreMatch objects using fallback algorithms
        """
        logger.info(f"Using intelligent fallback matching for traits: {traits}")

        try:
            genres = await self._get_genres()
            if not genres:
                return await self._fallback_trait_mapping(traits, max_results)

            # Use similarity-based matching when direct matches fail
            fallback_matches = []

            for trait in traits:
                # Try semantic expansion of traits
                expanded_traits = self._expand_trait_semantically(trait)

                # Find genres that match expanded traits
                for expanded_trait in expanded_traits:
                    for genre in genres:
                        similarity = self._calculate_trait_semantic_match(expanded_trait, genre)
                        if similarity > 0.3:  # Lower threshold for fallback
                            match = GenreMatch(
                                genre=genre,
                                confidence=similarity * 0.8,  # Reduce confidence for fallback
                                matching_traits=[trait],
                                matching_reasons=[f"Semantic expansion: {trait} -> {expanded_trait}"]
                            )
                            fallback_matches.append(match)

            # Remove duplicates and sort by confidence
            unique_matches = {}
            for match in fallback_matches:
                key = match.genre.name
                if key not in unique_matches or match.confidence > unique_matches[key].confidence:
                    unique_matches[key] = match

            result = list(unique_matches.values())
            result.sort(key=lambda x: x.confidence, reverse=True)

            return result[:max_results]

        except Exception as e:
            logger.error(f"Error in fallback matching: {e}")
            return await self._fallback_trait_mapping(traits, max_results)

    def _expand_trait_semantically(self, trait: str) -> List[str]:
        """Expand a trait into semantically related terms"""
        trait_expansions = {
            'melancholic': ['sad', 'melancholy', 'sorrowful', 'mournful', 'wistful', 'pensive'],
            'mysterious': ['enigmatic', 'cryptic', 'secretive', 'dark', 'hidden', 'obscure'],
            'brave': ['courageous', 'bold', 'fearless', 'heroic', 'valiant', 'strong'],
            'rebellious': ['defiant', 'revolutionary', 'anti-establishment', 'nonconformist', 'radical'],
            'intellectual': ['cerebral', 'thoughtful', 'analytical', 'scholarly', 'sophisticated'],
            'emotional': ['passionate', 'expressive', 'heartfelt', 'intense', 'moving'],
            'energetic': ['dynamic', 'vigorous', 'lively', 'spirited', 'animated', 'upbeat'],
            'peaceful': ['calm', 'serene', 'tranquil', 'relaxing', 'meditative', 'soothing'],
            'creative': ['artistic', 'innovative', 'imaginative', 'original', 'inventive'],
            'spiritual': ['transcendent', 'sacred', 'divine', 'mystical', 'ethereal']
        }

        trait_lower = trait.lower()
        if trait_lower in trait_expansions:
            return [trait] + trait_expansions[trait_lower]

        return [trait]

    def _calculate_hierarchical_boost(self, traits: List[str], genre: Genre) -> float:
        """Calculate hierarchical boost for genres based on subgenre relationships"""
        boost = 0.0

        # Check if any traits match subgenres
        if genre.subgenres:
            for trait in traits:
                trait_lower = trait.lower()
                for subgenre in genre.subgenres:
                    if trait_lower in subgenre.lower() or subgenre.lower() in trait_lower:
                        boost += 0.1  # Small boost for subgenre match

        # Check for parent-child relationships in genre families
        genre_name_lower = genre.name.lower()
        for trait in traits:
            trait_lower = trait.lower()

            # If trait suggests a parent genre and current genre is a subgenre
            if ('rock' in trait_lower and 'rock' in genre_name_lower and
                genre_name_lower != 'rock'):
                boost += 0.15
            elif ('metal' in trait_lower and 'metal' in genre_name_lower and
                  genre_name_lower != 'metal'):
                boost += 0.15
            elif ('electronic' in trait_lower and 'electronic' in genre_name_lower and
                  genre_name_lower != 'electronic'):
                boost += 0.15
            elif ('jazz' in trait_lower and 'jazz' in genre_name_lower and
                  genre_name_lower != 'jazz'):
                boost += 0.15

        return min(0.3, boost)  # Cap boost at 0.3

    def _calculate_trait_semantic_match(self, trait: str, genre: Genre) -> float:
        """Calculate semantic match between expanded trait and genre"""
        trait_lower = trait.lower()

        # Check all genre text fields
        genre_text_fields = [
            genre.name.lower(),
            genre.description.lower(),
            ' '.join(genre.characteristics).lower(),
            ' '.join(genre.mood_associations).lower(),
            ' '.join(genre.typical_instruments).lower()
        ]

        max_score = 0.0

        for text_field in genre_text_fields:
            if trait_lower in text_field:
                # Exact match gets high score
                max_score = max(max_score, 0.9)
            else:
                # Fuzzy match for partial similarity
                words = text_field.split()
                for word in words:
                    if len(word) > 3:  # Only consider meaningful words
                        ratio = SequenceMatcher(None, trait_lower, word).ratio()
                        if ratio > 0.7:  # High similarity threshold
                            max_score = max(max_score, ratio * 0.7)

        return max_score

    async def _fallback_trait_mapping(self, traits: List[str], max_results: int) -> List[GenreMatch]:
        """Fallback trait mapping using hardcoded mappings when wiki data unavailable"""
        logger.info("Using hardcoded fallback trait mappings")

        matches = []

        for trait in traits:
            trait_lower = trait.lower()
            if trait_lower in self._fallback_mappings:
                genres = self._fallback_mappings[trait_lower]
                for i, genre_name in enumerate(genres[:max_results]):
                    # Create a basic Genre object for fallback
                    fallback_genre = Genre(
                        name=genre_name,
                        description=f"Fallback genre for {trait}",
                        characteristics=[trait],
                        mood_associations=[trait],
                        typical_instruments=[],
                        source_url="fallback"
                    )

                    # Higher confidence for first match, decreasing for others
                    confidence = 0.8 - (i * 0.1)

                    match = GenreMatch(
                        genre=fallback_genre,
                        confidence=confidence,
                        matching_traits=[trait],
                        matching_reasons=[f"Hardcoded fallback mapping for {trait}"]
                    )
                    matches.append(match)

        # Sort by confidence and return top results
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:max_results]

    async def get_genre_instruments(self, genre_name: str, fallback_instruments: Optional[List[str]] = None) -> List[str]:
        """
        Get typical instruments for a genre from wiki data

        Args:
            genre_name: Name of the genre
            fallback_instruments: Fallback instruments if genre not found

        Returns:
            List of typical instruments for the genre
        """
        try:
            # Get genres from wiki data
            genres = await self._get_genres()

            if not genres:
                logger.warning("No wiki genres available for instrument lookup")
                return fallback_instruments or ['vocals', 'guitar', 'piano', 'drums']

            # Find the genre (with fuzzy matching if needed)
            genre = self._find_genre_by_name(genre_name)
            if not genre:
                genre = await self._fuzzy_find_genre(genre_name)

            if genre and genre.typical_instruments:
                logger.info(f"Found {len(genre.typical_instruments)} instruments for genre '{genre_name}' from wiki data")
                return genre.typical_instruments

            # Try to find similar genres and use their instruments
            similar_genres = await self.find_similar_genres(genre_name, max_results=3, similarity_threshold=0.3)

            if similar_genres:
                # Combine instruments from similar genres
                combined_instruments = []
                for similar_genre, similarity in similar_genres:
                    if similar_genre.typical_instruments:
                        combined_instruments.extend(similar_genre.typical_instruments)
                        logger.info(f"Using instruments from similar genre '{similar_genre.name}' (similarity: {similarity:.2f})")

                if combined_instruments:
                    # Remove duplicates while preserving order
                    unique_instruments = []
                    seen = set()
                    for instrument in combined_instruments:
                        if instrument.lower() not in seen:
                            unique_instruments.append(instrument)
                            seen.add(instrument.lower())

                    return unique_instruments[:8]  # Limit to 8 instruments

            # If no wiki data found, use fallback
            logger.info(f"No wiki instrument data found for genre '{genre_name}', using fallback")
            return fallback_instruments or ['vocals', 'guitar', 'piano', 'drums']

        except Exception as e:
            logger.error(f"Error getting instruments for genre '{genre_name}': {e}")
            return fallback_instruments or ['vocals', 'guitar', 'piano', 'drums']

    async def _fuzzy_find_genre(self, genre_name: str, threshold: float = 0.6) -> Optional[Genre]:
        """
        Find a genre using fuzzy string matching

        Args:
            genre_name: Name of the genre to find
            threshold: Minimum similarity threshold

        Returns:
            Best matching Genre or None if no good match found
        """
        genres = await self._get_genres()
        if not genres:
            return None

        best_match = None
        best_ratio = 0.0

        genre_name_lower = genre_name.lower()

        for genre in genres:
            # Check exact match first
            if genre.name.lower() == genre_name_lower:
                return genre

            # Check fuzzy match
            ratio = SequenceMatcher(None, genre_name_lower, genre.name.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = genre

        if best_match:
            logger.info(f"Fuzzy matched '{genre_name}' to '{best_match.name}' (similarity: {best_ratio:.2f})")

        return best_match

    def _get_fallback_mappings(self) -> Dict[str, List[str]]:
        """Get fallback trait-to-genre mappings for when wiki data is unavailable"""
        return {
            'melancholic': ['blues', 'folk', 'indie'],
            'mysterious': ['dark ambient', 'gothic', 'alternative'],
            'brave': ['rock', 'metal', 'punk'],
            'compassionate': ['soul', 'gospel', 'folk'],
            'rebellious': ['punk', 'alternative', 'grunge'],
            'intellectual': ['progressive', 'art rock', 'ambient'],
            'creative': ['indie', 'alternative', 'art pop'],
            'adventurous': ['electronic', 'synthwave', 'space rock'],
            'emotional': ['blues', 'soul', 'gospel'],
            'confident': ['rock', 'pop', 'electronic'],
            'vulnerable': ['indie', 'singer-songwriter', 'folk'],
            'ambitious': ['pop', 'electronic', 'rock'],
            'perfectionist': ['progressive', 'classical', 'jazz'],
            'authentic': ['folk', 'country', 'singer-songwriter'],
            'introspective': ['ambient', 'post-rock', 'indie'],
            'artistic': ['art pop', 'experimental', 'indie']
        }
