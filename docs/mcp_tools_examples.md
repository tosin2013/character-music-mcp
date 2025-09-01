# MCP Tools Usage Examples

## Overview

This document provides comprehensive working examples for all MCP tools after the diagnostic fixes. Each example includes proper input formats, expected outputs, and integration patterns.

## Individual Tool Examples

### 1. analyze_character_text

#### Basic Character Analysis

```python
import asyncio
from mcp_tools_integration import analyze_character_text
from mcp_shared_models import Context

async def example_character_analysis():
    """Example of basic character analysis"""
    
    # Sample text with clear character descriptions
    text = """
    Elena Rodriguez stood at the piano, her fingers dancing across the keys with 
    the precision of someone who had trained at the Barcelona Conservatory for 
    fifteen years. As a former jazz musician turned music teacher, she brought 
    passion to every lesson. Her students admired her dedication to preserving 
    musical heritage while embracing modern techniques.
    
    Elena's backstory was one of transformation. Born into a family of classical 
    musicians, she had rebelled in her twenties by joining a jazz fusion band. 
    Now, at forty-two, she found herself bridging both worlds, teaching young 
    musicians to respect tradition while finding their own voice.
    
    Her greatest fear was that the art of improvisation would be lost to 
    digital perfection. Her deepest desire was to inspire a new generation 
    of musicians who could feel the music, not just play it.
    """
    
    # Create context
    ctx = Context()
    
    # Analyze the text
    result = await analyze_character_text(text, ctx)
    
    # Display results
    print("=== Character Analysis Results ===")
    
    # Characters found
    characters = result["characters"]
    print(f"Characters found: {len(characters)}")
    
    for i, char_data in enumerate(characters):
        char = StandardCharacterProfile.from_dict(char_data)
        print(f"\nCharacter {i+1}: {char.name}")
        print(f"Physical: {char.physical_description}")
        print(f"Backstory: {char.backstory}")
        print(f"Motivations: {char.motivations}")
        print(f"Fears: {char.fears}")
        print(f"Desires: {char.desires}")
    
    # Narrative themes
    themes = result["narrative_themes"]
    print(f"\nNarrative themes: {themes}")
    
    # Emotional arc
    emotional_arc = result["emotional_arc"]
    print(f"\nEmotional arc:")
    for phase, emotion in emotional_arc.items():
        print(f"  {phase}: {emotion}")
    
    # Metadata
    metadata = result["analysis_metadata"]
    print(f"\nAnalysis metadata:")
    print(f"  Text length: {metadata['text_length']}")
    print(f"  Character count: {metadata['character_count']}")
    print(f"  Confidence: {metadata['confidence']:.2f}")
    
    return result

# Run the example
if __name__ == "__main__":
    asyncio.run(example_character_analysis())
```

**Expected Output:**
```
=== Character Analysis Results ===
Characters found: 1

Character 1: Elena Rodriguez
Physical: fingers dancing across keys with precision
Backstory: Former jazz musician turned music teacher, trained at Barcelona Conservatory
Motivations: ['preserve musical heritage', 'embrace modern techniques', 'inspire new generation']
Fears: ['art of improvisation being lost to digital perfection']
Desires: ['inspire musicians who can feel the music']

Narrative themes: ['musical education', 'tradition vs innovation', 'artistic transformation']

Emotional arc:
  beginning: passionate
  middle: reflective
  end: hopeful

Analysis metadata:
  Text length: 1247
  Character count: 1
  Confidence: 0.92
```

#### Multi-Character Analysis

```python
async def example_multi_character_analysis():
    """Example with multiple characters"""
    
    text = """
    The lighthouse keeper's daughter, Emma, had always been drawn to the sea. 
    Every night, she would climb to the top of the lighthouse and sing to the waves, 
    her voice carrying melodies that seemed to calm even the stormiest waters.
    
    Her father, Old Tom, worried about her obsession with the ocean's mysteries. 
    A practical man who had tended the lighthouse for thirty years, he feared 
    Emma's dreams would lead her away from the safety of their coastal home.
    
    One stormy night, Emma discovered a message in a bottle that would change 
    everything. The note was from Marcus, a traveling musician who had heard 
    her singing from his ship and was enchanted by her voice.
    """
    
    ctx = Context()
    result = await analyze_character_text(text, ctx)
    
    print("=== Multi-Character Analysis ===")
    characters = result["characters"]
    
    for char_data in characters:
        char = StandardCharacterProfile.from_dict(char_data)
        print(f"\nCharacter: {char.name}")
        print(f"Role: {char.first_appearance}")
        print(f"Relationships: {char.relationships}")
        print(f"Motivations: {char.motivations}")
    
    return result

asyncio.run(example_multi_character_analysis())
```

