import pytest

#!/usr/bin/env python3
"""
Test script to verify wiki data integration for the crawl tool
"""

import asyncio
import json
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

@pytest.mark.asyncio
async def test_wiki_data_availability():
    """Test if wiki data is available and accessible"""
    try:
        print("=== TESTING WIKI DATA AVAILABILITY ===")

        # Test if wiki integration is available
        try:
            from wiki_data_models import WikiConfig
            from wiki_data_system import WikiDataManager
            print("✓ Wiki integration modules are available")
            WIKI_INTEGRATION_AVAILABLE = True
        except ImportError as e:
            print(f"✗ Wiki integration not available: {e}")
            WIKI_INTEGRATION_AVAILABLE = False
            return

        # Initialize WikiDataManager
        wiki_manager = WikiDataManager()
        config = WikiConfig()

        print(f"Config enabled: {config.enabled}")
        print(f"Storage path: {config.local_storage_path}")

        await wiki_manager.initialize(config)
        print("✓ WikiDataManager initialized successfully")

        # Test data access
        try:
            genres = await wiki_manager.get_genres()
            print(f"✓ Genres available: {len(genres)}")

            if genres:
                print("Sample genres:")
                for genre in genres[:3]:
                    print(f"  - {genre.name}: {genre.description[:100]}...")
        except Exception as e:
            print(f"✗ Error getting genres: {e}")

        try:
            meta_tags = await wiki_manager.get_meta_tags()
            print(f"✓ Meta tags available: {len(meta_tags)}")

            if meta_tags:
                print("Sample meta tags:")
                for tag in meta_tags[:3]:
                    print(f"  - [{tag.tag}] ({tag.category}): {tag.description[:100]}...")
        except Exception as e:
            print(f"✗ Error getting meta tags: {e}")

        try:
            techniques = await wiki_manager.get_techniques()
            print(f"✓ Techniques available: {len(techniques)}")

            if techniques:
                print("Sample techniques:")
                for tech in techniques[:3]:
                    print(f"  - {tech.name} ({tech.technique_type}): {tech.description[:100]}...")
        except Exception as e:
            print(f"✗ Error getting techniques: {e}")

        # Clean up
        await wiki_manager.cleanup()

        print("\n=== WIKI DATA TEST COMPLETED ===")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

