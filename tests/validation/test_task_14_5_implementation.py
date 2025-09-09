#!/usr/bin/env python3
"""
Test implementation of Task 14.5: Replace hardcoded style and emotional tags with wiki data
"""

import asyncio

import pytest
import pytest_asyncio

from server import SunoCommandGenerator
from wiki_data_models import MetaTag
from wiki_data_system import WikiDataManager


class TestTask145Implementation:
    """Test the implementation of Task 14.5"""

    @pytest_asyncio.fixture
    def mock_wiki_data_manager(self):
        """Create a mock wiki data manager with sample meta tags"""
        manager = WikiDataManager()

        # Mock some meta tags
        sample_tags = [
            MetaTag(
                tag="[rock]",
                category="style",
                description="Rock music style",
                compatible_genres=["rock", "metal"],
                source_url="test://example.com"
            ),
            MetaTag(
                tag="[uplifting]",
                category="emotional",
                description="Uplifting and positive mood",
                compatible_genres=[],
                source_url="test://example.com"
            ),
            MetaTag(
                tag="[verse-chorus]",
                category="structural",
                description="Basic verse-chorus structure",
                compatible_genres=[],
                source_url="test://example.com"
            ),
            MetaTag(
                tag="[strong vocals]",
                category="vocal",
                description="Powerful vocal delivery",
                compatible_genres=["rock", "pop"],
                source_url="test://example.com"
            )
        ]

        # Mock the get_meta_tags method
        async def mock_get_meta_tags(category=None):
            if category:
                return [tag for tag in sample_tags if tag.category == category]
            return sample_tags

        manager.get_meta_tags = mock_get_meta_tags
        return manager

    @pytest.mark.asyncio
    async def test_fallback_style_tags_without_wiki(self):
        """Test that style tags work without wiki data"""
        generator = SunoCommandGenerator(None)

        # Test rock genre
        style_tags = await generator.get_style_tags_for_genre("rock")
        assert len(style_tags) > 0
        assert any("guitar" in tag.lower() or "rock" in tag.lower() for tag in style_tags)

        # Test jazz genre
        style_tags = await generator.get_style_tags_for_genre("jazz")
        assert len(style_tags) > 0
        assert any("jazz" in tag.lower() or "smooth" in tag.lower() for tag in style_tags)

    @pytest.mark.asyncio
    async def test_fallback_style_tags_with_wiki(self, mock_wiki_data_manager):
        """Test that style tags use wiki data when available"""
        generator = SunoCommandGenerator(mock_wiki_data_manager)

        style_tags = await generator.get_style_tags_for_genre("rock")
        assert len(style_tags) > 0
        # Should get wiki data
        assert "[rock]" in style_tags

    @pytest.mark.asyncio
    async def test_fallback_structure_tags_without_wiki(self):
        """Test that structure tags work without wiki data"""
        generator = SunoCommandGenerator(None)

        # Test simple complexity
        structure_tags = await generator.get_structure_tags_for_complexity("simple")
        assert len(structure_tags) > 0
        assert any("verse" in tag.lower() or "chorus" in tag.lower() for tag in structure_tags)

        # Test complex complexity
        structure_tags = await generator.get_structure_tags_for_complexity("complex")
        assert len(structure_tags) > 0
        assert any("bridge" in tag.lower() or "dynamic" in tag.lower() for tag in structure_tags)

    @pytest.mark.asyncio
    async def test_fallback_vocal_tags_without_wiki(self):
        """Test that vocal tags work without wiki data"""
        generator = SunoCommandGenerator(None)

        # Test powerful vocal style
        vocal_tags = await generator.get_vocal_tags_for_style("powerful")
        assert len(vocal_tags) > 0
        assert any("strong" in tag.lower() or "powerful" in tag.lower() for tag in vocal_tags)

        # Test smooth vocal style
        vocal_tags = await generator.get_vocal_tags_for_style("smooth")
        assert len(vocal_tags) > 0
        assert any("smooth" in tag.lower() or "refined" in tag.lower() for tag in vocal_tags)

    @pytest.mark.asyncio
    async def test_dynamic_emotion_tags(self):
        """Test that emotion tags are generated dynamically"""
        generator = SunoCommandGenerator(None)

        # Test joy emotion
        emotion_tags = await generator._get_fallback_emotion_tags("joy")
        assert len(emotion_tags) > 0
        assert any("uplifting" in tag.lower() or "happy" in tag.lower() for tag in emotion_tags)

        # Test sadness emotion
        emotion_tags = await generator._get_fallback_emotion_tags("sadness")
        assert len(emotion_tags) > 0
        assert any("melancholic" in tag.lower() or "sad" in tag.lower() for tag in emotion_tags)

        # Test anger emotion
        emotion_tags = await generator._get_fallback_emotion_tags("anger")
        assert len(emotion_tags) > 0
        assert any("aggressive" in tag.lower() or "intense" in tag.lower() for tag in emotion_tags)

    @pytest.mark.asyncio
    async def test_semantic_emotion_mapping(self):
        """Test that semantic emotion mapping works correctly"""
        generator = SunoCommandGenerator(None)

        # Test that happiness maps to joy-like tags
        emotion_tags = await generator._get_fallback_emotion_tags("happiness")
        assert len(emotion_tags) > 0
        assert any("uplifting" in tag.lower() or "happy" in tag.lower() for tag in emotion_tags)

        # Test that melancholy maps to sadness-like tags
        emotion_tags = await generator._get_fallback_emotion_tags("melancholy")
        assert len(emotion_tags) > 0
        assert any("melancholic" in tag.lower() or "sad" in tag.lower() for tag in emotion_tags)

    @pytest.mark.asyncio
    async def test_instrument_tags_enhancement(self):
        """Test that instrument tags are enhanced with genre and emotion context"""
        generator = SunoCommandGenerator(None)

        # Test guitar with rock genre
        instrument_tags = await generator._get_fallback_instrument_tags("guitar", "rock")
        assert len(instrument_tags) > 0
        assert any("guitar" in tag.lower() for tag in instrument_tags)
        # Should have rock-specific enhancements
        assert any("electric" in tag.lower() or "distorted" in tag.lower() or "powerful" in tag.lower() for tag in instrument_tags)

        # Test piano with jazz genre
        instrument_tags = await generator._get_fallback_instrument_tags("piano", "jazz")
        assert len(instrument_tags) > 0
        assert any("piano" in tag.lower() for tag in instrument_tags)
        # Should have jazz-specific enhancements
        assert any("improvised" in tag.lower() or "sophisticated" in tag.lower() for tag in instrument_tags)

    @pytest.mark.asyncio
    async def test_genre_specific_tags_enhancement(self):
        """Test that genre-specific tags are enhanced with wiki data when available"""
        generator = SunoCommandGenerator(None)

        # Test rock genre tags
        genre_tags = await generator._get_fallback_genre_tags("rock")
        assert isinstance(genre_tags, dict)
        assert "style" in genre_tags
        assert "emotional" in genre_tags
        assert "instrumental" in genre_tags
        assert "vocal" in genre_tags

        # Check that rock characteristics are present
        all_tags = []
        for category_tags in genre_tags.values():
            all_tags.extend(category_tags)

        assert any("rock" in tag.lower() or "guitar" in tag.lower() for tag in all_tags)

    @pytest.mark.asyncio
    async def test_no_hardcoded_fallback_dictionaries(self):
        """Test that hardcoded fallback dictionaries are no longer used"""
        generator = SunoCommandGenerator(None)

        # These attributes should not exist anymore
        assert not hasattr(generator, 'fallback_style_tags')
        assert not hasattr(generator, 'fallback_structure_tags')
        assert not hasattr(generator, 'fallback_vocal_tags')

    @pytest.mark.asyncio
    async def test_emotional_mapping_integration(self):
        """Test that emotional mapping uses the new dynamic system"""
        generator = SunoCommandGenerator(None)

        # Test emotion to meta tag mapping
        emotions = ["joy", "sadness", "anger"]
        emotion_mapping = await generator.create_emotion_to_meta_tag_mapping(emotions)

        assert isinstance(emotion_mapping, dict)
        assert "joy" in emotion_mapping
        assert "sadness" in emotion_mapping
        assert "anger" in emotion_mapping

        # Check that joy maps to uplifting tags
        joy_tags = emotion_mapping["joy"]
        assert len(joy_tags) > 0
        assert any("uplifting" in tag.lower() or "happy" in tag.lower() for tag in joy_tags)