### 2. generate_artist_personas

#### Basic Persona Generation

```python
async def example_persona_generation():
    """Example of generating artist personas from character analysis"""
    
    # First, analyze a character
    character_text = """
    Jake Morrison is a former truck driver turned country songwriter. 
    He writes about life on the road, small-town values, and the struggles 
    of working-class America. His weathered hands tell stories of years 
    behind the wheel, but now they craft melodies on his acoustic guitar.
    
    Jake's music comes from authentic experience - the loneliness of long 
    hauls, the beauty of sunrise over wheat fields, the camaraderie of 
    truck stops. He fears that his blue-collar background makes him an 
    outsider in Nashville's polished music scene, but his desire to give 
    voice to forgotten Americans drives him forward.
    """
    
    ctx = Context()
    
    # Step 1: Character analysis
    character_result = await analyze_character_text(character_text, ctx)
    
    # Step 2: Generate personas
    persona_result = await generate_artist_personas(character_result, ctx)
    
    print("=== Artist Persona Generation ===")
    
    # Display personas
    personas = persona_result["personas"]
    for i, persona_data in enumerate(personas):
        persona = ArtistPersona.from_dict(persona_data)
        print(f"\nPersona {i+1}: {persona.name}")
        print(f"Genre: {persona.genre}")
        print(f"Style: {persona.style_description}")
        print(f"Vocal characteristics: {persona.vocal_characteristics}")
        print(f"Lyrical themes: {persona.lyrical_themes}")
        print(f"Production preferences: {persona.production_preferences}")
        print(f"Character inspiration: {persona.character_inspiration}")
    
    # Genre mappings
    mappings = persona_result["genre_mappings"]
    print(f"\nGenre mappings: {mappings}")
    
    # Style recommendations
    recommendations = persona_result["style_recommendations"]
    print(f"Style recommendations: {recommendations}")
    
    return persona_result

asyncio.run(example_persona_generation())
```

**Expected Output:**
```
=== Artist Persona Generation ===

Persona 1: Jake Morrison
Genre: country
Style: authentic storytelling with acoustic foundation
Vocal characteristics: ['weathered', 'honest', 'conversational', 'working-class authenticity']
Lyrical themes: ['life on the road', 'small-town values', 'working-class struggles', 'American landscapes']
Production preferences: ['acoustic guitar foundation', 'minimal production', 'authentic recording', 'truck stop ambiance']
Character inspiration: Former truck driver with authentic blue-collar experience

Genre mappings: {'country': ['authentic', 'storytelling', 'working-class'], 'folk': ['acoustic', 'narrative', 'americana']}
Style recommendations: ['outlaw country', 'americana', 'folk country', 'trucker country']
```

### 3. creative_music_generation

#### Creative Concept Development

```python
async def example_creative_generation():
    """Example of creative music generation with meaningful analysis"""
    
    concept = "The bittersweet feeling of leaving home for the first time"
    style_preference = "indie folk"
    
    ctx = Context()
    result = await creative_music_generation(concept, style_preference, ctx)
    
    print("=== Creative Music Generation ===")
    
    # Concept analysis
    analysis = result["concept_analysis"]
    print(f"Key elements: {analysis['key_elements']}")
    print(f"Musical themes: {analysis['musical_themes']}")
    print(f"Emotional content: {analysis['emotional_content']}")
    print(f"Genre suggestions: {analysis['genre_suggestions']}")
    
    # Creative variations
    variations = result["creative_variations"]
    print(f"\nCreative variations ({len(variations)}):")
    for i, variation in enumerate(variations):
        print(f"  {i+1}. {variation['title']}")
        print(f"     Approach: {variation['approach']}")
        print(f"     Elements: {variation['musical_elements']}")
    
    # Production commands
    commands = result["production_commands"]
    print(f"\nSuno AI Commands:")
    for cmd in commands:
        print(f"  {cmd}")
    
    # Style adaptations
    adaptations = result["style_adaptations"]
    print(f"\nStyle adaptations for {style_preference}:")
    print(f"  Instrumentation: {adaptations['instrumentation']}")
    print(f"  Tempo: {adaptations['tempo']}")
    print(f"  Mood: {adaptations['mood']}")
    
    return result

asyncio.run(example_creative_generation())
```

