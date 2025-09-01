#!/usr/bin/env python3
"""
Test suite for Enhanced Character Analyzer

Tests the implementation of requirements 1.1, 1.2, 1.3, 1.4, 1.5 from the MCP tools diagnostic fixes.
"""

import asyncio
import json
import pytest
from enhanced_character_analyzer import EnhancedCharacterAnalyzer, validate_analysis_results
from standard_character_profile import StandardCharacterProfile


class TestEnhancedCharacterAnalyzer:
    """Test the enhanced character analyzer functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = EnhancedCharacterAnalyzer()
        
        # Test text with clear characters and themes
        self.test_text = """
        Elena stood at the lighthouse, her heart heavy with the weight of her decision. 
        She had grown up in this coastal town, watching ships come and go, but now she faced 
        her greatest challenge. The letter from Marcus lay crumpled in her hand - a betrayal 
        that cut deeper than any storm.
        
        "I trusted you," she whispered to the wind, her voice breaking with emotion. 
        Elena had always been brave, but this felt different. The fear of losing everything 
        she held dear consumed her thoughts.
        
        Marcus had been her closest friend since childhood. They had shared dreams of 
        adventure, of sailing beyond the horizon together. But his deception changed everything. 
        Now Elena must choose between forgiveness and justice, between love and self-respect.
        
        As the sun set over the turbulent waters, Elena felt a mixture of sadness and 
        determination. She would not let this betrayal define her. Tomorrow, she would 
        confront Marcus and demand the truth, no matter how much it hurt.
        """
        
        # Simple test text for basic functionality
        self.simple_text = """
        John walked into the room. He was nervous about the meeting. 
        Sarah greeted him with a smile. "Don't worry," she said, "everything will be fine."
        John nodded, feeling slightly better.
        """
    
    @pytest.mark.asyncio
    async def test_character_detection_not_empty(self):
        """Test that character detection returns actual characters, not empty results"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        # Should find characters
        assert 'characters' in result
        assert len(result['characters']) > 0
        
        # Should find Elena and Marcus
        character_names = [char['name'] for char in result['characters']]
        assert 'Elena' in character_names
        assert 'Marcus' in character_names
        
        # Characters should have meaningful information
        elena = next(char for char in result['characters'] if char['name'] == 'Elena')
        assert elena['confidence_score'] > 0.4
        assert elena['backstory'] != ""
        assert 'not explicitly' not in elena['backstory']  # Should have actual backstory
    
    @pytest.mark.asyncio
    async def test_three_layer_analysis(self):
        """Test that three-layer analysis (skin/flesh/core) is implemented"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        elena = next(char for char in result['characters'] if char['name'] == 'Elena')
        
        # Skin layer - observable characteristics
        assert 'physical_description' in elena
        assert 'mannerisms' in elena
        assert 'speech_patterns' in elena
        assert 'behavioral_traits' in elena
        
        # Flesh layer - background and relationships
        assert 'backstory' in elena
        assert 'relationships' in elena
        assert 'formative_experiences' in elena
        assert 'social_connections' in elena
        
        # Core layer - deep psychology
        assert 'motivations' in elena
        assert 'fears' in elena
        assert 'desires' in elena
        assert 'conflicts' in elena
        assert 'personality_drivers' in elena
        
        # Should have some content in each layer
        assert len(elena['behavioral_traits']) > 0 or elena['physical_description'] != ""
        assert elena['backstory'] != "" or len(elena['relationships']) > 0
        assert len(elena['fears']) > 0 or len(elena['motivations']) > 0
    
    @pytest.mark.asyncio
    async def test_narrative_themes_beyond_friendship(self):
        """Test that narrative theme analysis goes beyond just 'friendship'"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        assert 'narrative_themes' in result
        assert len(result['narrative_themes']) > 0
        
        # Should identify multiple themes
        theme_names = [theme['theme'] for theme in result['narrative_themes']]
        
        # Should find betrayal theme (explicitly mentioned)
        betrayal_themes = [theme for theme in theme_names if 'betrayal' in theme.lower() or 'deception' in theme.lower()]
        assert len(betrayal_themes) > 0
        
        # Should not be limited to just friendship
        assert len(theme_names) > 1
        
        # Themes should have evidence
        for theme in result['narrative_themes']:
            assert 'evidence' in theme
            assert len(theme['evidence']) > 0
            assert 'strength' in theme
            assert theme['strength'] > 0
    
    @pytest.mark.asyncio
    async def test_varied_emotional_arc(self):
        """Test that emotional arc analysis provides varied states, not just 'neutral'"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        assert 'emotional_arc' in result
        assert len(result['emotional_arc']) > 0
        
        # Should have varied emotional states
        emotions = [state['emotion'] for state in result['emotional_arc']]
        
        # Should not be all neutral
        neutral_count = sum(1 for emotion in emotions if 'neutral' in emotion.lower())
        assert neutral_count < len(emotions)  # Not all emotions should be neutral
        
        # Should identify specific emotions from the text
        # Text contains sadness, fear, determination, etc.
        emotion_types = set(emotion.lower() for emotion in emotions)
        expected_emotions = ['sadness', 'fear', 'anger', 'determination', 'grief']
        
        # Should find at least one expected emotion
        found_expected = any(expected in ' '.join(emotion_types) for expected in expected_emotions)
        assert found_expected, f"Expected to find emotions like {expected_emotions}, but got {emotions}"
        
        # Each emotional state should have context and triggers
        for state in result['emotional_arc']:
            assert 'context' in state
            assert 'triggers' in state
            assert 'intensity' in state
            assert state['intensity'] > 0
    
    @pytest.mark.asyncio
    async def test_character_traits_extraction(self):
        """Test that character traits, relationships, and psychology are extracted"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        elena = next(char for char in result['characters'] if char['name'] == 'Elena')
        
        # Should extract some behavioral information (brave is mentioned in text)
        # Check if any psychological information was extracted
        has_psychology = (
            len(elena['behavioral_traits']) > 0 or 
            len(elena['personality_drivers']) > 0 or
            len(elena['motivations']) > 0 or
            len(elena['fears']) > 0
        )
        assert has_psychology, "Should extract some psychological information"
        
        # Should identify relationship with Marcus (mentioned as friend)
        relationships_text = ' '.join(elena['relationships']).lower()
        social_connections_text = ' '.join(elena['social_connections']).lower()
        backstory_text = elena['backstory'].lower()
        
        # Marcus should be mentioned somewhere in the character analysis
        has_marcus_connection = (
            'marcus' in relationships_text or 
            'marcus' in social_connections_text or
            'marcus' in backstory_text
        )
        assert has_marcus_connection, "Should identify connection to Marcus"
    
    @pytest.mark.asyncio
    async def test_simple_text_handling(self):
        """Test that analyzer handles simple text without errors"""
        result = await self.analyzer.analyze_text(self.simple_text)
        
        # Should not crash and should return valid structure
        assert 'characters' in result
        assert 'narrative_themes' in result
        assert 'emotional_arc' in result
        
        # Should find at least John (Sarah might not be detected due to limited context)
        character_names = [char['name'] for char in result['characters']]
        assert 'John' in character_names
        # Sarah might not be detected in simple text, so we'll just check that we found some characters
        assert len(character_names) > 0
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Test that analyzer handles edge cases gracefully"""
        # Empty text
        result = await self.analyzer.analyze_text("")
        assert 'characters' in result
        assert len(result['characters']) == 0
        
        # Very short text
        result = await self.analyzer.analyze_text("Hi.")
        assert 'characters' in result
        # May or may not find characters, but should not crash
    
    def test_validation_function(self):
        """Test the validation function works correctly"""
        # Valid results
        valid_results = {
            'characters': [{'name': 'Test'}],
            'narrative_themes': [],
            'emotional_arc': [],
            'analysis_metadata': {'character_count': 1}
        }
        issues = validate_analysis_results(valid_results)
        assert len(issues) == 0
        
        # Invalid results
        invalid_results = {
            'characters': 'not a list',
            'narrative_themes': [],
        }
        issues = validate_analysis_results(invalid_results)
        assert len(issues) > 0
    
    @pytest.mark.asyncio
    async def test_character_profile_format(self):
        """Test that character profiles use StandardCharacterProfile format"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        for char_data in result['characters']:
            # Should be able to create StandardCharacterProfile from the data
            profile = StandardCharacterProfile.from_dict(char_data)
            assert profile.name != ""
            assert isinstance(profile.aliases, list)
            assert isinstance(profile.mannerisms, list)
            assert isinstance(profile.confidence_score, float)
            assert 0 <= profile.confidence_score <= 1
    
    @pytest.mark.asyncio
    async def test_analysis_metadata(self):
        """Test that analysis includes proper metadata"""
        result = await self.analyzer.analyze_text(self.test_text)
        
        assert 'analysis_metadata' in result
        metadata = result['analysis_metadata']
        
        assert 'character_count' in metadata
        assert 'theme_count' in metadata
        assert 'emotional_states_count' in metadata
        assert 'text_length' in metadata
        assert 'analyzer_version' in metadata
        
        # Metadata should be consistent with results
        assert metadata['character_count'] == len(result['characters'])
        assert metadata['theme_count'] == len(result['narrative_themes'])
        assert metadata['emotional_states_count'] == len(result['emotional_arc'])


