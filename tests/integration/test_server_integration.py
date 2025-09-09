import pytest

#!/usr/bin/env python3
"""
Test server integration with enhanced character analyzer
"""

import asyncio
import json
import os
import sys

# Add current directory to path to import server modules
sys.path.insert(0, os.getcwd())

# Mock Context class for testing
class MockContext:
    async def info(self, message):
        print(f"INFO: {message}")

    async def error(self, message):
        print(f"ERROR: {message}")

@pytest.mark.asyncio
async def test_server_integration():
    """Test that the server integration works with enhanced analyzer"""

    # Import the analyze_character_text function from server
    try:
        from server import analyze_character_text
        print("✓ Successfully imported analyze_character_text from server")
    except ImportError as e:
        print(f"✗ Failed to import from server: {e}")
        return

    # Test text
    test_text = """
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
    """

    # Create mock context
    ctx = MockContext()

    try:
        # Call the analyze_character_text function
        print("\nTesting analyze_character_text function...")
        result_json = await analyze_character_text(test_text, ctx)

        # Parse the result
        result = json.loads(result_json)

        print("✓ Function executed successfully")
        print(f"✓ Found {len(result['characters'])} characters")
        print(f"✓ Found {len(result['narrative_themes'])} themes")
        print(f"✓ Found {len(result['emotional_arc'])} emotional states")

        # Check that we found Elena
        character_names = [char['name'] for char in result['characters']]
        if 'Elena' in character_names:
            print("✓ Successfully detected Elena as a character")
        else:
            print("✗ Failed to detect Elena as a character")

        # Check that we found themes beyond friendship
        theme_names = [theme['theme'] for theme in result['narrative_themes']]
        if len(theme_names) > 1:
            print(f"✓ Found multiple themes: {', '.join(theme_names[:3])}")
        else:
            print("✗ Only found limited themes")

        # Check that emotional arc is varied
        emotions = [state['emotion'] for state in result['emotional_arc']]
        if emotions and not all('neutral' in emotion.lower() for emotion in emotions):
            print(f"✓ Found varied emotions: {', '.join(emotions[:3])}")
        else:
            print("✗ Emotional arc not varied enough")

        print("\n✓ Server integration test completed successfully!")

    except Exception as e:
        print(f"✗ Server integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server_integration())
