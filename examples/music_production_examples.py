#!/usr/bin/env python3
"""
Music Production Company Workflow Examples

Demonstrates the enhanced character-to-music production pipeline with
artist stories, producer guidance, and music bible generation.
"""

import asyncio

# ================================================================================================
# EXAMPLE 1: Complete Music Production Workflow
# ================================================================================================

async def example_complete_production_workflow():
    """
    Example of the full music production company workflow
    From narrative text to complete music bible with Suno commands
    """

    # Sample narrative text
    narrative_text = """
    Sarah Chen stood at the edge of the rooftop, city lights blurring through tears she refused
    to acknowledge. Twenty-seven years of perfect grades, perfect smile, perfect daughter—all
    crumbling like the facade it had always been. The weight of others' expectations had carved
    hollows in her chest where dreams used to live. Her phone buzzed with another message from
    her mother about the promotion she'd just rejected, choosing instead this moment of raw truth.
    The wind carried away her whispered confession: "I never wanted to be perfect. I wanted to be
    real." Below, the city hummed its indifferent symphony, but for the first time, Sarah heard
    her own voice rising above the noise—fragile, frightened, but finally, devastatingly free.
    """

    print("=== COMPLETE MUSIC PRODUCTION WORKFLOW ===\n")

    # Step 1: Character Analysis
    print("Step 1: Analyzing character using three-layer methodology...")
    character_analysis = {
        "tool": "analyze_character",
        "input": {
            "narrative_text": narrative_text,
            "analysis_depth": "comprehensive"
        },
        "expected_output": {
            "characters": [{
                "name": "Sarah Chen",
                "aliases": [],
                "physical_description": "27-year-old woman on a rooftop",
                "mannerisms": ["refusing to acknowledge tears", "whispering confessions"],
                "speech_patterns": ["raw honesty", "emotional revelation"],
                "behavioral_traits": ["perfectionist facade", "breaking free"],
                "backstory": "Lifetime of meeting others' expectations, perfect daughter role",
                "relationships": ["controlling mother", "societal pressures"],
                "formative_experiences": ["constant pressure for perfection", "recent job rejection"],
                "social_connections": ["family expectations", "professional obligations"],
                "motivations": ["authenticity", "self-discovery", "freedom"],
                "fears": ["disappointing others", "being truly seen", "vulnerability"],
                "desires": ["to be real", "authentic self-expression", "emotional freedom"],
                "conflicts": ["perfection vs authenticity", "others' dreams vs own dreams"],
                "personality_drivers": ["need for truth", "emotional liberation"],
                "confidence_score": 0.95,
                "importance_score": 1.0
            }]
        }
    }

    # Step 2: Generate Artist Story
    print("\nStep 2: Creating introspective artist story...")
    artist_story = {
        "tool": "generate_artist_story",
        "input": {
            "character_data": character_analysis["expected_output"]["characters"][0]
        },
        "expected_output": {
            "origin_narrative": "Born from a lifetime of meeting others' expectations, shaped by constant pressure for perfection, this artist emerged from the depths of perfection vs authenticity to find their voice through music.",
            "introspective_themes": [
                "confronting disappointing others",
                "confronting being truly seen",
                "searching for authentic self-expression",
                "searching for emotional freedom",
                "reconciling perfection vs authenticity"
            ],
            "personal_journey": "A journey driven by authenticity, marked by 2 significant relationships, each song a chapter in understanding need for truth.",
            "artistic_manifesto": "Music as a weapon against disappointing others, every note a declaration of authenticity. Raw truth over polished lies.",
            "album_concepts": [
                {
                    "title": "Shadows and Light",
                    "theme": "Exploring the duality of perfection vs authenticity",
                    "narrative": "A sonic journey through internal battles"
                },
                {
                    "title": "Echoes of Connection",
                    "theme": "The impact of relationships on identity",
                    "narrative": "Stories of 2 souls intertwined"
                },
                {
                    "title": "Chasing Horizons",
                    "theme": "The pursuit of authentic self-expression",
                    "narrative": "An odyssey of longing and discovery"
                }
            ],
            "emotional_arc": "From isolation through struggle to acceptance",
            "key_life_moments": [
                "The moment when constant pressure for perfection",
                "The moment when recent job rejection"
            ],
            "artistic_evolution": "From perfectionist facade observer to bold storyteller, driven by need for truth"
        }
    }

    # Step 3: Generate Musical Persona
    print("\nStep 3: Creating musical persona...")
    musical_persona = {
        "tool": "generate_musical_persona",
        "input": {
            "character_profile": character_analysis["expected_output"]["characters"][0]
        },
        "expected_output": {
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
            "genre_justification": "Indie's raw authenticity matches her journey from perfection to truth"
        }
    }

    # Step 4: Producer Analysis
    print("\nStep 4: AI Producer analyzing production needs...")
    producer_analysis = {
        "tool": "analyze_production",
        "input": {
            "artist_persona_data": musical_persona["expected_output"],
            "artist_story_data": artist_story["expected_output"]
        },
        "expected_output": {
            "production_style": "Minimal, authentic production emphasizing emotional rawness",
            "prompt_complexity": "detailed",
            "meta_tag_strategy": [
                "[Verse] [Introspective]",
                "[Chorus] [Emotional Peak]",
                "[Bridge] [Revelation]",
                "[Lo-fi]",
                "[Intimate]",
                "[Raw Production]"
            ],
            "version_preference": "V3.5",
            "genre_nuances": {
                "recommended": [
                    "Use [Raw Vocals] for authenticity",
                    "Keep production minimal"
                ],
                "avoid": ["overproduced effects", "heavy compression"],
                "signature_elements": ["[Lo-fi]", "[Intimate]", "[Raw Production]"]
            },
            "chord_progression_hints": [
                "Minor key progression",
                "i-iv-i-v pattern",
                "Suspended chords for tension"
            ],
            "vocal_style_tags": ["[Emotional Vocals]", "[Vulnerable Delivery]", "[Raw Intensity]"],
            "vocal_effect_preferences": ["Minimal processing", "Subtle reverb for space"],
            "mixing_preferences": {
                "vocals": "Upfront and dry",
                "instruments": "Spacious with natural dynamics",
                "overall": "Emphasis on clarity and emotion"
            },
            "sound_palette": ["acoustic guitar", "minimal piano", "Warm analog textures", "Room ambience"],
            "reference_artists": ["Phoebe Bridgers", "Bon Iver"],
            "collaboration_approach": "Solo focus with minimal external collaboration"
        }
    }

    # Step 5: Get Suno Knowledge
    print("\nStep 5: Fetching Suno AI best practices...")

    # Step 6: Create Music Bible
    print("\nStep 6: Creating comprehensive music bible...")
    music_bible = {
        "tool": "create_music_bible",
        "input": {
            "character_data": character_analysis["expected_output"]["characters"][0],
            "artist_persona_data": musical_persona["expected_output"],
            "artist_story_data": artist_story["expected_output"],
            "producer_profile_data": producer_analysis["expected_output"]
        },
        "expected_output": {
            "summary": {
                "artist_name": "Fragile Freedom",
                "artist_description": "Fragile Freedom emerges from the urban landscape as a vulnerable storyteller who crafts intimate confessions, channeling the tension between perfection and authenticity into raw truth over polished perfection through indie soundscapes that confront listeners with uncomfortable truths.",
                "production_approach": "Minimal, authentic production emphasizing emotional rawness",
                "total_songs": 5,
                "album_concept": "A sonic autobiography following From isolation through struggle to acceptance...",
                "key_themes": [
                    "confronting disappointing others",
                    "confronting being truly seen",
                    "searching for authentic self-expression"
                ]
            },
            "song_blueprints": [
                {
                    "title": "Shadows of Others",
                    "character_inspiration": "Sarah Chen's perfection vs authenticity",
                    "introspective_angle": "confronting disappointing others",
                    "primary_prompt": "Introspective indie exploring confronting disappointing others, vulnerable and raw emotional delivery vocals with Minimal, authentic production emphasizing emotional rawness. Raw honesty meets acoustic guitar.",
                    "meta_tags": ["[Verse]", "[Chorus]", "[Bridge]", "[Intense]", "[Building Tension]", "[Emotional Vocals]", "[Vulnerable Delivery]"],
                    "vocal_delivery_notes": "Intimate delivery, close-mic technique, breath as emotion",
                    "emotional_arc": "Tension → Recognition → Catharsis"
                }
            ],
            "prompt_templates": [
                "Introspective indie with [Emotional Vocals], exploring [THEME], melancholic indie with vulnerable vocals",
                "Story-driven indie about [NARRATIVE], Minimal, authentic production emphasizing emotional rawness, featuring acoustic guitar",
                "Experimental indie fusion, [EMOTION] journey, blending alternative elements"
            ],
            "production_philosophy": "Every production choice serves the story. Minimal, authentic production emphasizing emotional rawness allows Music as a weapon against disappointing others, every note a declaration of authenticity. Raw truth over polished lies. Technical excellence never overshadows emotional truth."
        }
    }

    # Step 7: Generate Suno Commands
    print("\nStep 7: Creating optimized Suno AI commands...")
    suno_commands = {
        "tool": "create_suno_command",
        "input": {
            "artist_persona": musical_persona["expected_output"],
            "character_profile": character_analysis["expected_output"]["characters"][0]
        },
        "expected_output": {
            "commands": [
                {
                    "command_type": "simple",
                    "prompt": "A indie song about authenticity vs facade, conveying fragility with vulnerable and raw emotional delivery. Inspired by Sarah Chen's journey and experiences.",
                    "style_tags": ["[Lo-fi]", "[Intimate]", "[Raw Production]"]
                },
                {
                    "command_type": "custom",
                    "prompt": "Vulnerable indie confession, acoustic guitar and minimal piano, raw vocals exploring the weight of perfection, building from whispered verses to emotional chorus, Sarah Chen's rooftop revelation",
                    "style_tags": ["[Intimate Production]", "[Emotional Build]", "[Raw Vocals]", "[Minimal]"]
                },
                {
                    "command_type": "bracket_notation",
                    "prompt": "[Intro] [Soft Acoustic Guitar] [Whispered]\n[Verse 1] [Vulnerable] Twenty-seven years of perfect smiles / Crumbling facades and hidden trials\n[Pre-Chorus] [Building] The weight of dreams that were never mine\n[Chorus] [Emotional Peak] [Raw] I choose to be real, not perfect / Let the tears fall, I'm worth it\n[Bridge] [Revelation] [Fragile] Finally free, devastatingly me\n[Outro] [Acceptance] [Soft]"
                }
            ]
        }
    }

    print("\n=== WORKFLOW COMPLETE ===")
    print("\nGenerated Output Summary:")
    print(f"- Artist Name: {musical_persona['expected_output']['artist_name']}")
    print(f"- Production Style: {producer_analysis['expected_output']['production_style']}")
    print(f"- Album Concept: {artist_story['expected_output']['album_concepts'][0]['title']}")
    print(f"- Total Song Blueprints: {music_bible['expected_output']['summary']['total_songs']}")
    print(f"- Suno Command Variations: {len(suno_commands['expected_output']['commands'])}")

    return {
        "character": character_analysis,
        "story": artist_story,
        "persona": musical_persona,
        "producer": producer_analysis,
        "bible": music_bible,
        "commands": suno_commands
    }