### 4. complete_workflow

#### End-to-End Workflow Example

```python
async def example_complete_workflow():
    """Example of complete workflow execution"""
    
    input_text = """
    Maria Santos grew up in the vibrant streets of Mexico City, where mariachi 
    music filled the air every evening. As a child, she would sneak out to 
    listen to the street musicians, dreaming of one day joining their ranks. 
    
    Now twenty-eight, Maria has moved to Los Angeles, carrying her grandmother's 
    vintage guitar and a heart full of traditional songs. She struggles to 
    blend her Mexican heritage with the contemporary music scene, fearing that 
    authenticity might be lost in translation.
    
    Her deepest desire is to create music that honors her roots while speaking 
    to a new generation of Mexican-Americans who, like her, navigate between 
    two worlds.
    """
    
    ctx = Context()
    
    print("=== Complete Workflow Execution ===")
    print("Starting workflow...")
    
    try:
        result = await complete_workflow(input_text, ctx)
        
        if result["workflow_status"] == "completed":
            print("✅ Workflow completed successfully!")
            
            # Display results from each step
            print("\n--- Character Analysis ---")
            characters = result["analysis"]["characters"]
            print(f"Characters found: {len(characters)}")
            
            print("\n--- Artist Personas ---")
            personas = result["personas"]["personas"]
            print(f"Personas generated: {len(personas)}")
            
            print("\n--- Suno Commands ---")
            commands = result["commands"]["suno_commands"]
            print(f"Commands created: {len(commands)}")
            for cmd in commands[:3]:  # Show first 3
                print(f"  {cmd}")
            
            # Execution metadata
            metadata = result["execution_metadata"]
            print(f"\nExecution metadata:")
            print(f"  Steps completed: {metadata['steps_completed']}")
            print(f"  Total time: {metadata['total_time']:.2f}s")
            
        else:
            print("❌ Workflow failed")
            errors = result["execution_metadata"]["errors"]
            for error in errors:
                print(f"  Error: {error}")
    
    except Exception as e:
        print(f"❌ Workflow exception: {e}")
    
    return result

asyncio.run(example_complete_workflow())
```

### 5. process_universal_content

#### Dynamic Content Processing

```python
async def example_universal_content_processing():
    """Example of dynamic content processing without hardcoded content"""
    
    # Test with different character descriptions
    test_cases = [
        {
            "description": """
            Sarah Chen is a classically trained violinist who moved to Nashville 
            to explore country music. She struggles with blending her formal training 
            with the raw emotion of country storytelling.
            """,
            "genre": "country",
            "location": "Nashville"
        },
        {
            "description": """
            DJ Khalil grew up in Detroit's underground hip-hop scene. He produces 
            beats that blend classic Motown samples with modern trap elements, 
            creating a unique sound that honors his city's musical legacy.
            """,
            "genre": "hip-hop"
        },
        {
            "description": """
            Luna Blackwood is a gothic folk singer from the Pacific Northwest. 
            Her haunting melodies are inspired by ancient forests and forgotten 
            folklore, creating atmospheric music that transports listeners to 
            mystical realms.
            """,
            "genre": "gothic folk",
            "location": "Pacific Northwest"
        }
    ]
    
    ctx = Context()
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: Dynamic Processing ===")
        
        result = await process_universal_content(
            character_description=test_case["description"],
            genre=test_case.get("genre"),
            location=test_case.get("location"),
            ctx=ctx
        )
        
        # Verify no hardcoded content
        result_str = str(result)
        assert "Bristol" not in result_str, "Found hardcoded Bristol reference"
        assert "Marcus" not in result_str, "Found hardcoded Marcus reference"
        
        print(f"✅ No hardcoded content detected")
        
        # Display results
        character = result["character"]
        print(f"Character name: {character['name']}")
        print(f"Genre: {result['genre']}")
        print(f"Location: {result['location']}")
        print(f"Backstory preview: {result['backstory'][:100]}...")
        
        # Processing metadata
        metadata = result["processing_metadata"]
        print(f"Extraction confidence: {metadata['extraction_confidence']:.2f}")
        print(f"Genre source: {metadata['genre_source']}")

asyncio.run(example_universal_content_processing())
```

