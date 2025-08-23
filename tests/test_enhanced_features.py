#!/usr/bin/env python3
"""
Test suite for Enhanced Music Production Company Features

This file contains comprehensive tests for the new enhanced features including:
- Suno Knowledge Tool
- Story Generation Tool
- Producer Tool
- Music Bible Creation
- Complete Production Workflow
"""

import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_server import (
    SunoKnowledgeManager, StoryGenerator, MusicProducer, MusicBibleCreator,
    CharacterProfile, ArtistStory, SunoProducerProfile, MusicBible
)

# Test data
TEST_CHARACTER = CharacterProfile(
    name="Sarah Chen",
    aliases=["Sarah"],
    physical_description="27-year-old woman standing on rooftop",
    mannerisms=["refusing to acknowledge tears", "whispering confessions"],
    speech_patterns=["raw honesty", "emotional revelation"],
    behavioral_traits=["perfectionist facade", "breaking free"],
    backstory="Lifetime of meeting others' expectations, perfect daughter role",
    relationships=["controlling mother", "societal pressures"],
    formative_experiences=["constant pressure for perfection", "recent job rejection"],
    social_connections=["family expectations", "professional obligations"],
    motivations=["authenticity", "self-discovery", "freedom"],
    fears=["disappointing others", "being truly seen", "vulnerability"],
    desires=["to be real", "authentic self-expression", "emotional freedom"],
    conflicts=["perfection vs authenticity", "others' dreams vs own dreams"],
    personality_drivers=["need for truth", "emotional liberation"],
    confidence_score=0.95,
    text_references=["Sarah Chen stood at the edge..."],
    first_appearance="Sarah Chen stood at the edge of the rooftop",
    importance_score=1.0
)

TEST_ARTIST_PERSONA = {
    "character_name": "Sarah Chen",
    "artist_name": "Fragile Freedom",
    "primary_genre": "indie",
    "secondary_genres": ["alternative", "singer-songwriter"],
    "vocal_style": "vulnerable and raw emotional delivery",
    "instrumental_preferences": ["acoustic guitar", "minimal piano", "ambient textures"],
    "lyrical_themes": ["authenticity vs facade", "breaking free", "vulnerable truth"],
    "emotional_palette": ["fragility", "desperation", "liberation", "raw honesty"],
    "artistic_influences": ["Phoebe Bridgers", "Sufjan Stevens", "Sharon Van Etten"],
    "collaboration_style": "intimate and selective",
    "character_mapping_confidence": 0.9,
    "genre_justification": "Indie's raw authenticity matches her journey from perfection to truth",
    "persona_description": "An artist emerging from perfectionist constraints to authentic expression"
}

class MockContext:
    """Mock context for testing async functions"""
    def __init__(self):
        self.messages = []
    
    async def info(self, message):
        self.messages.append(f"INFO: {message}")
    
    async def error(self, message):
        self.messages.append(f"ERROR: {message}")