# ================================================================================================
# EXAMPLE 2: Introspective Music Focus
# ================================================================================================

async def example_introspective_music_generation():
    """
    Example focused on generating deeply introspective music
    from character psychological profiles
    """

    print("\n=== INTROSPECTIVE MUSIC GENERATION ===\n")

    # Character with deep internal conflicts
    character_profile = {
        "name": "Marcus Rivera",
        "fears": ["abandonment", "never being enough", "losing himself in others' needs"],
        "desires": ["unconditional acceptance", "creative freedom", "genuine connection"],
        "conflicts": ["loyalty vs self-preservation", "tradition vs innovation"],
        "motivations": ["healing generational trauma", "building authentic community"],
        "formative_experiences": ["father's departure at age 7", "finding solace in music", "grandmother's last words about staying true"]
    }

    # Generate introspective themes
    print("Extracting introspective themes from psychological profile...")
    introspective_themes = [
        "confronting abandonment",
        "searching for unconditional acceptance",
        "reconciling loyalty vs self-preservation",
        "healing generational trauma"
    ]

    # Create song concepts
    print("\nGenerating introspective song concepts...")
    song_concepts = [
        {
            "title": "Empty Chairs",
            "theme": "confronting abandonment",
            "prompt": "Haunting indie ballad about empty spaces left by those who leave, [Whispered Verses] building to [Cathartic Chorus], minimal piano and distant echoes",
            "emotional_journey": "Loss → Anger → Understanding → Self-reliance"
        },
        {
            "title": "Mirrors and Masks",
            "theme": "searching for unconditional acceptance",
            "prompt": "Vulnerable folk exploring the faces we wear for others, [Raw Vocals] [Acoustic Guitar] [Building Intensity], stripping away pretense layer by layer",
            "emotional_journey": "Performance → Exhaustion → Revelation → Authenticity"
        },
        {
            "title": "Bloodlines",
            "theme": "healing generational trauma",
            "prompt": "Atmospheric indie confronting inherited pain, [Spoken Word Intro] [Emotional Verses] [Powerful Bridge], breaking cycles through understanding",
            "emotional_journey": "Recognition → Confrontation → Forgiveness → Liberation"
        }
    ]

    print("\nIntrospective Album Narrative:")
    print("'Letters to My Ghosts' - A journey through the shadows of abandonment to the light of self-acceptance.")
    print("Each song peels back layers of protection to reveal the raw truth beneath.")

    return {
        "character": character_profile,
        "themes": introspective_themes,
        "songs": song_concepts
    }