### 6. create_character_album

#### Album Creation with Unique Tracks

```python
async def example_character_album_creation():
    """Example of creating character-based album with unique tracks"""
    
    character_description = """
    Tommy "Wheels" Rodriguez is a former motorcycle mechanic turned blues guitarist. 
    After losing his leg in an accident, he channeled his pain and resilience into 
    music. His blues are raw and honest, telling stories of working-class struggle, 
    physical challenges, and the healing power of music.
    """
    
    ctx = Context()
    
    result = await create_character_album(
        character_description=character_description,
        genre="blues",
        album_theme="Road to Recovery",
        track_count=6,
        ctx=ctx
    )
    
    print("=== Character Album Creation ===")
    
    # Album information
    album = result["album_info"]
    print(f"Album: '{album['title']}' by {album['artist']}")
    print(f"Genre: {album['genre']}")
    print(f"Theme: {album['theme']}")
    print(f"Track count: {album['track_count']}")
    
    # Individual tracks
    tracks = result["tracks"]
    print(f"\nTracks:")
    
    for track in tracks:
        print(f"\n{track['track_number']}. {track['title']}")
        print(f"   Theme: {track['theme']}")
        print(f"   Mood: {track['mood']}")
        print(f"   Character connection: {track['character_connection']}")
        print(f"   Lyrics preview: {track['lyrics'][:100]}...")
        print(f"   Suno command: {track['suno_command']}")
        
        # Verify unique content
        if track['track_number'] > 1:
            prev_track = tracks[track['track_number'] - 2]
            assert track['lyrics'] != prev_track['lyrics'], f"Track {track['track_number']} has duplicate lyrics"
            print(f"   ✅ Unique lyrics confirmed")
    
    # Character filter
    char_filter = result["character_filter"]
    print(f"\nCharacter filter applied: {char_filter}")
    
    # Album metadata
    metadata = result["album_metadata"]
    print(f"\nAlbum metadata:")
    print(f"  Character consistency: {metadata['character_consistency']:.2f}")
    print(f"  Genre adherence: {metadata['genre_adherence']:.2f}")
    
    return result

asyncio.run(example_character_album_creation())
```

### 7. create_story_integrated_album

#### Story-Based Album Creation

```python
async def example_story_integrated_album():
    """Example of creating album from narrative story"""
    
    narrative = """
    The lighthouse keeper's daughter, Emma, had always been drawn to the sea. 
    Every night, she would climb to the top of the lighthouse and sing to the waves, 
    her voice carrying melodies that seemed to calm even the stormiest waters.
    
    Her father, Old Tom, worried about her obsession with the ocean's mysteries. 
    A practical man who had tended the lighthouse for thirty years, he feared 
    Emma's dreams would lead her away from the safety of their coastal home.
    
    One stormy night, Emma discovered a message in a bottle that would change 
    everything. The note was from Marcus, a traveling musician who had heard 
    her singing from his ship and was enchanted by her voice. He wrote of distant 
    shores and musical adventures, inviting her to join him on a journey across 
    the seven seas.
    
    Emma faced an impossible choice: stay with her father and the lighthouse 
    that had been her world, or follow her heart into the unknown waters of 
    love and music.
    """
    
    ctx = Context()
    
    result = await create_story_integrated_album(
        narrative_text=narrative,
        musical_style="folk",
        ctx=ctx
    )
    
    print("=== Story-Integrated Album ===")
    
    # Check character detection success
    integration_meta = result["integration_metadata"]
    if integration_meta["character_detection_success"]:
        print("✅ Character detection successful")
        
        # Story analysis
        story = result["story_analysis"]
        characters = story["characters"]
        print(f"\nCharacters detected: {[c['name'] for c in characters]}")
        print(f"Plot points: {story['plot_points']}")
        print(f"Themes: {story['themes']}")
        
        # Album concept
        concept = result["album_concept"]
        print(f"\nAlbum: '{concept['title']}'")
        print(f"Narrative structure: {concept['narrative_structure']}")
        print(f"Character focus: {concept['character_focus']}")
        print(f"Musical style: {concept['musical_style']}")
        
        # Tracks
        tracks = result["tracks"]
        print(f"\nTracks ({len(tracks)}):")
        for track in tracks:
            print(f"  {track['title']} - {track['character_connection']}")
        
        # Integration quality
        print(f"\nIntegration quality:")
        print(f"  Story coherence: {integration_meta['story_coherence']:.2f}")
        print(f"  Musical alignment: {integration_meta['musical_alignment']:.2f}")
        
    else:
        print("❌ Character detection failed")
        print("This indicates an issue with the character detection algorithm")
    
    return result

asyncio.run(example_story_integrated_album())
```