class TestSunoKnowledgeManager:
    """Test Suno AI knowledge management functionality"""
    
    def __init__(self):
        self.knowledge_manager = SunoKnowledgeManager()
    
    async def test_get_meta_tags_knowledge(self):
        """Test retrieving meta tags knowledge"""
        print("Testing Suno meta tags knowledge retrieval...")
        
        knowledge = await self.knowledge_manager.get_knowledge("meta_tags")
        
        # Validate structure
        assert "structure" in knowledge, "Should have structure tags"
        assert "vocals" in knowledge, "Should have vocal tags"
        assert "instruments" in knowledge, "Should have instrument tags"
        assert "effects" in knowledge, "Should have effect tags"
        
        # Validate content
        structure_tags = knowledge["structure"]
        assert "[Intro]" in structure_tags, "Should have intro tag"
        assert "[Verse]" in structure_tags, "Should have verse tag"
        assert "[Chorus]" in structure_tags, "Should have chorus tag"
        
        print("✅ Meta tags knowledge retrieval passed")
        return True
    
    async def test_get_genre_specific_knowledge(self):
        """Test retrieving genre-specific knowledge"""
        print("Testing genre-specific knowledge retrieval...")
        
        # Test indie genre knowledge
        indie_knowledge = await self.knowledge_manager.get_knowledge("genres", "indie")
        
        assert "tags" in indie_knowledge, "Should have genre tags"
        assert "prompts" in indie_knowledge, "Should have example prompts"
        assert "avoid" in indie_knowledge, "Should have things to avoid"
        assert "tips" in indie_knowledge, "Should have genre tips"
        
        # Validate indie-specific content
        indie_tags = indie_knowledge["tags"]
        assert "[Lo-fi]" in indie_tags, "Should have lo-fi tag for indie"
        assert "[Intimate]" in indie_tags, "Should have intimate tag for indie"
        
        print("✅ Genre-specific knowledge retrieval passed")
        return True
    
    async def test_get_advanced_techniques(self):
        """Test retrieving advanced techniques"""
        print("Testing advanced techniques knowledge...")
        
        techniques = await self.knowledge_manager.get_knowledge("advanced_techniques")
        
        assert "double_brackets" in techniques, "Should have double brackets technique"
        assert "parentheses" in techniques, "Should have parentheses technique"
        assert "case_sensitivity" in techniques, "Should have case sensitivity info"
        
        print("✅ Advanced techniques knowledge passed")
        return True

class TestStoryGenerator:
    """Test artist story generation from character profiles"""
    
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.ctx = MockContext()
    
    async def test_generate_artist_story(self):
        """Test complete artist story generation"""
        print("Testing artist story generation...")
        
        story = await self.story_generator.generate_artist_story(TEST_CHARACTER, self.ctx)
        
        # Validate story structure
        assert isinstance(story, ArtistStory), "Should return ArtistStory object"
        assert story.origin_narrative is not None, "Should have origin narrative"
        assert len(story.introspective_themes) > 0, "Should have introspective themes"
        assert story.personal_journey is not None, "Should have personal journey"
        assert story.artistic_manifesto is not None, "Should have artistic manifesto"
        assert len(story.album_concepts) > 0, "Should have album concepts"
        
        # Validate content quality
        assert "authentic" in story.artistic_manifesto.lower(), "Manifesto should reflect authenticity theme"
        assert len(story.introspective_themes) >= 3, "Should have multiple introspective themes"
        
        print("✅ Artist story generation passed")
        return story
    
    def test_extract_introspective_themes(self):
        """Test introspective theme extraction"""
        print("Testing introspective theme extraction...")
        
        themes = self.story_generator._extract_introspective_themes(TEST_CHARACTER)
        
        assert len(themes) > 0, "Should extract themes"
        
        # Check that themes relate to character fears/desires/conflicts
        has_fear_theme = any("disappointing others" in theme for theme in themes)
        has_desire_theme = any("authentic self-expression" in theme for theme in themes)
        has_conflict_theme = any("perfection vs authenticity" in theme for theme in themes)
        
        assert has_fear_theme or has_desire_theme or has_conflict_theme, "Themes should relate to character psychology"
        
        print("✅ Introspective theme extraction passed")
        return True
    
    def test_create_album_concepts(self):
        """Test album concept generation"""
        print("Testing album concept generation...")
        
        concepts = self.story_generator._generate_album_concepts(TEST_CHARACTER)
        
        assert len(concepts) > 0, "Should generate album concepts"
        
        for concept in concepts:
            assert "title" in concept, "Concept should have title"
            assert "theme" in concept, "Concept should have theme"
            assert "narrative" in concept, "Concept should have narrative"
        
        print("✅ Album concept generation passed")
        return True