# ================================================================================================
# EXAMPLE 3: Producer Tool Focus
# ================================================================================================

async def example_producer_guidance():
    """
    Example showcasing the AI Producer tool's capabilities
    for creating detailed production guidance
    """

    print("\n=== AI PRODUCER GUIDANCE EXAMPLE ===\n")

    # Artist requiring production guidance
    artist_info = {
        "artist_name": "Echoing Silence",
        "genre": "electronic",
        "themes": ["isolation in digital age", "human connection through screens"],
        "vocal_style": "ethereal and processed",
        "emotional_core": "melancholic hope"
    }

    print("Producer Analysis for:", artist_info["artist_name"])
    print("\nProduction Recommendations:")

    production_guide = {
        "overall_approach": "Contrast cold digital textures with warm human elements",
        "sound_design": {
            "foundation": "Analog-modeled synthesizers for warmth",
            "textures": "Glitchy artifacts representing digital interference",
            "space": "Generous reverb suggesting vast digital landscapes"
        },
        "vocal_production": {
            "main_chain": "Light autotune for otherworldly quality",
            "effects": "Delay throws on emotional phrases",
            "layering": "Whispered doubles for intimacy"
        },
        "arrangement_tips": {
            "intro": "Start with isolated glitch sounds, gradually humanize",
            "verses": "Sparse, leave room for vocal vulnerability",
            "chorus": "Full spectrum warmth contrasting verse emptiness",
            "bridge": "Strip to raw vocal with single analog pad"
        },
        "suno_optimization": {
            "meta_tags": ["[Ethereal]", "[Glitch]", "[Ambient]", "[Emotional]"],
            "prompt_structure": "Melancholic electronic exploring {theme}, ethereal processed vocals over glitchy production, analog warmth meets digital cold",
            "avoid": "Harsh digital distortion that masks emotion"
        },
        "reference_tracks": {
            "production": "James Blake - 'Retrograde'",
            "vocals": "FKA twigs - 'Two Weeks'",
            "atmosphere": "Arca - 'Desafío'"
        }
    }

    print("\nKey Production Philosophy:")
    print("'Technology as a medium for human emotion, not a barrier to it.'")

    return production_guide