### 8. analyze_artist_psychology

#### Psychological Analysis Example

```python
async def example_psychology_analysis():
    """Example of artist psychology analysis"""
    
    # Create character profile
    character_profile = {
        "name": "Alex Rivera",
        "physical_description": "Tall, expressive eyes, calloused fingertips from guitar playing",
        "backstory": "Former street performer who overcame addiction through music",
        "motivations": ["express inner turmoil", "connect with others", "inspire recovery"],
        "fears": ["relapse", "being misunderstood", "creative stagnation"],
        "desires": ["artistic recognition", "emotional healing", "helping others"],
        "conflicts": ["perfectionism vs spontaneity", "vulnerability vs protection"],
        "personality_drivers": ["empathy", "introspection", "authenticity", "resilience"]
    }
    
    ctx = Context()
    
    result = await analyze_artist_psychology(character_profile, ctx)
    
    print("=== Artist Psychology Analysis ===")
    
    # Psychological profile
    psychology = result["psychological_profile"]
    print(f"Personality type: {psychology['personality_type']}")
    print(f"Creative drivers: {psychology['creative_drivers']}")
    print(f"Emotional patterns: {psychology['emotional_patterns']}")
    print(f"Artistic influences: {psychology['artistic_influences']}")
    
    # Musical implications
    music = result["musical_implications"]
    print(f"\nMusical implications:")
    print(f"  Preferred genres: {music['preferred_genres']}")
    print(f"  Lyrical themes: {music['lyrical_themes']}")
    print(f"  Performance style: {music['performance_style']}")
    print(f"  Collaboration tendencies: {music['collaboration_tendencies']}")
    
    # Creative recommendations
    recommendations = result["creative_recommendations"]
    print(f"\nCreative recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")
    
    # Analysis metadata
    metadata = result["analysis_metadata"]
    print(f"\nAnalysis metadata:")
    print(f"  Confidence score: {metadata['confidence_score']:.2f}")
    print(f"  Analysis depth: {metadata['analysis_depth']}")
    print(f"  Psychological complexity: {metadata['psychological_complexity']:.2f}")
    
    return result

asyncio.run(example_psychology_analysis())
```

### 9. crawl_suno_wiki_best_practices

#### Wiki Best Practices Retrieval

```python
async def example_wiki_best_practices():
    """Example of retrieving Suno wiki best practices"""
    
    ctx = Context()
    
    # Test different practice types
    practice_types = ["all", "prompting", "meta_tags", "techniques"]
    
    for practice_type in practice_types:
        print(f"\n=== Wiki Best Practices: {practice_type} ===")
        
        result = await crawl_suno_wiki_best_practices(practice_type, ctx)
        
        # Check for actual data (not empty)
        practices = result["best_practices"]
        assert len(practices["prompting_guidelines"]) > 0, "No prompting guidelines found"
        
        print(f"✅ Retrieved {practice_type} practices successfully")
        
        # Display sample data
        if practice_type == "all" or practice_type == "prompting":
            guidelines = practices["prompting_guidelines"]
            print(f"Prompting guidelines ({len(guidelines)}):")
            for guideline in guidelines[:3]:  # Show first 3
                print(f"  • {guideline}")
        
        if practice_type == "all" or practice_type == "meta_tags":
            meta_tags = practices["meta_tag_usage"]
            print(f"Meta tag usage ({len(meta_tags)}):")
            for tag_info in meta_tags[:3]:  # Show first 3
                print(f"  • {tag_info['tag']}: {tag_info['description']}")
        
        if practice_type == "all" or practice_type == "techniques":
            techniques = practices["technique_tips"]
            print(f"Technique tips ({len(techniques)}):")
            for tip in techniques[:3]:  # Show first 3
                print(f"  • {tip['name']}: {tip['description']}")
        
        # Wiki data info
        wiki_data = result["wiki_data"]
        print(f"Data sources: {len(wiki_data['source_urls'])} URLs")
        print(f"Last updated: {wiki_data['last_updated']}")
        
        # Practical examples
        examples = result["practical_examples"]
        if examples:
            print(f"Practical examples: {len(examples)}")
    
    return result

asyncio.run(example_wiki_best_practices())
```

