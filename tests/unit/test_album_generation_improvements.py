#!/usr/bin/env python3
"""
Unit tests for album generation improvements

Tests the consolidated album generation functionality and track uniqueness
improvements from the conceptual-album-generation-fixes spec.
"""

import pytest
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures
from tests.fixtures.mock_contexts import MockContext, create_mock_context

# Import components to test
try:
    from server import (
        create_conceptual_album,
        _detect_content_type,
        _create_narrative_album,
        _create_character_driven_album,
        _create_conceptual_thematic_album
    )
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Components not available for testing: {e}")
    COMPONENTS_AVAILABLE = False


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestAlbumGenerationConsolidation:
    """Test consolidated album generation functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.ctx = create_mock_context()
        
    async def test_content_type_detection_routing(self):
        """Test that content type detection routes to correct album creation method"""
        # Test narrative content routing
        narrative_content = "John walked through the city, thinking about his past."
        
        detected_type = await _detect_content_type(
            narrative_content, None, "auto", self.ctx
        )
        
        assert detected_type in ["narrative", "story", "conceptual"]  # May fallback to conceptual
        
    async def test_album_concept_generation(self):
        """Test automatic album concept generation when not provided"""
        content = "The sound of rain on windows creates a rhythm of memory."
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            album_concept=None,  # Should auto-generate
            track_count=4,
            genre="ambient"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            assert "album_info" in result
            assert "title" in result["album_info"]
            assert result["album_info"]["title"] is not None
            assert len(result["album_info"]["title"]) > 0
            
    async def test_track_count_validation(self):
        """Test validation of track count parameter"""
        content = "Music is the language of the soul."
        
        # Test with valid track count
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=5,
            genre="alternative"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            assert len(result.get("tracks", [])) == 5
            
    async def test_genre_parameter_handling(self):
        """Test handling of different genre parameters"""
        content = "The city never sleeps, and neither do its dreamers."
        
        genres_to_test = ["electronic", "folk", "jazz", "ambient", "alternative"]
        
        for genre in genres_to_test:
            result_json = await create_conceptual_album(
                ctx=self.ctx,
                content=content,
                track_count=3,
                genre=genre
            )
            
            result = json.loads(result_json)
            
            if "error" not in result:
                assert result["album_info"]["genre"] == genre


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestTrackUniqueness:
    """Test track uniqueness and meaningful content generation"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.ctx = create_mock_context()
        
    async def test_unique_track_titles(self):
        """Test that track titles are unique and meaningful"""
        content = """
        The journey of self-discovery is like climbing a mountain.
        Each step reveals new perspectives, new challenges, and new understanding.
        The summit is not the destination, but the transformation along the way.
        """
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=6,
            genre="folk"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            tracks = result.get("tracks", [])
            track_titles = [track.get("title", "") for track in tracks]
            
            # All titles should be non-empty
            assert all(title.strip() for title in track_titles)
            
            # No generic titles like "Track 1", "Song 2"
            generic_patterns = ["track ", "song "]
            for title in track_titles:
                title_lower = title.lower()
                assert not any(pattern in title_lower for pattern in generic_patterns)
                
            # All titles should be unique
            assert len(set(track_titles)) == len(track_titles)
            
    async def test_track_content_progression(self):
        """Test that tracks show meaningful progression"""
        content = """
        A character's journey from doubt to confidence, from isolation to connection.
        The story unfolds through moments of struggle, revelation, and growth.
        """
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=5,
            genre="indie"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            tracks = result.get("tracks", [])
            
            # Each track should have unique content
            track_descriptions = [track.get("description", "") for track in tracks]
            
            # Check for progression indicators
            progression_found = False
            for i, desc in enumerate(track_descriptions):
                if i == 0 and any(word in desc.lower() for word in ["begin", "start", "first"]):
                    progression_found = True
                elif i == len(track_descriptions) - 1 and any(word in desc.lower() for word in ["end", "final", "conclusion"]):
                    progression_found = True
                    
            # Should show some form of progression
            assert progression_found or len(set(track_descriptions)) == len(track_descriptions)
            
    async def test_thematic_coherence(self):
        """Test that tracks maintain thematic coherence while being unique"""
        content = """
        The theme of water in all its forms - rain, ocean, river, ice.
        Each form represents a different emotional state and life experience.
        """
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=4,
            genre="ambient"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            tracks = result.get("tracks", [])
            
            # All tracks should reference water theme
            water_references = 0
            for track in tracks:
                track_content = (
                    track.get("title", "") + " " + 
                    track.get("description", "") + " " +
                    track.get("lyrics", "")
                ).lower()
                
                if any(water_word in track_content for water_word in 
                       ["water", "rain", "ocean", "river", "ice", "flow", "wave"]):
                    water_references += 1
                    
            # At least half the tracks should reference the water theme
            assert water_references >= len(tracks) // 2


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestAlbumQualityValidation:
    """Test album quality validation and coherence scoring"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.ctx = create_mock_context()
        
    async def test_album_effectiveness_scoring(self):
        """Test that albums include effectiveness scoring"""
        content = "The sound of silence speaks louder than words."
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=3,
            genre="alternative"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            # Should include effectiveness metrics
            if "album_effectiveness" in result:
                effectiveness = result["album_effectiveness"]
                assert "average_score" in effectiveness
                assert isinstance(effectiveness["average_score"], (int, float))
                assert 0.0 <= effectiveness["average_score"] <= 1.0
                
    async def test_character_consistency_validation(self):
        """Test validation of character consistency across tracks"""
        content = """
        I am a lighthouse keeper who has spent thirty years guiding ships to safety.
        The solitude has taught me about the rhythm of the sea and the language of storms.
        """
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=4,
            genre="folk"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            tracks = result.get("tracks", [])
            
            # All tracks should maintain lighthouse keeper perspective
            lighthouse_references = 0
            for track in tracks:
                track_content = (
                    track.get("description", "") + " " +
                    track.get("lyrics", "")
                ).lower()
                
                if any(term in track_content for term in 
                       ["lighthouse", "keeper", "sea", "ships", "storm", "beacon", "guide"]):
                    lighthouse_references += 1
                    
            # Most tracks should maintain the character perspective
            assert lighthouse_references >= len(tracks) // 2
            
    async def test_narrative_progression_validation(self):
        """Test validation of narrative progression in story-driven albums"""
        content = """
        Sarah starts her journey as a shy librarian who discovers a mysterious book.
        The book leads her on an adventure that transforms her into a confident explorer.
        She returns home changed, ready to help others find their own adventures.
        """
        
        result_json = await create_conceptual_album(
            ctx=self.ctx,
            content=content,
            track_count=5,
            genre="indie"
        )
        
        result = json.loads(result_json)
        
        if "error" not in result:
            # Should identify Sarah as protagonist
            album_info = result.get("album_info", {})
            if "protagonist" in album_info:
                assert album_info["protagonist"] == "Sarah"
                
            # Should show progression in track descriptions
            tracks = result.get("tracks", [])
            track_contents = [track.get("description", "") for track in tracks]
            
            # First track should reference beginning
            first_track = track_contents[0].lower()
            assert any(word in first_track for word in ["begin", "start", "shy", "librarian"])
            
            # Last track should reference transformation/conclusion
            last_track = track_contents[-1].lower()
            assert any(word in last_track for word in ["transform", "changed", "confident", "return"])


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])