# ================================================================================================
# EXAMPLE 4: Music Bible Usage
# ================================================================================================

async def example_music_bible_usage():
    """
    Example showing how to use a generated Music Bible
    for actual music production
    """

    print("\n=== USING YOUR MUSIC BIBLE ===\n")

    # Sample Music Bible excerpt
    music_bible_excerpt = {
        "artist": "Fragile Freedom",
        "album": "Letters to Yesterday",
        "production_philosophy": "Raw truth over polished perfection",
        "song_blueprint": {
            "title": "Rooftop Confessions",
            "recording_notes": {
                "vocals": "Single take preferred, keep breath sounds",
                "guitar": "Fingerpicked, slight fret noise is good",
                "ambience": "Record actual room tone, not artificial reverb"
            },
            "suno_prompt": "Intimate indie confession, [Whispered Intro] 'I never wanted to be perfect' [Vulnerable Verse] fingerpicked guitar and breath, [Building Chorus] emotional release, [Soft Outro] acceptance",
            "meta_tags": ["[Raw Recording]", "[Emotional Build]", "[Intimate]"],
            "performance_notes": "Channel the rooftop moment - fragile but free"
        }
    }

    print("Step-by-Step Production Process:")
    print("\n1. PRE-PRODUCTION")
    print("   - Review emotional arc: Confession → Vulnerability → Liberation")
    print("   - Set up intimate recording space")
    print("   - Prepare artist mentally for vulnerable performance")

    print("\n2. SUNO GENERATION")
    print("   - Use primary prompt first")
    print("   - If needed, try variations with different meta tag orders")
    print("   - Save seeds that capture the right emotion")

    print("\n3. PRODUCTION NOTES")
    print("   - Vocal approach:", music_bible_excerpt["song_blueprint"]["recording_notes"]["vocals"])
    print("   - Instrumental:", music_bible_excerpt["song_blueprint"]["recording_notes"]["guitar"])
    print("   - Atmosphere:", music_bible_excerpt["song_blueprint"]["recording_notes"]["ambience"])

    print("\n4. QUALITY CHECK")
    print("   - Does it feel authentic rather than performed?")
    print("   - Is the vulnerability palpable?")
    print("   - Does it serve the story?")

    return music_bible_excerpt