### 10. create_suno_commands

#### Suno Command Generation

```python
async def example_suno_command_creation():
    """Example of creating practical Suno AI commands"""
    
    # First generate personas
    character_text = """
    Zara Moon is an electronic music producer from Berlin's underground scene. 
    She creates atmospheric techno that blends organic field recordings with 
    synthetic textures, crafting soundscapes that tell stories of urban solitude 
    and digital connection.
    """
    
    ctx = Context()
    
    # Step 1: Character analysis
    character_result = await analyze_character_text(character_text, ctx)
    
    # Step 2: Generate personas
    persona_result = await generate_artist_personas(character_result, ctx)
    
    # Step 3: Create Suno commands
    command_result = await create_suno_commands(
        persona_data=persona_result,
        character_data=character_result,
        ctx=ctx
    )
    
    print("=== Suno Command Creation ===")
    
    # Generated commands
    commands = command_result["suno_commands"]
    print(f"Generated {len(commands)} Suno commands:")
    
    for i, cmd in enumerate(commands):
        print(f"\n{i+1}. {cmd}")
        
        # Verify command format
        assert "[" in cmd and "]" in cmd, f"Command {i+1} missing meta tags"
        assert len(cmd) > 20, f"Command {i+1} too short"
        print(f"   ✅ Command format valid")
    
    # Command breakdown
    breakdown = command_result["command_breakdown"]
    print(f"\nCommand breakdown:")
    
    for item in breakdown:
        print(f"\nCommand: {item['command']}")
        print(f"Purpose: {item['purpose']}")
        print(f"Meta tags: {item['meta_tags']}")
        print(f"Style elements: {item['style_elements']}")
        print(f"Persona connection: {item['persona_connection']}")
    
    # Meta tags used
    meta_tags = command_result["meta_tags_used"]
    print(f"\nMeta tags used: {meta_tags}")
    
    # Style parameters
    style_params = command_result["style_parameters"]
    print(f"Style parameters: {style_params}")
    
    # Generation metadata
    metadata = command_result["generation_metadata"]
    print(f"\nGeneration metadata:")
    print(f"  Commands generated: {metadata['commands_generated']}")
    print(f"  Persona compatibility: {metadata['persona_compatibility']:.2f}")
    print(f"  Suno format compliance: {metadata['suno_format_compliance']}")
    
    return command_result

asyncio.run(example_suno_command_creation())
```

### 11. understand_topic_with_emotions

#### Emotional Topic Analysis

```python
async def example_emotional_topic_analysis():
    """Example of meaningful emotional topic analysis"""
    
    test_topics = [
        {
            "topic": "The bittersweet feeling of leaving home for the first time",
            "context": "Young adult moving to college, mix of excitement and nostalgia"
        },
        {
            "topic": "Finding love after heartbreak",
            "context": "Someone who thought they'd never trust again"
        },
        {
            "topic": "The weight of unfulfilled dreams",
            "context": "Middle-aged person reflecting on paths not taken"
        }
    ]
    
    ctx = Context()
    
    for i, test_case in enumerate(test_topics):
        print(f"\n=== Emotional Analysis {i+1} ===")
        print(f"Topic: {test_case['topic']}")
        print(f"Context: {test_case['context']}")
        
        result = await understand_topic_with_emotions(
            topic=test_case["topic"],
            context=test_case["context"],
            ctx=ctx
        )
        
        # Emotional analysis
        emotions = result["emotional_analysis"]
        print(f"\nEmotional analysis:")
        print(f"  Primary emotions: {emotions['primary_emotions']}")
        print(f"  Emotional intensity: {emotions['emotional_intensity']:.2f}")
        print(f"  Contextual factors: {emotions['contextual_factors']}")
        
        # Verify not generic "contemplative" response
        assert "contemplative" not in emotions["primary_emotions"] or len(emotions["primary_emotions"]) > 1
        print(f"  ✅ Non-generic emotional analysis")
        
        # Musical recommendations
        music = result["musical_recommendations"]
        print(f"\nMusical recommendations:")
        print(f"  Genre suggestions: {music['genre_suggestions']}")
        print(f"  Tempo: {music['tempo_recommendations']}")
        print(f"  Key suggestions: {music['key_suggestions']}")
        print(f"  Instrumentation: {music['instrumentation']}")
        
        # Beat patterns
        patterns = result["beat_patterns"]
        print(f"\nBeat patterns ({len(patterns)}):")
        for pattern in patterns[:2]:  # Show first 2
            print(f"  • {pattern['pattern_name']} ({pattern['bpm_range']} BPM)")
            print(f"    {pattern['description']}")
            print(f"    Emotional fit: {pattern['emotional_fit']}")
        
        # Lyrical themes
        themes = result["lyrical_themes"]
        print(f"\nLyrical themes: {themes}")
        
        # Analysis metadata
        metadata = result["analysis_metadata"]
        print(f"\nAnalysis metadata:")
        print(f"  Topic complexity: {metadata['topic_complexity']:.2f}")
        print(f"  Emotional depth: {metadata['emotional_depth']:.2f}")
        print(f"  Musical alignment: {metadata['musical_alignment']:.2f}")

asyncio.run(example_emotional_topic_analysis())
```