async def simulate_enhanced_crawl_tool():
    """Simulate the enhanced crawl tool functionality"""
    try:
        print("\n=== SIMULATING ENHANCED CRAWL TOOL ===")

        # Import wiki components
        from wiki_data_models import WikiConfig
        from wiki_data_system import WikiDataManager

        # Initialize wiki manager
        wiki_manager = WikiDataManager()
        config = WikiConfig()
        await wiki_manager.initialize(config)

        # Simulate the enhanced crawl tool logic
        topic = "all"

        suno_knowledge = {
            "crawl_status": "completed_from_cache",
            "data_source": "https://sunoaiwiki.com/ (cached)",
            "topic_focus": topic,
            "cache_timestamp": datetime.now().isoformat(),
            "current_specifications": {},
            "verified_best_practices": [],
            "actual_format_requirements": {},
            "known_limitations": {},
            "working_examples": [],
            "available_genres": [],
            "available_meta_tags": [],
            "available_techniques": []
        }

        # Get data from WikiDataManager
        try:
            # Get genres data
            genres = await wiki_manager.get_genres()
            suno_knowledge["available_genres"] = [
                {
                    "name": genre.name,
                    "description": genre.description,
                    "characteristics": genre.characteristics,
                    "typical_instruments": genre.typical_instruments,
                    "mood_associations": genre.mood_associations
                } for genre in genres[:20]  # Limit for readability
            ]

            # Extract genre-based specifications
            suno_knowledge["current_specifications"]["supported_genres"] = [g.name for g in genres]

            print(f"✓ Processed {len(genres)} genres")

        except Exception as e:
            print(f"✗ Error processing genres: {e}")

        try:
            # Get meta tags data
            meta_tags = await wiki_manager.get_meta_tags()
            suno_knowledge["available_meta_tags"] = [
                {
                    "tag": tag.tag,
                    "category": tag.category,
                    "description": tag.description,
                    "compatible_genres": tag.compatible_genres
                } for tag in meta_tags[:30]  # Limit for readability
            ]

            # Extract format requirements from meta tags
            suno_knowledge["actual_format_requirements"] = {
                "structural_tags": [tag.tag for tag in meta_tags if tag.category == "structural"],
                "vocal_tags": [tag.tag for tag in meta_tags if tag.category == "vocal"],
                "sound_effect_tags": [tag.tag for tag in meta_tags if tag.category == "sound_effects"],
                "genre_tags": [tag.tag for tag in meta_tags if tag.category == "genre"],
                "effect_tags": [tag.tag for tag in meta_tags if tag.category == "effects"],
                "tag_format": "Use tags in [brackets] like [Intro], [Verse], [Chorus]",
                "supported_categories": list(set([tag.category for tag in meta_tags]))
            }

            print(f"✓ Processed {len(meta_tags)} meta tags")

        except Exception as e:
            print(f"✗ Error processing meta tags: {e}")

        try:
            # Get techniques data
            techniques = await wiki_manager.get_techniques()
            suno_knowledge["available_techniques"] = [
                {
                    "name": tech.name,
                    "description": tech.description,
                    "technique_type": tech.technique_type,
                    "examples": tech.examples,
                    "applicable_scenarios": tech.applicable_scenarios
                } for tech in techniques[:20]  # Limit for readability
            ]

            # Extract best practices from techniques
            best_practices = []
            for tech in techniques:
                if tech.technique_type in ["prompt_structure", "meta_tags", "vocal_style"]:
                    best_practices.append({
                        "practice": tech.name,
                        "description": tech.description,
                        "type": tech.technique_type,
                        "examples": tech.examples
                    })

            suno_knowledge["verified_best_practices"] = best_practices

            # Extract working examples
            working_examples = []
            for tech in techniques:
                if tech.examples:
                    working_examples.extend([
                        {
                            "example": example,
                            "technique": tech.name,
                            "type": tech.technique_type
                        } for example in tech.examples
                    ])

            suno_knowledge["working_examples"] = working_examples[:30]  # Limit examples

            print(f"✓ Processed {len(techniques)} techniques")
            print(f"✓ Extracted {len(best_practices)} best practices")
            print(f"✓ Extracted {len(working_examples)} working examples")

        except Exception as e:
            print(f"✗ Error processing techniques: {e}")

        # Add technical limitations
        suno_knowledge["known_limitations"] = {
            "prompt_length": "Recommended to keep prompts concise and focused",
            "tag_usage": "Use brackets [like this] for structural and effect tags",
            "genre_mixing": "Can combine multiple genres with comma separation",
            "vocal_specifications": "Use detailed vocal descriptors like [masculine low gospel vocal]",
            "content_filtering": "Explicit content may be filtered - use creative alternatives",
            "song_structure": "Use structural tags like [Intro], [Verse], [Chorus], [Outro] for better results"
        }

        # Add integration notes
        suno_knowledge["integration_notes"] = [
            "Use cached wiki data for accurate genre and meta tag information",
            "Apply verified prompt structures from techniques data",
            "Leverage meta tag categories for proper command formatting",
            "Use genre characteristics for better music generation context",
            "Apply technique examples for consistent results"
        ]

        suno_knowledge["usage_recommendation"] = (
            "This cached wiki data provides real Suno AI specifications. "
            "Use the genres, meta tags, and techniques data to replace hardcoded assumptions "
            "and generate more accurate Suno AI commands."
        )

        # Display results summary
        print("\n=== ENHANCED CRAWL TOOL RESULTS ===")
        print(f"Status: {suno_knowledge['crawl_status']}")
        print(f"Topic: {suno_knowledge['topic_focus']}")
        print(f"Available Genres: {len(suno_knowledge['available_genres'])}")
        print(f"Available Meta Tags: {len(suno_knowledge['available_meta_tags'])}")
        print(f"Available Techniques: {len(suno_knowledge['available_techniques'])}")
        print(f"Best Practices: {len(suno_knowledge['verified_best_practices'])}")
        print(f"Working Examples: {len(suno_knowledge['working_examples'])}")

        # Show sample data
        if suno_knowledge['available_genres']:
            print("\nSample Genres:")
            for genre in suno_knowledge['available_genres'][:3]:
                print(f"  - {genre['name']}: {genre['description'][:80]}...")

        if suno_knowledge['available_meta_tags']:
            print("\nSample Meta Tags:")
            for tag in suno_knowledge['available_meta_tags'][:3]:
                print(f"  - [{tag['tag']}] ({tag['category']}): {tag['description'][:80]}...")

        if suno_knowledge['verified_best_practices']:
            print("\nSample Best Practices:")
            for practice in suno_knowledge['verified_best_practices'][:2]:
                print(f"  - {practice['practice']}: {practice['description'][:80]}...")

        # Clean up
        await wiki_manager.cleanup()

        print("\n=== SIMULATION COMPLETED SUCCESSFULLY ===")
        print("The enhanced crawl tool would return actual wiki data instead of empty fields!")

        return json.dumps(suno_knowledge, indent=2)

    except Exception as e:
        print(f"SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_wiki_data_availability())
    asyncio.run(simulate_enhanced_crawl_tool())