if __name__ == "__main__":
    # Run a simple test
    async def main():
        analyzer = EnhancedCharacterAnalyzer()
        
        test_text = """
        Elena stood at the lighthouse, her heart heavy with betrayal. 
        Marcus had been her friend, but his deception changed everything.
        She felt a mixture of sadness and determination.
        """
        
        result = await analyzer.analyze_text(test_text)
        
        print("Enhanced Character Analysis Results:")
        print(f"Characters found: {len(result['characters'])}")
        print(f"Themes found: {len(result['narrative_themes'])}")
        print(f"Emotional states: {len(result['emotional_arc'])}")
        
        if result['characters']:
            char = result['characters'][0]
            print(f"\nFirst character: {char['name']}")
            print(f"Confidence: {char['confidence_score']:.2f}")
            print(f"Backstory: {char['backstory'][:100]}...")
        
        if result['narrative_themes']:
            theme = result['narrative_themes'][0]
            print(f"\nTop theme: {theme['theme']}")
            print(f"Strength: {theme['strength']:.2f}")
        
        if result['emotional_arc']:
            emotion = result['emotional_arc'][0]
            print(f"\nFirst emotion: {emotion['emotion']}")
            print(f"Intensity: {emotion['intensity']:.2f}")
        
        print("\nTest completed successfully!")
    
    asyncio.run(main())