# ================================================================================================
# EXAMPLE 5: Troubleshooting Common Issues
# ================================================================================================

async def example_troubleshooting():
    """
    Example of troubleshooting common issues in the workflow
    """

    print("\n=== TROUBLESHOOTING GUIDE ===\n")

    issues_and_solutions = {
        "Issue: Generic Suno Output": {
            "symptoms": "Music sounds like typical genre without character depth",
            "solutions": [
                "Add more specific emotional descriptors",
                "Use character-specific metaphors in prompts",
                "Layer meta tags gradually instead of all at once",
                "Reference specific moments from character story"
            ],
            "example_fix": "Instead of 'sad indie song', use 'vulnerable indie exploring the weight of others' dreams, whispered confessions over fingerpicked guitar'"
        },
        "Issue: Conflicting Musical Elements": {
            "symptoms": "Genre and emotional tone don't align",
            "solutions": [
                "Ensure genre matches character psychology",
                "Use bridging elements between contrasting sections",
                "Simplify to core emotion first, add complexity later"
            ],
            "example_fix": "For internal conflict, use dynamic shifts: [Soft Doubt] to [Powerful Resolution]"
        },
        "Issue: Lost Character Voice": {
            "symptoms": "Music doesn't reflect character's unique perspective",
            "solutions": [
                "Return to character's key quotes or moments",
                "Use character's specific fears/desires as lyrical themes",
                "Incorporate character's speech patterns into vocal style"
            ],
            "example_fix": "Sarah's 'I wanted to be real' becomes the central hook with raw, unpolished delivery"
        },
        "Issue: Overproduced Sound": {
            "symptoms": "Production overshadows emotional authenticity",
            "solutions": [
                "Reduce effect tags",
                "Emphasize [Raw], [Minimal], [Intimate]",
                "Strip back to voice + one instrument first"
            ],
            "example_fix": "Remove [Epic Production], add [Bedroom Recording] [Honest]"
        }
    }

    print("Quick Diagnostic Questions:")
    print("1. Can you hear the character's story in the music?")
    print("2. Does the production serve or distract from the emotion?")
    print("3. Would the character actually create this music?")
    print("4. Is the vulnerability authentic or performed?")

    return issues_and_solutions

# ================================================================================================
# MAIN EXECUTION
# ================================================================================================

async def main():
    """Run all examples"""
    print("MUSIC PRODUCTION COMPANY WORKFLOW EXAMPLES")
    print("=" * 50)

    # Run examples
    await example_complete_production_workflow()
    await example_introspective_music_generation()
    await example_producer_guidance()
    await example_music_bible_usage()
    await example_troubleshooting()

    print("\n" + "=" * 50)
    print("EXAMPLES COMPLETE")
    print("\nThese examples demonstrate the full capabilities of the enhanced")
    print("character-driven music production system. Use them as templates")
    print("for your own creative projects.")

if __name__ == "__main__":
    asyncio.run(main())