## Integration Workflow Examples

### Complete Music Production Workflow

```python
async def complete_music_production_example():
    """Complete example from character description to Suno commands"""
    
    # Input character description
    character_description = """
    Amara Okafor is a Nigerian-American singer-songwriter who grew up between 
    Lagos and Brooklyn. Her music blends Afrobeat rhythms with contemporary R&B, 
    creating a sound that honors her heritage while speaking to her American 
    experience. She struggles with questions of identity and belonging, using 
    music as a bridge between her two worlds.
    """
    
    ctx = Context()
    
    print("=== Complete Music Production Workflow ===")
    
    # Step 1: Character Analysis
    print("\n1. Analyzing character...")
    character_result = await analyze_character_text(character_description, ctx)
    characters = character_result["characters"]
    print(f"   ✅ Found {len(characters)} character(s)")
    
    # Step 2: Generate Artist Personas
    print("\n2. Generating artist personas...")
    persona_result = await generate_artist_personas(character_result, ctx)
    personas = persona_result["personas"]
    print(f"   ✅ Generated {len(personas)} persona(s)")
    
    # Step 3: Analyze Psychology
    print("\n3. Analyzing artist psychology...")
    psychology_result = await analyze_artist_psychology(characters[0], ctx)
    personality_type = psychology_result["psychological_profile"]["personality_type"]
    print(f"   ✅ Personality type: {personality_type}")
    
    # Step 4: Get Best Practices
    print("\n4. Retrieving Suno best practices...")
    practices_result = await crawl_suno_wiki_best_practices("all", ctx)
    guidelines_count = len(practices_result["best_practices"]["prompting_guidelines"])
    print(f"   ✅ Retrieved {guidelines_count} guidelines")
    
    # Step 5: Create Suno Commands
    print("\n5. Creating Suno commands...")
    command_result = await create_suno_commands(persona_result, character_result, ctx)
    commands = command_result["suno_commands"]
    print(f"   ✅ Generated {len(commands)} commands")
    
    # Step 6: Create Character Album
    print("\n6. Creating character album...")
    album_result = await create_character_album(
        character_description=character_description,
        genre="afrobeat-r&b",
        album_theme="Between Worlds",
        track_count=5,
        ctx=ctx
    )
    tracks = album_result["tracks"]
    print(f"   ✅ Created album with {len(tracks)} tracks")
    
    # Final Results Summary
    print("\n=== Workflow Results Summary ===")
    
    # Character info
    main_character = StandardCharacterProfile.from_dict(characters[0])
    print(f"Artist: {main_character.name}")
    print(f"Background: {main_character.backstory[:100]}...")
    
    # Persona info
    main_persona = ArtistPersona.from_dict(personas[0])
    print(f"Genre: {main_persona.genre}")
    print(f"Style: {main_persona.style_description}")
    
    # Album info
    album_info = album_result["album_info"]
    print(f"Album: '{album_info['title']}'")
    print(f"Theme: {album_info['theme']}")
    
    # Sample Suno commands
    print(f"\nSample Suno commands:")
    for cmd in commands[:2]:
        print(f"  {cmd}")
    
    # Sample track
    sample_track = tracks[0]
    print(f"\nSample track: '{sample_track['title']}'")
    print(f"Lyrics preview: {sample_track['lyrics'][:150]}...")
    
    return {
        "character": character_result,
        "personas": persona_result,
        "psychology": psychology_result,
        "practices": practices_result,
        "commands": command_result,
        "album": album_result
    }

# Run complete workflow
if __name__ == "__main__":
    asyncio.run(complete_music_production_example())
```