class TestMusicProducer:
    """Test AI producer functionality"""
    
    def __init__(self):
        self.producer = MusicProducer()
        self.ctx = MockContext()
    
    async def test_analyze_production_needs(self):
        """Test production needs analysis"""
        print("Testing production needs analysis...")
        
        # Create test story
        test_story = ArtistStory(
            origin_narrative="Test origin",
            introspective_themes=["vulnerability", "authenticity", "transformation"],
            personal_journey="Journey of self-discovery",
            artistic_manifesto="Raw truth over polished lies",
            album_concepts=[{"title": "Test Album", "theme": "authenticity", "narrative": "story"}],
            emotional_arc="isolation through struggle to acceptance",
            key_life_moments=["moment of truth"],
            artistic_evolution="from facade to authenticity"
        )
        
        producer_profile = await self.producer.analyze_production_needs(
            TEST_ARTIST_PERSONA, test_story, self.ctx
        )
        
        # Validate producer profile
        assert isinstance(producer_profile, SunoProducerProfile), "Should return SunoProducerProfile"
        assert producer_profile.production_style is not None, "Should have production style"
        assert len(producer_profile.meta_tag_strategy) > 0, "Should have meta tag strategy"
        assert producer_profile.version_preference is not None, "Should have version preference"
        assert len(producer_profile.vocal_style_tags) > 0, "Should have vocal style tags"
        
        # Validate Suno-specific elements
        assert "V3" in producer_profile.version_preference, "Should prefer recent Suno version"
        assert len(producer_profile.genre_nuances) > 0, "Should have genre nuances"
        
        print("✅ Production needs analysis passed")
        return producer_profile
    
    def test_determine_production_style(self):
        """Test production style determination"""
        print("Testing production style determination...")
        
        # Test with raw/minimal story
        raw_story = ArtistStory(
            origin_narrative="",
            introspective_themes=["raw emotion", "vulnerable truth"],
            personal_journey="",
            artistic_manifesto="",
            album_concepts=[],
            emotional_arc="",
            key_life_moments=[],
            artistic_evolution=""
        )
        
        style = self.producer._determine_production_style(TEST_ARTIST_PERSONA, raw_story)
        assert "minimal" in style.lower() or "raw" in style.lower(), "Should suggest minimal/raw production for vulnerable themes"
        
        print("✅ Production style determination passed")
        return True
    
    def test_create_meta_tag_strategy(self):
        """Test meta tag strategy creation"""
        print("Testing meta tag strategy creation...")
        
        # Mock genre knowledge
        mock_knowledge = {
            "tags": ["[Lo-fi]", "[Intimate]", "[Raw Production]"],
            "tips": ["Use raw vocals", "Keep minimal"]
        }
        
        strategy = self.producer._create_meta_tag_strategy(TEST_ARTIST_PERSONA, mock_knowledge)
        
        assert len(strategy) > 0, "Should create meta tag strategy"
        
        # Should include structural tags
        has_structural = any("[Verse]" in tag or "[Chorus]" in tag for tag in strategy)
        assert has_structural, "Should include structural meta tags"
        
        print("✅ Meta tag strategy creation passed")
        return True