if __name__ == "__main__":
    # Run a simple test
    async def run_simple_test():
        test_instance = TestTask145Implementation()

        print("Testing fallback style tags...")
        await test_instance.test_fallback_style_tags_without_wiki()
        print("✓ Style tags test passed")

        print("Testing fallback structure tags...")
        await test_instance.test_fallback_structure_tags_without_wiki()
        print("✓ Structure tags test passed")

        print("Testing fallback vocal tags...")
        await test_instance.test_fallback_vocal_tags_without_wiki()
        print("✓ Vocal tags test passed")

        print("Testing dynamic emotion tags...")
        await test_instance.test_dynamic_emotion_tags()
        print("✓ Emotion tags test passed")

        print("Testing semantic emotion mapping...")
        await test_instance.test_semantic_emotion_mapping()
        print("✓ Semantic emotion mapping test passed")

        print("Testing instrument tags enhancement...")
        await test_instance.test_instrument_tags_enhancement()
        print("✓ Instrument tags enhancement test passed")

        print("Testing no hardcoded dictionaries...")
        await test_instance.test_no_hardcoded_fallback_dictionaries()
        print("✓ No hardcoded dictionaries test passed")

        print("Testing emotional mapping integration...")
        await test_instance.test_emotional_mapping_integration()
        print("✓ Emotional mapping integration test passed")

        print("\nAll Task 14.5 implementation tests passed! ✅")

    asyncio.run(run_simple_test())