### Error Handling Example

```python
async def error_handling_example():
    """Example of proper error handling with MCP tools"""
    
    # Test cases with potential issues
    test_cases = [
        {
            "name": "Valid input",
            "text": "John Smith is a jazz musician from New Orleans.",
            "should_succeed": True
        },
        {
            "name": "Empty text",
            "text": "",
            "should_succeed": False
        },
        {
            "name": "No clear characters",
            "text": "The music was beautiful.",
            "should_succeed": False
        }
    ]
    
    ctx = Context()
    
    for test_case in test_cases:
        print(f"\n=== Testing: {test_case['name']} ===")
        
        try:
            result = await analyze_character_text(test_case["text"], ctx)
            
            if test_case["should_succeed"]:
                print("✅ Test passed as expected")
                characters = result["characters"]
                print(f"   Found {len(characters)} characters")
            else:
                print("⚠️  Test succeeded but was expected to fail")
                
        except Exception as e:
            if not test_case["should_succeed"]:
                print("✅ Test failed as expected")
                print(f"   Error: {e}")
            else:
                print("❌ Test failed unexpectedly")
                print(f"   Error: {e}")

asyncio.run(error_handling_example())
```

## Best Practices for Using MCP Tools

### 1. Input Validation

```python
def validate_character_input(text: str) -> bool:
    """Validate text input for character analysis"""
    
    if not text or len(text.strip()) < 50:
        return False, "Text too short for meaningful character analysis"
    
    # Check for character indicators
    character_indicators = [
        "name", "character", "person", "musician", "artist",
        "he ", "she ", "they ", "his ", "her ", "their "
    ]
    
    text_lower = text.lower()
    if not any(indicator in text_lower for indicator in character_indicators):
        return False, "Text doesn't appear to contain character descriptions"
    
    return True, "Valid input"

# Usage
is_valid, message = validate_character_input(input_text)
if not is_valid:
    print(f"Input validation failed: {message}")
```

### 2. Result Verification

```python
def verify_tool_results(result: Dict[str, Any], tool_name: str) -> bool:
    """Verify tool results meet quality standards"""
    
    if tool_name == "analyze_character_text":
        characters = result.get("characters", [])
        if len(characters) == 0:
            return False, "No characters found"
        
        for char_data in characters:
            if not char_data.get("name"):
                return False, "Character missing name"
    
    elif tool_name == "generate_artist_personas":
        personas = result.get("personas", [])
        if len(personas) == 0:
            return False, "No personas generated"
        
        for persona_data in personas:
            if not persona_data.get("genre"):
                return False, "Persona missing genre"
    
    return True, "Results valid"

# Usage
is_valid, message = verify_tool_results(result, "analyze_character_text")
if not is_valid:
    print(f"Result verification failed: {message}")
```

### 3. Performance Monitoring

```python
import time
from typing import Dict, Any, Callable

async def monitor_tool_performance(
    tool_func: Callable,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Monitor tool performance and results"""
    
    start_time = time.time()
    
    try:
        result = await tool_func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        return {
            "result": result,
            "performance": {
                "execution_time": execution_time,
                "success": True,
                "error": None
            }
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        
        return {
            "result": None,
            "performance": {
                "execution_time": execution_time,
                "success": False,
                "error": str(e)
            }
        }

# Usage
monitored_result = await monitor_tool_performance(
    analyze_character_text,
    input_text,
    ctx
)

if monitored_result["performance"]["success"]:
    print(f"Tool executed in {monitored_result['performance']['execution_time']:.2f}s")
else:
    print(f"Tool failed: {monitored_result['performance']['error']}")
```

This comprehensive examples document provides working code for all MCP tools, demonstrating proper usage patterns, error handling, and integration workflows. Each example includes expected outputs and verification steps to ensure the tools are working correctly.