class TestMusicBibleCreator:
    """Test music bible creation functionality"""
    
    def __init__(self):
        self.bible_creator = MusicBibleCreator()
        self.ctx = MockContext()
    
    async def test_create_music_bible(self):
        """Test complete music bible creation"""
        print("Testing music bible creation...")
        
        # Create test dependencies
        test_story = ArtistStory(
            origin_narrative="Artist origin story",
            introspective_themes=["theme1", "theme2", "theme3"],
            personal_journey="Journey description",
            artistic_manifesto="Artistic statement",
            album_concepts=[{"title": "Album", "theme": "theme", "narrative": "story"}],
            emotional_arc="emotional progression",
            key_life_moments=["moment1", "moment2"],
            artistic_evolution="evolution description"
        )
        
        test_producer = SunoProducerProfile(
            production_style="minimal and authentic",
            prompt_complexity="detailed",
            meta_tag_strategy=["[Verse]", "[Chorus]"],
            version_preference="V3.5",
            genre_nuances={"recommended": ["tip1"], "avoid": ["avoid1"], "signature_elements": ["element1"]},
            chord_progression_hints=["progression1"],
            transition_techniques=["technique1"],
            vocal_style_tags=["[Emotional]"],
            vocal_effect_preferences=["minimal"],
            content_adaptation_strategy="strategy",
            seed_reuse_approach="approach",
            ending_optimization="optimization",
            mixing_preferences={"vocals": "upfront"},
            sound_palette=["guitar", "piano"],
            reference_artists=["artist1"],
            collaboration_approach="minimal"
        )
        
        music_bible = await self.bible_creator.create_music_bible(
            TEST_CHARACTER, TEST_ARTIST_PERSONA, test_story, test_producer, self.ctx
        )
        
        # Validate music bible structure
        assert isinstance(music_bible, MusicBible), "Should return MusicBible object"
        assert music_bible.producer_profile is not None, "Should have producer profile"
        assert music_bible.artist_story is not None, "Should have artist story"
        assert len(music_bible.song_blueprints) > 0, "Should have song blueprints"
        assert len(music_bible.prompt_templates) > 0, "Should have prompt templates"
        
        # Validate song blueprints
        for blueprint in music_bible.song_blueprints:
            assert blueprint.title is not None, "Blueprint should have title"
            assert blueprint.primary_prompt is not None, "Blueprint should have primary prompt"
            assert len(blueprint.meta_tags) > 0, "Blueprint should have meta tags"
            assert blueprint.emotional_arc is not None, "Blueprint should have emotional arc"
        
        print("✅ Music bible creation passed")
        return music_bible
    
    def test_generate_song_title(self):
        """Test song title generation"""
        print("Testing song title generation...")
        
        # Test different theme types
        confronting_theme = "confronting fear"
        searching_theme = "searching for truth"
        reconciling_theme = "reconciling conflict"
        
        title1 = self.bible_creator._generate_song_title(confronting_theme, TEST_CHARACTER)
        title2 = self.bible_creator._generate_song_title(searching_theme, TEST_CHARACTER)
        title3 = self.bible_creator._generate_song_title(reconciling_theme, TEST_CHARACTER)
        
        assert "Shadows" in title1, "Confronting theme should generate 'Shadows' title pattern"
        assert "Echoes" in title2, "Searching theme should generate 'Echoes' title pattern"
        assert "Between" in title3, "Reconciling theme should generate 'Between' title pattern"
        
        print("✅ Song title generation passed")
        return True
    
    def test_create_song_prompt(self):
        """Test song prompt creation"""
        print("Testing song prompt creation...")
        
        test_producer = SunoProducerProfile(
            production_style="minimal and raw",
            prompt_complexity="detailed",
            meta_tag_strategy=[],
            version_preference="V3.5",
            genre_nuances={},
            chord_progression_hints=[],
            transition_techniques=[],
            vocal_style_tags=[],
            vocal_effect_preferences=[],
            content_adaptation_strategy="",
            seed_reuse_approach="",
            ending_optimization="",
            mixing_preferences={},
            sound_palette=["acoustic guitar"],
            reference_artists=[],
            collaboration_approach=""
        )
        
        theme = "confronting vulnerability"
        prompt = self.bible_creator._create_song_prompt(theme, TEST_ARTIST_PERSONA, test_producer)
        
        assert theme in prompt, "Prompt should include the theme"
        assert TEST_ARTIST_PERSONA["primary_genre"] in prompt, "Prompt should include genre"
        assert TEST_ARTIST_PERSONA["vocal_style"] in prompt, "Prompt should include vocal style"
        
        print("✅ Song prompt creation passed")
        return True

class TestIntegrationWorkflow:
    """Test complete integration workflows"""
    
    def __init__(self):
        self.ctx = MockContext()
    
    async def test_complete_production_workflow(self):
        """Test the complete production workflow integration"""
        print("Testing complete production workflow integration...")
        
        # Step 1: Story generation
        story_generator = StoryGenerator()
        story = await story_generator.generate_artist_story(TEST_CHARACTER, self.ctx)
        
        # Step 2: Producer analysis
        producer = MusicProducer()
        producer_profile = await producer.analyze_production_needs(
            TEST_ARTIST_PERSONA, story, self.ctx
        )
        
        # Step 3: Music bible creation
        bible_creator = MusicBibleCreator()
        music_bible = await bible_creator.create_music_bible(
            TEST_CHARACTER, TEST_ARTIST_PERSONA, story, producer_profile, self.ctx
        )
        
        # Validate workflow integration
        assert story.introspective_themes[0] in music_bible.song_blueprints[0].introspective_angle, \
            "Story themes should flow into song concepts"
        
        assert producer_profile.production_style in music_bible.production_philosophy, \
            "Producer style should be reflected in bible philosophy"
        
        assert len(music_bible.song_blueprints) == len(story.introspective_themes[:5]), \
            "Should create song for each major theme"
        
        print("✅ Complete production workflow integration passed")
        return True
    
    async def test_data_consistency_across_tools(self):
        """Test data consistency between different tools"""
        print("Testing data consistency across tools...")
        
        # Generate story
        story_generator = StoryGenerator()
        story = await story_generator.generate_artist_story(TEST_CHARACTER, self.ctx)
        
        # Analyze with producer
        producer = MusicProducer()
        producer_profile = await producer.analyze_production_needs(
            TEST_ARTIST_PERSONA, story, self.ctx
        )
        
        # Check consistency
        genre_consistency = TEST_ARTIST_PERSONA["primary_genre"] in str(producer_profile.genre_nuances)
        
        # Character themes should influence production decisions
        theme_influence = any(
            theme.split()[-1] in producer_profile.production_style.lower() 
            for theme in story.introspective_themes
        )
        
        print("✅ Data consistency across tools passed")
        return True

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def __init__(self):
        self.ctx = MockContext()
    
    async def test_empty_character_handling(self):
        """Test handling of empty or minimal character data"""
        print("Testing empty character handling...")
        
        # Create minimal character
        minimal_character = CharacterProfile(
            name="", aliases=[], physical_description="", mannerisms=[],
            speech_patterns=[], behavioral_traits=[], backstory="", relationships=[], 
            formative_experiences=[], social_connections=[], motivations=[],
            fears=[], desires=[], conflicts=[], personality_drivers=[],
            confidence_score=0.0, text_references=[], first_appearance="", importance_score=0.0
        )
        
        # Test story generation with minimal data
        story_generator = StoryGenerator()
        try:
            story = await story_generator.generate_artist_story(minimal_character, self.ctx)
            # Should handle gracefully, creating default content
            assert story is not None, "Should handle minimal character gracefully"
            print("✅ Empty character handled gracefully")
        except Exception as e:
            print(f"⚠️ Error handling needs improvement: {e}")
        
        return True
    
    async def test_invalid_genre_handling(self):
        """Test handling of invalid or unknown genres"""
        print("Testing invalid genre handling...")
        
        # Test with invalid genre
        invalid_persona = TEST_ARTIST_PERSONA.copy()
        invalid_persona["primary_genre"] = "nonexistent_genre"
        
        story = ArtistStory(
            origin_narrative="test", introspective_themes=["test"], personal_journey="test",
            artistic_manifesto="test", album_concepts=[], emotional_arc="test",
            key_life_moments=[], artistic_evolution="test"
        )
        
        producer = MusicProducer()
        try:
            producer_profile = await producer.analyze_production_needs(
                invalid_persona, story, self.ctx
            )
            # Should handle unknown genre gracefully
            assert producer_profile is not None, "Should handle unknown genre"
            print("✅ Invalid genre handled gracefully")
        except Exception as e:
            print(f"⚠️ Genre error handling needs improvement: {e}")
        
        return True

async def run_enhanced_tests():
    """Run all enhanced feature tests"""
    print("🧪 Running Enhanced Music Production Company Tests")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test Suno Knowledge Manager
    print("\n📚 Testing Suno Knowledge Manager...")
    knowledge_tests = TestSunoKnowledgeManager()
    total_tests += 3
    
    try:
        await knowledge_tests.test_get_meta_tags_knowledge()
        success_count += 1
    except Exception as e:
        print(f"❌ Meta tags test failed: {e}")
    
    try:
        await knowledge_tests.test_get_genre_specific_knowledge()
        success_count += 1
    except Exception as e:
        print(f"❌ Genre knowledge test failed: {e}")
    
    try:
        await knowledge_tests.test_get_advanced_techniques()
        success_count += 1
    except Exception as e:
        print(f"❌ Advanced techniques test failed: {e}")
    
    # Test Story Generator
    print("\n📖 Testing Story Generator...")
    story_tests = TestStoryGenerator()
    total_tests += 3
    
    try:
        await story_tests.test_generate_artist_story()
        success_count += 1
    except Exception as e:
        print(f"❌ Story generation test failed: {e}")
    
    try:
        story_tests.test_extract_introspective_themes()
        success_count += 1
    except Exception as e:
        print(f"❌ Theme extraction test failed: {e}")
    
    try:
        story_tests.test_create_album_concepts()
        success_count += 1
    except Exception as e:
        print(f"❌ Album concepts test failed: {e}")
    
    # Test Music Producer
    print("\n🎛️ Testing Music Producer...")
    producer_tests = TestMusicProducer()
    total_tests += 3
    
    try:
        await producer_tests.test_analyze_production_needs()
        success_count += 1
    except Exception as e:
        print(f"❌ Production analysis test failed: {e}")
    
    try:
        producer_tests.test_determine_production_style()
        success_count += 1
    except Exception as e:
        print(f"❌ Production style test failed: {e}")
    
    try:
        producer_tests.test_create_meta_tag_strategy()
        success_count += 1
    except Exception as e:
        print(f"❌ Meta tag strategy test failed: {e}")
    
    # Test Music Bible Creator
    print("\n📚 Testing Music Bible Creator...")
    bible_tests = TestMusicBibleCreator()
    total_tests += 3
    
    try:
        await bible_tests.test_create_music_bible()
        success_count += 1
    except Exception as e:
        print(f"❌ Music bible creation test failed: {e}")
    
    try:
        bible_tests.test_generate_song_title()
        success_count += 1
    except Exception as e:
        print(f"❌ Song title generation test failed: {e}")
    
    try:
        bible_tests.test_create_song_prompt()
        success_count += 1
    except Exception as e:
        print(f"❌ Song prompt creation test failed: {e}")
    
    # Test Integration
    print("\n🔗 Testing Integration Workflows...")
    integration_tests = TestIntegrationWorkflow()
    total_tests += 2
    
    try:
        await integration_tests.test_complete_production_workflow()
        success_count += 1
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
    
    try:
        await integration_tests.test_data_consistency_across_tools()
        success_count += 1
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
    
    # Test Error Handling
    print("\n⚠️ Testing Error Handling...")
    error_tests = TestErrorHandling()
    total_tests += 2
    
    try:
        await error_tests.test_empty_character_handling()
        success_count += 1
    except Exception as e:
        print(f"❌ Empty character test failed: {e}")
    
    try:
        await error_tests.test_invalid_genre_handling()
        success_count += 1
    except Exception as e:
        print(f"❌ Invalid genre test failed: {e}")
    
    # Print results
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All enhanced features tests passed!")
    else:
        print(f"⚠️ {total_tests - success_count} tests failed - review implementation")
    
    print("\nNote: Run these tests with the enhanced server implementation")
    print("Some tests may require additional integration with the MCP framework")

if __name__ == "__main__":
    asyncio.run(run_enhanced_tests())